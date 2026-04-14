#!/usr/bin/env python3
"""FormalMATH benchmark — Knuckledragger+SymPy pipeline on 5,560 math problems.

First non-Lean result on FormalMATH. Current SOTA: 16.46% (Kimina-Prover, Lean 4).

Usage:
    python benchmarks/formalmath_bench.py --model gpt-5.4-mini --n 30   # test run
    python benchmarks/formalmath_bench.py --model gpt-5.4-mini --n 500  # full stratified
"""
from __future__ import annotations

import argparse
import json
import logging
import os
import random
import sys
import time
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from benchmarks.kd_bench_v3 import attempt_problem
from benchmarks.kd_bench import SYSTEM as BASE_SYSTEM, build_prompt  # noqa: F401
from benchmarks.minif2f_bench import get_provider

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Dataset loading with stratified sampling
# ---------------------------------------------------------------------------

def load_formalmath(n: int | None = None, seed: int = 42) -> list[dict]:
    """Load FormalMATH from HuggingFace with stratified sampling by top-level domain."""
    from datasets import load_dataset

    ds = load_dataset("SphereLab/FormalMATH-All")["train"]
    logger.info("Loaded FormalMATH: %d total problems", len(ds))

    # Parse all problems
    all_problems = []
    for row in ds:
        domain_full = row.get("domain", "Unknown")
        top_domain = domain_full.split(" -> ")[0].strip() if " -> " in domain_full else domain_full.strip()
        all_problems.append({
            "id": row["theorem_names"],
            "statement": row["refined_statement"],
            "proof_hint": row.get("solution", ""),
            "domain": domain_full,
            "top_domain": top_domain,
            "source": row.get("source", ""),
        })

    # Domain distribution
    domain_counts = Counter(p["top_domain"] for p in all_problems)
    logger.info("Domain distribution (full dataset):")
    for d, c in domain_counts.most_common():
        logger.info("  %s: %d (%.1f%%)", d, c, c / len(all_problems) * 100)

    if n is None or n >= len(all_problems):
        random.seed(seed)
        random.shuffle(all_problems)
        return all_problems

    # Stratified sampling: proportional to domain frequency
    random.seed(seed)
    by_domain = defaultdict(list)
    for p in all_problems:
        by_domain[p["top_domain"]].append(p)

    # Shuffle within each domain
    for domain in by_domain:
        random.shuffle(by_domain[domain])

    total = len(all_problems)
    sampled = []
    remainder = 0.0
    domain_targets = {}

    # Compute proportional counts
    for domain, problems in sorted(by_domain.items(), key=lambda x: -len(x[1])):
        exact = len(problems) / total * n + remainder
        count = int(exact)
        remainder = exact - count
        # At least 1 from each domain if available
        count = max(1, min(count, len(problems)))
        domain_targets[domain] = count

    # Adjust to hit exactly n
    current_total = sum(domain_targets.values())
    if current_total < n:
        # Add more from the largest domains
        for domain in sorted(by_domain.keys(), key=lambda d: -len(by_domain[d])):
            if current_total >= n:
                break
            avail = len(by_domain[domain]) - domain_targets[domain]
            add = min(avail, n - current_total)
            domain_targets[domain] += add
            current_total += add
    elif current_total > n:
        # Remove from smallest domains (but keep at least 1)
        for domain in sorted(by_domain.keys(), key=lambda d: len(by_domain[d])):
            if current_total <= n:
                break
            can_remove = domain_targets[domain] - 1
            remove = min(can_remove, current_total - n)
            domain_targets[domain] -= remove
            current_total -= remove

    # Sample
    for domain, count in domain_targets.items():
        sampled.extend(by_domain[domain][:count])

    random.shuffle(sampled)

    logger.info("Stratified sample: %d problems", len(sampled))
    sample_counts = Counter(p["top_domain"] for p in sampled)
    for d, c in sample_counts.most_common():
        logger.info("  %s: %d", d, c)

    return sampled


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="FormalMATH benchmark (Knuckledragger+SymPy)")
    parser.add_argument("--model", default="gpt-5.4-mini")
    parser.add_argument("--n", type=int, default=None, help="Number of problems (stratified sample)")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--attempts", type=int, default=3, help="Independent attempts per problem")
    parser.add_argument("--repairs", type=int, default=2, help="Repair retries per attempt")
    parser.add_argument("--save-code", default="benchmarks/formalmath_audit")
    parser.add_argument("--output", default=None)
    args = parser.parse_args()

    problems = load_formalmath(args.n, args.seed)
    provider = get_provider(args.model)

    if not args.output:
        ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        args.output = f"benchmarks/formalmath_{args.model}_{ts}.json"

    results = []
    proved = 0
    failed = 0
    domain_stats = defaultdict(lambda: {"proved": 0, "total": 0, "certified": 0})

    print(f"\n{'='*60}")
    print(f"FormalMATH Benchmark: {len(problems)} problems (stratified)")
    print(f"Model: {args.model}")
    print(f"Attempts: {args.attempts} | Repairs: {args.repairs}/attempt")
    print(f"Pipeline: Knuckledragger+SymPy v3 (multi-attempt + hints + CE repair)")
    print(f"SOTA to beat: 16.46% (Kimina-Prover, Lean 4)")
    print(f"{'='*60}\n")

    t_start = time.time()

    for i, p in enumerate(problems, 1):
        top_domain = p.get("top_domain", "Unknown")
        print(f"[{i}/{len(problems)}] {p['id'][:50]}... [{top_domain}]", end=" ", flush=True)

        r = attempt_problem(p, provider, n_attempts=args.attempts,
                           max_repairs=args.repairs, save_dir=args.save_code)
        r["domain"] = p.get("domain", "")
        r["top_domain"] = top_domain
        r["source"] = p.get("source", "")
        results.append(r)

        s = r["status"]
        t = r["time_s"]
        cert = " [CERT]" if r.get("has_certificate") else ""
        hint = " [HINT]" if r.get("sympy_hint") else ""
        att = r.get("attempt", "?")

        domain_stats[top_domain]["total"] += 1

        if s == "proved":
            proved += 1
            domain_stats[top_domain]["proved"] += 1
            if r.get("has_certificate"):
                domain_stats[top_domain]["certified"] += 1
            print(f"PROVED{cert}{hint} (att={att}, {t:.1f}s)")
        else:
            failed += 1
            print(f"FAILED{hint} ({t:.1f}s)")

        total = proved + failed
        elapsed = time.time() - t_start
        rate = proved / total * 100
        eta = elapsed / total * (len(problems) - total)
        print(f"  Running: {proved}/{total} = {rate:.1f}% | ETA: {eta/60:.0f}m")

        # Save intermediate results every 10 problems
        if total % 10 == 0:
            _save_results(args, results, proved, failed, domain_stats, partial=True)

    # Final summary
    total = len(results)
    rate = proved / total * 100 if total else 0
    cert_count = sum(1 for r in results if r.get("has_certificate") and r["status"] == "proved")
    hint_count = sum(1 for r in results if r.get("sympy_hint"))
    multi_att = sum(1 for r in results if r["status"] == "proved" and r.get("attempt", 1) > 1)

    print(f"\n{'='*60}")
    print(f"FORMALMATH RESULTS: {proved}/{total} proved ({rate:.1f}%)")
    print(f"  SOTA comparison: 16.46% (Kimina-Prover, Lean 4)")
    print(f"  With certificate: {cert_count}/{total} ({cert_count/total*100:.1f}%)")
    print(f"  Needed multiple attempts: {multi_att}")
    print(f"  SymPy hints helped: {hint_count} problems had hints")
    print(f"  Failed: {failed}")
    print(f"{'='*60}")

    print(f"\nBy domain:")
    for domain in sorted(domain_stats.keys(), key=lambda d: -domain_stats[d]["total"]):
        ds = domain_stats[domain]
        dr = ds["proved"] / ds["total"] * 100 if ds["total"] else 0
        cr = ds["certified"] / ds["total"] * 100 if ds["total"] else 0
        print(f"  {domain}: {ds['proved']}/{ds['total']} ({dr:.1f}%) | cert: {ds['certified']} ({cr:.1f}%)")

    by_source = defaultdict(lambda: {"proved": 0, "total": 0})
    for r in results:
        src = r.get("source", "unknown")
        by_source[src]["total"] += 1
        if r["status"] == "proved":
            by_source[src]["proved"] += 1

    print(f"\nBy source:")
    for src in sorted(by_source.keys(), key=lambda s: -by_source[s]["total"]):
        ss = by_source[src]
        sr = ss["proved"] / ss["total"] * 100 if ss["total"] else 0
        print(f"  {src}: {ss['proved']}/{ss['total']} ({sr:.1f}%)")

    _save_results(args, results, proved, failed, domain_stats, partial=False)


def _save_results(args, results, proved, failed, domain_stats, partial=False):
    total = len(results)
    rate = proved / total * 100 if total else 0
    cert_count = sum(1 for r in results if r.get("has_certificate") and r["status"] == "proved")

    output_data = {
        "benchmark": "FormalMATH-kd-v3",
        "model": args.model,
        "seed": args.seed,
        "n_problems": total,
        "proved": proved,
        "certified": cert_count,
        "failed": failed,
        "rate": rate,
        "certified_rate": cert_count / total * 100 if total else 0,
        "sota_comparison": {"kimina_prover_lean4": 16.46},
        "partial": partial,
        "attempts_per_problem": args.attempts,
        "repairs_per_attempt": args.repairs,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "domain_breakdown": {
            domain: {
                "proved": ds["proved"],
                "total": ds["total"],
                "certified": ds["certified"],
                "rate": ds["proved"] / ds["total"] * 100 if ds["total"] else 0,
            }
            for domain, ds in domain_stats.items()
        },
        "results": results,
    }
    os.makedirs(os.path.dirname(args.output) or ".", exist_ok=True)
    with open(args.output, "w") as f:
        json.dump(output_data, f, indent=2)
    if not partial:
        print(f"\nSaved to {args.output}")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""KD v3 pipeline for ProofNet and MATH5 cross-benchmarks.

Reuses the v3 pipeline (multi-attempt + SymPy hints + CE repair) on non-miniF2F datasets.

Usage:
    python benchmarks/kd_v3_cross.py --benchmark proofnet --model gpt-5.4-mini --n 50
    python benchmarks/kd_v3_cross.py --benchmark math5 --model claude-sonnet-4-5-20250929 --n 50
"""
from __future__ import annotations

import argparse
import json
import logging
import os
import random
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from benchmarks.kd_bench_v3 import attempt_problem
from benchmarks.minif2f_bench import get_provider

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")


def load_proofnet(n: int | None, seed: int = 42) -> list[dict]:
    from huggingface_hub import hf_hub_download
    path = hf_hub_download("hoskinson-center/proofnet", "test.jsonl", repo_type="dataset")
    problems = []
    with open(path) as f:
        for line in f:
            row = json.loads(line)
            problems.append({
                "id": row.get("id", f"proofnet_{len(problems)}"),
                "statement": row.get("nl_statement", row.get("formal_statement", "")),
                "proof_hint": row.get("nl_proof", ""),
            })
    random.seed(seed)
    random.shuffle(problems)
    if n:
        problems = problems[:n]
    print(f"Loaded {len(problems)} ProofNet problems (seed={seed})")
    return problems


def load_math5(n: int | None, seed: int = 42) -> list[dict]:
    from datasets import load_dataset
    ds = load_dataset("lighteval/MATH-Hard", split="test")
    problems = [
        {
            "id": f"math5_{row['type'].lower().replace(' ', '_')}_{i}",
            "statement": row["problem"],
            "proof_hint": row.get("solution", ""),
        }
        for i, row in enumerate(ds)
    ]
    random.seed(seed)
    random.shuffle(problems)
    if n:
        problems = problems[:n]
    print(f"Loaded {len(problems)} MATH Level 5 problems (seed={seed})")
    return problems


def main():
    parser = argparse.ArgumentParser(description="KD v3 cross-benchmark")
    parser.add_argument("--benchmark", required=True, choices=["proofnet", "math5"])
    parser.add_argument("--model", default="gpt-5.4-mini")
    parser.add_argument("--n", type=int, default=50)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--attempts", type=int, default=3)
    parser.add_argument("--repairs", type=int, default=2)
    parser.add_argument("--save-code", default=None)
    parser.add_argument("--output", default=None)
    args = parser.parse_args()

    if args.benchmark == "proofnet":
        problems = load_proofnet(args.n, args.seed)
    else:
        problems = load_math5(args.n, args.seed)

    provider = get_provider(args.model)

    if not args.save_code:
        args.save_code = f"benchmarks/kd_v3_{args.benchmark}_audit"
    if not args.output:
        ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        args.output = f"benchmarks/kd_v3_{args.benchmark}_{args.model}_{ts}.json"

    results = []
    proved = 0
    failed = 0

    print(f"\n{'='*60}")
    print(f"KD v3 {args.benchmark.upper()}: {len(problems)} problems")
    print(f"Model: {args.model} | Attempts: {args.attempts}")
    print(f"{'='*60}\n")

    for i, p in enumerate(problems, 1):
        print(f"[{i}/{len(problems)}] {p['id']}...", end=" ", flush=True)
        r = attempt_problem(p, provider, n_attempts=args.attempts,
                           max_repairs=args.repairs, save_dir=args.save_code)
        results.append(r)

        s = r["status"]
        t = r["time_s"]
        cert = " [CERT]" if r.get("has_certificate") else ""
        if s == "proved":
            proved += 1
            print(f"PROVED{cert} ({t:.1f}s)")
        else:
            failed += 1
            print(f"FAILED ({t:.1f}s)")

        total = proved + failed
        print(f"  Running: {proved}/{total} = {proved/total*100:.1f}%")

    total = len(results)
    rate = proved / total * 100 if total else 0
    cert_count = sum(1 for r in results if r.get("has_certificate") and r["status"] == "proved")

    print(f"\n{'='*60}")
    print(f"RESULTS: {proved}/{total} proved ({rate:.1f}%)")
    print(f"  With certificate: {cert_count}/{total} ({cert_count/total*100:.1f}%)")
    print(f"{'='*60}")

    output_data = {
        "benchmark": f"{args.benchmark}-kd-v3",
        "model": args.model,
        "seed": args.seed,
        "n_problems": total,
        "proved": proved,
        "certified": cert_count,
        "failed": failed,
        "rate": rate,
        "certified_rate": cert_count / total * 100 if total else 0,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "results": results,
    }
    os.makedirs(os.path.dirname(args.output) or ".", exist_ok=True)
    with open(args.output, "w") as f:
        json.dump(output_data, f, indent=2)
    print(f"\nSaved to {args.output}")


if __name__ == "__main__":
    main()

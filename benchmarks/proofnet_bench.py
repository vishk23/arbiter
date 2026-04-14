#!/usr/bin/env python3
"""ProofNet benchmark for Arbiter's Z3 proof generation pipeline.

371 undergraduate-level math problems. COPRA achieved 26.5% with GPT-4 + Lean.

Usage:
    python benchmarks/proofnet_bench.py --model gpt-5.4-mini --n 50
"""
from __future__ import annotations

import argparse
import json
import os
import random
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from benchmarks.minif2f_bench import attempt_problem, get_provider

import logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")


def load_proofnet(n: int | None, seed: int = 42) -> list[dict]:
    """Load ProofNet test problems."""
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


def main():
    parser = argparse.ArgumentParser(description="ProofNet benchmark")
    parser.add_argument("--model", default="gpt-5.4-mini")
    parser.add_argument("--n", type=int, default=50)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--retries", type=int, default=2)
    parser.add_argument("--output", default=None)
    args = parser.parse_args()

    problems = load_proofnet(args.n, args.seed)
    provider = get_provider(args.model)

    if not args.output:
        ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        args.output = f"benchmarks/proofnet_{args.model}_{ts}.json"

    results = []
    proved = 0
    failed = 0
    errors = 0

    print(f"\n{'='*60}")
    print(f"ProofNet Benchmark: {len(problems)} problems")
    print(f"Model: {args.model} | Retries: {args.retries} | Seed: {args.seed}")
    print(f"{'='*60}\n")

    for i, problem in enumerate(problems, 1):
        print(f"[{i}/{len(problems)}] {problem['id']}...", end=" ", flush=True)
        result = attempt_problem(problem, provider, max_retries=args.retries)
        results.append(result)

        status = result["status"]
        t = result["time_s"]
        if status == "proved":
            proved += 1
            print(f"PROVED ({t:.1f}s)")
        elif status == "failed_proof":
            failed += 1
            print(f"FAILED ({t:.1f}s)")
        else:
            errors += 1
            print(f"ERROR: {status} ({t:.1f}s)")

        total_so_far = proved + failed + errors
        rate = proved / total_so_far * 100
        print(f"  Running: {proved}/{total_so_far} = {rate:.1f}%")

    total = len(results)
    rate = proved / total * 100 if total else 0
    print(f"\n{'='*60}")
    print(f"RESULTS: {proved}/{total} proved ({rate:.1f}%)")
    print(f"  Proved: {proved} | Failed: {failed} | Errors: {errors}")
    print(f"  Comparison: COPRA = 26.5% (GPT-4 + Lean)")
    print(f"{'='*60}")

    output_data = {
        "benchmark": "ProofNet",
        "model": args.model,
        "seed": args.seed,
        "n_problems": total,
        "proved": proved,
        "failed": failed,
        "errors": errors,
        "rate": rate,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "results": results,
    }
    os.makedirs(os.path.dirname(args.output) or ".", exist_ok=True)
    with open(args.output, "w") as f:
        json.dump(output_data, f, indent=2)
    print(f"\nSaved to {args.output}")


if __name__ == "__main__":
    main()

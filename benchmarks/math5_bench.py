#!/usr/bin/env python3
"""MATH Level 5 benchmark for Arbiter's Z3 proof generation pipeline.

Tests on the hardest problems from Hendrycks MATH dataset.

Usage:
    python benchmarks/math5_bench.py --model gpt-5.4-mini --n 50
    python benchmarks/math5_bench.py --model gpt-5.4 --n 100
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

from benchmarks.minif2f_bench import (
    SYSTEM_PROMPT,
    attempt_problem,
    get_provider,
    run_z3_module,
)

import logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")


def load_math5(n: int | None, seed: int = 42) -> list[dict]:
    """Load MATH Level 5 problems."""
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
    parser = argparse.ArgumentParser(description="MATH Level 5 benchmark")
    parser.add_argument("--model", default="gpt-5.4-mini")
    parser.add_argument("--n", type=int, default=50)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--retries", type=int, default=2)
    parser.add_argument("--output", default=None)
    args = parser.parse_args()

    problems = load_math5(args.n, args.seed)
    provider = get_provider(args.model)

    if not args.output:
        ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        args.output = f"benchmarks/math5_{args.model}_{ts}.json"

    results = []
    proved = 0
    failed = 0
    errors = 0

    print(f"\n{'='*60}")
    print(f"MATH Level 5 Benchmark: {len(problems)} problems")
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
    print(f"{'='*60}")

    # Breakdown by math type
    by_type = {}
    for r in results:
        parts = r["id"].split("_")
        mtype = "_".join(parts[1:-1])
        if mtype not in by_type:
            by_type[mtype] = {"proved": 0, "total": 0}
        by_type[mtype]["total"] += 1
        if r["status"] == "proved":
            by_type[mtype]["proved"] += 1

    print("\nBy type:")
    for t, s in sorted(by_type.items()):
        sr = s["proved"] / s["total"] * 100
        print(f"  {t}: {s['proved']}/{s['total']} ({sr:.0f}%)")

    output_data = {
        "benchmark": "MATH-Level5",
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

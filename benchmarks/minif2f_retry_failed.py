#!/usr/bin/env python3
"""Retry failed miniF2F problems with a different/bigger model."""
from __future__ import annotations

import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

bench_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(bench_dir.parent / "src"))
sys.path.insert(0, str(bench_dir.parent))

from benchmarks.minif2f_bench import attempt_problem, get_provider, load_problems

# Load previous results to find failures
PREV = "benchmarks/minif2f_hard_gpt-5.4-mini_20260414_040629.json"


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", default="gpt-5.4")
    parser.add_argument("--prev", default=PREV)
    parser.add_argument("--retries", type=int, default=3)
    args = parser.parse_args()

    with open(args.prev) as f:
        prev = json.load(f)

    failed_ids = {r["id"] for r in prev["results"] if r["status"] != "proved"}
    print(f"Retrying {len(failed_ids)} failed problems with {args.model}")

    # Load full dataset to get problem statements
    from datasets import load_dataset
    ds = load_dataset("cat-searcher/minif2f-lean4", split="test")
    problems = [
        {"id": row["id"], "statement": row["informal_stmt"], "proof_hint": row.get("informal_proof", "")}
        for row in ds if row["id"] in failed_ids
    ]

    provider = get_provider(args.model)
    results = []
    proved = 0

    for i, p in enumerate(problems, 1):
        print(f"[{i}/{len(problems)}] {p['id']}...", end=" ", flush=True)
        r = attempt_problem(p, provider, max_retries=args.retries)
        results.append(r)
        if r["status"] == "proved":
            proved += 1
            print(f"PROVED ({r['time_s']:.1f}s, {r['attempts']} attempts)")
        else:
            print(f"{r['status']} ({r['time_s']:.1f}s)")
        print(f"  Running: {proved}/{i}")

    total = len(results)
    rate = proved / total * 100 if total else 0
    print(f"\n{'='*60}")
    print(f"RETRY RESULTS with {args.model}: {proved}/{total} ({rate:.1f}%)")
    print(f"{'='*60}")

    # Combined score
    orig_proved = sum(1 for r in prev["results"] if r["status"] == "proved")
    combined = orig_proved + proved
    combined_total = len(prev["results"])
    print(f"\nCombined (mini + {args.model} retry): {combined}/{combined_total} = {combined/combined_total*100:.1f}%")

    ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    out = f"benchmarks/minif2f_retry_{args.model}_{ts}.json"
    with open(out, "w") as f:
        json.dump({"model": args.model, "retried": len(failed_ids), "proved": proved, "results": results}, f, indent=2)
    print(f"Saved to {out}")


if __name__ == "__main__":
    main()

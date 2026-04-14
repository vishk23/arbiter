#!/usr/bin/env python3
"""Regenerate Z3 proofs and save source code for manual audit.

For each proved problem, regenerates the Z3 module and saves both
the source code and execution output to a directory for inspection.

Usage:
    python benchmarks/regen_for_audit.py --results benchmarks/minif2f_hard_gpt-5.4-mini_20260414_040629.json
"""
from __future__ import annotations

import json
import os
import sys
import tempfile
import subprocess
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from benchmarks.minif2f_bench import (
    get_provider, SYSTEM_PROMPT, build_user_prompt,
)
from arbiter.config import TokenBudgets
from arbiter.providers.base import strip_markdown_fences
from arbiter.schemas import Z3GenResult

_B = TokenBudgets()


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--results", required=True)
    parser.add_argument("--model", default="gpt-5.4-mini")
    parser.add_argument("--outdir", default="benchmarks/audit")
    parser.add_argument("--n", type=int, default=None, help="Only audit first N")
    args = parser.parse_args()

    with open(args.results) as f:
        data = json.load(f)

    from datasets import load_dataset
    ds = load_dataset("cat-searcher/minif2f-lean4", split="test")
    prob_map = {row["id"]: {
        "id": row["id"],
        "statement": row["informal_stmt"],
        "proof_hint": row.get("informal_proof", ""),
    } for row in ds}

    proved = [r for r in data["results"] if r["status"] == "proved"]
    if args.n:
        proved = proved[:args.n]

    provider = get_provider(args.model)
    os.makedirs(args.outdir, exist_ok=True)

    for i, r in enumerate(proved, 1):
        pid = r["id"]
        problem = prob_map.get(pid)
        if not problem:
            continue

        print(f"[{i}/{len(proved)}] {pid}...", end=" ", flush=True)

        user = build_user_prompt(problem)
        try:
            response = provider.call_structured(
                SYSTEM_PROMPT, user, Z3GenResult, max_tokens=_B.large
            )
            code = response.get("module_code", "") if isinstance(response, dict) else response.module_code
            code = strip_markdown_fences(code)
        except Exception as e:
            print(f"ERROR: {e}")
            continue

        # Save source code
        code_path = os.path.join(args.outdir, f"{pid}.py")
        with open(code_path, "w") as f:
            f.write(code)

        # Execute and save output
        try:
            result = subprocess.run(
                [sys.executable, code_path],
                capture_output=True, text=True, timeout=60
            )
            output = result.stdout if result.returncode == 0 else f"EXIT {result.returncode}\n{result.stderr}"
        except subprocess.TimeoutExpired:
            output = "TIMEOUT"

        out_path = os.path.join(args.outdir, f"{pid}.out")
        with open(out_path, "w") as f:
            f.write(output)

        # Save problem statement
        stmt_path = os.path.join(args.outdir, f"{pid}.problem")
        with open(stmt_path, "w") as f:
            f.write(problem["statement"])

        ok = "passed" not in output.lower() or "False" not in output
        print("OK" if ok else "FAIL")

    print(f"\nAudit files saved to {args.outdir}/")
    print(f"Each problem has .py (source), .out (output), .problem (statement)")


if __name__ == "__main__":
    main()

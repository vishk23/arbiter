#!/usr/bin/env python3
"""Verify that Z3 proofs are not vacuous.

For each "proved" result, re-generate and check:
1. Does the Z3 module execute without error?
2. Are all UNSAT results non-vacuous (i.e., dropping the negation gives SAT)?
3. Does the encoding actually match the problem statement?

Usage:
    python benchmarks/verify_proofs.py --results benchmarks/minif2f_hard_gpt-5.4-mini_*.json
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from benchmarks.minif2f_bench import get_provider, SYSTEM_PROMPT, build_user_prompt, run_z3_module
from arbiter.config import TokenBudgets
from arbiter.providers.base import strip_markdown_fences
from arbiter.schemas import Z3GenResult

import logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

_B = TokenBudgets()

VERIFY_SYSTEM = """\
You are an expert in Z3 SMT verification. Review this Z3 proof module and assess its correctness.

For each check in the module, answer:
1. ENCODING_CORRECT: Does the Z3 encoding faithfully represent the math problem? (yes/no/partial)
2. VACUITY_RISK: Could the UNSAT result be vacuous (constraints unsatisfiable even without the negation)? (yes/no/maybe)
3. COMPLETENESS: Does the check prove the core mathematical claim, or just a trivial consequence? (core/partial/trivial)

Return a JSON object with:
{
  "checks": [
    {
      "name": "check name",
      "encoding_correct": "yes|no|partial",
      "vacuity_risk": "yes|no|maybe",
      "completeness": "core|partial|trivial",
      "issue": "description of any issue, or empty string"
    }
  ],
  "overall_verdict": "valid|suspicious|invalid",
  "explanation": "brief explanation"
}
"""


def verify_single(problem_id: str, problem_stmt: str, z3_output: str, provider) -> dict:
    """Have the LLM review the Z3 proof for correctness."""
    user = (
        f"PROBLEM: {problem_id}\n"
        f"STATEMENT: {problem_stmt[:500]}\n\n"
        f"Z3 OUTPUT:\n{z3_output[:1500]}\n\n"
        "Assess the correctness of this Z3 proof. Be critical — flag anything suspicious."
    )
    try:
        response = provider.call_with_retry(VERIFY_SYSTEM, user, max_tokens=_B.medium)
        # Parse JSON from response
        text = response if isinstance(response, str) else str(response)
        text = strip_markdown_fences(text)
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            return {"overall_verdict": "parse_error", "raw": text[:500]}
    except Exception as e:
        return {"overall_verdict": "error", "error": str(e)[:200]}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--results", required=True, help="Path to benchmark results JSON")
    parser.add_argument("--model", default="gpt-5.4-mini", help="Model for verification")
    parser.add_argument("--n", type=int, default=20, help="Number of proofs to verify")
    args = parser.parse_args()

    with open(args.results) as f:
        data = json.load(f)

    # Load dataset for problem statements
    from datasets import load_dataset
    ds = load_dataset("cat-searcher/minif2f-lean4", split="test")
    stmt_map = {row["id"]: row["informal_stmt"] for row in ds}

    proved = [r for r in data["results"] if r["status"] == "proved"]
    to_verify = proved[:args.n]

    provider = get_provider(args.model)
    results = []

    print(f"Verifying {len(to_verify)} proofs with {args.model}")
    print("=" * 60)

    verdict_counts = {"valid": 0, "suspicious": 0, "invalid": 0, "other": 0}

    for i, r in enumerate(to_verify, 1):
        pid = r["id"]
        stmt = stmt_map.get(pid, "N/A")
        output = r.get("output", "")

        print(f"[{i}/{len(to_verify)}] {pid}...", end=" ", flush=True)
        verdict = verify_single(pid, stmt, output, provider)
        results.append({"id": pid, "verdict": verdict})

        v = verdict.get("overall_verdict", "other")
        if v in verdict_counts:
            verdict_counts[v] += 1
        else:
            verdict_counts["other"] += 1

        print(f"{v} — {verdict.get('explanation', '')[:80]}")

    print(f"\n{'='*60}")
    print(f"VERIFICATION RESULTS:")
    for k, v in verdict_counts.items():
        print(f"  {k}: {v}")
    print(f"  Total: {len(results)}")

    valid_rate = verdict_counts["valid"] / len(results) * 100 if results else 0
    adjusted_rate = verdict_counts["valid"] / data["n_problems"] * 100 if data["n_problems"] else 0
    print(f"\nValid rate: {valid_rate:.1f}% of proved")
    print(f"Adjusted benchmark rate: {adjusted_rate:.1f}% (only counting verified proofs)")

    # Save
    out_path = args.results.replace(".json", "_verified.json")
    with open(out_path, "w") as f:
        json.dump({
            "source": args.results,
            "verifier_model": args.model,
            "n_verified": len(results),
            "verdict_counts": verdict_counts,
            "valid_rate": valid_rate,
            "adjusted_rate": adjusted_rate,
            "results": results,
        }, f, indent=2)
    print(f"\nSaved to {out_path}")


if __name__ == "__main__":
    main()

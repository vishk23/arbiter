#!/usr/bin/env python3
"""miniF2F benchmark for Arbiter's Z3 proof generation pipeline.

Tests whether an LLM can generate Z3 proofs for math competition problems.
Stratified by difficulty: mathd (easy), amc (medium), aime/imo (hard).

Usage:
    python benchmarks/minif2f_bench.py --model gpt-5.4-mini --tier hard --n 20
    python benchmarks/minif2f_bench.py --model gpt-5.4-mini --tier all --n 50
    python benchmarks/minif2f_bench.py --model gpt-5.4 --tier hard --n 35
"""
from __future__ import annotations

import argparse
import json
import logging
import os
import random
import subprocess
import sys
import tempfile
import textwrap
import time
from datetime import datetime, timezone
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from arbiter.config import TokenBudgets
from arbiter.providers.base import BaseProvider, strip_markdown_fences
from arbiter.schemas import Z3GenResult

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)
_B = TokenBudgets()

# ---------------------------------------------------------------------------
# Dataset loading
# ---------------------------------------------------------------------------

TIERS = {
    "easy": lambda pid: pid.startswith("mathd"),
    "medium": lambda pid: "amc" in pid,
    "hard": lambda pid: "aime" in pid or "imo" in pid,
    "all": lambda _: True,
}


def load_problems(tier: str, n: int | None, seed: int = 42) -> list[dict]:
    """Load miniF2F test-split problems filtered by difficulty tier."""
    from datasets import load_dataset

    ds = load_dataset("cat-searcher/minif2f-lean4", split="test")
    tier_fn = TIERS[tier]
    problems = [
        {
            "id": row["id"],
            "statement": row["informal_stmt"],
            "proof_hint": row.get("informal_proof", ""),
        }
        for row in ds
        if tier_fn(row["id"])
    ]
    random.seed(seed)
    random.shuffle(problems)
    if n:
        problems = problems[:n]
    logger.info("Loaded %d %s-tier problems (seed=%d)", len(problems), tier, seed)
    return problems


# ---------------------------------------------------------------------------
# Z3 proof generation prompt
# ---------------------------------------------------------------------------

SYSTEM_PROMPT = textwrap.dedent("""\
    You are an expert in formal verification using the Z3 SMT solver (Python).
    Given a math problem, generate a standalone Python module that PROVES the result using Z3.

    REQUIREMENTS:
    1. Import from z3: Solver, Optimize, Real, Int, Bool, And, Or, Not, Implies,
       ForAll, Exists, sat, unsat, RealVal, IntVal, Sum, Product, If, etc.
    2. Export a verify() -> dict function returning {"check1": {...}}.
    3. Each check dict must have:
       - name: str (descriptive title)
       - result: "SAT" | "UNSAT" | "UNKNOWN"
       - expected: what the proof expects (usually "UNSAT" for proofs)
       - explanation: what the result means
       - passed: bool (True if result matches expected)
    4. Include if __name__ == "__main__" block that calls verify() and prints results.

    PROOF STRATEGY:
    - For "prove P" problems: encode ¬P as constraints, check UNSAT.
      If UNSAT → P is proven (no counterexample exists).
    - For "find x such that..." problems: encode constraints, check SAT.
      If SAT → extract solution from model.
    - For "show equality" problems: encode LHS ≠ RHS, check UNSAT.
    - For "determine all x" problems: encode the constraints, find solutions.

    Z3 TIPS:
    - Use Real('x') for real-valued variables
    - Use Int('n') for integers
    - ForAll([x], Implies(condition, result)) for universal proofs
    - For inequalities involving products, avoid division — multiply both sides
    - For bounded quantifiers, use And(x >= lo, x <= hi, ...) inside ForAll
    - Timeout: set s.set("timeout", 30000) for hard problems (30s)
    - If a problem involves cos/sin/trig: these are NOT natively in Z3.
      You can encode algebraic identities or use uninterpreted functions.
    - For number theory: use Int, modular arithmetic with %, divisibility with x % d == 0

    IMPORTANT: Return ONLY valid Python in module_code. No markdown fences.
""")


def build_user_prompt(problem: dict, *, no_hints: bool = False) -> str:
    """Build user prompt for a single miniF2F problem."""
    parts = [
        f"PROBLEM ID: {problem['id']}\n",
        f"STATEMENT:\n{problem['statement']}\n",
    ]
    if not no_hints and problem.get("proof_hint"):
        parts.append(f"PROOF HINT (informal):\n{problem['proof_hint']}\n")
    parts.append(
        "Generate a Z3 proof module. The verify() function should return a dict "
        "of checks, each with 'passed': True if the proof succeeds.\n"
        "Return module_code and check_names."
    )
    return "\n".join(parts)


# ---------------------------------------------------------------------------
# Execution
# ---------------------------------------------------------------------------

def run_z3_module(code: str, timeout: int = 60) -> tuple[bool, str]:
    """Write code to temp file, execute, return (success, output)."""
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".py", delete=False, dir="/tmp"
    ) as f:
        f.write(code)
        path = f.name

    try:
        result = subprocess.run(
            [sys.executable, path],
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        if result.returncode == 0:
            return True, result.stdout
        return False, f"EXIT {result.returncode}\nSTDERR: {result.stderr[:500]}\nSTDOUT: {result.stdout[:500]}"
    except subprocess.TimeoutExpired:
        return False, f"TIMEOUT after {timeout}s"
    finally:
        os.unlink(path)


def attempt_problem(
    problem: dict,
    provider: BaseProvider,
    max_retries: int = 2,
    z3_timeout: int = 60,
    no_hints: bool = False,
    temperature: float | None = None,
) -> dict:
    """Generate and test Z3 proof for one problem. Returns result dict."""
    t0 = time.time()
    user_prompt = build_user_prompt(problem, no_hints=no_hints)
    extra_kwargs = {}
    if temperature is not None:
        extra_kwargs["temperature"] = temperature

    # Initial generation
    try:
        response = provider.call_structured(
            SYSTEM_PROMPT, user_prompt, Z3GenResult, max_tokens=_B.large
        )
        code = response.get("module_code", "") if isinstance(response, dict) else response.module_code
        code = strip_markdown_fences(code)
    except Exception as e:
        return {
            "id": problem["id"],
            "status": "generation_error",
            "error": str(e)[:300],
            "attempts": 0,
            "time_s": time.time() - t0,
        }

    # Try execution with retries
    for attempt in range(1, max_retries + 2):
        success, output = run_z3_module(code, timeout=z3_timeout)
        if success:
            # Parse output to check if proofs passed
            passed = "passed" not in output.lower() or "True" in output
            # More precise: look for passed: False
            any_failed = "False" in output and "passed" in output.lower()
            return {
                "id": problem["id"],
                "status": "proved" if not any_failed else "failed_proof",
                "output": output[:1000],
                "attempts": attempt,
                "time_s": time.time() - t0,
            }

        if attempt <= max_retries:
            # Repair attempt
            fix_system = "Fix the Z3 proof module. Return corrected module_code."
            fix_user = (
                f"PROBLEM: {problem['statement'][:500]}\n\n"
                f"CODE:\n{code[:2000]}\n\n"
                f"ERROR:\n{output[:500]}\n\n"
                "Fix the error and return working module_code and check_names."
            )
            try:
                response = provider.call_structured(
                    fix_system, fix_user, Z3GenResult, max_tokens=_B.large
                )
                code = response.get("module_code", "") if isinstance(response, dict) else response.module_code
                code = strip_markdown_fences(code)
            except Exception as e:
                return {
                    "id": problem["id"],
                    "status": "repair_error",
                    "error": str(e)[:300],
                    "attempts": attempt,
                    "time_s": time.time() - t0,
                }

    return {
        "id": problem["id"],
        "status": "execution_error",
        "error": output[:500],
        "attempts": max_retries + 1,
        "time_s": time.time() - t0,
    }


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def get_provider(model: str) -> BaseProvider:
    """Instantiate the right provider for the model name."""
    from arbiter.config import ProviderConfig

    cfg = ProviderConfig(model=model)
    if model.startswith("gpt") or model.startswith("o"):
        from arbiter.providers.openai import OpenAIProvider
        return OpenAIProvider(cfg)
    elif model.startswith("claude"):
        from arbiter.providers.anthropic import AnthropicProvider
        return AnthropicProvider(cfg)
    elif model.startswith("grok") or model.startswith("xai"):
        from arbiter.providers.xai import XaiProvider
        return XaiProvider(cfg)
    elif model.startswith("gemini"):
        from arbiter.providers.google import GoogleProvider
        return GoogleProvider(cfg)
    else:
        from arbiter.providers.openai import OpenAIProvider
        return OpenAIProvider(cfg)


def main():
    parser = argparse.ArgumentParser(description="miniF2F benchmark for Arbiter Z3")
    parser.add_argument("--model", default="gpt-5.4-mini", help="LLM model name")
    parser.add_argument("--tier", default="hard", choices=list(TIERS.keys()))
    parser.add_argument("--n", type=int, default=None, help="Number of problems (None=all)")
    parser.add_argument("--seed", type=int, default=42, help="Random seed")
    parser.add_argument("--retries", type=int, default=2, help="Max repair retries per problem")
    parser.add_argument("--z3-timeout", type=int, default=60, help="Z3 execution timeout in seconds")
    parser.add_argument("--no-hints", action="store_true", help="Omit proof hints from prompts")
    parser.add_argument("--temperature", type=float, default=None, help="LLM temperature")
    parser.add_argument("--output", default=None, help="Output JSON file")
    args = parser.parse_args()

    problems = load_problems(args.tier, args.n, args.seed)
    provider = get_provider(args.model)

    if not args.output:
        ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        args.output = f"benchmarks/minif2f_{args.tier}_{args.model}_{ts}.json"

    results = []
    proved = 0
    failed = 0
    errors = 0

    print(f"\n{'='*60}")
    print(f"miniF2F Benchmark: {len(problems)} {args.tier}-tier problems")
    print(f"Model: {args.model} | Retries: {args.retries} | Seed: {args.seed}")
    print(f"{'='*60}\n")

    for i, problem in enumerate(problems, 1):
        print(f"[{i}/{len(problems)}] {problem['id']}...", end=" ", flush=True)
        result = attempt_problem(
            problem, provider,
            max_retries=args.retries,
            z3_timeout=args.z3_timeout,
            no_hints=args.no_hints,
            temperature=args.temperature,
        )
        results.append(result)

        status = result["status"]
        t = result["time_s"]
        if status == "proved":
            proved += 1
            print(f"PROVED ({t:.1f}s, {result['attempts']} attempt(s))")
        elif status == "failed_proof":
            failed += 1
            print(f"FAILED PROOF ({t:.1f}s)")
        else:
            errors += 1
            print(f"ERROR: {status} ({t:.1f}s)")

        # Running tally
        total = proved + failed + errors
        rate = proved / total * 100 if total else 0
        print(f"  Running: {proved}/{total} = {rate:.1f}%")

    # Summary
    total = len(results)
    rate = proved / total * 100 if total else 0
    print(f"\n{'='*60}")
    print(f"RESULTS: {proved}/{total} proved ({rate:.1f}%)")
    print(f"  Proved: {proved} | Failed proof: {failed} | Errors: {errors}")
    print(f"  Avg time: {sum(r['time_s'] for r in results)/total:.1f}s per problem")
    print(f"{'='*60}")

    # Breakdown by source
    from collections import Counter
    by_source = {}
    for r in results:
        src = r["id"].split("_")[0]
        if src not in by_source:
            by_source[src] = {"proved": 0, "total": 0}
        by_source[src]["total"] += 1
        if r["status"] == "proved":
            by_source[src]["proved"] += 1

    print("\nBy source:")
    for src, stats in sorted(by_source.items()):
        sr = stats["proved"] / stats["total"] * 100
        print(f"  {src}: {stats['proved']}/{stats['total']} ({sr:.0f}%)")

    # Save
    output_data = {
        "model": args.model,
        "tier": args.tier,
        "seed": args.seed,
        "n_problems": total,
        "proved": proved,
        "failed_proof": failed,
        "errors": errors,
        "rate": rate,
        "retries": args.retries,
        "z3_timeout": args.z3_timeout,
        "no_hints": args.no_hints,
        "temperature": args.temperature,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "results": results,
    }

    os.makedirs(os.path.dirname(args.output) or ".", exist_ok=True)
    with open(args.output, "w") as f:
        json.dump(output_data, f, indent=2)
    print(f"\nResults saved to {args.output}")


if __name__ == "__main__":
    main()

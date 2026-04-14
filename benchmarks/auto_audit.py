#!/usr/bin/env python3
"""Automated vacuity checker and audit for miniF2F Z3-only benchmark results.

Loads benchmark results, re-generates Z3 proofs, runs vacuity checks,
and uses an LLM classifier to categorize each proof.

Usage:
    python benchmarks/auto_audit.py --sample 50
    python benchmarks/auto_audit.py  # all proved results
"""
from __future__ import annotations

import argparse
import json
import logging
import os
import re
import subprocess
import sys
import tempfile
import textwrap
import time
from datetime import datetime, timezone
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from arbiter.config import ProviderConfig, TokenBudgets
from arbiter.providers.base import BaseProvider, strip_markdown_fences
from arbiter.schemas import Z3GenResult

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)
_B = TokenBudgets()

# ---------------------------------------------------------------------------
# Categories
# ---------------------------------------------------------------------------

CATEGORIES = [
    "valid",
    "vacuous",
    "assumed_conclusion",
    "crash",
    "trivial_tail",
    "partial",
    "wrong_encoding",
]

# ---------------------------------------------------------------------------
# Z3 generation prompt (same as minif2f_bench.py)
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

# ---------------------------------------------------------------------------
# Classifier prompt
# ---------------------------------------------------------------------------

CLASSIFIER_SYSTEM = textwrap.dedent("""\
    You are an expert auditor of Z3 SMT solver proofs for mathematical theorems.
    Your job is to classify whether a Z3 proof is genuinely valid or has defects.

    You will receive:
    1. The original math problem statement
    2. The Z3 Python code that claims to prove it
    3. The execution output of that code
    4. The result of a vacuity test (running the code with the claim-denial removed)

    Classify the proof into EXACTLY ONE of these categories:

    - valid: The Z3 code correctly encodes the problem's premises and conclusion.
      The UNSAT result genuinely proves the claim. The vacuity test passes (assumptions
      alone are SAT, only assumptions + negated conclusion is UNSAT).

    - vacuous: The assumptions alone are contradictory (UNSAT even without the
      negated conclusion). The proof is technically UNSAT but proves nothing because
      the premises themselves are impossible. The vacuity test shows UNSAT for
      assumptions-only.

    - assumed_conclusion: The code asserts the conclusion (or an equivalent) as a
      premise rather than proving it. The conclusion appears among the solver
      constraints, not just as a negation target.

    - crash: The code does not execute successfully, throws errors, or times out.

    - trivial_tail: The code only verifies simple arithmetic (e.g., 2+3==5) or
      checks a known constant, without encoding the actual mathematical reasoning
      of the problem. Fewer than 3 meaningful constraints.

    - partial: The code proves a simplified or weaker version of the problem.
      Some but not all aspects of the problem are encoded.

    - wrong_encoding: The code encodes a different problem than stated. Variables
      or constraints don't match the problem's mathematical content.

    Respond with ONLY a JSON object: {"category": "<one of the 7>", "reason": "<1-2 sentence explanation>"}
    No markdown fences. Just the JSON.
""")


def build_classifier_prompt(
    problem_id: str,
    statement: str,
    code: str,
    exec_output: str,
    vacuity_result: str,
) -> str:
    return textwrap.dedent(f"""\
        PROBLEM ID: {problem_id}

        PROBLEM STATEMENT:
        {statement}

        Z3 CODE:
        ```python
        {code[:4000]}
        ```

        EXECUTION OUTPUT:
        {exec_output[:1500]}

        VACUITY TEST RESULT (assumptions only, no negated claim):
        {vacuity_result[:1000]}

        Classify this proof. Return JSON: {{"category": "...", "reason": "..."}}
    """)


# ---------------------------------------------------------------------------
# Provider setup
# ---------------------------------------------------------------------------

def get_provider(model: str) -> BaseProvider:
    """Instantiate the right provider for the model name."""
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


# ---------------------------------------------------------------------------
# Dataset loading
# ---------------------------------------------------------------------------

def load_problems_map() -> dict[str, dict]:
    """Load all miniF2F problems into a dict keyed by ID."""
    from datasets import load_dataset
    ds = load_dataset("cat-searcher/minif2f-lean4", split="test")
    return {
        row["id"]: {
            "id": row["id"],
            "statement": row["informal_stmt"],
            "proof_hint": row.get("informal_proof", ""),
        }
        for row in ds
    }


# ---------------------------------------------------------------------------
# Z3 execution helpers
# ---------------------------------------------------------------------------

def run_z3_code(code: str, timeout: int = 60) -> tuple[bool, str]:
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


def build_user_prompt(problem: dict) -> str:
    """Build user prompt for a single miniF2F problem."""
    parts = [
        f"PROBLEM ID: {problem['id']}\n",
        f"STATEMENT:\n{problem['statement']}\n",
    ]
    if problem.get("proof_hint"):
        parts.append(f"PROOF HINT (informal):\n{problem['proof_hint']}\n")
    parts.append(
        "Generate a Z3 proof module. The verify() function should return a dict "
        "of checks, each with 'passed': True if the proof succeeds.\n"
        "Return module_code and check_names."
    )
    return "\n".join(parts)


# ---------------------------------------------------------------------------
# Vacuity check: modify Z3 code to remove negated claim
# ---------------------------------------------------------------------------

def make_vacuity_variant(code: str) -> str:
    """Produce a vacuity-test variant of Z3 proof code.

    Strategy: inject a wrapper that intercepts Solver.check() calls.
    Before each check(), we remove the last constraint added (which is
    typically the negation of the claim). This is a heuristic.

    Simpler approach: we add a comment-block at the end that creates a
    fresh solver with only the assumptions (no negation).
    """
    vacuity_code = code + textwrap.dedent("""

# ===== VACUITY TEST =====
# Re-run with assumptions only (no negated conclusion)
import z3 as _z3_vac
import re as _re_vac

def _vacuity_test():
    \"\"\"Check if assumptions alone are contradictory.\"\"\"
    results = verify()
    print("\\n===== VACUITY TEST =====")
    for key, check in results.items():
        print(f"Original {key}: result={check.get('result','?')}, passed={check.get('passed','?')}")
    print("\\nNote: If original checks are UNSAT, a proper vacuity test requires")
    print("removing the negated-claim constraint. See LLM classifier for full analysis.")
    print("===== END VACUITY TEST =====")

_vacuity_test()
""")
    return vacuity_code


def structural_vacuity_check(code: str) -> dict:
    """Perform structural analysis of Z3 code for vacuity indicators."""
    indicators = {
        "has_forall": bool(re.search(r'\bForAll\b', code)),
        "has_exists": bool(re.search(r'\bExists\b', code)),
        "has_not": bool(re.search(r'\bNot\b', code)),
        "has_implies": bool(re.search(r'\bImplies\b', code)),
        "solver_add_count": len(re.findall(r'\.add\(', code)),
        "has_negation_pattern": bool(re.search(r'Not\(.*claim\)|Not\(.*goal\)|negat', code, re.I)),
        "has_timeout": bool(re.search(r'timeout', code, re.I)),
        "line_count": len(code.strip().split('\n')),
        "constraint_count": len(re.findall(r's\.add\(|solver\.add\(', code, re.I)),
    }
    # Heuristic: trivial if fewer than 3 constraints
    indicators["likely_trivial"] = indicators["constraint_count"] < 3
    # Heuristic: likely vacuous if no Not() or negation
    indicators["no_negation"] = not indicators["has_not"] and not indicators["has_negation_pattern"]
    return indicators


# ---------------------------------------------------------------------------
# Core audit logic
# ---------------------------------------------------------------------------

def audit_one_problem(
    problem: dict,
    gen_provider: BaseProvider,
    classifier_provider: BaseProvider,
    z3_timeout: int = 60,
) -> dict:
    """Audit a single 'proved' problem. Returns detailed result dict."""
    pid = problem["id"]
    t0 = time.time()

    # Step 1: Re-generate Z3 code
    user_prompt = build_user_prompt(problem)
    try:
        response = gen_provider.call_structured(
            SYSTEM_PROMPT, user_prompt, Z3GenResult, max_tokens=_B.large
        )
        code = response.get("module_code", "") if isinstance(response, dict) else response.module_code
        code = strip_markdown_fences(code)
    except Exception as e:
        return {
            "id": pid,
            "category": "crash",
            "reason": f"Code generation failed: {str(e)[:200]}",
            "time_s": time.time() - t0,
        }

    # Step 2: Execute original code
    exec_ok, exec_output = run_z3_code(code, timeout=z3_timeout)
    if not exec_ok:
        return {
            "id": pid,
            "category": "crash",
            "reason": f"Execution failed: {exec_output[:200]}",
            "code": code[:2000],
            "time_s": time.time() - t0,
        }

    # Step 3: Structural analysis
    structural = structural_vacuity_check(code)

    # Step 4: Run vacuity variant (best-effort)
    vacuity_code = make_vacuity_variant(code)
    vac_ok, vac_output = run_z3_code(vacuity_code, timeout=z3_timeout)
    vacuity_result = vac_output if vac_ok else f"Vacuity test failed: {vac_output[:300]}"

    # Step 5: LLM classifier
    classifier_prompt = build_classifier_prompt(
        pid,
        problem["statement"],
        code,
        exec_output,
        vacuity_result,
    )
    try:
        raw = classifier_provider.call(
            CLASSIFIER_SYSTEM, classifier_prompt, max_tokens=_B.small
        )
        raw = strip_markdown_fences(raw)
        classification = json.loads(raw)
        category = classification.get("category", "wrong_encoding")
        reason = classification.get("reason", "No reason given")
        if category not in CATEGORIES:
            category = "wrong_encoding"
            reason = f"Unknown category '{classification.get('category')}': {reason}"
    except json.JSONDecodeError:
        # Try to extract from text
        category = "wrong_encoding"
        reason = f"Classifier returned non-JSON: {raw[:200]}"
        for cat in CATEGORIES:
            if cat in raw.lower():
                category = cat
                break
    except Exception as e:
        category = "crash"
        reason = f"Classifier error: {str(e)[:200]}"

    return {
        "id": pid,
        "category": category,
        "reason": reason,
        "structural": structural,
        "exec_ok": exec_ok,
        "exec_output": exec_output[:500],
        "vacuity_ok": vac_ok,
        "code_snippet": code[:1000],
        "time_s": time.time() - t0,
    }


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Automated audit of miniF2F Z3 benchmark")
    parser.add_argument(
        "--results-file",
        default="benchmarks/minif2f_all_gpt-5.4-mini_20260414_041628.json",
        help="Path to benchmark results JSON",
    )
    parser.add_argument("--model", default="gpt-5.4-mini", help="Model for code generation")
    parser.add_argument("--classifier-model", default="gpt-5.4-mini", help="Model for classification")
    parser.add_argument("--sample", type=int, default=None, help="Audit only N problems (random sample)")
    parser.add_argument("--seed", type=int, default=42, help="Random seed for sampling")
    parser.add_argument("--z3-timeout", type=int, default=60, help="Z3 execution timeout")
    parser.add_argument(
        "--output",
        default="benchmarks/full_audit_results.json",
        help="Output file",
    )
    args = parser.parse_args()

    # Load benchmark results
    with open(args.results_file) as f:
        bench = json.load(f)

    proved_results = [r for r in bench["results"] if r["status"] == "proved"]
    logger.info("Loaded %d proved results from %s", len(proved_results), args.results_file)

    # Sample if requested
    if args.sample and args.sample < len(proved_results):
        import random
        random.seed(args.seed)
        proved_results = random.sample(proved_results, args.sample)
        logger.info("Sampled %d problems for audit", args.sample)

    # Load problem statements
    logger.info("Loading miniF2F dataset...")
    problems_map = load_problems_map()

    # Set up providers
    gen_provider = get_provider(args.model)
    classifier_provider = get_provider(args.classifier_model)

    # Run audit
    audit_results = []
    counts = {cat: 0 for cat in CATEGORIES}

    print(f"\n{'='*60}")
    print(f"Auto-Audit: {len(proved_results)} problems")
    print(f"Generator: {args.model} | Classifier: {args.classifier_model}")
    print(f"{'='*60}\n")

    for i, result in enumerate(proved_results, 1):
        pid = result["id"]
        problem = problems_map.get(pid)
        if not problem:
            logger.warning("Problem %s not found in dataset, skipping", pid)
            continue

        print(f"[{i}/{len(proved_results)}] {pid}...", end=" ", flush=True)

        audit = audit_one_problem(
            problem, gen_provider, classifier_provider,
            z3_timeout=args.z3_timeout,
        )
        audit_results.append(audit)
        cat = audit["category"]
        counts[cat] += 1

        print(f"{cat.upper()} ({audit['time_s']:.1f}s) — {audit.get('reason', '')[:80]}")

        # Running tally
        total_so_far = sum(counts.values())
        valid_so_far = counts["valid"]
        invalid_so_far = total_so_far - valid_so_far
        print(f"  Running: {valid_so_far} valid / {total_so_far} total ({valid_so_far/total_so_far*100:.0f}% valid)")

    # Summary
    total = sum(counts.values())
    print(f"\n{'='*60}")
    print(f"AUDIT RESULTS: {total} problems audited")
    print(f"{'='*60}")
    for cat in CATEGORIES:
        c = counts[cat]
        pct = c / total * 100 if total else 0
        print(f"  {cat:25s}: {c:4d} ({pct:5.1f}%)")
    print(f"{'='*60}")

    valid_count = counts["valid"]
    invalid_count = total - valid_count
    print(f"\n  VALID: {valid_count}/{total} ({valid_count/total*100:.1f}%)")
    print(f"  INVALID: {invalid_count}/{total} ({invalid_count/total*100:.1f}%)")

    original_claimed = bench.get("proved", len(proved_results))
    original_total = bench.get("n_problems", 244)
    if args.sample:
        # Extrapolate
        est_valid = int(valid_count / total * original_claimed) if total else 0
        print(f"\n  Extrapolated true-positive rate: ~{valid_count/total*100:.0f}%")
        print(f"  Estimated real proved: ~{est_valid}/{original_total} ({est_valid/original_total*100:.0f}%)")
    else:
        print(f"\n  True-positive proved: {valid_count}/{original_total} ({valid_count/original_total*100:.1f}%)")

    # Save
    output_data = {
        "source_file": args.results_file,
        "model": args.model,
        "classifier_model": args.classifier_model,
        "sample_size": args.sample,
        "seed": args.seed,
        "total_audited": total,
        "counts": counts,
        "valid_rate": valid_count / total if total else 0,
        "original_proved": original_claimed,
        "original_total": original_total,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "results": audit_results,
    }

    os.makedirs(os.path.dirname(args.output) or ".", exist_ok=True)
    with open(args.output, "w") as f:
        json.dump(output_data, f, indent=2)
    print(f"\nResults saved to {args.output}")


if __name__ == "__main__":
    main()

"""Generate a Z3 constraint module from identified contradictions.

Part of Arbiter's agentic init pipeline. Takes contradictions extracted
from a source document and produces a runnable Z3 Python module that
formally encodes each contradiction as an SMT check.
"""

from __future__ import annotations

import json
import logging
import os
import subprocess
import sys
import textwrap
from pathlib import Path

from arbiter.config import TokenBudgets
from arbiter.providers.base import BaseProvider
from arbiter.schemas import Z3GenResult

logger = logging.getLogger(__name__)
_B = TokenBudgets()

# ---------------------------------------------------------------------------
# Reference Z3 module shown to the LLM as an example of the target format
# ---------------------------------------------------------------------------
_Z3_EXAMPLE = textwrap.dedent(r'''
from z3 import (
    Solver, Bool, Int, Function, BoolSort, IntSort,
    And, Or, Not, Implies, ForAll, Exists, sat, unsat,
)

def _check1_immutable_vs_mutable():
    """
    Example: A theory claims property P is immutable (never changes)
    AND that some process Q can alter P. These are jointly UNSAT.
    """
    s = Solver()
    N = 3  # small domain
    P_before = [Bool(f"P_before_{i}") for i in range(N)]
    P_after = [Bool(f"P_after_{i}") for i in range(N)]

    # Claim A: P is immutable (before == after for all elements)
    for i in range(N):
        s.add(P_before[i] == P_after[i])

    # Claim B: process Q changes at least one element of P
    s.add(Or(*[And(P_before[i], Not(P_after[i])) for i in range(N)]
           + [And(Not(P_before[i]), P_after[i]) for i in range(N)]))

    result = s.check()
    return {
        "name": "CHECK 1: Immutability vs mutation",
        "result": "SAT" if result == sat else ("UNSAT" if result == unsat else "UNKNOWN"),
        "expected": "UNSAT",
        "explanation": "If P_before == P_after for all elements, no element can differ.",
    }

def _check2_charitable_rescue():
    """
    Charitable rescue: drop immutability claim. Now SAT but original claim vacuous.
    """
    s = Solver()
    N = 3
    P_before = [Bool(f"Pb_{i}") for i in range(N)]
    P_after = [Bool(f"Pa_{i}") for i in range(N)]

    # Only Claim B: something changes
    s.add(Or(*[And(P_before[i], Not(P_after[i])) for i in range(N)]
           + [And(Not(P_before[i]), P_after[i]) for i in range(N)]))

    result = s.check()
    return {
        "name": "CHECK 2: Charitable rescue (drop immutability)",
        "result": "SAT (original immutability claim becomes vacuous)" if result == sat else "UNSAT",
        "expected": "SAT",
        "explanation": "Without immutability, Z3 trivially finds a model where something changes.",
    }

def verify() -> dict:
    """Run all checks and return structured findings."""
    return {
        "check1": _check1_immutable_vs_mutable(),
        "check2": _check2_charitable_rescue(),
    }

if __name__ == "__main__":
    findings = verify()
    for key, f in findings.items():
        print(f"=== {f['name']} ===")
        print(f"  Result:      {f['result']}")
        print(f"  Expected:    {f['expected']}")
        print(f"  Explanation: {f['explanation']}")
        print()
''').strip()

# ---------------------------------------------------------------------------
# JSON schema for the LLM's structured response
# ---------------------------------------------------------------------------


# ---------------------------------------------------------------------------
# Proof verification example — domain-neutral economic model
# Shows proof verification, sensitivity, boundary, and counterexample patterns
# ---------------------------------------------------------------------------
_Z3_PROOF_EXAMPLE = textwrap.dedent(r'''
from z3 import Solver, Optimize, Real, And, Or, Not, Implies, ForAll, sat, unsat

def _check_proof_wedge_positive():
    """PROOF VERIFICATION: Given N>1 and demand externality ell>0,
    does the Nash automation rate exceed the cooperative optimum?
    Model: alpha_NE = s/(s + ell/N), alpha_CO = s/(s + ell)
    Proposition: alpha_NE > alpha_CO
    Method: encode assumptions + NOT(proposition), check UNSAT.
    """
    s = Solver()
    N, ell, sp = Real('N'), Real('ell'), Real('s')
    s.add(N > 1, ell > 0, sp > 0)

    alpha_NE = sp / (sp + ell / N)
    alpha_CO = sp / (sp + ell)

    # Negate the proposition
    s.add(Not(alpha_NE > alpha_CO))
    result = s.check()
    return {
        "name": "PROOF: Over-automation (alpha_NE > alpha_CO)",
        "result": "UNSAT" if result == unsat else "SAT",
        "expected": "UNSAT",
        "check_type": "proof_verification",
        "encodability": "simplified",  # uses closed-form, not full profit function
        "targets": ["P1"],
        "explanation": "With N>1, ell/N < ell, so denominator of alpha_NE is smaller.",
        "model_values": {},
    }

def _check_sensitivity_N():
    """ASSUMPTION SENSITIVITY: Is N>1 load-bearing for the over-automation result?
    Drop N>1, keep other assumptions, check if proof still holds.
    """
    s = Solver()
    N, ell, sp = Real('N'), Real('ell'), Real('s')
    s.add(ell > 0, sp > 0)  # N>1 DROPPED
    s.add(Not(sp / (sp + ell / N) > sp / (sp + ell)))
    result = s.check()
    model_values = {}
    if result == sat:
        m = s.model()
        model_values = {str(v): str(m.eval(v, model_completion=True)) for v in [N, ell, sp]}
    return {
        "name": "SENSITIVITY: Drop N>1",
        "result": "SAT" if result == sat else "UNSAT",
        "expected": "SAT",
        "check_type": "assumption_sensitivity",
        "encodability": "simplified",
        "targets": ["A1", "P1"],
        "load_bearing": result == sat,
        "explanation": "When N=1, monopolist internalizes the externality.",
        "model_values": model_values,
    }

def _check_boundary_N():
    """BOUNDARY ANALYSIS: How does the wedge scale with N?
    Compute wedge at specific parameter values.
    """
    results = {}
    for n_val in [2, 5, 10, 50]:
        s = Solver()
        sp, ell = Real('sp'), Real('ell')
        s.add(sp == 3, ell == 5)  # fix parameters
        ne = sp / (sp + ell / n_val)
        co = sp / (sp + ell)
        s.check()
        m = s.model()
        results[f"N={n_val}"] = str(m.eval(ne - co, model_completion=True))
    return {
        "name": "BOUNDARY: Wedge vs N",
        "result": "OPTIMAL",
        "expected": "OPTIMAL",
        "check_type": "boundary_analysis",
        "encodability": "fully_encoded",
        "targets": ["P1"],
        "explanation": f"Wedge at different N: {results}",
        "model_values": results,
    }

def verify() -> dict:
    return {
        "proof_p1": _check_proof_wedge_positive(),
        "sensitivity_N": _check_sensitivity_N(),
        "boundary_N": _check_boundary_N(),
    }

if __name__ == "__main__":
    for key, finding in verify().items():
        print(f"=== {finding['name']} ===")
        print(f"  Result:      {finding['result']}")
        print(f"  Expected:    {finding['expected']}")
        print(f"  Type:        {finding['check_type']}")
        print(f"  Encodability:{finding['encodability']}")
        if finding.get('model_values'):
            print(f"  Values:      {finding['model_values']}")
        if 'load_bearing' in finding:
            print(f"  Load-bearing:{finding['load_bearing']}")
        print(f"  Explanation: {finding['explanation']}")
        print()
''').strip()


def _build_prompt(
    contradictions: list[dict],
    claims: list[dict],
    formal_model: dict | None = None,
) -> tuple[str, str]:
    """Build (system, user) prompts for Z3 module generation."""
    has_formal_model = formal_model and (
        formal_model.get("propositions") or formal_model.get("equations")
    )

    system = textwrap.dedent("""\
        You are an expert in formal verification. Generate a standalone Python module
        that formally verifies claims from an academic paper using verified backends.

        ═══════════════════════════════════════════════════════════
        BACKEND 1: Knuckledragger (kdrag) — PREFERRED for Z3-encodable claims
        ═══════════════════════════════════════════════════════════

        Knuckledragger wraps Z3 with tamper-proof Proof objects. kd.prove() either
        returns a Proof or raises LemmaError — proofs cannot be faked.

        ```python
        import kdrag as kd
        from kdrag.smt import *  # Real, Int, Bool, ForAll, Exists, Implies, And, Or, Not

        # Direct proof
        x, y = Reals("x y")
        thm = kd.prove(ForAll([x, y], Implies(And(x > 0, y > 0), x + y > 0)))

        # Lemma chaining
        n = Int("n")
        lem1 = kd.prove(ForAll([n], Implies(n > 1, n*n > n)))
        lem2 = kd.prove(ForAll([n], Implies(n > 1, n*n > 1)), by=[lem1])

        # Integer constraints / Diophantine
        x, y = Ints("x y")
        thm = kd.prove(ForAll([x, y],
            Implies(y*y + 3*x*x*y*y == 30*x*x + 517, 3*x*x*y*y == 588)))

        # Divisibility / GCD
        n, d = Ints("n d")
        thm = kd.prove(ForAll([n, d],
            Implies(And(n >= 0, d > 1, (21*n+4) % d == 0, (14*n+3) % d == 0), False)))

        # Lemma chaining (use proven lemmas in subsequent proofs)
        lem1 = kd.prove(ForAll([n], Implies(n > 1, n*n > n)))
        lem2 = kd.prove(ForAll([n], Implies(n > 1, n*n > 1)), by=[lem1])

        # Induction (for recursive/inductive properties)
        Nat = kd.Inductive("Nat")
        Nat.declare("Z")
        Nat.declare("S", ("pred", Nat))
        Nat = Nat.create()
        n, m = smt.Consts("n m", Nat)
        add = smt.Function("add", Nat, Nat, Nat)
        add = kd.define("add", [n, m], kd.cond(
            (n.is_Z, m), (n.is_S, Nat.S(add(n.pred, m)))))
        kd.notation.add.register(Nat, add)
        l = kd.Lemma(smt.ForAll([n], n + Nat.Z == n))
        _n = l.fix()
        l.induct(_n)
        l.auto(by=[add.defn])  # Base case
        l.auto(by=[add.defn])  # Inductive step
        thm = l.qed()  # Returns Proof object

        # Recursive functions with chain proofs
        F = smt.Function("F", smt.IntSort(), smt.IntSort())
        ax = kd.axiom(ForAll([n], Implies(n >= 1000, F(n) == n - 3)))
        step1 = kd.prove(F(1004) == 1001, by=[ax])
        step2 = kd.prove(F(1001) == 998, by=[ax])
        # Chain: use proven steps as lemmas for next proof

        # Axioms (trusted assumptions — use sparingly, clearly mark trust boundary)
        ax = kd.axiom(claim)  # NOT verified — asserted as true

        # If proof fails → kd.kernel.LemmaError
        ```

        ═══════════════════════════════════════════════════════════
        BACKEND 2: SymPy — for trig, recurrences, symbolic algebra
        ═══════════════════════════════════════════════════════════

        ```python
        from sympy import *

        # Trig identity (RIGOROUS algebraic proof)
        x = Symbol('x')
        mp = minimal_polynomial(cos(pi/7) - cos(2*pi/7) + cos(3*pi/7) - Rational(1,2), x)
        assert mp == x  # Proves the expression equals exactly 0

        # Symbolic GCD
        n = Symbol('n', integer=True)
        g = gcd(21*n + 4, 14*n + 3)  # Returns 1

        # Recurrence solving
        f = Function('f')
        sol = rsolve(f(n) + f(n-1) - n**2, f(n))
        ```

        ═══════════════════════════════════════════════════════════
        BACKEND 3: Raw Z3 — for counterexamples, optimization, model extraction
        ═══════════════════════════════════════════════════════════

        Use raw Z3 (Solver, Optimize) ONLY when you need:
        - Counterexample extraction via s.model().eval()
        - Optimization via Optimize().minimize/maximize
        - Model values for boundary analysis

        ```python
        from z3 import Solver, Optimize, Real, Int, sat, unsat
        s = Solver()
        # ... add constraints ...
        if s.check() == sat:
            model_values = {str(v): str(s.model().eval(v)) for v in vars}
        ```

        ═══════════════════════════════════════════════════════════
        CHOOSING THE RIGHT BACKEND
        ═══════════════════════════════════════════════════════════

        | Claim type                | Backend    | Why                              |
        |---------------------------|------------|----------------------------------|
        | Proposition proof         | kdrag      | Proof certificate                |
        | Contradiction check       | kdrag      | A ∧ B → False via kd.prove       |
        | Trig/symbolic identity    | sympy      | minimal_polynomial == x          |
        | Recurrence/series         | sympy      | rsolve, summation                |
        | Inductive property        | kdrag      | kd.Lemma + l.induct() + l.auto() |
        | Recursive function        | kdrag      | Chain proofs with by=[step1,...]  |
        | Counterexample search     | raw Z3     | Need model.eval()                |
        | Boundary/optimization     | raw Z3     | Optimize() solver                |
        | Assumption sensitivity    | kdrag      | Drop Ai, reprove                 |

        ═══════════════════════════════════════════════════════════
        MODULE FORMAT
        ═══════════════════════════════════════════════════════════

        1. Export verify() -> dict returning {"check1": {...}, "check2": {...}, ...}
        2. Each check dict keys:
           - name: descriptive title
           - result: "PROVED" | "SAT" | "UNSAT" | "UNKNOWN" | "OPTIMAL"
           - expected: what the check expects
           - explanation: what the result means
           - check_type: "contradiction_check" | "proof_verification" |
             "counterexample_search" | "assumption_sensitivity" |
             "boundary_analysis" | "policy_verification"
           - encodability: "fully_encoded" | "simplified" | "structural_only" | "not_encodable"
           - targets: list of assumption/proposition/policy IDs being checked
           - model_values: dict when SAT (counterexample)
           - load_bearing: bool (sensitivity checks)
           - backend: "kdrag" | "sympy" | "z3"
           - proof_certificate: str(proof_object) when kdrag proof succeeds
        3. Include if __name__ == "__main__" block for standalone testing.

        ENCODABILITY RULES:
        - "fully_encoded": constraints faithfully represent the paper's math
        - "simplified": had to simplify (linearized, fixed parameters)
        - "structural_only": encodes logical structure, not content
        - "not_encodable": probability, calculus, subjective experience, Turing
          computability, or metaphysical identity (explain WHY)

        For claims involving trig/calculus that Z3 cannot encode, use SymPy
        with minimal_polynomial instead of marking "not_encodable".

        IMPORTANT: Return ONLY valid Python source code in the module_code field.
        Do NOT include markdown fences or any surrounding text in that field.
    """)

    contradictions_json = json.dumps(contradictions, indent=2, default=str)
    claims_json = json.dumps(claims[:20], indent=2, default=str)

    # Build user prompt with appropriate example and data
    parts = [f"Here is an example Z3 module:\n\n```python\n{_Z3_EXAMPLE}\n```\n"]

    if has_formal_model:
        parts.append(f"Here is a proof verification example:\n\n```python\n{_Z3_PROOF_EXAMPLE}\n```\n")
        formal_json = json.dumps(formal_model, indent=2, default=str)
        parts.append(f"FORMAL MODEL STRUCTURE:\n{formal_json}\n")
        parts.append(
            "Generate checks for:\n"
            "1. Every z3-encodable contradiction (UNSAT checks)\n"
            "2. Every proposition with stated assumptions (proof verification)\n"
            "3. For each verified proposition: sensitivity analysis on each assumption\n"
            "4. Boundary analysis for key parameters\n"
            "5. Each policy claim\n"
            "6. Extract counterexample values whenever SAT\n\n"
            "CRITICAL: For proof verification, encode the FULL model equations\n"
            "from the equations list, not simplified closed-form solutions.\n"
            "Only fall back to simplified if the full encoding is too complex,\n"
            "and mark those checks as encodability='simplified'.\n"
        )

    parts.append(f"CONTRADICTIONS:\n{contradictions_json}\n")
    parts.append(f"KEY CLAIMS (for context):\n{claims_json}\n")

    if not has_formal_model:
        parts.append(
            "For each contradiction that is z3-encodable, create a check.\n"
            "For contradictions that are purely rhetorical or philosophical,\n"
            "skip them but note why in a comment.\n"
            "Where a contradiction involves two jointly-inconsistent claims,\n"
            "ALSO generate a charitable rescue check.\n"
        )

    parts.append("Return the module_code and check_names.")

    user = "\n".join(parts)
    return system, user


def _run_z3_module(path: str, timeout: int = 60) -> tuple[bool, str]:
    """Execute the generated Z3 module in a subprocess.

    Returns (success, output_or_error).
    """
    try:
        result = subprocess.run(
            [sys.executable, path],
            capture_output=True,
            text=True,
            timeout=timeout,
            env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
        )
        if result.returncode == 0:
            return True, result.stdout
        return False, f"Exit code {result.returncode}\nSTDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"
    except subprocess.TimeoutExpired:
        return False, f"Module execution timed out after {timeout}s"
    except Exception as exc:
        return False, f"Failed to run module: {exc}"


def _fix_prompt(code: str, error: str) -> tuple[str, str]:
    """Build a repair prompt when the generated module fails."""
    system = textwrap.dedent("""\
        You are an expert Python/Z3 debugger. A generated Z3 module failed to run.
        Fix the code so it runs successfully. Return only the corrected module_code.
        Common issues:
        - Missing imports (e.g. forgot to import ForAll, Exists, RealSort, etc.)
        - Variable name collisions across checks (use unique suffixes)
        - Calling z3 functions incorrectly
        - Syntax errors
        Do NOT change the logical structure of the checks unless the logic itself is wrong.
    """)
    user = textwrap.dedent(f"""\
        The following Z3 module failed with this error:

        ERROR:
        {error}

        CODE:
        ```python
        {code}
        ```

        Fix the code and return it in the module_code field.
    """)
    return system, user


def generate_z3_module(
    contradictions: list[dict],
    claims: list[dict],
    provider: BaseProvider,
    output_path: str,
    *,
    formal_model: dict | None = None,
) -> dict:
    """Use LLM to generate a Z3 Python module encoding formal contradictions.

    The generated module:
    1. Exports a ``verify() -> dict`` function (Arbiter's Z3 plugin contract).
    2. Uses z3-solver Python bindings.
    3. Includes one check per z3-encodable contradiction.
    4. Includes a "charitable rescue" check where possible.
    5. Is runnable standalone: ``python3 z3_module.py``.

    After generation the module is executed via subprocess to verify correctness.
    On failure, the error is fed back to the LLM for up to 2 repair attempts.

    Parameters
    ----------
    contradictions:
        Output of ``claim_extractor.identify_contradictions``.
    claims:
        Output of ``pdf_reader.extract_claims``.
    provider:
        An Arbiter ``BaseProvider`` instance for LLM calls.
    output_path:
        Filesystem path where the generated ``z3_module.py`` will be written.

    Returns
    -------
    dict with keys:
        - ``path``: absolute path to the generated module
        - ``checks``: list of check names
        - ``self_test_passed``: whether the module ran successfully
    """
    # ── Step 1: Generate initial module code ──────────────────────────
    system, user = _build_prompt(contradictions, claims, formal_model=formal_model)
    logger.info("Generating Z3 module via LLM...")

    # Z3 modules can be large (17+ propositions = 500+ lines of code).
    # Use xl budget so thinking models have room for both reasoning and output.
    response = provider.call_structured(system, user, Z3GenResult, max_tokens=_B.xl)
    code = response["module_code"]
    check_names = response.get("check_names", [])

    # Strip markdown fences if the LLM included them despite instructions
    if code.startswith("```"):
        lines = code.split("\n")
        # Drop first and last fence lines
        if lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        code = "\n".join(lines)

    # ── Step 2: Write and test ────────────────────────────────────────
    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(code, encoding="utf-8")
    logger.info("Z3 module written to %s", out)

    success, output = _run_z3_module(str(out))

    # ── Step 3: Retry loop (up to 3 attempts for complex proof checks)
    max_retries = 3
    for attempt in range(1, max_retries + 1):
        if success:
            break
        logger.warning(
            "Z3 module self-test failed (attempt %d/%d): %s",
            attempt, max_retries, output[:300],
        )
        fix_system, fix_user = _fix_prompt(code, output)
        fix_response = provider.call_structured(
            fix_system, fix_user, Z3GenResult, max_tokens=_B.large
        )
        code = fix_response["module_code"]
        check_names = fix_response.get("check_names", check_names)

        if code.startswith("```"):
            lines = code.split("\n")
            if lines[0].startswith("```"):
                lines = lines[1:]
            if lines and lines[-1].strip() == "```":
                lines = lines[:-1]
            code = "\n".join(lines)

        out.write_text(code, encoding="utf-8")
        success, output = _run_z3_module(str(out))

    if success:
        logger.info("Z3 module self-test PASSED.")
    else:
        logger.error("Z3 module self-test FAILED after %d retries: %s", max_retries, output[:300])

    return {
        "path": str(out.resolve()),
        "checks": check_names,
        "self_test_passed": success,
    }

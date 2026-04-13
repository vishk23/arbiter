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
    And, Or, Not, Implies, sat, unsat,
)

def _check1_example():
    """
    Encode two constraints that are jointly UNSAT.
    """
    s = Solver()
    N = 5
    nodes = range(N)

    E0 = [[Bool(f"E0_{u}_{v}") for v in nodes] for u in nodes]
    E1 = [[Bool(f"E1_{u}_{v}") for v in nodes] for u in nodes]

    # DAG ordering witnesses
    ord0 = [Int(f"ord0_{u}") for u in nodes]
    ord1 = [Int(f"ord1_{u}") for u in nodes]
    for u in nodes:
        s.add(ord0[u] >= 0, ord0[u] < N)
        s.add(ord1[u] >= 0, ord1[u] < N)
        for v in nodes:
            s.add(Implies(E0[u][v], ord0[u] < ord0[v]))
            s.add(Implies(E1[u][v], ord1[u] < ord1[v]))

    # Constraint A: G is fixed across time slices
    for u in nodes:
        for v in nodes:
            s.add(E0[u][v] == E1[u][v])

    # Constraint B: some edge is created between t0 and t1
    creation_disjuncts = []
    for u in nodes:
        for v in nodes:
            creation_disjuncts.append(And(Not(E0[u][v]), E1[u][v]))
    s.add(Or(*creation_disjuncts))

    result = s.check()
    return {
        "name": "CHECK 1: Example",
        "result": "SAT" if result == sat else ("UNSAT" if result == unsat else "UNKNOWN"),
        "expected": "UNSAT",
        "explanation": "Constraints A and B are directly contradictory.",
    }

def _check2_charitable_rescue():
    """
    Charitable rescue: drop Constraint A. Now SAT but original claim vacuous.
    """
    s = Solver()
    N = 5
    nodes = range(N)
    E0 = [[Bool(f"E0b_{u}_{v}") for v in nodes] for u in nodes]
    E1 = [[Bool(f"E1b_{u}_{v}") for v in nodes] for u in nodes]
    ord0 = [Int(f"ord0b_{u}") for u in nodes]
    ord1 = [Int(f"ord1b_{u}") for u in nodes]
    for u in nodes:
        s.add(ord0[u] >= 0, ord0[u] < N)
        s.add(ord1[u] >= 0, ord1[u] < N)
        for v in nodes:
            s.add(Implies(E0[u][v], ord0[u] < ord0[v]))
            s.add(Implies(E1[u][v], ord1[u] < ord1[v]))
    creation = []
    for u in nodes:
        for v in nodes:
            creation.append(And(Not(E0[u][v]), E1[u][v]))
    s.add(Or(*creation))
    result = s.check()
    return {
        "name": "CHECK 2: Charitable rescue",
        "result": "SAT (but original claim becomes vacuous)" if result == sat else "UNSAT",
        "expected": "SAT",
        "explanation": "Without the fixedness constraint, Z3 finds a model.",
    }

def verify() -> dict:
    """Run all checks and return structured findings."""
    return {
        "check1": _check1_example(),
        "check2": _check2_charitable_rescue(),
    }

if __name__ == "__main__":
    findings = verify()
    for key, f in findings.items():
        print(f"=== {f['name']} ===")
        print(f"Result: {f['result']}")
        if "expected" in f:
            print(f"Expected: {f['expected']}")
        print(f"Explanation: {f['explanation']}")
        print()
''').strip()

# ---------------------------------------------------------------------------
# JSON schema for the LLM's structured response
# ---------------------------------------------------------------------------


def _build_prompt(contradictions: list[dict], claims: list[dict]) -> tuple[str, str]:
    """Build (system, user) prompts for Z3 module generation."""
    system = textwrap.dedent("""\
        You are an expert in formal verification with the Z3 SMT solver (Python bindings).
        Your task: given a set of contradictions identified in a source document, generate
        a standalone Python module that encodes each contradiction as a Z3 satisfiability check.

        REQUIREMENTS:
        1. Import only from z3 (z3-solver package). Standard library is also OK.
        2. Define one private _check function per z3-encodable contradiction.
        3. Where possible, include a "charitable rescue" check that relaxes the contradiction
           to show it becomes SAT but the original claim becomes vacuous.
        4. Export a public verify() -> dict function that calls all checks and returns
           {"check1": {...}, "check2": {...}, ...} where each value has keys:
           name, result, expected, explanation.
        5. Include an if __name__ == "__main__" block that calls verify() and pretty-prints.
        6. Use descriptive variable names. Include docstrings on each _check function
           explaining what is being encoded and what result is expected.
        7. The result field should be "SAT" or "UNSAT" or "UNKNOWN" based on z3's output.
        8. Every check MUST call s.check() and return its result.

        IMPORTANT: Return ONLY valid Python source code in the module_code field.
        Do NOT include markdown fences or any surrounding text in that field.
    """)

    contradictions_json = json.dumps(contradictions, indent=2, default=str)
    claims_json = json.dumps(claims[:20], indent=2, default=str)  # cap context size

    user = textwrap.dedent(f"""\
        Here is an example Z3 module that follows the required pattern:

        ```python
        {_Z3_EXAMPLE}
        ```

        Now generate a Z3 module for the following contradictions found in a source document.

        CONTRADICTIONS:
        {contradictions_json}

        KEY CLAIMS (for context):
        {claims_json}

        For each contradiction that is z3-encodable (involves formal/logical/mathematical
        claims that can be modeled with Boolean/Int variables and constraints), create a check.
        For contradictions that are purely rhetorical or philosophical, skip them but note why
        in a comment.

        Where a contradiction involves two jointly-inconsistent claims, ALSO generate a
        charitable rescue check that drops one constraint to show what survives.

        Return the module_code and check_names.
    """)
    return system, user


def _run_z3_module(path: str, timeout: int = 30) -> tuple[bool, str]:
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
    system, user = _build_prompt(contradictions, claims)
    logger.info("Generating Z3 module via LLM...")

    response = provider.call_structured(system, user, Z3GenResult, max_tokens=_B.large)
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

    # ── Step 3: Retry loop (up to 2 attempts) ────────────────────────
    max_retries = 2
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

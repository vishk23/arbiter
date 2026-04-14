from typing import Any, Dict, List

import kdrag as kd
from kdrag.smt import *
from kdrag.kernel import LemmaError


def verify() -> Dict[str, Any]:
    checks: List[Dict[str, Any]] = []

    # We verify the classification for affine candidates f(x)=2x+c:
    # (1) every such function satisfies the FE for all integers a,b,c
    # (2) numerical sanity checks on concrete constants/inputs
    #
    # The full uniqueness argument over all integer functions is second-order and
    # not directly encodable in first-order SMT/kdrag. We therefore report that
    # limitation explicitly instead of faking a proof.

    a, b, c = Ints("a b c")

    def add_check(name: str, passed: bool, backend: str, proof_type: str, details: str) -> None:
        checks.append({
            "name": name,
            "passed": bool(passed),
            "backend": backend,
            "proof_type": proof_type,
            "details": details,
        })

    # Certified proof that every affine function f(x)=2x+c is a solution.
    try:
        lhs = (2 * (2 * a + c) + c) + 2 * (2 * b + c)
        rhs = 2 * ((2 * (a + b) + c)) + c
        thm_family = kd.prove(ForAll([a, b, c], lhs == rhs))
        add_check(
            name="affine_family_satisfies_equation",
            passed=True,
            backend="kdrag",
            proof_type="certificate",
            details=f"Certified by kdrag/Z3: {thm_family}",
        )
    except LemmaError as e:
        add_check(
            name="affine_family_satisfies_equation",
            passed=False,
            backend="kdrag",
            proof_type="certificate",
            details=f"kdrag failed to certify that f(x)=2x+c satisfies the equation: {e}",
        )

    # Certified algebraic identity corresponding to the substitution in the hint:
    # If f(x)=2x+c then f(f(b)) = c + 2 f(b).
    try:
        bb, cc = Ints("bb cc")
        thm_iter = kd.prove(ForAll([bb, cc], 2 * (2 * bb + cc) + cc == cc + 2 * (2 * bb + cc)))
        add_check(
            name="iterated_form_matches_hint_for_affine_solution",
            passed=True,
            backend="kdrag",
            proof_type="certificate",
            details=f"Certified by kdrag/Z3: {thm_iter}",
        )
    except LemmaError as e:
        add_check(
            name="iterated_form_matches_hint_for_affine_solution",
            passed=False,
            backend="kdrag",
            proof_type="certificate",
            details=f"kdrag failed on the iterated identity for affine solutions: {e}",
        )

    # Numerical sanity checks.
    numerical_cases = [
        {"c": 0, "a": 1, "b": -3},
        {"c": 5, "a": -2, "b": 4},
        {"c": -7, "a": 3, "b": 0},
    ]
    num_ok = True
    num_details_parts = []
    for case in numerical_cases:
        cc = case["c"]
        aa = case["a"]
        bbv = case["b"]

        def f(x: int, cst: int = cc) -> int:
            return 2 * x + cst

        lhs_v = f(2 * aa) + 2 * f(bbv)
        rhs_v = f(f(aa + bbv))
        ok = lhs_v == rhs_v
        num_ok = num_ok and ok
        num_details_parts.append(
            f"c={cc}, a={aa}, b={bbv}: lhs={lhs_v}, rhs={rhs_v}, passed={ok}"
        )
    add_check(
        name="numerical_sanity_affine_examples",
        passed=num_ok,
        backend="numerical",
        proof_type="numerical",
        details="; ".join(num_details_parts),
    )

    # Explicitly record the limitation on full uniqueness.
    add_check(
        name="full_uniqueness_over_all_integer_functions",
        passed=False,
        backend="kdrag",
        proof_type="certificate",
        details=(
            "The IMO statement asks to determine all functions f: Z -> Z satisfying a functional equation. "
            "A complete uniqueness proof quantifies over arbitrary integer functions, which is a second-order claim "
            "and is not directly representable in first-order SMT/kdrag. The user-provided hint relies on surjectivity "
            "when replacing x=f(b), but surjectivity is not established from the equation alone inside this encoding. "
            "Therefore this module rigorously certifies that every function of the form f(x)=2x+c is a solution, "
            "but it does not certify the converse in the SMT backend."
        ),
    )

    proved = all(ch["passed"] for ch in checks)
    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    import json
    print(json.dumps(verify(), indent=2, sort_keys=True))
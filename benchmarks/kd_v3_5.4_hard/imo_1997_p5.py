import math
from typing import List, Dict, Any

import kdrag as kd
from kdrag.smt import *
from sympy import Integer


def _check_kdrag_base_ge_2_nonnegative_power_lower_bound() -> Dict[str, Any]:
    name = "kdrag_pow_ge_one_for_base_ge_2"
    try:
        t, k = Ints("t k")
        thm = kd.prove(
            ForAll([t, k], Implies(And(t >= 2, k >= 0), t**k >= 1))
        )
        return {
            "name": name,
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": str(thm),
        }
    except Exception as e:
        return {
            "name": name,
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"kdrag proof failed: {e}",
        }


def _check_kdrag_no_r_ge_3_solution() -> Dict[str, Any]:
    name = "kdrag_no_solutions_when_r_ge_3"
    try:
        t, r = Ints("t r")
        thm = kd.prove(
            ForAll(
                [t, r],
                Implies(And(t >= 2, r >= 3), t**r - 2 > r),
            )
        )
        return {
            "name": name,
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": str(thm),
        }
    except Exception as e:
        return {
            "name": name,
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"kdrag proof failed: {e}",
        }


def _check_case_r1_unique() -> Dict[str, Any]:
    name = "case_r_eq_1_unique_gives_t3_b1"
    passed = False
    details = ""
    try:
        sols = []
        for t in range(2, 100):
            denom = t - 2
            if denom != 0 and 1 % denom == 0:
                b = 1 // denom
                if b > 0 and b * (t - 2) == 1:
                    sols.append((t, b))
        passed = sols == [(3, 1)]
        details = f"Solutions to b*(t-2)=1 with t>=2,b>=1 found in exhaustive integer search up to t<100: {sols}. By positivity, this forces t-2=1 and b=1, so uniquely (t,b)=(3,1)."
    except Exception as e:
        details = f"computation failed: {e}"
    return {
        "name": name,
        "passed": passed,
        "backend": "numerical",
        "proof_type": "numerical",
        "details": details,
    }


def _check_case_r2_unique() -> Dict[str, Any]:
    name = "case_r_eq_2_unique_gives_t2_b1"
    passed = False
    details = ""
    try:
        sols = []
        for t in range(2, 100):
            denom = t * t - 2
            if denom != 0 and 2 % denom == 0:
                b = 2 // denom
                if b > 0 and b * (t * t - 2) == 2:
                    sols.append((t, b))
        passed = sols == [(2, 1)]
        details = f"Solutions to b*(t^2-2)=2 with t>=2,b>=1 found in exhaustive integer search up to t<100: {sols}. Since t^2-2>=2, positivity forces t^2-2=2 and b=1, so uniquely (t,b)=(2,1)."
    except Exception as e:
        details = f"computation failed: {e}"
    return {
        "name": name,
        "passed": passed,
        "backend": "numerical",
        "proof_type": "numerical",
        "details": details,
    }


def _check_claimed_solutions_directly() -> Dict[str, Any]:
    name = "claimed_solutions_satisfy_equation"
    try:
        sols = [(1, 1), (16, 2), (27, 3)]
        vals = []
        ok = True
        for x, y in sols:
            lhs = Integer(x) ** (Integer(y) ** 2)
            rhs = Integer(y) ** Integer(x)
            vals.append((x, y, lhs == rhs))
            ok = ok and (lhs == rhs)
        return {
            "name": name,
            "passed": ok,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Direct exact integer evaluation on claimed solutions: {vals}",
        }
    except Exception as e:
        return {
            "name": name,
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"evaluation failed: {e}",
        }


def _check_small_bruteforce_sanity() -> Dict[str, Any]:
    name = "small_bruteforce_sanity"
    try:
        found = []
        for x in range(1, 101):
            for y in range(1, 21):
                if x ** (y * y) == y ** x:
                    found.append((x, y))
        expected = [(1, 1), (16, 2), (27, 3)]
        return {
            "name": name,
            "passed": found == expected,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Brute-force search over 1<=x<=100, 1<=y<=20 found exactly {found}",
        }
    except Exception as e:
        return {
            "name": name,
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"brute-force failed: {e}",
        }


def _check_overall_argument_summary() -> Dict[str, Any]:
    name = "overall_argument_summary"
    details = (
        "Verified backbone: (1) kdrag proves for integers t>=2 and r>=3 that t^r-2>r, excluding all r>=3 in the reduced equation b(t^r-2)=r; "
        "(2) numerical exact checks show the only positive solutions for r=1 and r=2 are (t,b)=(3,1) and (2,1), giving (x,y)=(27,3) and (16,2); "
        "(3) direct exact evaluation verifies (1,1),(16,2),(27,3) satisfy x^(y^2)=y^x. "
        "What is not machine-certified here is the classical unique-factorization reduction from x^(y^2)=y^x to x=t^a, y=t^b and then to b(t^r-2)=r. "
        "Therefore this module provides certified verification of the decisive reduced arithmetic and strong sanity checks, but not a fully formalized end-to-end proof of the number-theoretic reduction."
    )
    return {
        "name": name,
        "passed": False,
        "backend": "numerical",
        "proof_type": "numerical",
        "details": details,
    }


def verify() -> Dict[str, Any]:
    checks: List[Dict[str, Any]] = []
    checks.append(_check_kdrag_base_ge_2_nonnegative_power_lower_bound())
    checks.append(_check_kdrag_no_r_ge_3_solution())
    checks.append(_check_case_r1_unique())
    checks.append(_check_case_r2_unique())
    checks.append(_check_claimed_solutions_directly())
    checks.append(_check_small_bruteforce_sanity())
    checks.append(_check_overall_argument_summary())
    proved = all(ch["passed"] for ch in checks)
    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    import json
    print(json.dumps(verify(), indent=2))
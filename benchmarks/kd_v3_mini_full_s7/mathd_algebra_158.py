from sympy import symbols, Eq, solve, Integer

try:
    import kdrag as kd
    from kdrag.smt import Ints, Int, ForAll, Implies, And
except Exception:  # pragma: no cover
    kd = None


def verify():
    checks = []
    proved = True

    # Check 1: Verified certificate via kdrag for the core arithmetic claim.
    if kd is not None:
        try:
            a = Int("a")
            thm = kd.prove(
                ForAll([a], Implies(And(5 * a + 20 == 60), a == 8))
            )
            checks.append(
                {
                    "name": "kdrag_core_solution",
                    "passed": True,
                    "backend": "kdrag",
                    "proof_type": "certificate",
                    "details": f"kd.prove succeeded: {thm}",
                }
            )
        except Exception as e:
            proved = False
            checks.append(
                {
                    "name": "kdrag_core_solution",
                    "passed": False,
                    "backend": "kdrag",
                    "proof_type": "certificate",
                    "details": f"kdrag proof failed: {type(e).__name__}: {e}",
                }
            )
    else:
        proved = False
        checks.append(
            {
                "name": "kdrag_core_solution",
                "passed": False,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": "kdrag is unavailable in this environment.",
            }
        )

    # Check 2: Symbolic derivation using SymPy, validated by exact arithmetic.
    x = symbols("x", integer=True)
    sol = solve(Eq(x + (x + 2) + (x + 4) + (x + 6) + (x + 8), sum([1, 3, 5, 7, 9, 11, 13, 15]) - 4), x)
    passed_sympy = sol == [8] or sol == (8,) or sol == 8
    if not passed_sympy:
        proved = False
    checks.append(
        {
            "name": "sympy_solve_equation",
            "passed": bool(passed_sympy),
            "backend": "sympy",
            "proof_type": "numerical",
            "details": f"solve returned {sol}; expected x = 8.",
        }
    )

    # Check 3: Numerical sanity check at the concrete solution.
    a_val = 8
    even_sum = a_val + (a_val + 2) + (a_val + 4) + (a_val + 6) + (a_val + 8)
    odd_sum = sum([1, 3, 5, 7, 9, 11, 13, 15])
    passed_num = (even_sum == odd_sum - 4) and (even_sum == 60) and (odd_sum == 64)
    if not passed_num:
        proved = False
    checks.append(
        {
            "name": "numerical_sanity_check",
            "passed": bool(passed_num),
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"For a=8, even_sum={even_sum}, odd_sum={odd_sum}.",
        }
    )

    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    print(verify())
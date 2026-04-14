from sympy import Symbol, Eq, solve, summation
import kdrag as kd
from kdrag.smt import Int, Ints, ForAll, Implies, And


def verify():
    checks = []
    proved = True

    # Check 1: Verified proof with kdrag/Z3 that the arithmetic setup forces x = 8.
    name = "kdrag_forced_smallest_even_integer_is_8"
    try:
        x = Int("x")
        # Encoding the problem statement:
        # 5 consecutive even integers: x, x+2, x+4, x+6, x+8
        # Sum is 4 less than the sum of first 8 odd counting numbers (1..15), which is 64.
        # Therefore 5x + 20 = 60, so x = 8.
        thm = kd.prove(x == 8, by=[])
        passed = False
        details = "Unexpectedly proved x == 8 without assumptions; this check is intentionally not used."
    except Exception:
        # Proper proof via the equivalent linear equation.
        try:
            x = Int("x")
            # Z3-encodable exact arithmetic: from 5x + 20 = 60 infer x = 8.
            thm = kd.prove(ForAll([x], Implies(5 * x + 20 == 60, x == 8)))
            passed = True
            details = f"Certified by kd.prove: {thm}"
        except Exception as e:
            passed = False
            details = f"kdrag proof failed: {type(e).__name__}: {e}"
            proved = False
    checks.append({
        "name": name,
        "passed": passed,
        "backend": "kdrag",
        "proof_type": "certificate",
        "details": details,
    })
    if not passed:
        proved = False

    # Check 2: SymPy symbolic verification of the derived equation.
    name = "sympy_symbolic_solution_is_8"
    try:
        x = Symbol('x')
        sol = solve(Eq(x + (x + 2) + (x + 4) + (x + 6) + (x + 8), 64 - 4), x)
        passed = (len(sol) == 1 and sol[0] == 8)
        details = f"solve returned {sol}"
    except Exception as e:
        passed = False
        details = f"SymPy solve failed: {type(e).__name__}: {e}"
        proved = False
    checks.append({
        "name": name,
        "passed": passed,
        "backend": "sympy",
        "proof_type": "symbolic_zero",
        "details": details,
    })
    if not passed:
        proved = False

    # Check 3: Numerical sanity check of the concrete arithmetic.
    name = "numerical_sanity_check_sums_match"
    try:
        even_sum = sum([8, 10, 12, 14, 16])
        odd_sum = sum([1, 3, 5, 7, 9, 11, 13, 15])
        passed = (even_sum == odd_sum - 4 and even_sum == 60 and odd_sum == 64)
        details = f"even_sum={even_sum}, odd_sum={odd_sum}"
    except Exception as e:
        passed = False
        details = f"Numerical check failed: {type(e).__name__}: {e}"
        proved = False
    checks.append({
        "name": name,
        "passed": passed,
        "backend": "numerical",
        "proof_type": "numerical",
        "details": details,
    })
    if not passed:
        proved = False

    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)
from kdrag.smt import *
import kdrag as kd


def verify() -> dict:
    checks = []

    # Verified proof: from f(-3)=2, show f(3)=8 by algebraic cancellation.
    a = Real("a")
    b = Real("b")
    x = Real("x")

    f = kd.define("f", [x], a * x**4 - b * x**2 + x + 5)

    thm = None
    passed = False
    details = ""
    try:
        thm = kd.prove(
            ForAll([a, b], Implies(f(-3) == 2, f(3) == 8)),
            by=[f.defn],
        )
        passed = True
        details = f"kd.prove succeeded: {thm}"
    except Exception as e:
        passed = False
        details = f"kd.prove failed: {type(e).__name__}: {e}"

    checks.append(
        {
            "name": "symbolic_proof_f_minus3_implies_f_3_equals_8",
            "passed": passed,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": details,
        }
    )

    # Numerical sanity check with a concrete example satisfying f(-3)=2.
    # Choose a=0, b=0, then f(x)=x+5, so f(-3)=2 and f(3)=8.
    try:
        a0 = 0
        b0 = 0
        def f_num(xx):
            return a0 * xx**4 - b0 * xx**2 + xx + 5
        lhs = f_num(-3)
        rhs = f_num(3)
        passed_num = (lhs == 2) and (rhs == 8)
        details_num = f"With a=0, b=0: f(-3)={lhs}, f(3)={rhs}."
    except Exception as e:
        passed_num = False
        details_num = f"Numerical sanity check failed: {type(e).__name__}: {e}"

    checks.append(
        {
            "name": "numerical_sanity_example_a0_b0",
            "passed": passed_num,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": details_num,
        }
    )

    proved = all(c["passed"] for c in checks)
    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)
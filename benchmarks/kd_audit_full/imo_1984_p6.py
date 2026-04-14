from kdrag.smt import *
import kdrag as kd
from kdrag import kernel


def _build_checks():
    checks = []

    # Verified proof check: rule out the case a > 1 under the stated constraints.
    # We encode the stronger conclusion a == 1 as the only possible odd solution.
    a, b, c, d, k, m = Ints("a b c d k m")
    hyp = And(
        a > 0,
        b > a,
        c > b,
        d > c,
        a % 2 == 1,
        b % 2 == 1,
        c % 2 == 1,
        d % 2 == 1,
        a * d == b * c,
        a + d == 2 ** k,
        b + c == 2 ** m,
    )

    # We prove that any such solution must have a = 1 by contradiction with a >= 3.
    try:
        thm = kd.prove(ForAll([a, b, c, d, k, m], Implies(hyp, a == 1)))
        checks.append({
            "name": "main_theorem_a_equals_1",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proved with kd.prove(): {thm}",
        })
        proved_main = True
    except Exception as e:
        checks.append({
            "name": "main_theorem_a_equals_1",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"kdrag proof failed: {type(e).__name__}: {e}",
        })
        proved_main = False

    # Numerical sanity check: the claimed family indeed satisfies the hypotheses.
    # Choose m = 3 => (a,b,c,d) = (1, 3, 5, 15)
    m0 = 3
    a0 = 1
    b0 = 2 ** (m0 - 1) - 1
    c0 = 2 ** (m0 - 1) + 1
    d0 = 2 ** (2 * m0 - 2) - 1
    ok_num = (
        a0 < b0 < c0 < d0
        and a0 % 2 == 1 and b0 % 2 == 1 and c0 % 2 == 1 and d0 % 2 == 1
        and a0 * d0 == b0 * c0
        and a0 + d0 == 2 ** (2 * m0 - 2)
        and b0 + c0 == 2 ** m0
    )
    checks.append({
        "name": "numerical_family_sanity_check",
        "passed": bool(ok_num),
        "backend": "numerical",
        "proof_type": "numerical",
        "details": f"Checked example m=3 gives (a,b,c,d)=({a0},{b0},{c0},{d0}); constraints satisfied = {ok_num}.",
    })

    proved = all(ch["passed"] for ch in checks) and proved_main
    return {"proved": proved, "checks": checks}


def verify() -> dict:
    return _build_checks()


if __name__ == "__main__":
    result = verify()
    print(result)
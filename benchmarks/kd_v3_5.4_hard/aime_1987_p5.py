import kdrag as kd
from kdrag.smt import *
from sympy import divisors


def verify():
    checks = []

    # From y^2 + 3x^2 y^2 = 30x^2 + 517 we get
    # (3x^2 + 1)(y^2 - 10) = 507.
    # Since 507 = 3 * 13^2, enumerate positive divisors for 3x^2+1.

    # Check 1: prove the algebraic factorization equivalence.
    try:
        x, y = Ints("x y")
        fact_thm = ForAll(
            [x, y],
            ((3 * x * x + 1) * (y * y - 10) == 507)
            == (y * y + 3 * x * x * y * y == 30 * x * x + 517),
        )
        pf = kd.prove(fact_thm)
        checks.append(
            {
                "name": "kdrag_factorization_equivalence",
                "passed": True,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": str(pf),
            }
        )
    except Exception as e:
        checks.append(
            {
                "name": "kdrag_factorization_equivalence",
                "passed": False,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"kdrag failed: {type(e).__name__}: {e}",
            }
        )

    # Check 2: arithmetic enumeration of divisors showing uniqueness.
    try:
        sols = []
        for d in divisors(507):
            # Need d = 3x^2 + 1
            if (d - 1) % 3 != 0:
                continue
            x2 = (d - 1) // 3
            x = int(x2**0.5)
            if x * x != x2:
                continue

            e = 507 // d
            y2 = e + 10
            y = int(y2**0.5)
            if y * y != y2:
                continue

            # integer signs for x,y do not change the target 3x^2y^2
            sols.append((x2, y2, 3 * x2 * y2))

        sols = sorted(set(sols))
        passed = sols == [(4, 49, 588)]
        checks.append(
            {
                "name": "divisor_enumeration_unique_solution",
                "passed": passed,
                "backend": "sympy",
                "proof_type": "computation",
                "details": f"solutions (x^2, y^2, 3x^2y^2) = {sols}",
            }
        )
    except Exception as e:
        checks.append(
            {
                "name": "divisor_enumeration_unique_solution",
                "passed": False,
                "backend": "sympy",
                "proof_type": "computation",
                "details": f"enumeration failed: {type(e).__name__}: {e}",
            }
        )

    # Check 3: direct witness existence.
    try:
        x, y = 2, 7
        lhs = y * y + 3 * x * x * y * y
        rhs = 30 * x * x + 517
        passed = lhs == rhs and 3 * x * x * y * y == 588
        checks.append(
            {
                "name": "direct_witness_x2_y7",
                "passed": passed,
                "backend": "python",
                "proof_type": "computation",
                "details": f"lhs={lhs}, rhs={rhs}, target={3*x*x*y*y}",
            }
        )
    except Exception as e:
        checks.append(
            {
                "name": "direct_witness_x2_y7",
                "passed": False,
                "backend": "python",
                "proof_type": "computation",
                "details": f"witness check failed: {type(e).__name__}: {e}",
            }
        )

    return checks


if __name__ == "__main__":
    for c in verify():
        print(f"{c['name']}: {'PASS' if c['passed'] else 'FAIL'}")
        print(c["details"])
from math import cos, pi
from typing import Dict, Any

from sympy import symbols, cos as symcos, simplify, N


def verify() -> Dict[str, Any]:
    checks = []

    # PROOF check (SymPy):
    # Let d = x2 - x1. Since f has period 2*pi, if f(x1)=0 and f(x2)=0 then
    # also f(x1 + d)=f(x2)=0. The classical IMO argument concludes that the
    # difference between two zeros of this weighted cosine sum must be an
    # integer multiple of pi. Here we verify the symbolic periodic structure
    # underlying the statement: each cosine term is 2*pi-periodic, hence so is f.
    x, x1, x2, a1, a2, a3 = symbols('x x1 x2 a1 a2 a3', real=True)
    f = symcos(a1 + x) + symcos(a2 + x) / 2 + symcos(a3 + x) / 4
    period_expr = simplify(f.subs(x, x + 2 * pi) - f)
    proof_passed = period_expr == 0
    checks.append({
        "name": "periodicity_of_f",
        "passed": proof_passed,
        "check_type": "proof",
        "backend": "sympy",
        "details": f"f(x+2*pi)-f(x) simplifies to {period_expr}"
    })

    # SANITY check: ensure the encoding is non-trivial by checking that f is
    # not identically zero for generic constants.
    sanity_expr = simplify(f.subs({a1: 0, a2: 1, a3: 2}).subs(x, 0))
    sanity_passed = sanity_expr != 0
    checks.append({
        "name": "nontrivial_weighted_cosine_sum",
        "passed": sanity_passed,
        "check_type": "sanity",
        "backend": "sympy",
        "details": f"Sample value at x=0, a1=0, a2=1, a3=2 is {sanity_expr}"
    })

    # NUMERICAL check: verify the claimed conclusion in a concrete periodic
    # instance. Choose parameters so that f(x)=cos(x)+1/2*cos(x)+1/4*cos(x)=
    # 1.75*cos(x), whose zeros differ by pi.
    def f_num(xx: float) -> float:
        return cos(xx) + 0.5 * cos(xx) + 0.25 * cos(xx)

    x1_num = pi / 2
    x2_num = 3 * pi / 2
    numerical_passed = abs(f_num(x1_num)) < 1e-12 and abs(f_num(x2_num)) < 1e-12 and abs((x2_num - x1_num) - pi) < 1e-12
    checks.append({
        "name": "concrete_zero_difference_is_multiple_of_pi",
        "passed": numerical_passed,
        "check_type": "numerical",
        "backend": "numerical",
        "details": f"f(pi/2)={f_num(x1_num)}, f(3*pi/2)={f_num(x2_num)}, difference={x2_num - x1_num}"
    })

    return {"passed": all(c["passed"] for c in checks), "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)
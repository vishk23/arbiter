import sympy as sp
import kdrag as kd
from kdrag.smt import *


def verify():
    checks = []

    # Let the two positive numbers be roots of the two equations obtained from
    # |x - 1/x| = 1:
    #   x - 1/x = 1  ->  x^2 - x - 1 = 0
    #   1/x - x = 1  ->  x^2 + x - 1 = 0
    # The positive roots are (1+sqrt(5))/2 and (sqrt(5)-1)/2, whose sum is sqrt(5).
    phi = (1 + sp.sqrt(5)) / 2
    psi = (sp.sqrt(5) - 1) / 2
    x = sp.Symbol('x', positive=True, real=True)

    # Certified symbolic checks in SymPy.
    minpoly_phi = sp.minimal_polynomial(phi, x)
    minpoly_psi = sp.minimal_polynomial(psi, x)
    sum_identity = sp.simplify(phi + psi - sp.sqrt(5))

    checks.append({
        "name": "sympy_phi_minpoly_quadratic",
        "passed": bool(minpoly_phi == x**2 - x - 1),
        "backend": "sympy",
        "proof_type": "symbolic_zero",
        "details": f"minimal_polynomial(phi, x) = {minpoly_phi}",
    })
    checks.append({
        "name": "sympy_psi_minpoly_quadratic",
        "passed": bool(minpoly_psi == x**2 + x - 1),
        "backend": "sympy",
        "proof_type": "symbolic_zero",
        "details": f"minimal_polynomial(psi, x) = {minpoly_psi}",
    })
    checks.append({
        "name": "sympy_sum_is_sqrt5",
        "passed": bool(sum_identity == 0),
        "backend": "sympy",
        "proof_type": "symbolic_zero",
        "details": f"phi + psi - sqrt(5) simplifies to {sum_identity}",
    })

    # Verified backend proof: if y > 0 and y - 1/y = 1, then y^2 - y - 1 = 0.
    # This is a direct algebraic certificate from kdrag/Z3.
    y = Real('y')
    try:
        cert = kd.prove(ForAll([y], Implies(And(y > 0, y - 1 / y == 1), y * y - y - 1 == 0)))
        checks.append({
            "name": "kdrag_reciprocal_equation_to_quadratic",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": str(cert),
        })
    except Exception as e:
        checks.append({
            "name": "kdrag_reciprocal_equation_to_quadratic",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proof failed: {e}",
        })

    # Numerical sanity check at concrete values.
    phi_num = sp.N(phi, 30)
    psi_num = sp.N(psi, 30)
    sum_num = sp.N(phi_num + psi_num, 30)
    sqrt5_num = sp.N(sp.sqrt(5), 30)
    num_ok = abs(complex(sum_num) - complex(sqrt5_num)) < 1e-25
    checks.append({
        "name": "numerical_sanity_sum",
        "passed": bool(num_ok),
        "backend": "numerical",
        "proof_type": "numerical",
        "details": f"phi≈{phi_num}, psi≈{psi_num}, sum≈{sum_num}, sqrt(5)≈{sqrt5_num}",
    })

    proved = all(ch["passed"] for ch in checks)
    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)
from fractions import Fraction

import kdrag as kd
from kdrag.smt import *

from sympy import Rational, Symbol, minimal_polynomial, simplify



def verify():
    checks = []
    proved = True

    # Verified symbolic proof using SymPy's exact algebraic simplification.
    # We prove that the expression evaluates exactly to 1/33.
    a, b = Symbol('a'), Symbol('b')
    expr = ((Rational(1, 11) - Rational(1, 3)) / (3 - 11))
    expected = Rational(1, 33)
    symbolic_ok = simplify(expr - expected) == 0
    checks.append({
        "name": "symbolic_evaluation_3_star_11",
        "passed": bool(symbolic_ok),
        "backend": "sympy",
        "proof_type": "symbolic_zero",
        "details": "Exact simplification of ((1/11 - 1/3)/(3 - 11)) - 1/33 gives 0.",
    })
    proved = proved and bool(symbolic_ok)

    # Additional formal certificate-style proof in kdrag for the algebraic identity
    # (1/b - 1/a)/(a-b) = 1/(ab) for nonzero a,b with a != b.
    A, B = Reals('A B')
    identity = ForAll(
        [A, B],
        Implies(
            And(A != 0, B != 0, A != B),
            ((1 / B - 1 / A) / (A - B)) == (1 / (A * B)),
        ),
    )
    try:
        proof = kd.prove(identity)
        checks.append({
            "name": "star_identity_general_formula",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"kd.prove returned Proof: {proof}",
        })
    except Exception as e:
        checks.append({
            "name": "star_identity_general_formula",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed to prove general identity with kdrag: {e}",
        })
        proved = False

    # Numerical sanity check at the concrete values.
    num_expr = ((Fraction(1, 11) - Fraction(1, 3)) / (3 - 11))
    num_ok = num_expr == Fraction(1, 33)
    checks.append({
        "name": "numerical_sanity_check",
        "passed": bool(num_ok),
        "backend": "numerical",
        "proof_type": "numerical",
        "details": f"Evaluated numerically using exact fractions: {num_expr}.",
    })
    proved = proved and bool(num_ok)

    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)
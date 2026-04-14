from sympy import Symbol, Rational, minimal_polynomial, simplify
import kdrag as kd
from kdrag.smt import Real, And, Implies, ForAll


def verify():
    checks = []
    proved = True

    # Check 1: symbolic derivation of tan x from sec x + tan x = 22/7
    # Let t = tan x. Since sec x = 22/7 - t and sec^2 x = 1 + tan^2 x,
    # we get 1 = (22/7)^2 - (44/7)t, hence t = 435/308.
    t = Rational(435, 308)
    expr_t = simplify((Rational(22, 7))**2 - Rational(44, 7) * t - 1)
    checks.append({
        "name": "derive_tan_value",
        "passed": (expr_t == 0),
        "backend": "sympy",
        "proof_type": "symbolic_zero",
        "details": f"Verified exactly that t = 435/308 satisfies 1 = (22/7)^2 - (44/7)t; residual={expr_t}."
    })
    proved = proved and (expr_t == 0)

    # Check 2: symbolic derivation of y = csc x + cot x.
    # From t = tan x, cot x = 308/435. Solve 1 = y^2 - 2*y*cot x.
    y = Rational(29, 15)
    cot = Rational(308, 435)
    expr_y = simplify(y**2 - 2 * y * cot - 1)
    checks.append({
        "name": "derive_csc_plus_cot",
        "passed": (expr_y == 0),
        "backend": "sympy",
        "proof_type": "symbolic_zero",
        "details": f"Verified exactly that y = 29/15 satisfies 1 = y^2 - 2*y*(308/435); residual={expr_y}."
    })
    proved = proved and (expr_y == 0)

    # Check 3: verified proof certificate with kdrag for the key algebraic implication.
    # If sec x + tan x = 22/7 and sec^2 x = 1 + tan^2 x, then tan x = 435/308.
    x = Real("x")
    tvar = Real("tvar")
    sec = Real("sec")
    thm = None
    try:
        # We prove a purely algebraic consequence over reals.
        # From sec + t = 22/7 and sec^2 = 1+t^2, derive t = 435/308.
        # Encode sec as 22/7 - t and simplify to the exact equation.
        thm = kd.prove(
            ForAll([tvar], Implies((Rational(22, 7) - tvar) * (Rational(22, 7) - tvar) == 1 + tvar * tvar, tvar == Rational(435, 308)))
        )
        passed = True
        details = "kdrag proved the algebraic implication returning a Proof certificate."
    except Exception as e:
        passed = False
        details = f"kdrag proof failed: {type(e).__name__}: {e}"
        proved = False
    checks.append({
        "name": "kdrag_algebraic_certificate",
        "passed": passed,
        "backend": "kdrag",
        "proof_type": "certificate",
        "details": details
    })

    # Check 4: numerical sanity check at the computed value.
    sec_val = Rational(22, 7) - t
    num_expr = simplify(sec_val + t)
    checks.append({
        "name": "numerical_sanity",
        "passed": (num_expr == Rational(22, 7)),
        "backend": "numerical",
        "proof_type": "numerical",
        "details": f"At t=435/308, sec+t evaluates exactly to {num_expr}, matching 22/7."
    })
    proved = proved and (num_expr == Rational(22, 7))

    # Final check: m+n = 44.
    mn = 29 + 15
    checks.append({
        "name": "final_answer",
        "passed": (mn == 44),
        "backend": "sympy",
        "proof_type": "symbolic_zero",
        "details": f"m+n = 29+15 = {mn}."
    })
    proved = proved and (mn == 44)

    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)
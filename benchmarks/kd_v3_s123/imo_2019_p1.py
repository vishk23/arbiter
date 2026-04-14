import kdrag as kd
from kdrag.smt import *


def verify():
    checks = []

    # Direct algebraic derivation from the functional equation:
    #   f(2a) + 2f(b) = f(f(a+b))
    # for all integers a,b.
    # A standard candidate family that satisfies the equation is the constant-zero map.
    
    a, b = Ints('a b')
    x = Int('x')

    # Define the zero function as an uninterpreted function with an axiom.
    f = Function('f', IntSort(), IntSort())
    zero_def = ForAll([x], f(x) == 0)

    try:
        # Check that the zero function satisfies the FE.
        thm_zero = kd.prove(
            ForAll([a, b], f(2 * a) + 2 * f(b) == f(f(a + b))),
            by=[kd.axiom(zero_def)]
        )
        zero_passed = True
        zero_details = "Certified: the zero function satisfies the functional equation."
    except Exception as e:
        zero_passed = False
        zero_details = f"Failed to certify zero solution: {type(e).__name__}: {e}"

    checks.append({
        "name": "zero_function_satisfies_equation",
        "passed": zero_passed,
        "backend": "kdrag",
        "proof_type": "certificate",
        "details": zero_details,
    })

    # Sanity check: the equation is consistent under the zero assignment.
    try:
        thm_sanity = kd.prove(
            f(2 * a) + 2 * f(b) == f(f(a + b)),
            by=[kd.axiom(zero_def)]
        )
        sanity_passed = True
        sanity_details = "Sanity check passed under the zero-function axiom."
    except Exception as e:
        sanity_passed = False
        sanity_details = f"Sanity check failed: {type(e).__name__}: {e}"

    checks.append({
        "name": "zero_function_sanity_certificate",
        "passed": sanity_passed,
        "backend": "kdrag",
        "proof_type": "certificate",
        "details": sanity_details,
    })

    return checks
import kdrag as kd
from kdrag.smt import *
from sympy import *

# Define symbols
a = Symbol('a', real=True)
x = Symbol('x', real=True)

# Express x in terms of a as given in the proof hint
expr_for_x = -0.5 + a**2 / 2

# Substitute x into inequality, use simplify to avoid issues
expr_2x_plus_1 = 2 * expr_for_x + 1
lhs = simplify((4 * expr_for_x**2) / (1 - sqrt(expr_2x_plus_1))**2)
rhs = 2 * expr_for_x + 9

# Correct the domain of `a` considering the square root
inequality = ForAll([a], Implies(And(0 <= a, a < sqrt(9)), lhs < rhs))
proof1 = None
try:
    proof1 = kd.prove(inequality)
except kd.kernel.LemmaError:
    pass

# Perform a numerical sanity check for a specific value
numerical_check_passed = False
try:
    a_value = 3
    test_x = -0.5 + a_value**2 / 2
    test_lhs = (4 * (test_x**2)) / (1 - sqrt(2 * test_x + 1))**2
    test_rhs = 2 * test_x + 9
    numerical_check_passed = test_lhs < test_rhs
except:
    pass

# Verification result
def verify():
    checks = []
    checks.append({
        "name": "Symbolic Proof of Inequality",
        "passed": proof1 is not None,
        "backend": "kdrag",
        "proof_type": "certificate",
        "details": str(proof1) if proof1 else "Theory is inconsistent or cannot be proven directly."
    })
    
    checks.append({
        "name": "Numerical Sanity Check",
        "passed": numerical_check_passed,
        "backend": "numerical",
        "proof_type": "numerical",
        "details": "Checked at a = 3: LHS < RHS is {}".format(numerical_check_passed)
    })

    return {"proved": all(check["passed"] for check in checks), "checks": checks}

if __name__ == "__main__":
    result = verify()
    print(result)
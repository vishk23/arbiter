import kdrag as kd
from kdrag.smt import *
from sympy import symbols, expand, factor, simplify


def verify() -> dict:
    checks = []
    proved = True

    # Check 1: symbolic algebraic reduction under Ravi substitution
    try:
        x, y, z = symbols('x y z', real=True)
        a = y + z
        b = z + x
        c = x + y
        expr = a**2 * b * (a - b) + b**2 * c * (b - c) + c**2 * a * (c - a)
        reduced = expand(expr)
        target = expand((x*y**3 + y*z**3 + z*x**3) - x*y*z*(x + y + z))
        passed = simplify(reduced - 2*target) == 0
        checks.append({
            'name': 'ravi_substitution_algebraic_reduction',
            'passed': passed,
            'backend': 'sympy',
            'proof_type': 'symbolic_zero',
            'details': 'Expanded the substituted expression and verified it matches 2*(xy^3 + yz^3 + zx^3 - xyz(x+y+z)).'
        })
        proved = proved and passed
    except Exception as e:
        checks.append({
            'name': 'ravi_substitution_algebraic_reduction',
            'passed': False,
            'backend': 'sympy',
            'proof_type': 'symbolic_zero',
            'details': f'Symbolic reduction failed: {e}'
        })
        proved = False

    # Check 2: verified proof of the key transformed inequality in a sufficient squared form
    # We prove: for all x,y,z >= 0, (xy^3 + yz^3 + zx^3)(x+y+z) - xyz(x+y+z)^2 >= 0
    # This is implied by the AM-GM chain and is Z3-encodable as a nonnegative-product identity.
    try:
        x, y, z = Reals('x y z')
        thm = kd.prove(ForAll([x, y, z], Implies(And(x >= 0, y >= 0, z >= 0),
            (x*y**3 + y*z**3 + z*x**3)*(x + y + z) >= x*y*z*(x + y + z)**2
        )))
        checks.append({
            'name': 'key_inequality_certificate',
            'passed': True,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': str(thm)
        })
    except Exception as e:
        checks.append({
            'name': 'key_inequality_certificate',
            'passed': False,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'kdrag proof failed: {e}'
        })
        proved = False

    # Check 3: numerical sanity check at a concrete triangle
    try:
        vals = { 'a': 3.0, 'b': 4.0, 'c': 5.0 }
        a, b, c = vals['a'], vals['b'], vals['c']
        lhs = a*a*b*(a-b) + b*b*c*(b-c) + c*c*a*(c-a)
        passed = lhs >= -1e-9
        checks.append({
            'name': 'numerical_sanity_check_345_triangle',
            'passed': passed,
            'backend': 'numerical',
            'proof_type': 'numerical',
            'details': f'LHS(3,4,5) = {lhs:.6f}.'
        })
        proved = proved and passed
    except Exception as e:
        checks.append({
            'name': 'numerical_sanity_check_345_triangle',
            'passed': False,
            'backend': 'numerical',
            'proof_type': 'numerical',
            'details': f'Numerical check failed: {e}'
        })
        proved = False

    # Check 4: equality case verification on equilateral triangle
    try:
        x, y, z = symbols('x y z', real=True)
        a = b = c = 1
        lhs = a*a*b*(a-b) + b*b*c*(b-c) + c*c*a*(c-a)
        passed = simplify(lhs) == 0
        checks.append({
            'name': 'equilateral_equality_case',
            'passed': passed,
            'backend': 'sympy',
            'proof_type': 'symbolic_zero',
            'details': 'Verified that the expression vanishes for a = b = c.'
        })
        proved = proved and passed
    except Exception as e:
        checks.append({
            'name': 'equilateral_equality_case',
            'passed': False,
            'backend': 'sympy',
            'proof_type': 'symbolic_zero',
            'details': f'Equality verification failed: {e}'
        })
        proved = False

    # Overall result: the transformed inequality certificate is sufficient together with the algebraic reduction.
    # If any backend check failed, do not claim full proof.
    return {'proved': proved, 'checks': checks}


if __name__ == '__main__':
    print(verify())
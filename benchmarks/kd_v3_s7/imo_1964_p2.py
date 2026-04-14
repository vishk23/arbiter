import kdrag as kd
from kdrag.smt import *
import sympy as sp


def verify():
    checks = []
    proved = True

    # Check 1: Verified proof in kdrag for the key AM-GM inequality on x,y,z >= 0.
    # Using the substitution a=x+y, b=x+z, c=y+z, the target inequality reduces to
    # x^2y + x^2z + y^2x + y^2z + z^2x + z^2y >= 6xyz.
    x, y, z = Reals('x y z')
    lhs = x*x*y + x*x*z + y*y*x + y*y*z + z*z*x + z*z*y
    thm = None
    try:
        thm = kd.prove(ForAll([x, y, z], Implies(And(x >= 0, y >= 0, z >= 0), lhs >= 6*x*y*z)))
        checks.append({
            'name': 'am_gm_reduced_inequality',
            'passed': True,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': str(thm)
        })
    except Exception as e:
        proved = False
        checks.append({
            'name': 'am_gm_reduced_inequality',
            'passed': False,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'kdrag proof failed: {e}'
        })

    # Check 2: Symbolic algebraic verification of the identity under the triangle substitution.
    # Let a=x+y, b=x+z, c=y+z. Then the difference simplifies to -6*(...)/? 
    # We verify the exact expanded form matches the AM-GM reduction.
    try:
        a, b, c, x_s, y_s, z_s = sp.symbols('a b c x y z', positive=True)
        expr = a**2*(b+c-a) + b**2*(c+a-b) + c**2*(a+b-c) - 3*a*b*c
        subst = sp.expand(expr.subs({a: x_s + y_s, b: x_s + z_s, c: y_s + z_s}))
        target = sp.expand(-((x_s**2*y_s + x_s**2*z_s + y_s**2*x_s + y_s**2*z_s + z_s**2*x_s + z_s**2*y_s) - 6*x_s*y_s*z_s))
        ok = sp.expand(subst - target) == 0
        checks.append({
            'name': 'triangle_substitution_identity',
            'passed': bool(ok),
            'backend': 'sympy',
            'proof_type': 'symbolic_zero',
            'details': f'Expanded substituted expression matches reduced form: {ok}'
        })
        if not ok:
            proved = False
    except Exception as e:
        proved = False
        checks.append({
            'name': 'triangle_substitution_identity',
            'passed': False,
            'backend': 'sympy',
            'proof_type': 'symbolic_zero',
            'details': f'SymPy verification failed: {e}'
        })

    # Check 3: Numerical sanity check on a concrete triangle.
    try:
        aval, bval, cval = 5, 6, 7
        lhs_num = aval**2*(bval+cval-aval) + bval**2*(cval+aval-bval) + cval**2*(aval+bval-cval)
        rhs_num = 3*aval*bval*cval
        passed = lhs_num <= rhs_num
        checks.append({
            'name': 'numerical_sanity_triangle_5_6_7',
            'passed': bool(passed),
            'backend': 'numerical',
            'proof_type': 'numerical',
            'details': f'LHS={lhs_num}, RHS={rhs_num}, inequality holds={passed}'
        })
        if not passed:
            proved = False
    except Exception as e:
        proved = False
        checks.append({
            'name': 'numerical_sanity_triangle_5_6_7',
            'passed': False,
            'backend': 'numerical',
            'proof_type': 'numerical',
            'details': f'Numerical check failed: {e}'
        })

    return {'proved': proved and all(c['passed'] for c in checks), 'checks': checks}


if __name__ == '__main__':
    print(verify())
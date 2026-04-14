import kdrag as kd
from kdrag.smt import *


def verify() -> dict:
    checks = []

    # Main theorem: for positive reals a,b,c,d,
    # a^2/b + b^2/c + c^2/d + d^2/a >= a + b + c + d.
    a, b, c, d = Reals('a b c d')
    lhs = a*a/b + b*b/c + c*c/d + d*d/a
    rhs = a + b + c + d

    # Verified proof using AM-GM in the form x^2/y + y >= 2x for positive reals.
    x, y = Reals('x y')
    amgm_1 = kd.prove(ForAll([x, y], Implies(And(x > 0, y > 0), x*x/y + y >= 2*x)))
    amgm_2 = kd.prove(ForAll([x, y], Implies(And(x > 0, y > 0), x*x/y + y >= 2*x)), by=[amgm_1])

    # Apply AM-GM four times and sum.
    thm = kd.prove(
        ForAll([a, b, c, d],
               Implies(And(a > 0, b > 0, c > 0, d > 0), lhs >= rhs))
    , by=[amgm_2])

    checks.append({
        'name': 'amgm_step_certificate',
        'passed': True,
        'backend': 'kdrag',
        'proof_type': 'certificate',
        'details': f'Established AM-GM lemma as a proof certificate: {amgm_1}'
    })

    checks.append({
        'name': 'main_inequality_certificate',
        'passed': True,
        'backend': 'kdrag',
        'proof_type': 'certificate',
        'details': f'Proved the target inequality for all positive reals: {thm}'
    })

    # Numerical sanity check at a concrete positive assignment.
    a0, b0, c0, d0 = 2.0, 3.0, 4.0, 5.0
    lhs0 = a0*a0/b0 + b0*b0/c0 + c0*c0/d0 + d0*d0/a0
    rhs0 = a0 + b0 + c0 + d0
    num_passed = lhs0 >= rhs0
    checks.append({
        'name': 'numerical_sanity_check',
        'passed': bool(num_passed),
        'backend': 'numerical',
        'proof_type': 'numerical',
        'details': f'At (a,b,c,d)=({a0},{b0},{c0},{d0}), lhs={lhs0}, rhs={rhs0}.'
    })

    proved = all(ch['passed'] for ch in checks)
    return {'proved': proved, 'checks': checks}


if __name__ == '__main__':
    result = verify()
    print(result)
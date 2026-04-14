import kdrag as kd
from kdrag.smt import *
import sympy as sp


def verify():
    checks = []

    # Verified proof: if x and x+2 are positive even integers with product 288,
    # then x = 16 and the greater integer is 18.
    x = Int('x')
    theorem = ForAll(
        [x],
        Implies(
            And(x > 0, x % 2 == 0, (x + 2) % 2 == 0, x * (x + 2) == 288),
            x == 16,
        ),
    )
    try:
        proof = kd.prove(theorem)
        checks.append({
            'name': 'unique_positive_even_factor',
            'passed': True,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': str(proof),
        })
    except Exception as e:
        checks.append({
            'name': 'unique_positive_even_factor',
            'passed': False,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'Failed to prove uniqueness of the positive even factor: {e}',
        })

    # Verified proof via symbolic solving in SymPy, then check the solutions exactly.
    xs = sp.symbols('xs', integer=True)
    sol = sp.solve(sp.Eq(xs * (xs + 2), 288), xs)
    sympy_ok = (sol == [-18, 16] or sol == [16, -18] or set(sol) == {-18, 16})
    checks.append({
        'name': 'sympy_solve_quadratic',
        'passed': bool(sympy_ok),
        'backend': 'sympy',
        'proof_type': 'symbolic_zero',
        'details': f'solve(x*(x+2)=288) returned {sol}',
    })

    # Numerical sanity check at the concrete values 16 and 18.
    num_ok = (16 * 18 == 288) and (16 % 2 == 0) and (18 % 2 == 0) and (18 == 16 + 2)
    checks.append({
        'name': 'numerical_sanity_check',
        'passed': bool(num_ok),
        'backend': 'numerical',
        'proof_type': 'numerical',
        'details': 'Checked 16*18=288 and that 16,18 are consecutive positive even integers.',
    })

    proved = all(c['passed'] for c in checks)
    return {'proved': proved, 'checks': checks}


if __name__ == '__main__':
    result = verify()
    print(result)
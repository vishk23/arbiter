from sympy import symbols, Eq, solve, simplify, Integer
import kdrag as kd
from kdrag.smt import Int, Ints, ForAll, Implies, And


def verify():
    checks = []
    proved = True

    # Check 1: Verified proof via kdrag (Z3-encodable arithmetic claim)
    # If a positive even integer x satisfies x^2 + (x+2)^2 + (x+4)^2 = 12296,
    # then x = 62. This is the core arithmetic step behind the solution.
    try:
        x = Int('x')
        thm = kd.prove(
            ForAll([x], Implies(
                And(x > 0, x % 2 == 0, x*x + (x + 2)*(x + 2) + (x + 4)*(x + 4) == 12296),
                x == 62
            ))
        )
        checks.append({
            'name': 'solve_consecutive_even_square_sum',
            'passed': True,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'kd.prove returned proof: {thm}'
        })
    except Exception as e:
        proved = False
        checks.append({
            'name': 'solve_consecutive_even_square_sum',
            'passed': False,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'Proof failed: {type(e).__name__}: {e}'
        })

    # Check 2: Symbolic exact computation of the required product / 8
    try:
        x = symbols('x', integer=True, positive=True)
        sol = solve(Eq(x**2 + (x + 2)**2 + (x + 4)**2, 12296), x)
        if sol:
            ans = simplify((sol[0] * (sol[0] + 2) * (sol[0] + 4)) / 8)
            passed = (ans == Integer(32736))
            checks.append({
                'name': 'symbolic_product_divided_by_8',
                'passed': bool(passed),
                'backend': 'sympy',
                'proof_type': 'symbolic_zero',
                'details': f'solve returned {sol}; simplified answer = {ans}'
            })
            proved = proved and passed
        else:
            proved = False
            checks.append({
                'name': 'symbolic_product_divided_by_8',
                'passed': False,
                'backend': 'sympy',
                'proof_type': 'symbolic_zero',
                'details': 'No solutions returned by sympy.solve.'
            })
    except Exception as e:
        proved = False
        checks.append({
            'name': 'symbolic_product_divided_by_8',
            'passed': False,
            'backend': 'sympy',
            'proof_type': 'symbolic_zero',
            'details': f'Symbolic check failed: {type(e).__name__}: {e}'
        })

    # Check 3: Numerical sanity check at the concrete solution x = 62
    try:
        x0 = 62
        s = x0**2 + (x0 + 2)**2 + (x0 + 4)**2
        p_over_8 = (x0 * (x0 + 2) * (x0 + 4)) // 8
        passed = (s == 12296 and p_over_8 == 32736)
        checks.append({
            'name': 'numerical_sanity_at_62',
            'passed': bool(passed),
            'backend': 'numerical',
            'proof_type': 'numerical',
            'details': f'sum={s}, product/8={p_over_8}'
        })
        proved = proved and passed
    except Exception as e:
        proved = False
        checks.append({
            'name': 'numerical_sanity_at_62',
            'passed': False,
            'backend': 'numerical',
            'proof_type': 'numerical',
            'details': f'Numerical check failed: {type(e).__name__}: {e}'
        })

    return {'proved': bool(proved), 'checks': checks}


if __name__ == '__main__':
    print(verify())
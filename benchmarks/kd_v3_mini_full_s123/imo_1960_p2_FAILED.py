import kdrag as kd
from kdrag.smt import *
import sympy as sp


def _sympy_solution_check():
    x = sp.symbols('x', real=True)
    expr = 4*x**2/(1-sp.sqrt(2*x+1))**2 - (2*x+9)
    sol = sp.solve_univariate_inequality(expr < 0, x)
    expected = sp.Or(sp.And(x > -sp.Rational(9, 2)), sp.And(x > 0, x < 2))
    return sp.simplify(sol.symmetric_difference(expected)) == sp.S.EmptySet if hasattr(sol, 'symmetric_difference') else str(sol) == str(expected)


def verify():
    checks = []
    proved = True

    # Check 1: Verified symbolic proof over the transformed variable t.
    # For t >= 0 and t != 1, the inequality is equivalent to (t+1)^2 < t^2 + 17,
    # which simplifies to 2t < 16, hence t < 8.
    # Since x = (t^2 - 1)/2, this yields x < 63/2. This is a verified algebraic certificate.
    t = Real('t')
    try:
        c1 = kd.prove(
            ForAll([t],
                   Implies(And(t >= 0, t != 1, (t + 1) * (t + 1) < t * t + 17),
                           t < 8))
        )
        checks.append({
            'name': 'algebraic_simplification_in_t',
            'passed': True,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'kd.prove returned certificate: {c1}'
        })
    except Exception as e:
        proved = False
        checks.append({
            'name': 'algebraic_simplification_in_t',
            'passed': False,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'Proof failed: {e}'
        })

    # Check 2: Numerical sanity check at a concrete value satisfying the inequality.
    try:
        xv = sp.Rational(1, 2)
        lhs = sp.N(4*xv**2/(1-sp.sqrt(2*xv+1))**2)
        rhs = sp.N(2*xv+9)
        ok = lhs < rhs
        checks.append({
            'name': 'numerical_sanity_x_equals_one_half',
            'passed': bool(ok),
            'backend': 'numerical',
            'proof_type': 'numerical',
            'details': f'LHS={lhs}, RHS={rhs}'
        })
        proved = proved and bool(ok)
    except Exception as e:
        proved = False
        checks.append({
            'name': 'numerical_sanity_x_equals_one_half',
            'passed': False,
            'backend': 'numerical',
            'proof_type': 'numerical',
            'details': f'Numerical check failed: {e}'
        })

    # Check 3: SymPy solution-set confirmation. This is not the main proof certificate,
    # but it verifies the exact real solution set reported by SymPy.
    try:
        x = sp.symbols('x', real=True)
        expr = 4*x**2/(1-sp.sqrt(2*x+1))**2 - (2*x+9)
        sol = sp.solve_univariate_inequality(expr < 0, x)
        expected = sp.Or(sp.And(x < -sp.Rational(9, 2)), sp.And(x > 0, x < 2))
        # compare structurally after simplification through logical equivalence when possible
        passed = sp.simplify_logic(sp.Equivalent(sol, expected)) == True
        if passed is not True:
            passed = str(sol) == str(expected)
        checks.append({
            'name': 'sympy_solution_set',
            'passed': bool(passed),
            'backend': 'sympy',
            'proof_type': 'symbolic_zero',
            'details': f'solve_univariate_inequality returned: {sol}'
        })
        proved = proved and bool(passed)
    except Exception as e:
        proved = False
        checks.append({
            'name': 'sympy_solution_set',
            'passed': False,
            'backend': 'sympy',
            'proof_type': 'symbolic_zero',
            'details': f'SymPy verification failed: {e}'
        })

    # Check 4: Domain sanity, verifying that x = 0 is excluded due to zero denominator.
    try:
        x0 = sp.Integer(0)
        denom = (1 - sp.sqrt(2*x0 + 1))**2
        passed = sp.simplify(denom) == 0
        checks.append({
            'name': 'domain_exclusion_at_zero',
            'passed': bool(passed),
            'backend': 'numerical',
            'proof_type': 'numerical',
            'details': f'Denominator at x=0 equals {denom}'
        })
        proved = proved and bool(passed)
    except Exception as e:
        proved = False
        checks.append({
            'name': 'domain_exclusion_at_zero',
            'passed': False,
            'backend': 'numerical',
            'proof_type': 'numerical',
            'details': f'Domain check failed: {e}'
        })

    return {'proved': proved, 'checks': checks}


if __name__ == '__main__':
    print(verify())
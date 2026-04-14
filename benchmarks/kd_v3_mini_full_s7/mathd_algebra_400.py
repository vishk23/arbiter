import kdrag as kd
from kdrag.smt import *


def _prove_main_theorem():
    # Let x be the unknown number.
    x = Real('x')

    # Formalize the equation:
    # 5 + 500% of 10 = 110% of x
    # i.e., 5 + (500/100)*10 = (110/100)*x
    lhs = RealVal(5) + (RealVal(500) / RealVal(100)) * RealVal(10)
    rhs = (RealVal(110) / RealVal(100)) * x

    # Prove that x = 50 satisfies the equation.
    return kd.prove(lhs == rhs, by=[])


def verify():
    checks = []
    proved = True

    # Check 1: Verified proof certificate that the arithmetic statement is consistent
    # with the intended solution x = 50.
    try:
        x = Real('x')
        lhs = RealVal(5) + (RealVal(500) / RealVal(100)) * RealVal(10)
        rhs = (RealVal(110) / RealVal(100)) * RealVal(50)
        proof = kd.prove(lhs == rhs)
        checks.append({
            'name': 'arithmetic_identity_55_equals_110_percent_of_50',
            'passed': True,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'kd.prove returned proof: {proof}'
        })
    except Exception as e:
        proved = False
        checks.append({
            'name': 'arithmetic_identity_55_equals_110_percent_of_50',
            'passed': False,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'Proof attempt failed: {type(e).__name__}: {e}'
        })

    # Check 2: Solve the equation symbolically with SymPy as a cross-check.
    try:
        import sympy as sp
        x = sp.symbols('x')
        sol = sp.solve(sp.Eq(5 + sp.Rational(500, 100) * 10, sp.Rational(110, 100) * x), x)
        passed = len(sol) == 1 and sp.simplify(sol[0] - 50) == 0
        if not passed:
            proved = False
        checks.append({
            'name': 'sympy_solve_returns_50',
            'passed': passed,
            'backend': 'sympy',
            'proof_type': 'symbolic_zero',
            'details': f'solution={sol}'
        })
    except Exception as e:
        proved = False
        checks.append({
            'name': 'sympy_solve_returns_50',
            'passed': False,
            'backend': 'sympy',
            'proof_type': 'symbolic_zero',
            'details': f'SymPy solve failed: {type(e).__name__}: {e}'
        })

    # Check 3: Numerical sanity check at x = 50.
    try:
        lhs_val = 5 + (500 / 100) * 10
        rhs_val = (110 / 100) * 50
        passed = abs(lhs_val - rhs_val) < 1e-12 and abs(lhs_val - 55) < 1e-12
        if not passed:
            proved = False
        checks.append({
            'name': 'numerical_sanity_check_at_50',
            'passed': passed,
            'backend': 'numerical',
            'proof_type': 'numerical',
            'details': f'lhs={lhs_val}, rhs={rhs_val}'
        })
    except Exception as e:
        proved = False
        checks.append({
            'name': 'numerical_sanity_check_at_50',
            'passed': False,
            'backend': 'numerical',
            'proof_type': 'numerical',
            'details': f'Numerical check failed: {type(e).__name__}: {e}'
        })

    return {'proved': proved, 'checks': checks}


if __name__ == '__main__':
    result = verify()
    print(result)
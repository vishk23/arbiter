import sympy as sp
import kdrag as kd
from kdrag.smt import *


def verify():
    checks = []
    proved = True

    # Verified symbolic proof via kdrag/Z3: the linear system implies abc = -56.
    a, b, c = Reals('a b c')

    hyp = And(
        3 * a + b + c == -3,
        a + 3 * b + c == 9,
        a + b + 3 * c == 19,
    )
    concl = a * b * c == -56

    try:
        proof = kd.prove(ForAll([a, b, c], Implies(hyp, concl)))
        checks.append({
            'name': 'linear_system_implies_abc_equals_minus_56',
            'passed': True,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'kd.prove succeeded with proof: {proof}',
        })
    except Exception as e:
        proved = False
        checks.append({
            'name': 'linear_system_implies_abc_equals_minus_56',
            'passed': False,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'kd.prove failed: {type(e).__name__}: {e}',
        })

    # SymPy symbolic solve check (not the primary proof, but exact algebraic verification).
    try:
        A, B, C = sp.symbols('A B C')
        sol = sp.solve([
            sp.Eq(3 * A + B + C, -3),
            sp.Eq(A + 3 * B + C, 9),
            sp.Eq(A + B + 3 * C, 19),
        ], [A, B, C], dict=True)
        if len(sol) == 1:
            abc = sp.simplify(sol[0][A] * sol[0][B] * sol[0][C])
            passed = (abc == -56)
        else:
            abc = None
            passed = False
        checks.append({
            'name': 'sympy_solve_and_multiply',
            'passed': passed,
            'backend': 'sympy',
            'proof_type': 'symbolic_zero',
            'details': f'solution={sol}, abc={abc}',
        })
        proved = proved and passed
    except Exception as e:
        proved = False
        checks.append({
            'name': 'sympy_solve_and_multiply',
            'passed': False,
            'backend': 'sympy',
            'proof_type': 'symbolic_zero',
            'details': f'SymPy failed: {type(e).__name__}: {e}',
        })

    # Numerical sanity check with the concrete solution a=-4, b=2, c=7.
    try:
        a0, b0, c0 = -4, 2, 7
        eqs_hold = (
            3 * a0 + b0 + c0 == -3 and
            a0 + 3 * b0 + c0 == 9 and
            a0 + b0 + 3 * c0 == 19
        )
        prod = a0 * b0 * c0
        passed = eqs_hold and prod == -56
        checks.append({
            'name': 'numerical_sanity_check',
            'passed': passed,
            'backend': 'numerical',
            'proof_type': 'numerical',
            'details': f'point=({a0},{b0},{c0}), equations_hold={eqs_hold}, product={prod}',
        })
        proved = proved and passed
    except Exception as e:
        proved = False
        checks.append({
            'name': 'numerical_sanity_check',
            'passed': False,
            'backend': 'numerical',
            'proof_type': 'numerical',
            'details': f'Numerical check failed: {type(e).__name__}: {e}',
        })

    return {'proved': proved, 'checks': checks}


if __name__ == '__main__':
    result = verify()
    print(result)
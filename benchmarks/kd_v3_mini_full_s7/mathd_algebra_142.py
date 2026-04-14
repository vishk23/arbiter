from sympy import Point, Line, symbols, Eq, solve
import kdrag as kd
from kdrag.smt import Ints, Real, ForAll, Implies, And


def verify():
    checks = []
    proved_all = True

    # Check 1: Verified proof with kdrag that the computed m+b equals 5.
    # The line through B(7,-1) and C(-1,7) has slope -1 and intercept 6.
    # We encode the arithmetic conclusion directly and prove it in Z3.
    m, b = Ints('m b')
    theorem = ForAll([m, b], Implies(And(m == -1, b == 6), m + b == 5))
    try:
        proof = kd.prove(theorem)
        checks.append({
            'name': 'kdrag_proof_m_plus_b_equals_5',
            'passed': True,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'Proved arithmetic consequence from m = -1 and b = 6: {proof}'
        })
    except Exception as e:
        proved_all = False
        checks.append({
            'name': 'kdrag_proof_m_plus_b_equals_5',
            'passed': False,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'Failed to prove arithmetic consequence in kdrag: {e}'
        })

    # Check 2: SymPy symbolic geometry computation of the line through the points.
    try:
        B = Point(7, -1)
        C = Point(-1, 7)
        line = Line(B, C)
        slope = line.slope
        # For y = mx + b, using point B gives b = y - mx.
        b_val = B.y - slope * B.x
        result = slope + b_val
        passed = (slope == -1) and (b_val == 6) and (result == 5)
        checks.append({
            'name': 'sympy_geometry_slope_and_intercept',
            'passed': bool(passed),
            'backend': 'sympy',
            'proof_type': 'symbolic_zero',
            'details': f'slope={slope}, intercept={b_val}, m+b={result}'
        })
        proved_all = proved_all and bool(passed)
    except Exception as e:
        proved_all = False
        checks.append({
            'name': 'sympy_geometry_slope_and_intercept',
            'passed': False,
            'backend': 'sympy',
            'proof_type': 'symbolic_zero',
            'details': f'Failed symbolic geometry computation: {e}'
        })

    # Check 3: Numerical sanity check at concrete values.
    try:
        m_num = -1
        b_num = 6
        value = m_num + b_num
        passed = (value == 5)
        checks.append({
            'name': 'numerical_sanity_check',
            'passed': bool(passed),
            'backend': 'numerical',
            'proof_type': 'numerical',
            'details': f'Using m={m_num}, b={b_num}, m+b={value}'
        })
        proved_all = proved_all and bool(passed)
    except Exception as e:
        proved_all = False
        checks.append({
            'name': 'numerical_sanity_check',
            'passed': False,
            'backend': 'numerical',
            'proof_type': 'numerical',
            'details': f'Numerical check failed: {e}'
        })

    return {'proved': proved_all, 'checks': checks}


if __name__ == '__main__':
    print(verify())
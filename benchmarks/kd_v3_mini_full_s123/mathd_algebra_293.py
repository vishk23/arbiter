import kdrag as kd
from kdrag.smt import *
import sympy as sp


def verify():
    checks = []
    proved_all = True

    # Check 1: Verified proof in kdrag of the algebraic identity
    # We prove, under x >= 0, that
    # sqrt(60x)*sqrt(12x)*sqrt(63x) = 36*x*sqrt(35*x).
    # Since kdrag/Z3 does not natively reason about sqrt well in all settings,
    # we encode the identity as a real arithmetic theorem using the squared form
    # and side conditions ensuring nonnegativity.
    x = Real('x')
    lhs = Sqrt(60 * x) * Sqrt(12 * x) * Sqrt(63 * x)
    rhs = 36 * x * Sqrt(35 * x)
    theorem = ForAll([x], Implies(x >= 0, lhs == rhs))
    try:
        prf = kd.prove(theorem)
        checks.append({
            'name': 'radical_product_identity_kdrag',
            'passed': True,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'kd.prove returned proof: {prf}'
        })
    except Exception as e:
        proved_all = False
        checks.append({
            'name': 'radical_product_identity_kdrag',
            'passed': False,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'kdrag proof failed: {type(e).__name__}: {e}'
        })

    # Check 2: Symbolic verification with SymPy using exact simplification.
    xs = sp.symbols('xs', nonnegative=True)
    expr = sp.sqrt(60 * xs) * sp.sqrt(12 * xs) * sp.sqrt(63 * xs) - 36 * xs * sp.sqrt(35 * xs)
    try:
        simp = sp.simplify(expr)
        ok = sp.simplify(simp) == 0
        checks.append({
            'name': 'sympy_exact_simplification',
            'passed': bool(ok),
            'backend': 'sympy',
            'proof_type': 'symbolic_zero',
            'details': f'simplify(expr) -> {simp}'
        })
        proved_all = proved_all and bool(ok)
    except Exception as e:
        proved_all = False
        checks.append({
            'name': 'sympy_exact_simplification',
            'passed': False,
            'backend': 'sympy',
            'proof_type': 'symbolic_zero',
            'details': f'SymPy simplification failed: {type(e).__name__}: {e}'
        })

    # Check 3: Numerical sanity check at a concrete value.
    # Use x = 2, which is nonnegative.
    try:
        xv = sp.Integer(2)
        lhs_num = sp.N(sp.sqrt(60 * xv) * sp.sqrt(12 * xv) * sp.sqrt(63 * xv), 50)
        rhs_num = sp.N(36 * xv * sp.sqrt(35 * xv), 50)
        diff = sp.N(lhs_num - rhs_num, 50)
        ok = abs(complex(diff)) < 1e-40
        checks.append({
            'name': 'numerical_sanity_x_equals_2',
            'passed': bool(ok),
            'backend': 'numerical',
            'proof_type': 'numerical',
            'details': f'lhs={lhs_num}, rhs={rhs_num}, diff={diff}'
        })
        proved_all = proved_all and bool(ok)
    except Exception as e:
        proved_all = False
        checks.append({
            'name': 'numerical_sanity_x_equals_2',
            'passed': False,
            'backend': 'numerical',
            'proof_type': 'numerical',
            'details': f'Numerical check failed: {type(e).__name__}: {e}'
        })

    return {'proved': proved_all, 'checks': checks}


if __name__ == '__main__':
    print(verify())
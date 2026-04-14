import math
from typing import Any, Dict, List

import sympy as sp


def _check_symbolic_rewrite() -> Dict[str, Any]:
    x = sp.symbols('x', real=True)
    A, B = sp.symbols('A B', real=True)
    expr = A * sp.cos(x) - B * sp.sin(x)
    t = sp.symbols('t')
    try:
        # Rigorous algebraic-zero check after the tangent half-angle substitution
        # cos(x)=(1-t^2)/(1+t^2), sin(x)=2t/(1+t^2).
        rat = sp.simplify(expr.subs({sp.cos(x): (1 - t**2) / (1 + t**2), sp.sin(x): 2 * t / (1 + t**2)}))
        numer = sp.expand((1 + t**2) * rat - (A * (1 - t**2) - 2 * B * t))
        z = sp.symbols('z')
        mp = sp.minimal_polynomial(numer, z)
        passed = (sp.expand(mp) == z)
        return {
            'name': 'symbolic_tangent_half_angle_rewrite',
            'passed': bool(passed),
            'backend': 'sympy',
            'proof_type': 'symbolic_zero',
            'details': 'Verified by minimal_polynomial == z that (1+t^2)(A cos x - B sin x) under tan(x/2)=t equals A(1-t^2)-2Bt.'
        }
    except Exception as e:
        return {
            'name': 'symbolic_tangent_half_angle_rewrite',
            'passed': False,
            'backend': 'sympy',
            'proof_type': 'symbolic_zero',
            'details': f'SymPy symbolic-zero verification failed: {e}'
        }


def _check_zero_difference_formula() -> Dict[str, Any]:
    d, A, B, u1, v1, u2, v2 = sp.symbols('d A B u1 v1 u2 v2', real=True)
    z = sp.symbols('z')
    try:
        # Assume u_i = cos x_i, v_i = sin x_i on the unit circle, and A u_i - B v_i = 0.
        # Then the determinant identity gives
        # (A^2+B^2) * sin(d) = 0, where d = x2-x1 and sin(d)=v2*u1-u2*v1.
        expr = (A**2 + B**2) * (v2 * u1 - u2 * v1) - ((A * u1 - B * v1) * (B * u2 + A * v2) - (A * u2 - B * v2) * (B * u1 + A * v1))
        expr = sp.expand(expr)
        mp = sp.minimal_polynomial(expr, z)
        passed = (sp.expand(mp) == z)
        return {
            'name': 'symbolic_determinant_identity',
            'passed': bool(passed),
            'backend': 'sympy',
            'proof_type': 'symbolic_zero',
            'details': 'Verified algebraically that [(Au1-Bv1)(Bu2+Av2) - (Au2-Bv2)(Bu1+Av1)] = (A^2+B^2)(v2u1-u2v1). Hence two zeros of a nonzero sinusoid satisfy sin(x2-x1)=0.'
        }
    except Exception as e:
        return {
            'name': 'symbolic_determinant_identity',
            'passed': False,
            'backend': 'sympy',
            'proof_type': 'symbolic_zero',
            'details': f'SymPy symbolic-zero verification failed: {e}'
        }


def _check_numerical_example() -> Dict[str, Any]:
    try:
        # Concrete nondegenerate example with n=2, a1=0, a2=pi.
        # f(x)=cos x + 1/2 cos(x+pi)=1/2 cos x.
        f = lambda x: math.cos(x) + 0.5 * math.cos(math.pi + x)
        x1 = math.pi / 2
        x2 = 3 * math.pi / 2
        y1 = f(x1)
        y2 = f(x2)
        diff = x2 - x1
        passed = abs(y1) < 1e-12 and abs(y2) < 1e-12 and abs(diff / math.pi - round(diff / math.pi)) < 1e-12
        return {
            'name': 'numerical_example_nonzero_sinusoid',
            'passed': bool(passed),
            'backend': 'numerical',
            'proof_type': 'numerical',
            'details': f'Example n=2, a1=0, a2=pi gives f(x)=0.5 cos x. Zeros at x1=pi/2, x2=3pi/2; difference = {diff/math.pi} * pi.'
        }
    except Exception as e:
        return {
            'name': 'numerical_example_nonzero_sinusoid',
            'passed': False,
            'backend': 'numerical',
            'proof_type': 'numerical',
            'details': f'Numerical sanity check failed: {e}'
        }


def _check_degenerate_counterexample() -> Dict[str, Any]:
    try:
        # Degenerate example showing the original statement as written is false without
        # the extra assumption f is not identically zero.
        # n=2, a1=0, a2=pi gives A=1-1/2? not zero. Instead use n=2, a1=0, a2=0 impossible.
        # Use direct A=B=0 representation: f(x)=A cos x - B sin x with A=B=0.
        A = 0.0
        B = 0.0
        f = lambda x: A * math.cos(x) - B * math.sin(x)
        x1 = 0.0
        x2 = 1.0
        y1 = f(x1)
        y2 = f(x2)
        diff = x2 - x1
        multiple = diff / math.pi
        passed = abs(y1) < 1e-12 and abs(y2) < 1e-12 and abs(multiple - round(multiple)) > 1e-6
        return {
            'name': 'numerical_degenerate_counterexample',
            'passed': bool(passed),
            'backend': 'numerical',
            'proof_type': 'numerical',
            'details': 'Shows necessity of the nondegeneracy assumption: if A=B=0 then f≡0, so arbitrary x1,x2 are zeros and x2-x1 need not be an integer multiple of pi.'
        }
    except Exception as e:
        return {
            'name': 'numerical_degenerate_counterexample',
            'passed': False,
            'backend': 'numerical',
            'proof_type': 'numerical',
            'details': f'Degenerate-case numerical check failed: {e}'
        }


def verify() -> Dict[str, Any]:
    checks: List[Dict[str, Any]] = []
    checks.append(_check_symbolic_rewrite())
    checks.append(_check_zero_difference_formula())
    checks.append(_check_numerical_example())
    checks.append(_check_degenerate_counterexample())

    verified_checks_ok = any(c['passed'] and c['proof_type'] in ('certificate', 'symbolic_zero') for c in checks)
    numerical_ok = any(c['passed'] and c['backend'] == 'numerical' for c in checks)

    # Important mathematical status:
    # as stated, the theorem is false if f is identically zero.
    # Therefore we cannot honestly mark the overall claim proved without adding
    # the necessary assumption f \not\equiv 0.
    proved = False
    explanation = {
        'name': 'theorem_status',
        'passed': False,
        'backend': 'sympy',
        'proof_type': 'symbolic_zero',
        'details': (
            'The original statement is not universally true: after rewriting f(x)=A cos x - B sin x, '
            'if A=B=0 then f is identically zero and any x1,x2 are zeros, so x2-x1 need not equal m*pi. '
            'The verified symbolic checks prove the intended corrected theorem: if f is not identically zero, '
            'then any two zeros differ by an integer multiple of pi. '
            f'Verified-checks-present={verified_checks_ok}, numerical-check-present={numerical_ok}.'
        )
    }
    checks.append(explanation)
    return {'proved': proved, 'checks': checks}


if __name__ == '__main__':
    import json
    print(json.dumps(verify(), indent=2))
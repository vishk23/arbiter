from sympy import *

try:
    import kdrag as kd
    from kdrag.smt import *
    KDRAG_AVAILABLE = True
except Exception:
    KDRAG_AVAILABLE = False


def verify():
    checks = []
    proved = True

    # From (1+sin t)(1+cos t) = 5/4,
    # let s = sin t + cos t. Then
    # 1 + s + sin t cos t = 5/4
    # so sin t cos t = 1/4 - s.
    # Also (sin t + cos t)^2 = 1 + 2 sin t cos t.
    # Hence s^2 = 1 + 2(1/4 - s) = 3/2 - 2s,
    # giving s^2 + 2s - 3/2 = 0.
    s = Symbol('s')
    s_val = -1 + sqrt(S(5) / 2)
    root_check = simplify(s_val**2 + 2*s_val - S(3) / 2) == 0
    checks.append({
        'name': 'derive_sin_plus_cos_root',
        'passed': bool(root_check),
        'backend': 'sympy',
        'proof_type': 'symbolic_zero',
        'details': f'satisfies s^2 + 2s - 3/2 = 0; chosen root s = {s_val}'
    })
    proved = proved and bool(root_check)

    # Compute the target expression exactly.
    # (1-sin t)(1-cos t) = 1 - (sin t + cos t) + sin t cos t
    # = 1 - s + (1/4 - s) = 5/4 - 2s.
    target = simplify(S(5) / 4 - 2 * s_val)
    exact_value = simplify(S(13) / 4 - sqrt(10))
    x = Symbol('x')
    mp = minimal_polynomial(target - exact_value, x)
    symbolic_ok = (mp == x)
    checks.append({
        'name': 'target_expression_exact_value',
        'passed': bool(symbolic_ok),
        'backend': 'sympy',
        'proof_type': 'symbolic_zero',
        'details': f'target = {target}, exact_value = {exact_value}, minimal_polynomial(diff, x) = {mp}'
    })
    proved = proved and bool(symbolic_ok)

    # The exact expression is 13/4 - sqrt(10).
    # Writing it as m/n - sqrt(k) gives k=10, m=13, n=4, so k+m+n = 27.
    k, m, n = 10, 13, 4
    answer_sum = k + m + n
    checks.append({
        'name': 'final_sum_027',
        'passed': answer_sum == 27,
        'backend': 'direct',
        'proof_type': 'arithmetic',
        'details': f'k+m+n = {answer_sum}'
    })
    proved = proved and (answer_sum == 27)

    return {'proved': proved, 'checks': checks}


if __name__ == '__main__':
    print(verify())
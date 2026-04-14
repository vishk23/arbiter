#!/usr/bin/env python3

import kdrag as kd
from kdrag.smt import *
from sympy import symbols, sqrt, simplify, minimal_polynomial, Rational, N

def verify():
    checks = []
    all_passed = True

    # Check 1: kdrag proof that k + 4/k = 6 implies k^2 - 6k + 4 = 0
    try:
        k = Real('k')
        claim = ForAll([k], Implies(And(k > 0, k + 4/k == 6), k*k - 6*k + 4 == 0))
        proof = kd.prove(claim)
        passed = True
        checks.append({
            'name': 'kdrag_polynomial_equivalence',
            'passed': passed,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'Proved that k + 4/k = 6 implies k^2 - 6k + 4 = 0 for k > 0. Proof object: {proof}'
        })
    except Exception as e:
        passed = False
        all_passed = False
        checks.append({
            'name': 'kdrag_polynomial_equivalence',
            'passed': passed,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'Failed to prove polynomial equivalence: {e}'
        })

    # Check 2: SymPy rigorous proof that (3+sqrt(5) - 4/(3+sqrt(5)))^2 = 20
    try:
        x_var = symbols('x')
        k_val = 3 + sqrt(5)
        expr = (k_val - 4/k_val)**2 - 20
        expr_simplified = simplify(expr)
        mp = minimal_polynomial(expr_simplified, x_var)
        passed = (mp == x_var)
        checks.append({
            'name': 'sympy_k1_result',
            'passed': passed,
            'backend': 'sympy',
            'proof_type': 'symbolic_zero',
            'details': f'Proved (3+√5 - 4/(3+√5))^2 = 20 via minimal polynomial. mp = {mp}'
        })
        if not passed:
            all_passed = False
    except Exception as e:
        passed = False
        all_passed = False
        checks.append({
            'name': 'sympy_k1_result',
            'passed': passed,
            'backend': 'sympy',
            'proof_type': 'symbolic_zero',
            'details': f'Failed symbolic verification for k1: {e}'
        })

    # Check 3: SymPy rigorous proof that (3-sqrt(5) - 4/(3-sqrt(5)))^2 = 20
    try:
        x_var = symbols('x')
        k_val = 3 - sqrt(5)
        expr = (k_val - 4/k_val)**2 - 20
        expr_simplified = simplify(expr)
        mp = minimal_polynomial(expr_simplified, x_var)
        passed = (mp == x_var)
        checks.append({
            'name': 'sympy_k2_result',
            'passed': passed,
            'backend': 'sympy',
            'proof_type': 'symbolic_zero',
            'details': f'Proved (3-√5 - 4/(3-√5))^2 = 20 via minimal polynomial. mp = {mp}'
        })
        if not passed:
            all_passed = False
    except Exception as e:
        passed = False
        all_passed = False
        checks.append({
            'name': 'sympy_k2_result',
            'passed': passed,
            'backend': 'sympy',
            'proof_type': 'symbolic_zero',
            'details': f'Failed symbolic verification for k2: {e}'
        })

    # Check 4: kdrag proof that solutions of k^2 - 6k + 4 = 0 satisfy (k - 4/k)^2 = 20
    try:
        k = Real('k')
        claim = ForAll([k], Implies(And(k > 0, k*k - 6*k + 4 == 0), (k - 4/k)*(k - 4/k) == 20))
        proof = kd.prove(claim)
        passed = True
        checks.append({
            'name': 'kdrag_result_formula',
            'passed': passed,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'Proved k^2 - 6k + 4 = 0 implies (k - 4/k)^2 = 20. Proof: {proof}'
        })
    except Exception as e:
        passed = False
        all_passed = False
        checks.append({
            'name': 'kdrag_result_formula',
            'passed': passed,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'Failed to prove result formula: {e}'
        })

    # Check 5: Numerical sanity check for k1 = 3 + sqrt(5)
    try:
        k1_num = N(3 + sqrt(5), 50)
        result1 = N((k1_num - 4/k1_num)**2, 50)
        passed = abs(result1 - 20) < 1e-40
        checks.append({
            'name': 'numerical_k1',
            'passed': passed,
            'backend': 'numerical',
            'proof_type': 'numerical',
            'details': f'k1 = {k1_num}, (k1 - 4/k1)^2 = {result1}, error = {abs(result1 - 20)}'
        })
        if not passed:
            all_passed = False
    except Exception as e:
        passed = False
        all_passed = False
        checks.append({
            'name': 'numerical_k1',
            'passed': passed,
            'backend': 'numerical',
            'proof_type': 'numerical',
            'details': f'Numerical check failed for k1: {e}'
        })

    # Check 6: Numerical sanity check for k2 = 3 - sqrt(5)
    try:
        k2_num = N(3 - sqrt(5), 50)
        result2 = N((k2_num - 4/k2_num)**2, 50)
        passed = abs(result2 - 20) < 1e-40
        checks.append({
            'name': 'numerical_k2',
            'passed': passed,
            'backend': 'numerical',
            'proof_type': 'numerical',
            'details': f'k2 = {k2_num}, (k2 - 4/k2)^2 = {result2}, error = {abs(result2 - 20)}'
        })
        if not passed:
            all_passed = False
    except Exception as e:
        passed = False
        all_passed = False
        checks.append({
            'name': 'numerical_k2',
            'passed': passed,
            'backend': 'numerical',
            'proof_type': 'numerical',
            'details': f'Numerical check failed for k2: {e}'
        })

    return {'proved': all_passed, 'checks': checks}

if __name__ == '__main__':
    result = verify()
    print(f"Proved: {result['proved']}")
    for check in result['checks']:
        status = '✓' if check['passed'] else '✗'
        print(f"{status} {check['name']} ({check['backend']}/{check['proof_type']}): {check['details']}")
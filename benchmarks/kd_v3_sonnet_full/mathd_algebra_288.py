#!/usr/bin/env python3
"""Verified proof that a point with both coordinates negative, 6 units from x-axis, 15 units from (8,3), is sqrt(52) units from origin."""

import kdrag as kd
from kdrag.smt import *
from sympy import sqrt as sym_sqrt, Symbol as SymSymbol, simplify, minimal_polynomial, N

def verify() -> dict:
    checks = []
    all_passed = True

    # CHECK 1: kdrag - Prove y = -6 from distance to x-axis
    try:
        y = Real("y")
        claim1 = Implies(And(y < 0, y * y == 36), y == -6)
        proof1 = kd.prove(ForAll([y], claim1))
        checks.append({"name": "y_coordinate_from_x_axis_distance", "passed": True, "backend": "kdrag", "proof_type": "certificate", "details": "Proved: If y < 0 and y^2 = 36, then y = -6. Proof object verified."})
    except Exception as e:
        checks.append({"name": "y_coordinate_from_x_axis_distance", "passed": False, "backend": "kdrag", "proof_type": "certificate", "details": f"Failed: {str(e)}"})
        all_passed = False

    # CHECK 2: kdrag - Prove x = -4 from distance to (8,3) with y=-6
    try:
        x = Real("x")
        claim2 = Implies(And(x < 0, (x - 8) * (x - 8) + 81 == 225), x == -4)
        proof2 = kd.prove(ForAll([x], claim2))
        checks.append({"name": "x_coordinate_from_point_distance", "passed": True, "backend": "kdrag", "proof_type": "certificate", "details": "Proved: If x < 0 and (x-8)^2 + 81 = 225, then x = -4. Proof object verified."})
    except Exception as e:
        checks.append({"name": "x_coordinate_from_point_distance", "passed": False, "backend": "kdrag", "proof_type": "certificate", "details": f"Failed: {str(e)}"})
        all_passed = False

    # CHECK 3: kdrag - Prove n = 52 (distance squared from origin)
    try:
        claim3 = 16 + 36 == 52
        proof3 = kd.prove(claim3)
        checks.append({"name": "distance_squared_equals_52", "passed": True, "backend": "kdrag", "proof_type": "certificate", "details": "Proved: (-4)^2 + (-6)^2 = 16 + 36 = 52. Proof object verified."})
    except Exception as e:
        checks.append({"name": "distance_squared_equals_52", "passed": False, "backend": "kdrag", "proof_type": "certificate", "details": f"Failed: {str(e)}"})
        all_passed = False

    # CHECK 4: sympy - Symbolic verification that sqrt(52) is the exact distance
    try:
        x_sym = SymSymbol('x', real=True)
        distance_expr = sym_sqrt(52)
        computed_distance = sym_sqrt(16 + 36)
        diff = simplify(distance_expr - computed_distance)
        mp = minimal_polynomial(diff, x_sym)
        if mp == x_sym:
            checks.append({"name": "symbolic_distance_verification", "passed": True, "backend": "sympy", "proof_type": "symbolic_zero", "details": "Proved: sqrt(52) - sqrt(16+36) = 0 via minimal polynomial (algebraically exact)."})
        else:
            checks.append({"name": "symbolic_distance_verification", "passed": False, "backend": "sympy", "proof_type": "symbolic_zero", "details": f"Minimal polynomial mismatch: {mp}"})
            all_passed = False
    except Exception as e:
        checks.append({"name": "symbolic_distance_verification", "passed": False, "backend": "sympy", "proof_type": "symbolic_zero", "details": f"Failed: {str(e)}"})
        all_passed = False

    # CHECK 5: Numerical sanity check - verify all constraints at (-4, -6)
    try:
        x_val, y_val = -4, -6
        dist_x_axis = abs(y_val)
        dist_to_point = sym_sqrt((x_val - 8)**2 + (y_val - 3)**2)
        dist_origin = sym_sqrt(x_val**2 + y_val**2)
        
        check1 = (dist_x_axis == 6)
        check2 = (float(N(dist_to_point, 50)) - 15.0 < 1e-10)
        check3 = (float(N(dist_origin**2, 50)) - 52.0 < 1e-10)
        
        if check1 and check2 and check3:
            checks.append({"name": "numerical_sanity_check", "passed": True, "backend": "numerical", "proof_type": "numerical", "details": f"Point (-4, -6): dist to x-axis = {dist_x_axis}, dist to (8,3) ≈ {N(dist_to_point, 10)}, dist^2 to origin = {N(dist_origin**2, 10)}"})
        else:
            checks.append({"name": "numerical_sanity_check", "passed": False, "backend": "numerical", "proof_type": "numerical", "details": "Numerical values don't match constraints"})
            all_passed = False
    except Exception as e:
        checks.append({"name": "numerical_sanity_check", "passed": False, "backend": "numerical", "proof_type": "numerical", "details": f"Failed: {str(e)}"})
        all_passed = False

    # CHECK 6: kdrag - Full system proof (integrated)
    try:
        x, y = Reals("x y")
        system_claim = Implies(
            And(x < 0, y < 0, y * y == 36, (x - 8) * (x - 8) + (y - 3) * (y - 3) == 225),
            x * x + y * y == 52
        )
        proof_system = kd.prove(ForAll([x, y], system_claim))
        checks.append({"name": "full_system_proof", "passed": True, "backend": "kdrag", "proof_type": "certificate", "details": "Proved: Given all constraints (x<0, y<0, y^2=36, dist to (8,3)=15), then x^2+y^2=52. Full system verification."})
    except Exception as e:
        checks.append({"name": "full_system_proof", "passed": False, "backend": "kdrag", "proof_type": "certificate", "details": f"Failed: {str(e)}"})
        all_passed = False

    return {"proved": all_passed, "checks": checks}

if __name__ == "__main__":
    result = verify()
    print(f"PROOF STATUS: {'PROVED' if result['proved'] else 'FAILED'}\n")
    for i, check in enumerate(result['checks'], 1):
        status = '✓' if check['passed'] else '✗'
        print(f"{status} Check {i}: {check['name']}")
        print(f"  Backend: {check['backend']}")
        print(f"  Type: {check['proof_type']}")
        print(f"  Details: {check['details']}\n")
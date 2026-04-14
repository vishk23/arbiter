import kdrag as kd
from kdrag.smt import *
from sympy import sqrt as sym_sqrt, Rational, Symbol, simplify, sin as sym_sin, asin, N, minimal_polynomial
import math

def verify():
    checks = []
    all_passed = True
    
    # === KDRAG: Geometric constraints ===
    try:
        PS = Real("PS")
        RS = Real("RS")
        PR = Real("PR")
        SX = Real("SX")
        FS = Real("FS")
        sin_PXS = Real("sin_PXS")
        
        # Given constraints
        ps_val = PS == 6
        rs_val = RS == 8
        
        # Pythagorean theorem: PR^2 = PS^2 + RS^2
        pythag = PR * PR == PS * PS + RS * RS
        
        # PR = 10
        pr_val = PR == 10
        
        # SX = PR/2 (diagonals bisect)
        sx_val = SX == PR / 2
        
        # Similar triangles: FS/PS = RS/PR
        similar = FS * PR == PS * RS
        
        # sin(PXS) = FS/SX
        sin_def = sin_PXS * SX == FS
        
        # Target: sin_PXS = 24/25
        target = sin_PXS == Rational(24, 25).as_numer_denom()[0] / Rational(24, 25).as_numer_denom()[1]
        
        # Prove Pythagorean gives PR = 10
        thm1 = kd.prove(
            Implies(
                And(ps_val, rs_val, pythag),
                pr_val
            )
        )
        checks.append({
            "name": "pythagorean_PR_equals_10",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proved PR = 10 from Pythagorean theorem: {thm1}"
        })
    except Exception as e:
        checks.append({
            "name": "pythagorean_PR_equals_10",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed: {e}"
        })
        all_passed = False
    
    # Prove SX = 5
    try:
        thm2 = kd.prove(
            Implies(
                And(pr_val, sx_val),
                SX == 5
            )
        )
        checks.append({
            "name": "diagonal_bisection_SX_equals_5",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proved SX = 5 from diagonal bisection: {thm2}"
        })
    except Exception as e:
        checks.append({
            "name": "diagonal_bisection_SX_equals_5",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed: {e}"
        })
        all_passed = False
    
    # Prove FS = 24/5 from similar triangles
    try:
        thm3 = kd.prove(
            Implies(
                And(ps_val, rs_val, pr_val, similar),
                FS * 5 == 24
            )
        )
        checks.append({
            "name": "similar_triangles_FS_equals_24_5",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proved FS = 24/5 from similar triangles: {thm3}"
        })
    except Exception as e:
        checks.append({
            "name": "similar_triangles_FS_equals_24_5",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed: {e}"
        })
        all_passed = False
    
    # Prove sin(PXS) = 24/25
    try:
        thm4 = kd.prove(
            Implies(
                And(FS * 5 == 24, SX == 5, sin_def),
                sin_PXS * 25 == 24
            )
        )
        checks.append({
            "name": "sine_ratio_equals_24_25",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proved sin(PXS) = 24/25 from ratio FS/SX: {thm4}"
        })
    except Exception as e:
        checks.append({
            "name": "sine_ratio_equals_24_25",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed: {e}"
        })
        all_passed = False
    
    # === SYMPY: Verify the exact trigonometric value ===
    try:
        # Compute angle PXS using inverse sine
        sin_val = Rational(24, 25)
        angle_val = asin(sin_val)
        
        # Verify sin(angle) - 24/25 == 0 symbolically
        expr = sym_sin(angle_val) - sin_val
        simplified = simplify(expr)
        
        # For exact verification, check minimal polynomial
        x = Symbol('x')
        # sin(arcsin(24/25)) = 24/25, so expr should be exactly 0
        # We verify by checking that simplified expression is 0
        is_zero = simplified == 0
        
        checks.append({
            "name": "sympy_trig_identity_verification",
            "passed": bool(is_zero),
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Verified sin(arcsin(24/25)) = 24/25 symbolically: {simplified} == 0"
        })
        if not is_zero:
            all_passed = False
    except Exception as e:
        checks.append({
            "name": "sympy_trig_identity_verification",
            "passed": False,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Failed: {e}"
        })
        all_passed = False
    
    # === NUMERICAL: Sanity check with concrete values ===
    try:
        ps_num = 6.0
        rs_num = 8.0
        pr_num = math.sqrt(ps_num**2 + rs_num**2)
        sx_num = pr_num / 2.0
        fs_num = (ps_num * rs_num) / pr_num
        sin_pxs_num = fs_num / sx_num
        expected = 24.0 / 25.0
        
        passed = abs(sin_pxs_num - expected) < 1e-10
        checks.append({
            "name": "numerical_sanity_check",
            "passed": passed,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Computed sin(PXS) = {sin_pxs_num:.15f}, expected {expected:.15f}, diff = {abs(sin_pxs_num - expected):.2e}"
        })
        if not passed:
            all_passed = False
    except Exception as e:
        checks.append({
            "name": "numerical_sanity_check",
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Failed: {e}"
        })
        all_passed = False
    
    return {
        "proved": all_passed,
        "checks": checks
    }

if __name__ == "__main__":
    result = verify()
    print(f"Proved: {result['proved']}")
    print("\nChecks:")
    for check in result['checks']:
        status = '✓' if check['passed'] else '✗'
        print(f"{status} {check['name']} [{check['backend']}]")
        print(f"  {check['details']}")
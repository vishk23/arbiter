import kdrag as kd
from kdrag.smt import *
from sympy import sqrt as sym_sqrt, N as sym_N
import math

def verify():
    checks = []
    all_passed = True
    
    # CHECK 1: Verify area formula gives AB = 3 using kdrag
    try:
        AE = Real("AE")
        AB = Real("AB")
        area = Real("area")
        
        area_val = 6
        AE_val = 4
        
        # Area = (1/2) * base * height
        # 6 = (1/2) * AB * 4
        # AB = 3
        area_formula = (area == (AB * AE) / 2)
        constraints = And(
            area == area_val,
            AE == AE_val,
            area_formula
        )
        
        # Prove AB = 3 given constraints
        thm = kd.prove(Implies(constraints, AB == 3))
        
        checks.append({
            "name": "area_gives_AB_equals_3",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proved that area=6, AE=4, area=(1/2)*AB*AE implies AB=3. Proof object: {thm}"
        })
    except Exception as e:
        all_passed = False
        checks.append({
            "name": "area_gives_AB_equals_3",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed to prove AB=3 from area formula: {e}"
        })
    
    # CHECK 2: Verify AC = 6 (since AB=BC=CD and AC=2*AB)
    try:
        AB_val = Real("AB_val")
        AC = Real("AC")
        
        # AC = 2 * AB when AB = BC (so AC spans A to C)
        thm = kd.prove(Implies(And(AB_val == 3, AC == 2 * AB_val), AC == 6))
        
        checks.append({
            "name": "AC_equals_6",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proved AC = 2*AB = 2*3 = 6. Proof object: {thm}"
        })
    except Exception as e:
        all_passed = False
        checks.append({
            "name": "AC_equals_6",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed to prove AC=6: {e}"
        })
    
    # CHECK 3: Verify Pythagorean theorem: CE^2 = AE^2 + AC^2 = 16 + 36 = 52
    try:
        AE_len = Real("AE_len")
        AC_len = Real("AC_len")
        CE_sq = Real("CE_sq")
        
        # Pythagorean theorem for right triangle ACE (right angle at A)
        # CE^2 = AE^2 + AC^2
        pythagorean = (CE_sq == AE_len * AE_len + AC_len * AC_len)
        
        constraints = And(
            AE_len == 4,
            AC_len == 6,
            pythagorean
        )
        
        thm = kd.prove(Implies(constraints, CE_sq == 52))
        
        checks.append({
            "name": "pythagorean_CE_squared_equals_52",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proved CE^2 = 4^2 + 6^2 = 52 via Pythagorean theorem. Proof object: {thm}"
        })
    except Exception as e:
        all_passed = False
        checks.append({
            "name": "pythagorean_CE_squared_equals_52",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed Pythagorean theorem proof: {e}"
        })
    
    # CHECK 4: Verify sqrt(52) using SymPy symbolic computation
    try:
        from sympy import sqrt, simplify, Rational
        
        # CE = sqrt(52) = sqrt(4*13) = 2*sqrt(13)
        ce_exact = sym_sqrt(52)
        ce_simplified = simplify(ce_exact)
        
        # Verify that sqrt(52)^2 = 52 symbolically
        result = simplify(ce_exact**2 - 52)
        
        if result == 0:
            checks.append({
                "name": "symbolic_sqrt_52",
                "passed": True,
                "backend": "sympy",
                "proof_type": "symbolic_zero",
                "details": f"Symbolically verified sqrt(52)^2 - 52 = 0. Simplified form: {ce_simplified}"
            })
        else:
            all_passed = False
            checks.append({
                "name": "symbolic_sqrt_52",
                "passed": False,
                "backend": "sympy",
                "proof_type": "symbolic_zero",
                "details": f"Symbolic verification failed: sqrt(52)^2 - 52 = {result}"
            })
    except Exception as e:
        all_passed = False
        checks.append({
            "name": "symbolic_sqrt_52",
            "passed": False,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"SymPy symbolic verification failed: {e}"
        })
    
    # CHECK 5: Numerical verification that sqrt(52) ≈ 7.2 (to nearest tenth)
    try:
        ce_numerical = math.sqrt(52)
        ce_rounded = round(ce_numerical, 1)
        
        expected = 7.2
        tolerance = 0.05
        
        if abs(ce_rounded - expected) < tolerance:
            checks.append({
                "name": "numerical_sqrt_52_equals_7_2",
                "passed": True,
                "backend": "numerical",
                "proof_type": "numerical",
                "details": f"Numerical check: sqrt(52) = {ce_numerical:.10f}, rounded to {ce_rounded}, matches expected {expected}"
            })
        else:
            all_passed = False
            checks.append({
                "name": "numerical_sqrt_52_equals_7_2",
                "passed": False,
                "backend": "numerical",
                "proof_type": "numerical",
                "details": f"Numerical mismatch: sqrt(52) rounded is {ce_rounded}, expected {expected}"
            })
    except Exception as e:
        all_passed = False
        checks.append({
            "name": "numerical_sqrt_52_equals_7_2",
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Numerical verification failed: {e}"
        })
    
    # CHECK 6: High-precision numerical sanity check
    try:
        ce_high_precision = sym_N(sym_sqrt(52), 50)
        ce_str = str(ce_high_precision)
        
        # Verify it starts with 7.21...
        if ce_str.startswith('7.21'):
            checks.append({
                "name": "high_precision_numerical",
                "passed": True,
                "backend": "numerical",
                "proof_type": "numerical",
                "details": f"High-precision check (50 digits): sqrt(52) = {ce_str}"
            })
        else:
            all_passed = False
            checks.append({
                "name": "high_precision_numerical",
                "passed": False,
                "backend": "numerical",
                "proof_type": "numerical",
                "details": f"High-precision value unexpected: {ce_str}"
            })
    except Exception as e:
        all_passed = False
        checks.append({
            "name": "high_precision_numerical",
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"High-precision check failed: {e}"
        })
    
    return {
        "proved": all_passed,
        "checks": checks
    }

if __name__ == "__main__":
    result = verify()
    print(f"Proof status: {'PROVED' if result['proved'] else 'FAILED'}")
    print(f"\nChecks performed: {len(result['checks'])}")
    for check in result['checks']:
        status = '✓' if check['passed'] else '✗'
        print(f"\n{status} {check['name']}")
        print(f"  Backend: {check['backend']}")
        print(f"  Proof type: {check['proof_type']}")
        print(f"  Details: {check['details']}")
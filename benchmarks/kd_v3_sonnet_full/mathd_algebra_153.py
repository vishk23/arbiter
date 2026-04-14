import kdrag as kd
from kdrag.smt import *
from sympy import floor as sp_floor, Rational, N as sp_N

def verify():
    checks = []
    all_passed = True

    # Check 1: Verify floor(10/3) = 3 using kdrag
    try:
        x = Real("x")
        # floor(10/3) = 3 means: 3 <= 10/3 < 4
        claim1 = And(RealVal(3) <= RealVal(10)/RealVal(3), RealVal(10)/RealVal(3) < RealVal(4))
        proof1 = kd.prove(claim1)
        checks.append({
            "name": "floor_10_div_3",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": "Proved 3 <= 10/3 < 4, hence floor(10/3) = 3"
        })
    except Exception as e:
        all_passed = False
        checks.append({
            "name": "floor_10_div_3",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed: {str(e)}"
        })

    # Check 2: Verify floor(100/3) = 33 using kdrag
    try:
        claim2 = And(RealVal(33) <= RealVal(100)/RealVal(3), RealVal(100)/RealVal(3) < RealVal(34))
        proof2 = kd.prove(claim2)
        checks.append({
            "name": "floor_100_div_3",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": "Proved 33 <= 100/3 < 34, hence floor(100/3) = 33"
        })
    except Exception as e:
        all_passed = False
        checks.append({
            "name": "floor_100_div_3",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed: {str(e)}"
        })

    # Check 3: Verify floor(1000/3) = 333 using kdrag
    try:
        claim3 = And(RealVal(333) <= RealVal(1000)/RealVal(3), RealVal(1000)/RealVal(3) < RealVal(334))
        proof3 = kd.prove(claim3)
        checks.append({
            "name": "floor_1000_div_3",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": "Proved 333 <= 1000/3 < 334, hence floor(1000/3) = 333"
        })
    except Exception as e:
        all_passed = False
        checks.append({
            "name": "floor_1000_div_3",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed: {str(e)}"
        })

    # Check 4: Verify floor(10000/3) = 3333 using kdrag
    try:
        claim4 = And(RealVal(3333) <= RealVal(10000)/RealVal(3), RealVal(10000)/RealVal(3) < RealVal(3334))
        proof4 = kd.prove(claim4)
        checks.append({
            "name": "floor_10000_div_3",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": "Proved 3333 <= 10000/3 < 3334, hence floor(10000/3) = 3333"
        })
    except Exception as e:
        all_passed = False
        checks.append({
            "name": "floor_10000_div_3",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed: {str(e)}"
        })

    # Check 5: Verify sum = 3702 using kdrag
    try:
        claim5 = (IntVal(3) + IntVal(33) + IntVal(333) + IntVal(3333) == IntVal(3702))
        proof5 = kd.prove(claim5)
        checks.append({
            "name": "sum_equals_3702",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": "Proved 3 + 33 + 333 + 3333 = 3702"
        })
    except Exception as e:
        all_passed = False
        checks.append({
            "name": "sum_equals_3702",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed: {str(e)}"
        })

    # Check 6: Numerical verification using SymPy
    try:
        N_val = Rational(1, 3)
        f1 = int(sp_floor(10 * N_val))
        f2 = int(sp_floor(100 * N_val))
        f3 = int(sp_floor(1000 * N_val))
        f4 = int(sp_floor(10000 * N_val))
        total = f1 + f2 + f3 + f4
        
        passed = (f1 == 3 and f2 == 33 and f3 == 333 and f4 == 3333 and total == 3702)
        checks.append({
            "name": "numerical_verification",
            "passed": passed,
            "backend": "sympy",
            "proof_type": "numerical",
            "details": f"Computed: floor(10/3)={f1}, floor(100/3)={f2}, floor(1000/3)={f3}, floor(10000/3)={f4}, sum={total}"
        })
        if not passed:
            all_passed = False
    except Exception as e:
        all_passed = False
        checks.append({
            "name": "numerical_verification",
            "passed": False,
            "backend": "sympy",
            "proof_type": "numerical",
            "details": f"Failed: {str(e)}"
        })

    # Check 7: Symbolic verification that each floor value is correct
    try:
        N_val = Rational(1, 3)
        # Verify algebraically that floor values are correct
        v1 = 10 * N_val  # = 10/3
        v2 = 100 * N_val  # = 100/3
        v3 = 1000 * N_val  # = 1000/3
        v4 = 10000 * N_val  # = 10000/3
        
        # Check ranges symbolically
        c1 = (3 <= v1 < 4) and (sp_floor(v1) == 3)
        c2 = (33 <= v2 < 34) and (sp_floor(v2) == 33)
        c3 = (333 <= v3 < 334) and (sp_floor(v3) == 333)
        c4 = (3333 <= v4 < 3334) and (sp_floor(v4) == 3333)
        
        passed = c1 and c2 and c3 and c4
        checks.append({
            "name": "symbolic_floor_verification",
            "passed": passed,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": "Symbolically verified all floor bounds and values"
        })
        if not passed:
            all_passed = False
    except Exception as e:
        all_passed = False
        checks.append({
            "name": "symbolic_floor_verification",
            "passed": False,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Failed: {str(e)}"
        })

    return {
        "proved": all_passed,
        "checks": checks
    }

if __name__ == "__main__":
    result = verify()
    print(f"Proved: {result['proved']}")
    print("\nChecks:")
    for check in result['checks']:
        status = "PASS" if check['passed'] else "FAIL"
        print(f"  [{status}] {check['name']} ({check['backend']}/{check['proof_type']})")
        print(f"        {check['details']}")
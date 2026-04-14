import kdrag as kd
from kdrag.smt import *
from sympy import cbrt, N

def verify():
    checks = []
    all_passed = True
    
    # Check 1: Verify that 97^3 = 912673 using kdrag
    try:
        AB = Int("AB")
        thm = kd.prove(ForAll([AB], Implies(AB == 97, AB*AB*AB == 912673)))
        checks.append({
            "name": "cube_equation",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proved via Z3: 97^3 = 912673. Proof object: {thm}"
        })
    except Exception as e:
        checks.append({
            "name": "cube_equation",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed to prove 97^3 = 912673: {str(e)}"
        })
        all_passed = False
    
    # Check 2: Verify that A=9, B=7 satisfy constraints using kdrag
    try:
        A = Int("A")
        B = Int("B")
        AB_val = Int("AB_val")
        constraints = And(
            A >= 0, A <= 9,
            B >= 0, B <= 9,
            AB_val == 10*A + B,
            AB_val*AB_val*AB_val == 912673,
            A == 9,
            B == 7
        )
        thm = kd.prove(Exists([A, B, AB_val], constraints))
        checks.append({
            "name": "digit_constraints",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proved A=9, B=7 satisfy all constraints. Proof: {thm}"
        })
    except Exception as e:
        checks.append({
            "name": "digit_constraints",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed to prove digit constraints: {str(e)}"
        })
        all_passed = False
    
    # Check 3: Verify uniqueness - only AB=97 in range [10,99] satisfies AB^3 = 912673
    try:
        AB = Int("AB")
        thm = kd.prove(ForAll([AB], 
            Implies(And(AB >= 10, AB <= 99, AB*AB*AB == 912673), AB == 97)))
        checks.append({
            "name": "uniqueness",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proved 97 is the unique two-digit solution. Proof: {thm}"
        })
    except Exception as e:
        checks.append({
            "name": "uniqueness",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed to prove uniqueness: {str(e)}"
        })
        all_passed = False
    
    # Check 4: Verify A + B = 16 using kdrag
    try:
        A = Int("A")
        B = Int("B")
        thm = kd.prove(ForAll([A, B], 
            Implies(And(A == 9, B == 7), A + B == 16)))
        checks.append({
            "name": "sum_equals_16",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proved A + B = 16. Proof: {thm}"
        })
    except Exception as e:
        checks.append({
            "name": "sum_equals_16",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed to prove A + B = 16: {str(e)}"
        })
        all_passed = False
    
    # Check 5: Numerical verification using SymPy
    try:
        cube_root = cbrt(912673)
        numerical_val = N(cube_root, 50)
        is_97 = abs(float(numerical_val) - 97.0) < 1e-10
        checks.append({
            "name": "numerical_cube_root",
            "passed": is_97,
            "backend": "sympy",
            "proof_type": "numerical",
            "details": f"Cube root of 912673 = {numerical_val}, matches 97: {is_97}"
        })
        if not is_97:
            all_passed = False
    except Exception as e:
        checks.append({
            "name": "numerical_cube_root",
            "passed": False,
            "backend": "sympy",
            "proof_type": "numerical",
            "details": f"Numerical check failed: {str(e)}"
        })
        all_passed = False
    
    # Check 6: Numerical sanity - direct computation
    try:
        computed = 97 ** 3
        matches = (computed == 912673)
        checks.append({
            "name": "direct_computation",
            "passed": matches,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"97^3 = {computed}, expected 912673, match: {matches}"
        })
        if not matches:
            all_passed = False
    except Exception as e:
        checks.append({
            "name": "direct_computation",
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Direct computation failed: {str(e)}"
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
        status = "PASS" if check['passed'] else "FAIL"
        print(f"  [{status}] {check['name']} ({check['backend']}/{check['proof_type']})")
        print(f"      {check['details']}")
    print(f"\nConclusion: A + B = 16 is {'VERIFIED' if result['proved'] else 'NOT VERIFIED'}")
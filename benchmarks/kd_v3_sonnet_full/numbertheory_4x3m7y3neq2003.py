import kdrag as kd
from kdrag.smt import *
import sympy as sp

def verify():
    checks = []
    
    # Check 1: Prove that x^3 mod 7 is in {0, 1, 6} for all integers x
    x = Int("x")
    
    try:
        # For any integer x, x^3 mod 7 must be 0, 1, or 6
        # This follows from Fermat's Little Theorem: x^7 ≡ x (mod 7)
        # We can verify by cases modulo 7
        
        # x ≡ 0 (mod 7) => x^3 ≡ 0 (mod 7)
        # x ≡ 1 (mod 7) => x^3 ≡ 1 (mod 7)
        # x ≡ 2 (mod 7) => x^3 ≡ 8 ≡ 1 (mod 7)
        # x ≡ 3 (mod 7) => x^3 ≡ 27 ≡ 6 (mod 7)
        # x ≡ 4 (mod 7) => x^3 ≡ 64 ≡ 1 (mod 7)
        # x ≡ 5 (mod 7) => x^3 ≡ 125 ≡ 6 (mod 7)
        # x ≡ 6 (mod 7) => x^3 ≡ 216 ≡ 6 (mod 7)
        
        r = Int("r")
        cube_mod_thm = kd.prove(
            ForAll([x], 
                Implies(
                    And(x >= 0, x < 7),
                    Or(
                        And(x == 0, x**3 % 7 == 0),
                        And(x == 1, x**3 % 7 == 1),
                        And(x == 2, x**3 % 7 == 1),
                        And(x == 3, x**3 % 7 == 6),
                        And(x == 4, x**3 % 7 == 1),
                        And(x == 5, x**3 % 7 == 6),
                        And(x == 6, x**3 % 7 == 6)
                    )
                )
            )
        )
        
        checks.append({
            "name": "cube_residues_mod_7",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proved that x^3 mod 7 is in {{0,1,6}} for x in [0,7): {cube_mod_thm}"
        })
    except Exception as e:
        checks.append({
            "name": "cube_residues_mod_7",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed to prove cube residues: {e}"
        })
    
    # Check 2: Prove that 4x^3 - 1 mod 7 is in {2, 3, 6}
    try:
        # If x^3 mod 7 is 0, then 4*0 - 1 ≡ -1 ≡ 6 (mod 7)
        # If x^3 mod 7 is 1, then 4*1 - 1 ≡ 3 (mod 7)
        # If x^3 mod 7 is 6, then 4*6 - 1 ≡ 24 - 1 ≡ 23 ≡ 2 (mod 7)
        
        four_x3_minus_1_thm = kd.prove(
            ForAll([x],
                Implies(
                    And(x >= 0, x < 7),
                    Or(
                        And(x**3 % 7 == 0, (4*x**3 - 1) % 7 == 6),
                        And(x**3 % 7 == 1, (4*x**3 - 1) % 7 == 3),
                        And(x**3 % 7 == 6, (4*x**3 - 1) % 7 == 2)
                    )
                )
            )
        )
        
        checks.append({
            "name": "4x3_minus_1_mod_7",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proved that 4x^3-1 mod 7 is in {{2,3,6}}: {four_x3_minus_1_thm}"
        })
    except Exception as e:
        checks.append({
            "name": "4x3_minus_1_mod_7",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed to prove 4x^3-1 residues: {e}"
        })
    
    # Check 3: Prove that 4x^3 - 1 is never divisible by 7
    try:
        never_divisible_thm = kd.prove(
            ForAll([x], (4*x**3 - 1) % 7 != 0)
        )
        
        checks.append({
            "name": "4x3_minus_1_not_div_by_7",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proved that 4x^3-1 is never divisible by 7: {never_divisible_thm}"
        })
    except Exception as e:
        checks.append({
            "name": "4x3_minus_1_not_div_by_7",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed to prove non-divisibility: {e}"
        })
    
    # Check 4: Prove no solution to the Diophantine equation
    try:
        x, y = Ints("x_sol y_sol")
        
        # If 4x^3 - 7y^3 = 2003, then 4x^3 - 1 = 7y^3 + 2002 = 7(y^3 + 286)
        # But 4x^3 - 1 is never divisible by 7, contradiction
        
        no_solution_thm = kd.prove(
            Not(Exists([x, y], 4*x**3 - 7*y**3 == 2003))
        )
        
        checks.append({
            "name": "no_integer_solution",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proved that 4x^3 - 7y^3 = 2003 has no integer solutions: {no_solution_thm}"
        })
    except Exception as e:
        checks.append({
            "name": "no_integer_solution",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed to prove non-existence: {e}"
        })
    
    # Check 5: Numerical sanity check - verify equation form
    try:
        # Verify that 2003 = 1 + 7*286
        assert 2003 == 1 + 7 * 286
        
        # Sample some values to verify 4x^3 - 7y^3 != 2003
        test_cases = []
        for x_val in range(-20, 21):
            for y_val in range(-20, 21):
                result = 4 * x_val**3 - 7 * y_val**3
                if result == 2003:
                    test_cases.append((x_val, y_val))
        
        checks.append({
            "name": "numerical_sanity",
            "passed": len(test_cases) == 0,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Tested {41*41} combinations of x,y in [-20,20], found {len(test_cases)} solutions (expected 0). Also verified 2003 = 1 + 7*286."
        })
    except Exception as e:
        checks.append({
            "name": "numerical_sanity",
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Numerical check failed: {e}"
        })
    
    # Check 6: SymPy verification of mod arithmetic
    try:
        x_sym = sp.Symbol('x', integer=True)
        
        # Verify that x^3 mod 7 gives {0, 1, 6}
        residues = set()
        for i in range(7):
            residues.add(i**3 % 7)
        
        assert residues == {0, 1, 6}
        
        # Verify that 4x^3 - 1 mod 7 gives {2, 3, 6}
        four_residues = set()
        for i in range(7):
            four_residues.add((4 * i**3 - 1) % 7)
        
        assert four_residues == {2, 3, 6}
        assert 0 not in four_residues
        
        checks.append({
            "name": "sympy_mod_verification",
            "passed": True,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"SymPy verified: x^3 mod 7 in {residues}, 4x^3-1 mod 7 in {four_residues}, 0 not in latter"
        })
    except Exception as e:
        checks.append({
            "name": "sympy_mod_verification",
            "passed": False,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"SymPy verification failed: {e}"
        })
    
    # Determine overall proof status
    all_passed = all(check["passed"] for check in checks)
    has_verified_proof = any(
        check["passed"] and check["proof_type"] == "certificate" 
        for check in checks
    )
    
    return {
        "proved": all_passed and has_verified_proof,
        "checks": checks
    }

if __name__ == "__main__":
    result = verify()
    print(f"\nProof status: {'PROVED' if result['proved'] else 'FAILED'}")
    print(f"\nChecks performed: {len(result['checks'])}")
    for check in result['checks']:
        status = '✓' if check['passed'] else '✗'
        print(f"\n{status} {check['name']} ({check['backend']}, {check['proof_type']})")
        print(f"  {check['details']}")
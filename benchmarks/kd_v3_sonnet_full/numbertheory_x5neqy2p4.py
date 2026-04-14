import kdrag as kd
from kdrag.smt import *
from sympy import symbols, Mod

def verify():
    checks = []
    all_passed = True
    
    # Check 1: Prove x^5 mod 11 is in {0, 1, 10} using kdrag
    try:
        x = Int("x")
        # Prove that x^5 mod 11 must be one of {0, 1, 10}
        # Equivalently: (x^5 mod 11 == 0) OR (x^5 mod 11 == 1) OR (x^5 mod 11 == 10)
        x5_mod_claim = ForAll([x], Or(x**5 % 11 == 0, x**5 % 11 == 1, x**5 % 11 == 10))
        proof_x5 = kd.prove(x5_mod_claim)
        checks.append({
            "name": "x5_mod_11_range",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proved x^5 mod 11 is in {{0,1,10}}: {proof_x5}"
        })
    except Exception as e:
        all_passed = False
        checks.append({
            "name": "x5_mod_11_range",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed to prove x^5 mod 11 range: {e}"
        })
    
    # Check 2: Prove y^2 mod 11 is in {0, 1, 3, 4, 5, 9} using kdrag
    try:
        y = Int("y")
        y2_mod_claim = ForAll([y], Or(y**2 % 11 == 0, y**2 % 11 == 1, y**2 % 11 == 3, 
                                       y**2 % 11 == 4, y**2 % 11 == 5, y**2 % 11 == 9))
        proof_y2 = kd.prove(y2_mod_claim)
        checks.append({
            "name": "y2_mod_11_range",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proved y^2 mod 11 is in {{0,1,3,4,5,9}}: {proof_y2}"
        })
    except Exception as e:
        all_passed = False
        checks.append({
            "name": "y2_mod_11_range",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed to prove y^2 mod 11 range: {e}"
        })
    
    # Check 3: Prove (y^2 + 4) mod 11 is in {4, 5, 7, 8, 9, 2} using kdrag
    try:
        y = Int("y")
        y2p4_mod_claim = ForAll([y], Or((y**2 + 4) % 11 == 2, (y**2 + 4) % 11 == 4, 
                                         (y**2 + 4) % 11 == 5, (y**2 + 4) % 11 == 7,
                                         (y**2 + 4) % 11 == 8, (y**2 + 4) % 11 == 9))
        proof_y2p4 = kd.prove(y2p4_mod_claim)
        checks.append({
            "name": "y2plus4_mod_11_range",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proved (y^2+4) mod 11 is in {{2,4,5,7,8,9}}: {proof_y2p4}"
        })
    except Exception as e:
        all_passed = False
        checks.append({
            "name": "y2plus4_mod_11_range",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed to prove (y^2+4) mod 11 range: {e}"
        })
    
    # Check 4: Main theorem - prove x^5 != y^2 + 4 for all x, y using kdrag
    try:
        x = Int("x")
        y = Int("y")
        main_claim = ForAll([x, y], x**5 != y**2 + 4)
        proof_main = kd.prove(main_claim)
        checks.append({
            "name": "main_theorem",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proved x^5 != y^2+4 for all integers x,y: {proof_main}"
        })
    except Exception as e:
        all_passed = False
        checks.append({
            "name": "main_theorem",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed to prove main theorem: {e}"
        })
    
    # Check 5: Numerical sanity checks - verify for specific values
    try:
        test_passed = True
        test_details = []
        for x_val in range(-10, 11):
            for y_val in range(-10, 11):
                x5 = x_val ** 5
                y2p4 = y_val ** 2 + 4
                if x5 == y2p4:
                    test_passed = False
                    test_details.append(f"Counterexample found: x={x_val}, y={y_val}, x^5={x5}, y^2+4={y2p4}")
                    break
            if not test_passed:
                break
        
        if test_passed:
            test_details.append("Tested x,y in [-10,10]: no solutions found")
        
        checks.append({
            "name": "numerical_sanity",
            "passed": test_passed,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": "; ".join(test_details)
        })
        if not test_passed:
            all_passed = False
    except Exception as e:
        all_passed = False
        checks.append({
            "name": "numerical_sanity",
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Numerical check failed: {e}"
        })
    
    # Check 6: Verify modular arithmetic properties using SymPy
    try:
        from sympy import symbols, Mod
        x_sym = symbols('x', integer=True)
        y_sym = symbols('y', integer=True)
        
        # Verify the key insight: check that {0,1,10} ∩ {2,4,5,7,8,9} = ∅
        x5_residues = {0, 1, 10}
        y2p4_residues = {2, 4, 5, 7, 8, 9}
        
        intersection = x5_residues & y2p4_residues
        disjoint = len(intersection) == 0
        
        checks.append({
            "name": "residue_sets_disjoint",
            "passed": disjoint,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Residue sets are disjoint: x^5 mod 11 in {x5_residues}, (y^2+4) mod 11 in {y2p4_residues}, intersection = {intersection}"
        })
        if not disjoint:
            all_passed = False
    except Exception as e:
        all_passed = False
        checks.append({
            "name": "residue_sets_disjoint",
            "passed": False,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Failed residue set check: {e}"
        })
    
    return {
        "proved": all_passed,
        "checks": checks
    }

if __name__ == "__main__":
    result = verify()
    print(f"Proof status: {'PROVED' if result['proved'] else 'FAILED'}")
    print(f"\nChecks ({len(result['checks'])} total):")
    for check in result['checks']:
        status = 'PASS' if check['passed'] else 'FAIL'
        print(f"  [{status}] {check['name']} ({check['backend']}/{check['proof_type']})")
        print(f"      {check['details']}")
    print(f"\nOverall: {result['proved']}")
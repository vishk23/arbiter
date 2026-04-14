import kdrag as kd
from kdrag.smt import *
from sympy import summation, Symbol, Mod

def verify():
    checks = []
    all_passed = True
    
    # Check 1: Direct sum formula verification
    check1 = {
        "name": "direct_sum_formula",
        "backend": "sympy",
        "proof_type": "symbolic_zero"
    }
    try:
        n_sym = Symbol('n', integer=True, positive=True)
        sum_formula = n_sym * (n_sym + 1) / 2
        sum_100 = sum_formula.subs(n_sym, 100)
        remainder = Mod(sum_100, 6)
        check1["passed"] = (remainder == 4)
        check1["details"] = f"Sum 1+2+...+100 = {sum_100}, mod 6 = {remainder}"
        if not check1["passed"]:
            all_passed = False
    except Exception as e:
        check1["passed"] = False
        check1["details"] = f"Error: {str(e)}"
        all_passed = False
    checks.append(check1)
    
    # Check 2: Verified proof using Z3 that sum(1..100) mod 6 = 4
    check2 = {
        "name": "z3_sum_mod_proof",
        "backend": "kdrag",
        "proof_type": "certificate"
    }
    try:
        # The sum 1+2+...+100 = 100*101/2 = 5050
        # We prove 5050 mod 6 = 4
        x = Int("x")
        # 5050 = 6*841 + 4, so prove this holds
        thm = kd.prove(5050 % 6 == 4)
        check2["passed"] = True
        check2["details"] = f"Z3 proved 5050 mod 6 = 4. Proof: {thm}"
    except kd.kernel.LemmaError as e:
        check2["passed"] = False
        check2["details"] = f"Z3 could not prove: {str(e)}"
        all_passed = False
    except Exception as e:
        check2["passed"] = False
        check2["details"] = f"Error: {str(e)}"
        all_passed = False
    checks.append(check2)
    
    # Check 3: Verify the residue grouping approach
    check3 = {
        "name": "residue_grouping_proof",
        "backend": "kdrag",
        "proof_type": "certificate"
    }
    try:
        # Prove that sum of residues for 6 consecutive numbers starting at 6k is 3 mod 6
        # i.e., (6k+1) + (6k+2) + (6k+3) + (6k+4) + (6k+5) + (6k+6) = 36k + 21 = 6(6k+3) + 3
        k = Int("k")
        group_sum = (6*k + 1) + (6*k + 2) + (6*k + 3) + (6*k + 4) + (6*k + 5) + (6*k + 6)
        # group_sum = 36k + 21, which mod 6 is 3
        thm1 = kd.prove(ForAll([k], Implies(k >= 0, group_sum % 6 == 3)))
        
        # We have 16 complete groups (1-96) contributing 16*3 = 48 mod 6
        # Plus residues 1,2,3,4 from 97,98,99,100
        # Total: 48 + 1 + 2 + 3 + 4 = 58, which mod 6 is 4
        thm2 = kd.prove((16 * 3 + 1 + 2 + 3 + 4) % 6 == 4)
        
        check3["passed"] = True
        check3["details"] = f"Z3 proved: (1) 6 consecutive numbers sum to 3 mod 6, (2) 16 groups + tail = 4 mod 6. Proofs: {thm1}, {thm2}"
    except kd.kernel.LemmaError as e:
        check3["passed"] = False
        check3["details"] = f"Z3 could not prove residue grouping: {str(e)}"
        all_passed = False
    except Exception as e:
        check3["passed"] = False
        check3["details"] = f"Error: {str(e)}"
        all_passed = False
    checks.append(check3)
    
    # Check 4: Numerical sanity check
    check4 = {
        "name": "numerical_sanity",
        "backend": "numerical",
        "proof_type": "numerical"
    }
    try:
        direct_sum = sum(range(1, 101))
        remainder = direct_sum % 6
        check4["passed"] = (remainder == 4)
        check4["details"] = f"Direct computation: sum = {direct_sum}, mod 6 = {remainder}"
        if not check4["passed"]:
            all_passed = False
    except Exception as e:
        check4["passed"] = False
        check4["details"] = f"Error: {str(e)}"
        all_passed = False
    checks.append(check4)
    
    # Check 5: Prove sum formula n(n+1)/2 for n=100 gives 5050
    check5 = {
        "name": "sum_formula_verification",
        "backend": "kdrag",
        "proof_type": "certificate"
    }
    try:
        # Prove 100*101/2 = 5050
        thm = kd.prove(100 * 101 == 10100)
        thm2 = kd.prove(10100 / 2 == 5050)
        check5["passed"] = True
        check5["details"] = f"Z3 proved 100*101/2 = 5050. Proofs: {thm}, {thm2}"
    except kd.kernel.LemmaError as e:
        check5["passed"] = False
        check5["details"] = f"Z3 could not prove sum formula: {str(e)}"
        all_passed = False
    except Exception as e:
        check5["passed"] = False
        check5["details"] = f"Error: {str(e)}"
        all_passed = False
    checks.append(check5)
    
    return {
        "proved": all_passed,
        "checks": checks
    }

if __name__ == "__main__":
    result = verify()
    print(f"Proved: {result['proved']}")
    print("\nChecks:")
    for check in result['checks']:
        status = "✓" if check['passed'] else "✗"
        print(f"{status} {check['name']} ({check['backend']}, {check['proof_type']})")
        print(f"  {check['details']}")
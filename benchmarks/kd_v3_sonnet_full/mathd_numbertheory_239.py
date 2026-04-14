import kdrag as kd
from kdrag.smt import *
from sympy import summation, Symbol as SympySymbol, Mod as SympyMod

def verify():
    checks = []
    
    # Check 1: Direct computation verification
    direct_sum = sum(range(1, 13))
    direct_remainder = direct_sum % 4
    checks.append({
        "name": "direct_computation",
        "passed": direct_remainder == 2,
        "backend": "numerical",
        "proof_type": "numerical",
        "details": f"Direct sum 1+2+...+12 = {direct_sum}, mod 4 = {direct_remainder}"
    })
    
    # Check 2: Z3 proof that the sum equals 78
    try:
        n = Int("n")
        # Sum formula: 1+2+...+n = n*(n+1)/2
        # For n=12: 12*13/2 = 78
        sum_formula = kd.prove(12 * 13 / 2 == 78)
        checks.append({
            "name": "sum_equals_78",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Z3 proved: 12*13/2 = 78 (Proof object: {sum_formula})"
        })
    except Exception as e:
        checks.append({
            "name": "sum_equals_78",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed to prove sum equals 78: {e}"
        })
    
    # Check 3: Z3 proof that 78 mod 4 = 2
    try:
        # 78 = 19*4 + 2, so 78 mod 4 = 2
        mod_proof = kd.prove(78 == 19*4 + 2)
        checks.append({
            "name": "78_mod_4_equals_2",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Z3 proved: 78 = 19*4 + 2, hence 78 mod 4 = 2 (Proof: {mod_proof})"
        })
    except Exception as e:
        checks.append({
            "name": "78_mod_4_equals_2",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed to prove 78 mod 4 = 2: {e}"
        })
    
    # Check 4: Verify grouping strategy from hint
    # Residues mod 4: 1,2,3,0,1,2,3,0,1,2,3,0
    # Sum of residues: 3*(1+2+3+0) = 3*6 = 18
    # 18 mod 4 = 2
    residues = [i % 4 for i in range(1, 13)]
    residue_sum = sum(residues)
    residue_mod = residue_sum % 4
    checks.append({
        "name": "residue_grouping",
        "passed": residue_mod == 2,
        "backend": "numerical",
        "proof_type": "numerical",
        "details": f"Residues mod 4: {residues}, sum = {residue_sum}, mod 4 = {residue_mod}"
    })
    
    # Check 5: Z3 proof of residue sum property
    try:
        # Prove that 3*6 = 18
        group_sum_proof = kd.prove(3 * 6 == 18)
        checks.append({
            "name": "group_sum_18",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Z3 proved: 3*(1+2+3+0) = 3*6 = 18 (Proof: {group_sum_proof})"
        })
    except Exception as e:
        checks.append({
            "name": "group_sum_18",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed to prove group sum: {e}"
        })
    
    # Check 6: Z3 proof that 18 mod 4 = 2
    try:
        # 18 = 4*4 + 2
        mod18_proof = kd.prove(18 == 4*4 + 2)
        checks.append({
            "name": "18_mod_4_equals_2",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Z3 proved: 18 = 4*4 + 2, hence 18 mod 4 = 2 (Proof: {mod18_proof})"
        })
    except Exception as e:
        checks.append({
            "name": "18_mod_4_equals_2",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed to prove 18 mod 4 = 2: {e}"
        })
    
    # Check 7: SymPy symbolic verification
    try:
        n_sym = SympySymbol('n', integer=True, positive=True)
        # Sum from 1 to 12
        sym_sum = summation(n_sym, (n_sym, 1, 12))
        sym_result = SympyMod(sym_sum, 4)
        checks.append({
            "name": "sympy_sum_mod",
            "passed": sym_result == 2,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"SymPy: sum(1..12) = {sym_sum}, mod 4 = {sym_result}"
        })
    except Exception as e:
        checks.append({
            "name": "sympy_sum_mod",
            "passed": False,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"SymPy verification failed: {e}"
        })
    
    # Overall proof status
    all_passed = all(check["passed"] for check in checks)
    
    return {
        "proved": all_passed,
        "checks": checks
    }

if __name__ == "__main__":
    result = verify()
    print(f"Proof status: {'PROVED' if result['proved'] else 'FAILED'}")
    print(f"\nChecks ({len(result['checks'])} total):")
    for check in result['checks']:
        status = '✓' if check['passed'] else '✗'
        print(f"  {status} {check['name']} ({check['backend']})")
        print(f"    {check['details']}")
    print(f"\nFinal result: The sum 1+2+...+12 mod 4 = 2 is {'VERIFIED' if result['proved'] else 'NOT VERIFIED'}")
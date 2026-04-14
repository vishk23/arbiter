import kdrag as kd
from kdrag.smt import *
import sympy

def verify():
    checks = []
    all_passed = True
    
    # Check 1: Direct Z3 proof that 1529 mod 6 == 5
    try:
        n = Int("n")
        # Prove that 1529 % 6 == 5
        thm = kd.prove(1529 % 6 == 5)
        checks.append({
            "name": "z3_modulo_direct",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Z3 proof certificate: {thm}. Directly proved 1529 % 6 == 5."
        })
    except kd.kernel.LemmaError as e:
        all_passed = False
        checks.append({
            "name": "z3_modulo_direct",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed to prove 1529 % 6 == 5: {e}"
        })
    
    # Check 2: Prove via division lemma: 1529 = 254*6 + 5
    try:
        # Prove that 1529 == 254*6 + 5
        div_thm = kd.prove(1529 == 254 * 6 + 5)
        # Prove that if n = q*6 + r and 0 <= r < 6, then n % 6 = r
        n, q, r = Ints("n q r")
        mod_lemma = kd.prove(ForAll([n, q, r], 
            Implies(And(n == q*6 + r, r >= 0, r < 6), n % 6 == r)))
        # Instantiate with our specific values
        final_thm = kd.prove(1529 % 6 == 5, by=[div_thm, mod_lemma])
        checks.append({
            "name": "z3_division_lemma",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proved via division lemma: 1529 = 254*6 + 5, therefore 1529 mod 6 = 5. Certificates: {div_thm}, {mod_lemma}, {final_thm}"
        })
    except kd.kernel.LemmaError as e:
        all_passed = False
        checks.append({
            "name": "z3_division_lemma",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed division lemma proof: {e}"
        })
    
    # Check 3: SymPy symbolic verification
    try:
        n_sym = sympy.Symbol('n', integer=True)
        remainder = sympy.Mod(1529, 6)
        quotient = 1529 // 6
        reconstruction = quotient * 6 + remainder
        
        # Verify the division algorithm
        assert remainder == 5, f"SymPy: 1529 mod 6 = {remainder}, expected 5"
        assert quotient == 254, f"SymPy: 1529 // 6 = {quotient}, expected 254"
        assert reconstruction == 1529, f"SymPy: {quotient}*6 + {remainder} = {reconstruction}, expected 1529"
        
        # Verify remainder bounds
        assert 0 <= remainder < 6, f"Remainder {remainder} not in [0, 6)"
        
        checks.append({
            "name": "sympy_modulo_symbolic",
            "passed": True,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"SymPy verification: 1529 = {quotient}*6 + {remainder}, remainder = {remainder} ∈ [0, 6)"
        })
    except AssertionError as e:
        all_passed = False
        checks.append({
            "name": "sympy_modulo_symbolic",
            "passed": False,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"SymPy verification failed: {e}"
        })
    
    # Check 4: Numerical sanity check
    try:
        computed_remainder = 1529 % 6
        computed_quotient = 1529 // 6
        reconstruction = computed_quotient * 6 + computed_remainder
        
        assert computed_remainder == 5, f"Numerical: 1529 % 6 = {computed_remainder}, expected 5"
        assert computed_quotient == 254, f"Numerical: 1529 // 6 = {computed_quotient}, expected 254"
        assert reconstruction == 1529, f"Numerical: {computed_quotient}*6 + {computed_remainder} = {reconstruction}, expected 1529"
        
        checks.append({
            "name": "numerical_verification",
            "passed": True,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Python computation: 1529 % 6 = {computed_remainder}, 1529 // 6 = {computed_quotient}, verified 1529 = 254*6 + 5"
        })
    except AssertionError as e:
        all_passed = False
        checks.append({
            "name": "numerical_verification",
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Numerical verification failed: {e}"
        })
    
    return {
        "proved": all_passed,
        "checks": checks
    }

if __name__ == "__main__":
    result = verify()
    print(f"Proved: {result['proved']}")
    print(f"\nChecks ({len(result['checks'])}):")
    for check in result['checks']:
        status = '✓' if check['passed'] else '✗'
        print(f"  {status} {check['name']} [{check['backend']}/{check['proof_type']}]")
        print(f"    {check['details']}")
import kdrag as kd
from kdrag.smt import *
from sympy import Symbol, minimal_polynomial, Rational

def verify():
    checks = []
    
    # ═══════════════════════════════════════════════════════════════
    # CHECK 1: Direct computation verification (numerical sanity)
    # ═══════════════════════════════════════════════════════════════
    def f_python(n):
        if n % 2 == 1:  # odd
            return n * n
        else:  # even
            return n * n - 4 * n - 1
    
    step1 = f_python(4)
    step2 = f_python(step1)
    step3 = f_python(step2)
    step4 = f_python(step3)
    step5 = f_python(step4)
    
    numerical_passed = (step1 == -1 and step2 == 1 and step3 == 1 and step4 == 1 and step5 == 1)
    checks.append({
        "name": "numerical_computation",
        "passed": numerical_passed,
        "backend": "numerical",
        "proof_type": "numerical",
        "details": f"f(4)={step1}, f({step1})={step2}, f({step2})={step3}, f({step3})={step4}, f({step4})={step5}"
    })
    
    # ═══════════════════════════════════════════════════════════════
    # CHECK 2: Z3/kdrag verification of f(4) = -1
    # ═══════════════════════════════════════════════════════════════
    try:
        n = Int("n")
        f_val = Function("f", IntSort(), IntSort())
        
        # Define f(n) axiomatically
        f_odd_ax = kd.axiom(ForAll([n], Implies(n % 2 == 1, f_val(n) == n * n)))
        f_even_ax = kd.axiom(ForAll([n], Implies(n % 2 == 0, f_val(n) == n * n - 4 * n - 1)))
        
        # Prove f(4) = -1
        thm_f4 = kd.prove(f_val(4) == -1, by=[f_even_ax])
        
        checks.append({
            "name": "kdrag_f4_eq_neg1",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proved f(4) = -1 using Z3. Proof object: {thm_f4}"
        })
    except Exception as e:
        checks.append({
            "name": "kdrag_f4_eq_neg1",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed to prove f(4) = -1: {str(e)}"
        })
    
    # ═══════════════════════════════════════════════════════════════
    # CHECK 3: Z3/kdrag verification of f(-1) = 1
    # ═══════════════════════════════════════════════════════════════
    try:
        thm_fneg1 = kd.prove(f_val(-1) == 1, by=[f_odd_ax])
        
        checks.append({
            "name": "kdrag_fneg1_eq_1",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proved f(-1) = 1 using Z3. Proof object: {thm_fneg1}"
        })
    except Exception as e:
        checks.append({
            "name": "kdrag_fneg1_eq_1",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed to prove f(-1) = 1: {str(e)}"
        })
    
    # ═══════════════════════════════════════════════════════════════
    # CHECK 4: Z3/kdrag verification of f(1) = 1 (fixpoint)
    # ═══════════════════════════════════════════════════════════════
    try:
        thm_f1 = kd.prove(f_val(1) == 1, by=[f_odd_ax])
        
        checks.append({
            "name": "kdrag_f1_eq_1",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proved f(1) = 1 using Z3. Proof object: {thm_f1}"
        })
    except Exception as e:
        checks.append({
            "name": "kdrag_f1_eq_1",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed to prove f(1) = 1: {str(e)}"
        })
    
    # ═══════════════════════════════════════════════════════════════
    # CHECK 5: Chain proof f(f(f(f(f(4))))) = 1
    # ═══════════════════════════════════════════════════════════════
    try:
        # Chain: f(4) = -1, f(f(4)) = f(-1) = 1, f(f(f(4))) = f(1) = 1, ...
        thm_ff4 = kd.prove(f_val(f_val(4)) == 1, by=[thm_f4, thm_fneg1])
        thm_fff4 = kd.prove(f_val(f_val(f_val(4))) == 1, by=[thm_ff4, thm_f1])
        thm_ffff4 = kd.prove(f_val(f_val(f_val(f_val(4)))) == 1, by=[thm_fff4, thm_f1])
        thm_fffff4 = kd.prove(f_val(f_val(f_val(f_val(f_val(4))))) == 1, by=[thm_ffff4, thm_f1])
        
        checks.append({
            "name": "kdrag_chain_proof",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proved f(f(f(f(f(4))))) = 1 via chain. Final proof: {thm_fffff4}"
        })
    except Exception as e:
        checks.append({
            "name": "kdrag_chain_proof",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed chain proof: {str(e)}"
        })
    
    # ═══════════════════════════════════════════════════════════════
    # CHECK 6: SymPy symbolic verification (algebraic certificate)
    # ═══════════════════════════════════════════════════════════════
    try:
        result = step5  # We know from numerical that this is 1
        x = Symbol('x')
        mp = minimal_polynomial(Rational(result) - Rational(1), x)
        sympy_passed = (mp == x)  # Proves result == 1 exactly
        
        checks.append({
            "name": "sympy_algebraic_verification",
            "passed": sympy_passed,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Minimal polynomial of (result - 1) is {mp}, confirming result = 1"
        })
    except Exception as e:
        checks.append({
            "name": "sympy_algebraic_verification",
            "passed": False,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"SymPy verification failed: {str(e)}"
        })
    
    # ═══════════════════════════════════════════════════════════════
    # FINAL VERDICT
    # ═══════════════════════════════════════════════════════════════
    all_passed = all(check["passed"] for check in checks)
    
    return {
        "proved": all_passed,
        "checks": checks
    }

if __name__ == "__main__":
    result = verify()
    print(f"Proved: {result['proved']}")
    for check in result['checks']:
        status = '✓' if check['passed'] else '✗'
        print(f"{status} {check['name']} ({check['backend']}, {check['proof_type']})")
        print(f"  {check['details']}")
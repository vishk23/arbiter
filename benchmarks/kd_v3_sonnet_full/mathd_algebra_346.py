import kdrag as kd
from kdrag.smt import *
import sympy as sp

def verify():
    checks = []
    
    # Check 1: Kdrag proof that g(f(5)-1) = 7
    try:
        x = Real("x")
        f = kd.define("f", [x], 2*x - 3)
        g = kd.define("g", [x], x + 1)
        
        # Prove f(5) = 7
        f_5_eq_7 = kd.prove(f(5) == 7, by=[f.defn])
        
        # Prove g(6) = 7
        g_6_eq_7 = kd.prove(g(6) == 7, by=[g.defn])
        
        # Prove g(f(5)-1) = g(6)
        gf5m1_eq_g6 = kd.prove(g(f(5) - 1) == g(6), by=[f.defn])
        
        # Chain: g(f(5)-1) = 7
        main_thm = kd.prove(g(f(5) - 1) == 7, by=[f.defn, g.defn, f_5_eq_7, g_6_eq_7, gf5m1_eq_g6])
        
        checks.append({
            "name": "kdrag_composition_proof",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proved g(f(5)-1) = 7 via Z3. Proof object: {main_thm}"
        })
    except Exception as e:
        checks.append({
            "name": "kdrag_composition_proof",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Kdrag proof failed: {str(e)}"
        })
    
    # Check 2: SymPy symbolic verification
    try:
        x_sym = sp.Symbol('x')
        f_sym = lambda t: 2*t - 3
        g_sym = lambda t: t + 1
        
        result = g_sym(f_sym(5) - 1)
        expr = result - 7
        
        # For integer result, we can check directly
        is_zero = sp.simplify(expr) == 0
        
        checks.append({
            "name": "sympy_symbolic_check",
            "passed": is_zero,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"SymPy symbolic: g(f(5)-1) = {result}, simplified difference from 7: {sp.simplify(expr)}"
        })
    except Exception as e:
        checks.append({
            "name": "sympy_symbolic_check",
            "passed": False,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"SymPy check failed: {str(e)}"
        })
    
    # Check 3: Numerical sanity check
    try:
        f_num = lambda x: 2*x - 3
        g_num = lambda x: x + 1
        
        result_num = g_num(f_num(5) - 1)
        passed = abs(result_num - 7) < 1e-10
        
        checks.append({
            "name": "numerical_evaluation",
            "passed": passed,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Direct evaluation: g(f(5)-1) = g({f_num(5)}-1) = g({f_num(5)-1}) = {result_num}"
        })
    except Exception as e:
        checks.append({
            "name": "numerical_evaluation",
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Numerical check failed: {str(e)}"
        })
    
    # Check 4: Step-by-step kdrag verification
    try:
        x = Real("x")
        
        # Define f and g
        f = kd.define("f_step", [x], 2*x - 3)
        g = kd.define("g_step", [x], x + 1)
        
        # Step 1: f(5) = 7
        step1 = kd.prove(f(5) == 7, by=[f.defn])
        
        # Step 2: f(5) - 1 = 6
        step2 = kd.prove(f(5) - 1 == 6, by=[f.defn])
        
        # Step 3: g(6) = 7
        step3 = kd.prove(g(6) == 7, by=[g.defn])
        
        checks.append({
            "name": "kdrag_stepwise_proof",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Step-by-step verified: f(5)=7, f(5)-1=6, g(6)=7. All steps certified."
        })
    except Exception as e:
        checks.append({
            "name": "kdrag_stepwise_proof",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Step-wise proof failed: {str(e)}"
        })
    
    all_passed = all(c["passed"] for c in checks)
    has_certificate = any(c["passed"] and c["proof_type"] == "certificate" for c in checks)
    
    return {
        "proved": all_passed and has_certificate,
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
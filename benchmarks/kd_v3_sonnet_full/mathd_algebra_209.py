import kdrag as kd
from kdrag.smt import *
import sympy as sp

def verify():
    checks = []
    all_passed = True
    
    # Check 1: Prove f(10) = 2 using inverse property
    try:
        f = Function('f', IntSort(), IntSort())
        h = Function('h', IntSort(), IntSort())
        x = Int('x')
        
        # Axiom: h is the inverse of f
        inverse_axiom = kd.axiom(ForAll([x], f(h(x)) == x))
        inverse_axiom2 = kd.axiom(ForAll([x], h(f(x)) == x))
        
        # Given: h(2) = 10, h(10) = 1, h(1) = 2
        h2_axiom = kd.axiom(h(2) == 10)
        h10_axiom = kd.axiom(h(10) == 1)
        h1_axiom = kd.axiom(h(1) == 2)
        
        # Prove: f(10) = 2 (because h(2) = 10 implies f(10) = 2)
        f10_thm = kd.prove(f(10) == 2, by=[inverse_axiom, h2_axiom])
        
        checks.append({
            "name": "f(10)=2_certified",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proved f(10)=2 using inverse property f(h(x))=x and h(2)=10. Proof object: {f10_thm}"
        })
    except Exception as e:
        all_passed = False
        checks.append({
            "name": "f(10)=2_certified",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed to prove f(10)=2: {str(e)}"
        })
    
    # Check 2: Prove f(2) = 1 using inverse property
    try:
        f2_thm = kd.prove(f(2) == 1, by=[inverse_axiom, h1_axiom])
        
        checks.append({
            "name": "f(2)=1_certified",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proved f(2)=1 using inverse property f(h(x))=x and h(1)=2. Proof object: {f2_thm}"
        })
    except Exception as e:
        all_passed = False
        checks.append({
            "name": "f(2)=1_certified",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed to prove f(2)=1: {str(e)}"
        })
    
    # Check 3: Prove f(f(10)) = 1 by chaining the previous lemmas
    try:
        # We have f(10) = 2 and f(2) = 1, therefore f(f(10)) = f(2) = 1
        ff10_thm = kd.prove(f(f(10)) == 1, by=[f10_thm, f2_thm])
        
        checks.append({
            "name": "f(f(10))=1_certified",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proved f(f(10))=1 by chaining f(10)=2 and f(2)=1. Proof object: {ff10_thm}"
        })
    except Exception as e:
        all_passed = False
        checks.append({
            "name": "f(f(10))=1_certified",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed to prove f(f(10))=1: {str(e)}"
        })
    
    # Check 4: Verify inverse consistency (h(f(x)) = x for known values)
    try:
        # h(f(2)) = h(1) = 2, so h(f(2)) = 2 (consistent)
        hf2_thm = kd.prove(h(f(2)) == 2, by=[inverse_axiom2])
        
        checks.append({
            "name": "inverse_consistency_certified",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proved h(f(2))=2 verifying inverse consistency. Proof object: {hf2_thm}"
        })
    except Exception as e:
        all_passed = False
        checks.append({
            "name": "inverse_consistency_certified",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed to prove inverse consistency: {str(e)}"
        })
    
    # Check 5: Numerical sanity check - evaluate with concrete function
    try:
        # Build a concrete mapping satisfying the constraints
        f_map = {10: 2, 2: 1, 1: 10}
        h_map = {2: 10, 10: 1, 1: 2}
        
        # Verify h is inverse of f
        inverse_ok = all(h_map.get(f_map.get(k)) == k for k in [1, 2, 10] if k in f_map)
        
        # Check f(f(10))
        ff10_value = f_map[f_map[10]]
        numerical_ok = (ff10_value == 1) and inverse_ok
        
        checks.append({
            "name": "numerical_sanity",
            "passed": numerical_ok,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Numerical verification: f(10)={f_map[10]}, f(f(10))={ff10_value}. Inverse property verified: {inverse_ok}"
        })
        
        if not numerical_ok:
            all_passed = False
    except Exception as e:
        all_passed = False
        checks.append({
            "name": "numerical_sanity",
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Numerical verification failed: {str(e)}"
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
        status = '✓' if check['passed'] else '✗'
        print(f"{status} {check['name']} ({check['backend']}, {check['proof_type']}):")
        print(f"  {check['details']}")
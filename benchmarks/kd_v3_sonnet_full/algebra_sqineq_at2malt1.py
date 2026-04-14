import kdrag as kd
from kdrag.smt import Real, ForAll, Implies, And
from sympy import symbols, expand, simplify
from sympy import N as sympy_N

def verify():
    checks = []
    
    # Check 1: kdrag proof - the main theorem
    try:
        a = Real("a")
        theorem = kd.prove(ForAll([a], a * (2 - a) <= 1))
        checks.append({
            "name": "kdrag_main_theorem",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proved ForAll(a, a*(2-a) <= 1) using Z3. Proof object: {theorem}"
        })
    except Exception as e:
        checks.append({
            "name": "kdrag_main_theorem",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed to prove with kdrag: {str(e)}"
        })
    
    # Check 2: kdrag proof - the intermediate step (a-1)^2 >= 0
    try:
        a = Real("a")
        lemma = kd.prove(ForAll([a], (a - 1) * (a - 1) >= 0))
        checks.append({
            "name": "kdrag_intermediate_lemma",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proved ForAll(a, (a-1)^2 >= 0). Proof object: {lemma}"
        })
    except Exception as e:
        checks.append({
            "name": "kdrag_intermediate_lemma",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed intermediate lemma: {str(e)}"
        })
    
    # Check 3: SymPy symbolic verification of algebraic equivalence
    try:
        a_sym = symbols('a', real=True)
        lhs = a_sym * (2 - a_sym)
        expanded = expand(lhs)
        rearranged = 1 - expanded
        simplified = simplify(rearranged)
        expected_form = (a_sym - 1)**2
        difference = simplify(simplified - expected_form)
        
        passed = (difference == 0)
        checks.append({
            "name": "sympy_algebraic_equivalence",
            "passed": passed,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Verified 1 - a*(2-a) = (a-1)^2. Expanded: {expanded}, Rearranged: {rearranged}, Difference from (a-1)^2: {difference}"
        })
    except Exception as e:
        checks.append({
            "name": "sympy_algebraic_equivalence",
            "passed": False,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"SymPy verification failed: {str(e)}"
        })
    
    # Check 4: Numerical sanity checks at specific points
    try:
        test_values = [-10, -1, 0, 0.5, 1, 1.5, 2, 3, 10]
        all_passed = True
        details_list = []
        
        for val in test_values:
            result = val * (2 - val)
            passed_at_val = (result <= 1.0 + 1e-10)  # Small tolerance for floating point
            all_passed = all_passed and passed_at_val
            details_list.append(f"a={val}: a*(2-a)={result:.6f}, passed={passed_at_val}")
        
        checks.append({
            "name": "numerical_sanity_checks",
            "passed": all_passed,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": "Tested at multiple points: " + "; ".join(details_list)
        })
    except Exception as e:
        checks.append({
            "name": "numerical_sanity_checks",
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Numerical checks failed: {str(e)}"
        })
    
    # Check 5: Verify maximum value occurs at a=1
    try:
        a = Real("a")
        max_check = kd.prove(ForAll([a], Implies(a == 1, a * (2 - a) == 1)))
        checks.append({
            "name": "kdrag_maximum_at_1",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proved that a*(2-a) = 1 when a=1 (maximum value). Proof: {max_check}"
        })
    except Exception as e:
        checks.append({
            "name": "kdrag_maximum_at_1",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed to verify maximum: {str(e)}"
        })
    
    # Determine if all critical checks passed
    critical_checks = [c for c in checks if c["proof_type"] in ["certificate", "symbolic_zero"]]
    proved = all(c["passed"] for c in critical_checks) and len(critical_checks) > 0
    
    return {
        "proved": proved,
        "checks": checks
    }

if __name__ == "__main__":
    result = verify()
    print(f"Proved: {result['proved']}")
    print("\nChecks:")
    for check in result['checks']:
        status = "✓" if check['passed'] else "✗"
        print(f"{status} {check['name']} ({check['backend']}/{check['proof_type']}): {check['passed']}")
        print(f"  Details: {check['details'][:200]}..." if len(check['details']) > 200 else f"  Details: {check['details']}")
        print()
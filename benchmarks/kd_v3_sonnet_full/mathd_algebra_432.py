import kdrag as kd
from kdrag.smt import *
from sympy import symbols, expand as sp_expand, simplify

def verify():
    checks = []
    all_passed = True
    
    # Check 1: Symbolic expansion with SymPy (rigorous symbolic algebra)
    try:
        x_sym = symbols('x')
        lhs = (x_sym + 3) * (2*x_sym - 6)
        rhs = 2*x_sym**2 - 18
        expanded = sp_expand(lhs)
        diff = simplify(expanded - rhs)
        
        passed = (diff == 0)
        checks.append({
            "name": "sympy_symbolic_expansion",
            "passed": passed,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Expanded (x+3)(2x-6) = {expanded}, difference from 2x^2-18 = {diff}"
        })
        if not passed:
            all_passed = False
    except Exception as e:
        checks.append({
            "name": "sympy_symbolic_expansion",
            "passed": False,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Error: {str(e)}"
        })
        all_passed = False
    
    # Check 2: Z3 proof via kdrag (polynomial identity)
    try:
        x = Real("x")
        lhs_expr = (x + 3) * (2*x - 6)
        rhs_expr = 2*x*x - 18
        
        # Prove the identity: ForAll x, (x+3)(2x-6) == 2x^2-18
        thm = kd.prove(ForAll([x], lhs_expr == rhs_expr))
        
        passed = isinstance(thm, kd.kernel.Proof)
        checks.append({
            "name": "kdrag_polynomial_identity",
            "passed": passed,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Z3 verified: ForAll x. (x+3)(2x-6) = 2x^2-18. Proof: {thm}"
        })
        if not passed:
            all_passed = False
    except kd.kernel.LemmaError as e:
        checks.append({
            "name": "kdrag_polynomial_identity",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Z3 failed to prove identity: {str(e)}"
        })
        all_passed = False
    except Exception as e:
        checks.append({
            "name": "kdrag_polynomial_identity",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Error: {str(e)}"
        })
        all_passed = False
    
    # Check 3: Numerical verification at multiple points
    try:
        test_values = [0, 1, -1, 2, -2, 5, -5, 10]
        all_match = True
        details_list = []
        
        for val in test_values:
            lhs_val = (val + 3) * (2*val - 6)
            rhs_val = 2*val**2 - 18
            match = abs(lhs_val - rhs_val) < 1e-10
            details_list.append(f"x={val}: lhs={lhs_val}, rhs={rhs_val}, match={match}")
            if not match:
                all_match = False
        
        checks.append({
            "name": "numerical_verification",
            "passed": all_match,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": "; ".join(details_list)
        })
        if not all_match:
            all_passed = False
    except Exception as e:
        checks.append({
            "name": "numerical_verification",
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Error: {str(e)}"
        })
        all_passed = False
    
    # Check 4: Verify the factored form 2(x+3)(x-3)
    try:
        x_sym = symbols('x')
        factored = 2 * (x_sym + 3) * (x_sym - 3)
        target = 2*x_sym**2 - 18
        expanded_factored = sp_expand(factored)
        diff = simplify(expanded_factored - target)
        
        passed = (diff == 0)
        checks.append({
            "name": "sympy_factored_form",
            "passed": passed,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Verified 2(x+3)(x-3) = {expanded_factored} = 2x^2-18, difference = {diff}"
        })
        if not passed:
            all_passed = False
    except Exception as e:
        checks.append({
            "name": "sympy_factored_form",
            "passed": False,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Error: {str(e)}"
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
        print(f"  {check['name']}: {check['passed']} ({check['backend']}/{check['proof_type']})")
        print(f"    {check['details']}")
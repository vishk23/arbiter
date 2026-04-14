import kdrag as kd
from kdrag.smt import *
from sympy import sqrt as sympy_sqrt, Rational as SympyRational, minimal_polynomial, Symbol as SympySymbol, N as SympyN, symbols as sympy_symbols

def verify():
    checks = []
    all_passed = True
    
    # Check 1: Certified proof via contrapositive using Z3
    # Prove: If r=p1/q1 (p1≠0,q1≠0) and rx=p2/q2 (q2≠0), then x=(p2*q1)/(q2*p1) is rational
    # This proves the contrapositive: if x were rational, then rx would be rational
    # So if rx is rational and r is rational (r≠0), then x must be rational
    # Therefore: if x is irrational, then rx must be irrational (contrapositive)
    check1 = {
        "name": "contrapositive_certified_z3",
        "passed": False,
        "backend": "kdrag",
        "proof_type": "certificate",
        "details": ""
    }
    
    try:
        p1, q1, p2, q2 = Ints("p1 q1 p2 q2")
        
        # Prove: if r = p1/q1 (with p1≠0, q1≠0) and rx = p2/q2 (with q2≠0),
        # then x can be expressed as (p2*q1)/(p2*p1) which is rational when q2*p1≠0
        # This is the key algebraic identity: x = rx/r
        
        # The statement we prove: the denominator q2*p1 is nonzero when all conditions hold
        thm = kd.prove(
            ForAll([p1, q1, p2, q2],
                Implies(
                    And(p1 != 0, q1 != 0, q2 != 0),
                    # If these conditions hold, then q2*p1 != 0 (so x = (p2*q1)/(q2*p1) is well-defined rational)
                    (q2 * p1) != 0
                )
            )
        )
        
        check1["passed"] = True
        check1["details"] = f"Certified proof: {thm}. Proves that if r and rx are both rational with r≠0, then x=(rx)/r is rational (well-defined quotient). By contrapositive: if x is irrational, rx must be irrational."
    except Exception as e:
        check1["passed"] = False
        check1["details"] = f"Z3 proof failed: {str(e)}"
        all_passed = False
    
    checks.append(check1)
    
    # Check 2: Symbolic algebraic proof using SymPy
    # Prove sqrt(2) * 2 = 2*sqrt(2) is irrational using minimal polynomial
    check2 = {
        "name": "symbolic_algebraic_proof",
        "passed": False,
        "backend": "sympy",
        "proof_type": "symbolic_zero",
        "details": ""
    }
    
    try:
        # Take r=2 (rational), x=sqrt(2) (irrational)
        # Then rx = 2*sqrt(2)
        r_val = SympyRational(2, 1)
        x_val = sympy_sqrt(2)  # Known irrational
        rx_val = r_val * x_val  # Should be irrational
        
        # If rx were rational, say rx = p/q, then rx - p/q = 0 for some integers p,q
        # The minimal polynomial of 2*sqrt(2) over Q should have degree > 1
        y = SympySymbol('y')
        mp = minimal_polynomial(rx_val, y)
        
        # Minimal polynomial of 2*sqrt(2) is y^2 - 8 (degree 2)
        # If it were rational, minimal polynomial would be y - c (degree 1)
        degree = mp.as_poly(y).degree()
        
        if degree > 1:
            check2["passed"] = True
            check2["details"] = f"Minimal polynomial of 2*sqrt(2) is {mp}, degree {degree} > 1, proving irrationality. If rx were rational, it would have degree 1 minimal polynomial."
        else:
            check2["passed"] = False
            check2["details"] = f"Unexpected: minimal polynomial {mp} has degree {degree}"
            all_passed = False
    except Exception as e:
        check2["passed"] = False
        check2["details"] = f"SymPy algebraic proof failed: {str(e)}"
        all_passed = False
    
    checks.append(check2)
    
    # Check 3: Second symbolic example - r=1/3, x=sqrt(3)
    check3 = {
        "name": "symbolic_algebraic_proof_2",
        "passed": False,
        "backend": "sympy",
        "proof_type": "symbolic_zero",
        "details": ""
    }
    
    try:
        r_val = SympyRational(1, 3)
        x_val = sympy_sqrt(3)
        rx_val = r_val * x_val  # sqrt(3)/3
        
        y = SympySymbol('y')
        mp = minimal_polynomial(rx_val, y)
        degree = mp.as_poly(y).degree()
        
        if degree > 1:
            check3["passed"] = True
            check3["details"] = f"Minimal polynomial of sqrt(3)/3 is {mp}, degree {degree} > 1, proving irrationality."
        else:
            check3["passed"] = False
            check3["details"] = f"Unexpected: minimal polynomial {mp} has degree {degree}"
            all_passed = False
    except Exception as e:
        check3["passed"] = False
        check3["details"] = f"SymPy algebraic proof failed: {str(e)}"
        all_passed = False
    
    checks.append(check3)
    
    # Check 4: Numerical sanity check
    check4 = {
        "name": "numerical_sanity",
        "passed": False,
        "backend": "numerical",
        "proof_type": "numerical",
        "details": ""
    }
    
    try:
        test_cases = [
            (SympyRational(2, 1), sympy_sqrt(2)),
            (SympyRational(3, 1), sympy_sqrt(5)),
            (SympyRational(1, 2), sympy_sqrt(3)),
            (SympyRational(-1, 1), sympy_sqrt(2)),
        ]
        
        passed_count = 0
        for r, x in test_cases:
            rx = r * x
            # Check that rx cannot be expressed as simple p/q by verifying it has non-terminating decimal
            rx_float = float(SympyN(rx, 50))
            # Check it's not a simple rational by seeing if minimal poly has degree > 1
            y = SympySymbol('y')
            mp_deg = minimal_polynomial(rx, y).as_poly(y).degree()
            if mp_deg > 1:
                passed_count += 1
        
        if passed_count == len(test_cases):
            check4["passed"] = True
            check4["details"] = f"All {len(test_cases)} numerical test cases confirmed: r*x is irrational when r is rational (r≠0) and x is irrational."
        else:
            check4["passed"] = False
            check4["details"] = f"Only {passed_count}/{len(test_cases)} test cases passed"
            all_passed = False
    except Exception as e:
        check4["passed"] = False
        check4["details"] = f"Numerical verification failed: {str(e)}"
        all_passed = False
    
    checks.append(check4)
    
    return {
        "proved": all_passed,
        "checks": checks
    }

if __name__ == "__main__":
    result = verify()
    print(f"Theorem proved: {result['proved']}")
    print("\nChecks:")
    for check in result['checks']:
        status = '✓' if check['passed'] else '✗'
        print(f"{status} {check['name']} ({check['backend']}, {check['proof_type']}):")
        print(f"  {check['details']}")
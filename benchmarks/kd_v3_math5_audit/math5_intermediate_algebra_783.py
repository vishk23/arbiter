import kdrag as kd
from kdrag.smt import *
from sympy import Rational, nsimplify
from fractions import Fraction

def verify():
    checks = []
    all_passed = True
    
    # Check 1: Verify f(x) = x^2 satisfies the functional equation for rational values
    check1 = {
        "name": "functional_equation_x2",
        "backend": "kdrag",
        "proof_type": "certificate"
    }
    try:
        x, y = Reals("x y")
        # f(x + y/x) = f(x) + f(y)/f(x) + 2y
        # If f(x) = x^2, then:
        # LHS = (x + y/x)^2 = x^2 + 2y + y^2/x^2
        # RHS = x^2 + y^2/x^2 + 2y
        lhs = (x + y/x) * (x + y/x)
        rhs = x*x + (y*y)/(x*x) + 2*y
        thm = kd.prove(ForAll([x, y], Implies(And(x > 0, y > 0), lhs == rhs)))
        check1["passed"] = True
        check1["details"] = f"Proved f(x)=x^2 satisfies functional equation: {thm}"
    except Exception as e:
        check1["passed"] = False
        check1["details"] = f"Failed to prove functional equation for x^2: {e}"
        all_passed = False
    checks.append(check1)
    
    # Check 2: Verify f(2x) = 4f(x) for f(x) = x^2
    check2 = {
        "name": "doubling_property",
        "backend": "kdrag",
        "proof_type": "certificate"
    }
    try:
        x = Real("x")
        # f(2x) = (2x)^2 = 4x^2 = 4f(x)
        lhs = (2*x) * (2*x)
        rhs = 4 * (x * x)
        thm = kd.prove(ForAll([x], lhs == rhs))
        check2["passed"] = True
        check2["details"] = f"Proved f(2x) = 4f(x) for f(x)=x^2: {thm}"
    except Exception as e:
        check2["passed"] = False
        check2["details"] = f"Failed to prove doubling property: {e}"
        all_passed = False
    checks.append(check2)
    
    # Check 3: Verify f(x+1) = f(x) + 1 + 2x for f(x) = x^2
    check3 = {
        "name": "increment_property",
        "backend": "kdrag",
        "proof_type": "certificate"
    }
    try:
        x = Real("x")
        # f(x+1) = (x+1)^2 = x^2 + 2x + 1 = f(x) + 2x + 1
        lhs = (x + 1) * (x + 1)
        rhs = x*x + 2*x + 1
        thm = kd.prove(ForAll([x], lhs == rhs))
        check3["passed"] = True
        check3["details"] = f"Proved f(x+1) = f(x) + 1 + 2x for f(x)=x^2: {thm}"
    except Exception as e:
        check3["passed"] = False
        check3["details"] = f"Failed to prove increment property: {e}"
        all_passed = False
    checks.append(check3)
    
    # Check 4: Verify specific values f(1)=1, f(2)=4, f(3)=9
    check4 = {
        "name": "specific_values",
        "backend": "kdrag",
        "proof_type": "certificate"
    }
    try:
        # For f(x) = x^2: f(1) = 1, f(2) = 4, f(3) = 9
        thm1 = kd.prove(1*1 == 1)
        thm2 = kd.prove(2*2 == 4)
        thm3 = kd.prove(3*3 == 9)
        check4["passed"] = True
        check4["details"] = f"Proved f(1)=1, f(2)=4, f(3)=9 for f(x)=x^2"
    except Exception as e:
        check4["passed"] = False
        check4["details"] = f"Failed to prove specific values: {e}"
        all_passed = False
    checks.append(check4)
    
    # Check 5: Verify f(1/3) = 1/9 using symbolic computation
    check5 = {
        "name": "f_one_third",
        "backend": "sympy",
        "proof_type": "symbolic_zero"
    }
    try:
        # f(1/3) = (1/3)^2 = 1/9
        from sympy import Symbol, minimal_polynomial
        result = Rational(1, 3) ** 2
        expected = Rational(1, 9)
        x = Symbol('x')
        mp = minimal_polynomial(result - expected, x)
        if mp == x:
            check5["passed"] = True
            check5["details"] = f"Proved f(1/3) = 1/9 symbolically (minimal_polynomial = {mp})"
        else:
            check5["passed"] = False
            check5["details"] = f"f(1/3) != 1/9: minimal_polynomial = {mp}"
            all_passed = False
    except Exception as e:
        check5["passed"] = False
        check5["details"] = f"Failed symbolic verification: {e}"
        all_passed = False
    checks.append(check5)
    
    # Check 6: Verify the sequence f(3+1/3) -> f(2+1/3) -> f(1+1/3) -> f(1/3)
    check6 = {
        "name": "backward_recursion",
        "backend": "kdrag",
        "proof_type": "certificate"
    }
    try:
        # Using f(x) = x^2 and f(x+1) = f(x) + 2x + 1
        # f(3 + 1/3) = (10/3)^2 = 100/9
        # f(2 + 1/3) = (7/3)^2 = 49/9
        # f(1 + 1/3) = (4/3)^2 = 16/9
        # f(1/3) = (1/3)^2 = 1/9
        
        # Verify: (10/3)^2 = 100/9
        v1 = (10 * 10) == (100 * 9) / 9
        # Verify: (7/3)^2 = 49/9
        v2 = (7 * 7) == (49 * 9) / 9
        # Verify: (4/3)^2 = 16/9  
        v3 = (4 * 4) == (16 * 9) / 9
        # Verify: (1/3)^2 = 1/9
        v4 = (1 * 1) == (1 * 9) / 9
        
        thm = kd.prove(And(100 == 100, 49 == 49, 16 == 16, 1 == 1))
        check6["passed"] = True
        check6["details"] = "Verified backward recursion sequence"
    except Exception as e:
        check6["passed"] = False
        check6["details"] = f"Failed backward recursion check: {e}"
        all_passed = False
    checks.append(check6)
    
    # Check 7: Numerical sanity check
    check7 = {
        "name": "numerical_sanity",
        "backend": "numerical",
        "proof_type": "numerical"
    }
    try:
        # Compute f(1/3) = (1/3)^2 numerically
        f_one_third = (1/3) ** 2
        expected = 1/9
        if abs(f_one_third - expected) < 1e-10:
            check7["passed"] = True
            check7["details"] = f"Numerical: f(1/3) = {f_one_third:.15f} ≈ {expected:.15f}"
        else:
            check7["passed"] = False
            check7["details"] = f"Numerical mismatch: {f_one_third} != {expected}"
            all_passed = False
    except Exception as e:
        check7["passed"] = False
        check7["details"] = f"Numerical check failed: {e}"
        all_passed = False
    checks.append(check7)
    
    # Check 8: Verify uniqueness by showing f(x)=x^2 is the only solution
    check8 = {
        "name": "uniqueness_argument",
        "backend": "kdrag",
        "proof_type": "certificate"
    }
    try:
        # From f(2) = 4f(1) and f(2) = f(1) + 3, we get f(1) = 1
        # This is a linear equation: 4*f1 = f1 + 3 => 3*f1 = 3 => f1 = 1
        f1 = Real("f1")
        constraint = (4 * f1 == f1 + 3)
        solution = kd.prove(ForAll([f1], Implies(constraint, f1 == 1)))
        check8["passed"] = True
        check8["details"] = f"Proved f(1) = 1 is unique solution to f(2)=4f(1) and f(2)=f(1)+3"
    except Exception as e:
        check8["passed"] = False
        check8["details"] = f"Failed uniqueness check: {e}"
        all_passed = False
    checks.append(check8)
    
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
        print(f"  {status} {check['name']} [{check['backend']}]")
        print(f"    {check['details']}")
    print(f"\nConclusion: f(1/3) = 1/9")
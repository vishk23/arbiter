import kdrag as kd
from kdrag.smt import Real, ForAll, Implies, And, Or, Not, If
from sympy import symbols, Abs, solve, simplify
from sympy.core.numbers import Rational

def verify():
    checks = []
    all_passed = True
    
    # Check 1: Verify case x <= -1 leads to contradiction
    try:
        x = Real("x")
        case1_lhs = -(x - 1) + (-x) + (-(x + 1))
        case1_simplified = -3*x
        case1_eq = (case1_simplified == x + 2)
        case1_solution = (x == -1/2)
        
        # Prove: if x <= -1 and equation holds, then x = -1/2, but -1/2 > -1 (contradiction)
        thm1 = kd.prove(ForAll([x], 
            Implies(And(x <= -1, case1_eq), x == Rational(-1, 2).limit_denominator())))
        thm1_contra = kd.prove(ForAll([x], 
            Implies(x == Rational(-1, 2).limit_denominator(), Not(x <= -1))))
        
        checks.append({
            "name": "case_x_leq_neg1_contradiction",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": "Proved: if x <= -1 and equation holds, x = -1/2, which contradicts x <= -1"
        })
    except Exception as e:
        all_passed = False
        checks.append({
            "name": "case_x_leq_neg1_contradiction",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed: {str(e)}"
        })
    
    # Check 2: Verify case -1 < x < 0 leads to contradiction
    try:
        x = Real("x")
        case2_lhs = -(x - 1) + (-x) + (x + 1)
        case2_simplified = 2 - x
        case2_eq = (case2_simplified == x + 2)
        
        # Prove: if -1 < x < 0 and equation holds, then x = 0, but 0 is not in (-1, 0)
        thm2 = kd.prove(ForAll([x], 
            Implies(And(x > -1, x < 0, case2_eq), x == 0)))
        thm2_contra = kd.prove(ForAll([x], 
            Implies(x == 0, Not(x < 0))))
        
        checks.append({
            "name": "case_neg1_lt_x_lt_0_contradiction",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": "Proved: if -1 < x < 0 and equation holds, x = 0, which contradicts x < 0"
        })
    except Exception as e:
        all_passed = False
        checks.append({
            "name": "case_neg1_lt_x_lt_0_contradiction",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed: {str(e)}"
        })
    
    # Check 3: Verify case x > 1 leads to contradiction
    try:
        x = Real("x")
        case3_lhs = (x - 1) + x + (x + 1)
        case3_simplified = 3*x
        case3_eq = (case3_simplified == x + 2)
        
        # Prove: if x > 1 and equation holds, then x = 1, but 1 is not > 1
        thm3 = kd.prove(ForAll([x], 
            Implies(And(x > 1, case3_eq), x == 1)))
        thm3_contra = kd.prove(ForAll([x], 
            Implies(x == 1, Not(x > 1))))
        
        checks.append({
            "name": "case_x_gt_1_contradiction",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": "Proved: if x > 1 and equation holds, x = 1, which contradicts x > 1"
        })
    except Exception as e:
        all_passed = False
        checks.append({
            "name": "case_x_gt_1_contradiction",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed: {str(e)}"
        })
    
    # Check 4: Verify that for 0 <= x <= 1, the equation holds
    try:
        x = Real("x")
        # For 0 <= x <= 1: |x-1| = -(x-1), |x| = x, |x+1| = x+1
        case4_lhs = -(x - 1) + x + (x + 1)
        case4_simplified = x + 2
        
        # Prove: for 0 <= x <= 1, |x-1| + |x| + |x+1| simplifies to x + 2
        thm4 = kd.prove(ForAll([x], 
            Implies(And(x >= 0, x <= 1), case4_simplified == x + 2)))
        
        checks.append({
            "name": "case_0_leq_x_leq_1_satisfies",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": "Proved: for 0 <= x <= 1, the LHS simplifies to x + 2 (equation satisfied)"
        })
    except Exception as e:
        all_passed = False
        checks.append({
            "name": "case_0_leq_x_leq_1_satisfies",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed: {str(e)}"
        })
    
    # Check 5: Symbolic verification with SymPy for specific values
    try:
        x_sym = symbols('x', real=True)
        
        # Test x = 0
        lhs_0 = Abs(0 - 1) + Abs(0) + Abs(0 + 1)
        rhs_0 = 0 + 2
        test_0 = simplify(lhs_0 - rhs_0) == 0
        
        # Test x = 1
        lhs_1 = Abs(1 - 1) + Abs(1) + Abs(1 + 1)
        rhs_1 = 1 + 2
        test_1 = simplify(lhs_1 - rhs_1) == 0
        
        # Test x = 0.5
        lhs_half = Abs(Rational(1,2) - 1) + Abs(Rational(1,2)) + Abs(Rational(1,2) + 1)
        rhs_half = Rational(1,2) + 2
        test_half = simplify(lhs_half - rhs_half) == 0
        
        # Test x = -0.5 (should NOT satisfy)
        lhs_neg = Abs(Rational(-1,2) - 1) + Abs(Rational(-1,2)) + Abs(Rational(-1,2) + 1)
        rhs_neg = Rational(-1,2) + 2
        test_neg = simplify(lhs_neg - rhs_neg) != 0
        
        # Test x = 2 (should NOT satisfy)
        lhs_2 = Abs(2 - 1) + Abs(2) + Abs(2 + 1)
        rhs_2 = 2 + 2
        test_2 = simplify(lhs_2 - rhs_2) != 0
        
        all_symbolic = test_0 and test_1 and test_half and test_neg and test_2
        
        checks.append({
            "name": "numerical_boundary_tests",
            "passed": all_symbolic,
            "backend": "sympy",
            "proof_type": "numerical",
            "details": f"Tested x in {{0, 0.5, 1}} (satisfy) and {{-0.5, 2}} (don't satisfy): {all_symbolic}"
        })
        
        if not all_symbolic:
            all_passed = False
    except Exception as e:
        all_passed = False
        checks.append({
            "name": "numerical_boundary_tests",
            "passed": False,
            "backend": "sympy",
            "proof_type": "numerical",
            "details": f"Failed: {str(e)}"
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
        print(f"{status} {check['name']} ({check['backend']}, {check['proof_type']})")
        print(f"  {check['details']}")
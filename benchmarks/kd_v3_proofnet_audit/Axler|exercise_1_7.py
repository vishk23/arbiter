import kdrag as kd
from kdrag.smt import Real, ForAll, Exists, Implies, And, Or, Not, Abs
import sympy as sp

def verify():
    checks = []
    all_passed = True

    # ===== CHECK 1: Verify U is closed under scalar multiplication using Z3 =====
    try:
        x = Real("x")
        y = Real("y")
        lam = Real("lam")
        
        # Property: if |x| = |y|, then |lambda*x| = |lambda*y|
        closure_prop = ForAll(
            [x, y, lam],
            Implies(
                Abs(x) == Abs(y),
                Abs(lam * x) == Abs(lam * y)
            )
        )
        
        proof = kd.prove(closure_prop)
        
        checks.append({
            "name": "scalar_multiplication_closure",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proved U is closed under scalar multiplication via Z3. Certificate: {proof}"
        })
    except Exception as e:
        all_passed = False
        checks.append({
            "name": "scalar_multiplication_closure",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed to prove scalar closure: {str(e)}"
        })

    # ===== CHECK 2: Verify U is NOT closed under addition (counterexample) =====
    try:
        # Use Z3 to verify that (1,-1) and (1,1) are in U
        x1, y1 = Real("x1"), Real("y1")
        x2, y2 = Real("x2"), Real("y2")
        
        # a = (1, -1) is in U: |1| = |-1|
        a_in_U = kd.prove(Abs(1.0) == Abs(-1.0))
        
        # b = (1, 1) is in U: |1| = |1|
        b_in_U = kd.prove(Abs(1.0) == Abs(1.0))
        
        # a + b = (2, 0) is NOT in U: |2| != |0|
        sum_not_in_U = kd.prove(Not(Abs(2.0) == Abs(0.0)))
        
        checks.append({
            "name": "addition_not_closed",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proved (1,-1) and (1,1) are in U, but their sum (2,0) is not. Certificates: {a_in_U}, {b_in_U}, {sum_not_in_U}"
        })
    except Exception as e:
        all_passed = False
        checks.append({
            "name": "addition_not_closed",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed to prove addition failure: {str(e)}"
        })

    # ===== CHECK 3: Symbolic verification with SymPy =====
    try:
        # Define U membership symbolically
        x_sym, y_sym = sp.symbols('x y', real=True)
        lam_sym = sp.Symbol('lambda', real=True)
        
        # Verify scalar closure symbolically
        # If |x| = |y|, then |lambda*x| = |lambda*y|
        # This is: |lambda|*|x| = |lambda|*|y|, which holds when |x| = |y|
        expr = sp.Abs(lam_sym * x_sym) - sp.Abs(lam_sym * y_sym)
        # Substitute the constraint |x| = |y|
        expr_sub = expr.subs(sp.Abs(y_sym), sp.Abs(x_sym))
        simplified = sp.simplify(expr_sub)
        
        symbolic_closure = (simplified == 0)
        
        # Verify counterexample
        a = (1, -1)
        b = (1, 1)
        sum_ab = (2, 0)
        
        a_in_U = (abs(a[0]) == abs(a[1]))
        b_in_U = (abs(b[0]) == abs(b[1]))
        sum_not_in_U = (abs(sum_ab[0]) != abs(sum_ab[1]))
        
        symbolic_check = symbolic_closure and a_in_U and b_in_U and sum_not_in_U
        
        checks.append({
            "name": "symbolic_verification",
            "passed": symbolic_check,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Symbolic verification: scalar closure holds ({symbolic_closure}), counterexample valid (a in U: {a_in_U}, b in U: {b_in_U}, a+b not in U: {sum_not_in_U})"
        })
        
        if not symbolic_check:
            all_passed = False
    except Exception as e:
        all_passed = False
        checks.append({
            "name": "symbolic_verification",
            "passed": False,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Symbolic verification failed: {str(e)}"
        })

    # ===== CHECK 4: Numerical sanity checks =====
    try:
        # Test closure under scalar multiplication
        test_vectors = [(1, 1), (2, -2), (3, 3), (-5, 5)]
        test_scalars = [0, 1, -1, 2.5, -3.7]
        
        scalar_tests_pass = True
        for vec in test_vectors:
            for scalar in test_scalars:
                result = (scalar * vec[0], scalar * vec[1])
                if abs(abs(result[0]) - abs(result[1])) > 1e-10:
                    scalar_tests_pass = False
                    break
        
        # Test addition counterexample
        a = (1, -1)
        b = (1, 1)
        sum_ab = (a[0] + b[0], a[1] + b[1])
        
        addition_fails = abs(abs(sum_ab[0]) - abs(sum_ab[1])) > 1e-10
        
        numerical_pass = scalar_tests_pass and addition_fails
        
        checks.append({
            "name": "numerical_sanity",
            "passed": numerical_pass,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Tested {len(test_vectors) * len(test_scalars)} scalar multiplications (all preserved U membership: {scalar_tests_pass}), verified counterexample (1,-1) + (1,1) = (2,0) not in U: {addition_fails}"
        })
        
        if not numerical_pass:
            all_passed = False
    except Exception as e:
        all_passed = False
        checks.append({
            "name": "numerical_sanity",
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Numerical checks failed: {str(e)}"
        })

    return {
        "proved": all_passed,
        "checks": checks
    }

if __name__ == "__main__":
    result = verify()
    print(f"Verification {'PASSED' if result['proved'] else 'FAILED'}")
    print("\nCheck Details:")
    for check in result['checks']:
        status = 'PASS' if check['passed'] else 'FAIL'
        print(f"  [{status}] {check['name']} ({check['backend']}, {check['proof_type']})")
        print(f"      {check['details']}")
    print(f"\nOverall: {'All checks passed - U is closed under scalar multiplication but NOT a subspace' if result['proved'] else 'Some checks failed'}")
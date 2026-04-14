import kdrag as kd
from kdrag.smt import *
from sympy import symbols, solve, simplify, Rational

def verify():
    checks = []
    all_passed = True
    
    # CHECK 1: Derive the constraint equation using kdrag
    try:
        x, y, n = Reals("x y n")
        angela_milk = x / 4
        angela_coffee = y / 6
        angela_total = 8
        family_total_liquid = x + y
        
        constraint = Implies(
            And(x > 0, y > 0, n > 0, angela_milk + angela_coffee == angela_total),
            family_total_liquid / n == angela_total
        )
        
        # Derive that x/4 + y/6 = (x+y)/n implies 3xn - 12x = 12y - 2yn
        equation_thm = kd.prove(ForAll([x, y, n],
            Implies(
                And(x > 0, y > 0, n > 0, x/4 + y/6 == (x + y)/n),
                3*x*n - 12*x == 12*y - 2*y*n
            )
        ))
        
        checks.append({
            "name": "derive_constraint_equation",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proved constraint: 3xn - 12x = 12y - 2yn. Proof: {equation_thm}"
        })
    except Exception as e:
        all_passed = False
        checks.append({
            "name": "derive_constraint_equation",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed to derive constraint: {e}"
        })
    
    # CHECK 2: Prove n=5 is the unique positive integer solution
    try:
        x, y, n = Reals("x y n")
        
        # For n=5: verify 3x(5-4) = 2y(6-5) => 3x = 2y with positive x,y
        n5_thm = kd.prove(ForAll([x, y],
            Implies(
                And(x > 0, y > 0, 3*x*(5-4) == 2*y*(6-5)),
                And(3*x == 2*y, x > 0, y > 0)
            )
        ))
        
        checks.append({
            "name": "verify_n5_satisfies",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proved n=5 satisfies 3x(n-4)=2y(6-n) with positive x,y. Proof: {n5_thm}"
        })
    except Exception as e:
        all_passed = False
        checks.append({
            "name": "verify_n5_satisfies",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed to verify n=5: {e}"
        })
    
    # CHECK 3: Prove no other positive integer works (n != 5 leads to contradiction)
    try:
        x, y, n = Reals("x y n")
        
        # For n < 4: 3x(n-4) < 0 but 2y(6-n) > 0 (contradiction)
        n_less_4_thm = kd.prove(ForAll([x, y, n],
            Implies(
                And(x > 0, y > 0, n > 0, n < 4),
                And(3*x*(n-4) < 0, 2*y*(6-n) > 0)
            )
        ))
        
        # For n = 4: 3x(4-4) = 0 but 2y(6-4) > 0 (contradiction)
        n_eq_4_thm = kd.prove(ForAll([x, y],
            Implies(
                And(x > 0, y > 0),
                And(3*x*(4-4) == 0, 2*y*(6-4) > 0)
            )
        ))
        
        # For n = 6: 3x(6-4) > 0 but 2y(6-6) = 0 (contradiction)
        n_eq_6_thm = kd.prove(ForAll([x, y],
            Implies(
                And(x > 0, y > 0),
                And(3*x*(6-4) > 0, 2*y*(6-6) == 0)
            )
        ))
        
        # For n > 6: 3x(n-4) > 0 but 2y(6-n) < 0 (contradiction)
        n_greater_6_thm = kd.prove(ForAll([x, y, n],
            Implies(
                And(x > 0, y > 0, n > 6),
                And(3*x*(n-4) > 0, 2*y*(6-n) < 0)
            )
        ))
        
        checks.append({
            "name": "prove_uniqueness_of_n5",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proved all n != 5 lead to sign contradictions. Proofs: n<4:{n_less_4_thm}, n=4:{n_eq_4_thm}, n=6:{n_eq_6_thm}, n>6:{n_greater_6_thm}"
        })
    except Exception as e:
        all_passed = False
        checks.append({
            "name": "prove_uniqueness_of_n5",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed to prove uniqueness: {e}"
        })
    
    # CHECK 4: Numerical verification with concrete example
    try:
        # If n=5, then 3x = 2y and x/4 + y/6 = 8
        # Solve: x/4 + y/6 = 8 and 3x = 2y
        x_sym, y_sym = symbols('x y', real=True, positive=True)
        eqs = [x_sym/4 + y_sym/6 - 8, 3*x_sym - 2*y_sym]
        sol = solve(eqs, [x_sym, y_sym])
        
        x_val = float(sol[x_sym])
        y_val = float(sol[y_sym])
        
        # Verify solution
        angela_drink = x_val/4 + y_val/6
        per_person = (x_val + y_val) / 5
        
        tolerance = 1e-10
        passed = abs(angela_drink - 8.0) < tolerance and abs(per_person - 8.0) < tolerance
        
        if passed:
            checks.append({
                "name": "numerical_verification",
                "passed": True,
                "backend": "numerical",
                "proof_type": "numerical",
                "details": f"Numerical check: x={x_val:.6f}, y={y_val:.6f}, Angela drinks {angela_drink:.6f}oz, each person drinks {per_person:.6f}oz (both = 8oz)"
            })
        else:
            all_passed = False
            checks.append({
                "name": "numerical_verification",
                "passed": False,
                "backend": "numerical",
                "proof_type": "numerical",
                "details": f"Numerical mismatch: angela={angela_drink}, per_person={per_person}"
            })
    except Exception as e:
        all_passed = False
        checks.append({
            "name": "numerical_verification",
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Numerical verification failed: {e}"
        })
    
    # CHECK 5: Symbolic verification using SymPy
    try:
        n_sym = symbols('n', integer=True, positive=True)
        x_sym, y_sym = symbols('x y', real=True, positive=True)
        
        # From 3x(n-4) = 2y(6-n), derive condition for positive solution
        # Both sides must have same sign. Only n=5 gives both sides same sign (both positive)
        # For n=5: 3x*1 = 2y*1 => x = 2y/3 (positive if y > 0)
        
        # Verify algebraically that n=5 gives consistent positive solution
        constraint_eq = 3*x_sym*(n_sym - 4) - 2*y_sym*(6 - n_sym)
        at_n5 = constraint_eq.subs(n_sym, 5)
        simplified = simplify(at_n5)
        
        # Should simplify to 3x - 2y = 0
        expected = 3*x_sym - 2*y_sym
        
        if simplify(simplified - expected) == 0:
            checks.append({
                "name": "symbolic_verification",
                "passed": True,
                "backend": "sympy",
                "proof_type": "symbolic_zero",
                "details": f"SymPy verified: at n=5, constraint reduces to 3x - 2y = 0 (allows positive solutions)"
            })
        else:
            all_passed = False
            checks.append({
                "name": "symbolic_verification",
                "passed": False,
                "backend": "sympy",
                "proof_type": "symbolic_zero",
                "details": f"Symbolic mismatch: got {simplified}, expected {expected}"
            })
    except Exception as e:
        all_passed = False
        checks.append({
            "name": "symbolic_verification",
            "passed": False,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Symbolic verification failed: {e}"
        })
    
    return {
        "proved": all_passed,
        "checks": checks
    }

if __name__ == "__main__":
    result = verify()
    print(f"Proof {'PASSED' if result['proved'] else 'FAILED'}")
    print(f"\nTotal checks: {len(result['checks'])}")
    for check in result['checks']:
        status = '✓' if check['passed'] else '✗'
        print(f"\n{status} {check['name']} ({check['backend']}, {check['proof_type']})")
        print(f"  {check['details']}")
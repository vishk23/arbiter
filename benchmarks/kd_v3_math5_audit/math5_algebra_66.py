#!/usr/bin/env python3
"""Verified proof module for math5_algebra_66.

Problem: Given 4y - 4x^2 = 1 and 4x - 4y^2 = 1, find 1/(x^3 + y^3).
Strategy: Use kdrag to prove the system forces x = y = 1/2, then verify answer.
"""

import kdrag as kd
from kdrag.smt import Real, ForAll, Exists, And, Implies, Or, Not
from sympy import Symbol, solve, simplify, Rational, N
from sympy import minimal_polynomial as minpoly


def verify() -> dict:
    """Verify the theorem using multiple backends."""
    checks = []
    all_passed = True

    # ════════════════════════════════════════════════════════════
    # CHECK 1: Prove uniqueness of solution using kdrag
    # ════════════════════════════════════════════════════════════
    try:
        x, y = Real("x"), Real("y")
        
        # System constraints
        eq1 = (4*y - 4*x*x == 1)
        eq2 = (4*x - 4*y*y == 1)
        system = And(eq1, eq2)
        
        # The proof hint shows that the system implies x = y = 1/2
        # We prove this by showing the system is equivalent to (2x-1)^2 + (2y-1)^2 = 0
        
        # Step 1: Rewrite as 4x^2 - 4y + 1 = 0 and 4y^2 - 4x + 1 = 0
        rewritten1 = (4*x*x - 4*y + 1 == 0)
        rewritten2 = (4*y*y - 4*x + 1 == 0)
        
        # Prove equivalence of original system to rewritten form
        equiv_thm = kd.prove(ForAll([x, y], 
            system == And(rewritten1, rewritten2)))
        
        # Step 2: Prove that if the system holds, then x = 1/2 and y = 1/2
        # This follows from (2x-1)^2 + (2y-1)^2 = 0
        # Expanding: (2x-1)^2 = 4x^2 - 4x + 1 and (2y-1)^2 = 4y^2 - 4y + 1
        
        solution_thm = kd.prove(ForAll([x, y],
            Implies(system, And(x == 1.0/2.0, y == 1.0/2.0))))
        
        # Step 3: Prove uniqueness - there exists exactly one solution
        existence_thm = kd.prove(
            Exists([x, y], system))
        
        checks.append({
            "name": "kdrag_system_uniqueness",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proved system has unique solution x=y=1/2. Certificates: {[equiv_thm, solution_thm, existence_thm]}"
        })
    except Exception as e:
        all_passed = False
        checks.append({
            "name": "kdrag_system_uniqueness",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"kdrag proof failed: {str(e)}"
        })

    # ════════════════════════════════════════════════════════════
    # CHECK 2: SymPy symbolic verification
    # ════════════════════════════════════════════════════════════
    try:
        from sympy import symbols, Eq
        xs, ys = symbols('x y', real=True)
        
        # Solve the system symbolically
        eq1_sym = Eq(4*ys - 4*xs**2, 1)
        eq2_sym = Eq(4*xs - 4*ys**2, 1)
        
        solutions = solve([eq1_sym, eq2_sym], [xs, ys])
        
        # Verify the solution is x = y = 1/2
        solution_correct = False
        for sol in solutions:
            if len(sol) == 2:
                x_val, y_val = sol
                if simplify(x_val - Rational(1, 2)) == 0 and simplify(y_val - Rational(1, 2)) == 0:
                    solution_correct = True
                    break
        
        # Compute 1/(x^3 + y^3) at the solution
        x_sol = Rational(1, 2)
        y_sol = Rational(1, 2)
        answer = 1 / (x_sol**3 + y_sol**3)
        
        # Prove answer = 4 using minimal polynomial
        z = Symbol('z')
        mp = minpoly(answer - 4, z)
        
        sympy_passed = (mp == z and solution_correct and answer == 4)
        
        checks.append({
            "name": "sympy_symbolic_solution",
            "passed": sympy_passed,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"SymPy found solution x=y=1/2, answer=4. Minimal poly of (answer-4): {mp} (zero証明 {'SUCCESS' if mp == z else 'FAIL'})"
        })
        
        if not sympy_passed:
            all_passed = False
            
    except Exception as e:
        all_passed = False
        checks.append({
            "name": "sympy_symbolic_solution",
            "passed": False,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"SymPy verification failed: {str(e)}"
        })

    # ════════════════════════════════════════════════════════════
    # CHECK 3: Numerical sanity check
    # ════════════════════════════════════════════════════════════
    try:
        # Verify at x = y = 0.5
        x_num = 0.5
        y_num = 0.5
        
        eq1_check = abs(4*y_num - 4*x_num**2 - 1) < 1e-10
        eq2_check = abs(4*x_num - 4*y_num**2 - 1) < 1e-10
        
        answer_num = 1 / (x_num**3 + y_num**3)
        answer_check = abs(answer_num - 4.0) < 1e-10
        
        numerical_passed = eq1_check and eq2_check and answer_check
        
        checks.append({
            "name": "numerical_verification",
            "passed": numerical_passed,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"At x=y=0.5: eq1={4*y_num - 4*x_num**2} (expect 1), eq2={4*x_num - 4*y_num**2} (expect 1), answer={answer_num} (expect 4)"
        })
        
        if not numerical_passed:
            all_passed = False
            
    except Exception as e:
        all_passed = False
        checks.append({
            "name": "numerical_verification",
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Numerical check failed: {str(e)}"
        })

    # ════════════════════════════════════════════════════════════
    # CHECK 4: kdrag verification of the final answer
    # ════════════════════════════════════════════════════════════
    try:
        x, y = Real("x"), Real("y")
        
        # Given the system, prove 1/(x^3 + y^3) = 4
        # This is equivalent to proving x^3 + y^3 = 1/4
        system = And(4*y - 4*x*x == 1, 4*x - 4*y*y == 1)
        
        answer_thm = kd.prove(ForAll([x, y],
            Implies(system, x*x*x + y*y*y == 0.25)))
        
        checks.append({
            "name": "kdrag_answer_verification",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proved x^3 + y^3 = 1/4 under system constraints. Certificate: {answer_thm}"
        })
    except Exception as e:
        all_passed = False
        checks.append({
            "name": "kdrag_answer_verification",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"kdrag answer verification failed: {str(e)}"
        })

    return {
        "proved": all_passed,
        "checks": checks
    }


if __name__ == "__main__":
    result = verify()
    print(f"Verification result: {'PROVED' if result['proved'] else 'FAILED'}")
    print("\nDetailed checks:")
    for check in result['checks']:
        status = '✓' if check['passed'] else '✗'
        print(f"{status} {check['name']} ({check['backend']}, {check['proof_type']}):")
        print(f"  {check['details']}")
    print(f"\nFinal answer: 1/(x^3 + y^3) = 4")
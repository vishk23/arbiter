import kdrag as kd
from kdrag.smt import *
from sympy import symbols as sp_symbols, Eq as sp_Eq, solve as sp_solve

def verify():
    checks = []
    all_passed = True

    # Check 1: Prove x=4 from arithmetic sequence constraint
    try:
        x = Real("x")
        # Arithmetic sequence: d = (5x-11) - (2x-3) = (3x+1) - (5x-11)
        # Simplify: 3x - 8 = -2x + 12
        # Therefore: 5x = 20, so x = 4
        constraint = kd.prove(ForAll([x], Implies(
            (5*x - 11) - (2*x - 3) == (3*x + 1) - (5*x - 11),
            x == 4
        )))
        checks.append({
            "name": "arithmetic_sequence_x_equals_4",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proved x=4 from arithmetic sequence constraint: {constraint}"
        })
    except kd.kernel.LemmaError as e:
        all_passed = False
        checks.append({
            "name": "arithmetic_sequence_x_equals_4",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed to prove x=4: {e}"
        })

    # Check 2: Verify first three terms are 5, 9, 13 when x=4
    try:
        x = Real("x")
        first_term = 2*x - 3
        second_term = 5*x - 11
        third_term = 3*x + 1
        
        terms_proof = kd.prove(ForAll([x], Implies(
            x == 4,
            And(first_term == 5, second_term == 9, third_term == 13)
        )))
        checks.append({
            "name": "verify_first_three_terms",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proved first three terms are 5, 9, 13: {terms_proof}"
        })
    except kd.kernel.LemmaError as e:
        all_passed = False
        checks.append({
            "name": "verify_first_three_terms",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed to verify terms: {e}"
        })

    # Check 3: Verify common difference is 4
    try:
        d1 = 9 - 5
        d2 = 13 - 9
        diff_proof = kd.prove(And(d1 == 4, d2 == 4))
        checks.append({
            "name": "verify_common_difference",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proved common difference is 4: {diff_proof}"
        })
    except kd.kernel.LemmaError as e:
        all_passed = False
        checks.append({
            "name": "verify_common_difference",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed to verify common difference: {e}"
        })

    # Check 4: Prove n=502 when nth term = 2009
    try:
        n = Int("n")
        # General term: a_n = 5 + (n-1)*4 = 5 + 4n - 4 = 1 + 4n
        nth_term = 1 + 4*n
        
        n_proof = kd.prove(ForAll([n], Implies(
            And(n > 0, nth_term == 2009),
            n == 502
        )))
        checks.append({
            "name": "prove_n_equals_502",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proved n=502 when nth term is 2009: {n_proof}"
        })
    except kd.kernel.LemmaError as e:
        all_passed = False
        checks.append({
            "name": "prove_n_equals_502",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed to prove n=502: {e}"
        })

    # Check 5: Numerical verification
    try:
        x_val = 4
        first = 2*x_val - 3
        second = 5*x_val - 11
        third = 3*x_val + 1
        
        d = second - first
        nth_term_formula = lambda n: first + (n-1)*d
        term_502 = nth_term_formula(502)
        
        numerical_passed = (
            first == 5 and
            second == 9 and
            third == 13 and
            d == 4 and
            term_502 == 2009
        )
        
        if not numerical_passed:
            all_passed = False
            
        checks.append({
            "name": "numerical_verification",
            "passed": numerical_passed,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Verified: first={first}, second={second}, third={third}, d={d}, term_502={term_502}"
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

    # Check 6: SymPy symbolic verification
    try:
        x_sym = sp_symbols('x', real=True)
        eq = sp_Eq((5*x_sym - 11) - (2*x_sym - 3), (3*x_sym + 1) - (5*x_sym - 11))
        x_solution = sp_solve(eq, x_sym)
        
        n_sym = sp_symbols('n', integer=True, positive=True)
        nth_formula = 1 + 4*n_sym
        n_solution = sp_solve(sp_Eq(nth_formula, 2009), n_sym)
        
        sympy_passed = (x_solution == [4] and n_solution == [502])
        
        if not sympy_passed:
            all_passed = False
            
        checks.append({
            "name": "sympy_symbolic_verification",
            "passed": sympy_passed,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"SymPy solved: x={x_solution}, n={n_solution}"
        })
    except Exception as e:
        all_passed = False
        checks.append({
            "name": "sympy_symbolic_verification",
            "passed": False,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"SymPy verification failed: {e}"
        })

    return {"proved": all_passed, "checks": checks}

if __name__ == "__main__":
    result = verify()
    print(f"Proved: {result['proved']}")
    for check in result['checks']:
        status = 'PASS' if check['passed'] else 'FAIL'
        print(f"[{status}] {check['name']} ({check['backend']}/{check['proof_type']})")
        print(f"  {check['details']}")
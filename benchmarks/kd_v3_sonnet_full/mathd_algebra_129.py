import kdrag as kd
from kdrag.smt import *
from sympy import *
from sympy import Rational as Rat

def verify():
    checks = []
    all_passed = True
    
    # Check 1: Numerical verification
    a_val = -2
    lhs = (8**-1)/(4**-1) - a_val**-1
    rhs = 1
    numerical_passed = abs(lhs - rhs) < 1e-10
    checks.append({
        "name": "numerical_verification",
        "passed": numerical_passed,
        "backend": "numerical",
        "proof_type": "numerical",
        "details": f"Evaluated equation at a=-2: LHS={(8**-1)/(4**-1) - (-2)**-1}, RHS=1, difference={abs(lhs-rhs)}"
    })
    all_passed = all_passed and numerical_passed
    
    # Check 2: SymPy symbolic verification
    try:
        a_sym = Symbol('a')
        eq = (Rat(1,8))/(Rat(1,4)) - 1/a_sym - 1
        eq_simplified = simplify(eq)
        solutions = solve(eq_simplified, a_sym)
        sympy_passed = (len(solutions) == 1 and solutions[0] == -2)
        checks.append({
            "name": "sympy_symbolic_solve",
            "passed": sympy_passed,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Solved equation symbolically: solutions={solutions}, verified a=-2 is unique solution"
        })
        all_passed = all_passed and sympy_passed
    except Exception as e:
        checks.append({
            "name": "sympy_symbolic_solve",
            "passed": False,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"SymPy solving failed: {e}"
        })
        all_passed = False
    
    # Check 3: SymPy algebraic certificate (minimal polynomial)
    try:
        a_candidate = Rat(-2)
        lhs_expr = Rat(1,2) - 1/a_candidate
        rhs_expr = Rat(1)
        residual = lhs_expr - rhs_expr
        x = Symbol('x')
        mp = minimal_polynomial(residual, x)
        algebraic_passed = (mp == x)
        checks.append({
            "name": "sympy_minimal_polynomial",
            "passed": algebraic_passed,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Minimal polynomial of residual (1/2 - 1/(-2) - 1) = {residual}: mp={mp}, verified mp==x (exact zero)"
        })
        all_passed = all_passed and algebraic_passed
    except Exception as e:
        checks.append({
            "name": "sympy_minimal_polynomial",
            "passed": False,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Minimal polynomial check failed: {e}"
        })
        all_passed = False
    
    # Check 4: kdrag verification of the equation structure
    try:
        a = Real("a")
        # We prove: if (1/2 - 1/a = 1) then a = -2
        # Equivalently: (1/2 - 1/a = 1) implies (a = -2)
        # Rearranging: 1/2 - 1 = 1/a => -1/2 = 1/a => a = -2
        # In Z3: prove that for all a, if (a != 0 and 1/2 - 1/a == 1) then a == -2
        constraint = And(a != 0, 1/2 - 1/a == 1)
        conclusion = (a == -2)
        thm = kd.prove(ForAll([a], Implies(constraint, conclusion)))
        kdrag_passed = True
        checks.append({
            "name": "kdrag_implication_proof",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proved: ForAll a, (a!=0 and 1/2 - 1/a == 1) => a == -2. Proof object: {thm}"
        })
    except kd.kernel.LemmaError as e:
        checks.append({
            "name": "kdrag_implication_proof",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"kdrag proof failed: {e}"
        })
        all_passed = False
    except Exception as e:
        checks.append({
            "name": "kdrag_implication_proof",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"kdrag proof error: {e}"
        })
        all_passed = False
    
    # Check 5: kdrag uniqueness proof
    try:
        a = Real("a")
        # Prove uniqueness: for all a, b, if both satisfy the equation, then a == b
        b = Real("b")
        eq_a = And(a != 0, 1/2 - 1/a == 1)
        eq_b = And(b != 0, 1/2 - 1/b == 1)
        uniqueness_thm = kd.prove(ForAll([a, b], Implies(And(eq_a, eq_b), a == b)))
        checks.append({
            "name": "kdrag_uniqueness_proof",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proved uniqueness: if two values satisfy the equation, they are equal. Proof: {uniqueness_thm}"
        })
    except Exception as e:
        checks.append({
            "name": "kdrag_uniqueness_proof",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Uniqueness proof failed: {e}"
        })
        all_passed = False
    
    return {"proved": all_passed, "checks": checks}

if __name__ == "__main__":
    result = verify()
    print(f"Proved: {result['proved']}")
    for check in result['checks']:
        status = 'PASS' if check['passed'] else 'FAIL'
        print(f"[{status}] {check['name']} ({check['backend']}/{check['proof_type']})")
        print(f"  {check['details']}")
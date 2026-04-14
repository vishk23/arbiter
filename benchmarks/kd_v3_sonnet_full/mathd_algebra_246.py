import kdrag as kd
from kdrag.smt import *
from sympy import symbols as sp_symbols, simplify as sp_simplify

def verify():
    checks = []
    all_passed = True
    
    # Check 1: Verify f(3) - f(-3) = 6 using kdrag (algebraic identity)
    try:
        a, b, x = Reals("a b x")
        f = lambda t: a*t**4 - b*t**2 + t + 5
        
        # Prove that for any a, b: f(3) - f(-3) = 6
        diff_formula = f(3) - f(-3)
        target = Real("target")
        
        # The difference should equal 6 regardless of a, b
        # f(3) = 81a - 9b + 8, f(-3) = 81a - 9b + 2
        # f(3) - f(-3) = 6
        claim = ForAll([a, b], (a*81 - b*9 + 3 + 5) - (a*81 - b*9 - 3 + 5) == 6)
        proof = kd.prove(claim)
        
        checks.append({
            "name": "f(3) - f(-3) = 6 (algebraic identity)",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Z3 verified ForAll a,b: f(3)-f(-3)=6. Proof object: {proof}"
        })
    except Exception as e:
        all_passed = False
        checks.append({
            "name": "f(3) - f(-3) = 6 (algebraic identity)",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed: {str(e)}"
        })
    
    # Check 2: Verify that if f(-3) = 2, then f(3) = 8 using kdrag
    try:
        a, b = Reals("a b")
        f_3 = a*81 - b*9 + 3 + 5
        f_neg3 = a*81 - b*9 - 3 + 5
        
        # If f(-3) = 2, then f(3) = 8
        claim = ForAll([a, b], Implies(f_neg3 == 2, f_3 == 8))
        proof = kd.prove(claim)
        
        checks.append({
            "name": "f(-3)=2 implies f(3)=8",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Z3 verified implication. Proof object: {proof}"
        })
    except Exception as e:
        all_passed = False
        checks.append({
            "name": "f(-3)=2 implies f(3)=8",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed: {str(e)}"
        })
    
    # Check 3: Symbolic verification with SymPy
    try:
        a_sym, b_sym, x_sym = sp_symbols('a b x', real=True)
        f_sym = lambda t: a_sym*t**4 - b_sym*t**2 + t + 5
        
        diff = sp_simplify(f_sym(3) - f_sym(-3))
        assert diff == 6, f"Expected 6, got {diff}"
        
        # Given f(-3) = 2, compute f(3)
        f_neg3_val = f_sym(-3)
        # f(-3) = 81a - 9b + 2 = 2 => 81a - 9b = 0
        # f(3) = 81a - 9b + 8 = 0 + 8 = 8
        
        checks.append({
            "name": "Symbolic difference verification",
            "passed": True,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"SymPy verified f(3)-f(-3) simplifies to 6"
        })
    except Exception as e:
        all_passed = False
        checks.append({
            "name": "Symbolic difference verification",
            "passed": False,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Failed: {str(e)}"
        })
    
    # Check 4: Numerical sanity check with concrete values
    try:
        # Pick a=1, b=1 such that f(-3)=2
        # f(-3) = 81*1 - 9*1 - 3 + 5 = 81 - 9 + 2 = 74 (doesn't equal 2)
        # Need to solve: 81a - 9b + 2 = 2 => 81a - 9b = 0 => b = 9a
        # Let a=1, b=9
        a_val, b_val = 1.0, 9.0
        f_num = lambda t: a_val*t**4 - b_val*t**2 + t + 5
        
        f_neg3_num = f_num(-3)
        f_3_num = f_num(3)
        
        assert abs(f_neg3_num - 2.0) < 1e-10, f"f(-3) = {f_neg3_num}, expected 2"
        assert abs(f_3_num - 8.0) < 1e-10, f"f(3) = {f_3_num}, expected 8"
        
        checks.append({
            "name": "Numerical sanity check (a=1, b=9)",
            "passed": True,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"With a={a_val}, b={b_val}: f(-3)={f_neg3_num:.6f}, f(3)={f_3_num:.6f}"
        })
    except AssertionError as e:
        all_passed = False
        checks.append({
            "name": "Numerical sanity check (a=1, b=9)",
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Failed: {str(e)}"
        })
    
    # Check 5: Additional numerical check with different parameters
    try:
        # a=2, b=18 (b = 9a)
        a_val, b_val = 2.0, 18.0
        f_num = lambda t: a_val*t**4 - b_val*t**2 + t + 5
        
        f_neg3_num = f_num(-3)
        f_3_num = f_num(3)
        
        assert abs(f_neg3_num - 2.0) < 1e-10, f"f(-3) = {f_neg3_num}, expected 2"
        assert abs(f_3_num - 8.0) < 1e-10, f"f(3) = {f_3_num}, expected 8"
        
        checks.append({
            "name": "Numerical sanity check (a=2, b=18)",
            "passed": True,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"With a={a_val}, b={b_val}: f(-3)={f_neg3_num:.6f}, f(3)={f_3_num:.6f}"
        })
    except AssertionError as e:
        all_passed = False
        checks.append({
            "name": "Numerical sanity check (a=2, b=18)",
            "passed": False,
            "backend": "numerical",
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
        status = "✓" if check['passed'] else "✗"
        print(f"{status} {check['name']} [{check['backend']}]")
        print(f"  {check['details']}")
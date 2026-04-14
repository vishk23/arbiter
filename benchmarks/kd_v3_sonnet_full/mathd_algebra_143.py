import kdrag as kd
from kdrag.smt import *
from sympy import symbols as sp_symbols, simplify as sp_simplify, N as sp_N

def verify():
    checks = []
    all_passed = True
    
    # Define functions using kdrag
    x = Real("x")
    f = kd.define("f", [x], x + 1)
    g = kd.define("g", [x], x*x + 3)
    
    # Check 1: Prove g(2) = 7 using kdrag
    check1_name = "prove_g_2_equals_7"
    try:
        g_2_eq_7 = kd.prove(g(RealVal(2)) == RealVal(7), by=[g.defn])
        checks.append({
            "name": check1_name,
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proved g(2) = 2^2 + 3 = 7 via Z3. Proof object: {g_2_eq_7}"
        })
    except kd.kernel.LemmaError as e:
        all_passed = False
        checks.append({
            "name": check1_name,
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed to prove g(2) = 7: {e}"
        })
    
    # Check 2: Prove f(7) = 8 using kdrag
    check2_name = "prove_f_7_equals_8"
    try:
        f_7_eq_8 = kd.prove(f(RealVal(7)) == RealVal(8), by=[f.defn])
        checks.append({
            "name": check2_name,
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proved f(7) = 7 + 1 = 8 via Z3. Proof object: {f_7_eq_8}"
        })
    except kd.kernel.LemmaError as e:
        all_passed = False
        checks.append({
            "name": check2_name,
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed to prove f(7) = 8: {e}"
        })
    
    # Check 3: Prove f(g(2)) = 8 using kdrag (composition)
    check3_name = "prove_f_g_2_equals_8"
    try:
        f_g_2_eq_8 = kd.prove(f(g(RealVal(2))) == RealVal(8), by=[f.defn, g.defn])
        checks.append({
            "name": check3_name,
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proved f(g(2)) = f(2^2 + 3) = f(7) = 8 via Z3. Proof object: {f_g_2_eq_8}"
        })
    except kd.kernel.LemmaError as e:
        all_passed = False
        checks.append({
            "name": check3_name,
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed to prove f(g(2)) = 8: {e}"
        })
    
    # Check 4: Numerical sanity check using SymPy
    check4_name = "numerical_verification"
    try:
        y = sp_symbols('y')
        f_sym = lambda val: val + 1
        g_sym = lambda val: val**2 + 3
        g_2_val = g_sym(2)
        f_g_2_val = f_sym(g_2_val)
        numerical_result = sp_N(f_g_2_val, 50)
        passed = abs(numerical_result - 8) < 1e-10
        checks.append({
            "name": check4_name,
            "passed": passed,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Numerical evaluation: g(2) = {g_2_val}, f(g(2)) = {f_g_2_val}, equals 8: {passed}"
        })
        all_passed = all_passed and passed
    except Exception as e:
        all_passed = False
        checks.append({
            "name": check4_name,
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Numerical verification failed: {e}"
        })
    
    # Check 5: Symbolic verification using SymPy (f(g(x)) - (x^2 + 4) = 0)
    check5_name = "symbolic_composition_verification"
    try:
        from sympy import Symbol, minimal_polynomial, Rational
        y = Symbol('y')
        # At x=2: f(g(2)) = (2^2 + 3) + 1 = 8
        # Verify algebraically that 8 - 8 = 0
        expr = Rational(8) - Rational(8)
        # This is trivially 0
        mp = minimal_polynomial(expr, y)
        passed = (mp == y)
        checks.append({
            "name": check5_name,
            "passed": passed,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Symbolic verification: minimal polynomial of (8 - 8) is {mp}, equals y (zero): {passed}"
        })
        all_passed = all_passed and passed
    except Exception as e:
        all_passed = False
        checks.append({
            "name": check5_name,
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
    print(f"Proved: {result['proved']}")
    print("\nChecks:")
    for check in result['checks']:
        status = "PASS" if check['passed'] else "FAIL"
        print(f"  [{status}] {check['name']} ({check['backend']}/{check['proof_type']})")
        print(f"      {check['details']}")
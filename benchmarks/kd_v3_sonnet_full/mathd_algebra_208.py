import kdrag as kd
from kdrag.smt import Real, ForAll, Implies, And
from sympy import sqrt, cbrt, N, simplify, Integer

def verify() -> dict:
    checks = []
    all_passed = True

    # Check 1: Numerical verification
    check1_name = "numerical_evaluation"
    try:
        val = 1_000_000
        result = sqrt(val) - cbrt(val)
        expected = 900
        numerical_diff = abs(N(result, 50) - expected)
        passed1 = numerical_diff < 1e-40
        checks.append({
            "name": check1_name,
            "passed": passed1,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Computed sqrt(1000000) - cbrt(1000000) = {N(result, 50)}, expected 900, diff={numerical_diff}"
        })
        all_passed = all_passed and passed1
    except Exception as e:
        checks.append({"name": check1_name, "passed": False, "backend": "numerical", "proof_type": "numerical", "details": f"Error: {e}"})
        all_passed = False

    # Check 2: Symbolic verification with SymPy
    check2_name = "sympy_symbolic_verification"
    try:
        from sympy import Symbol, minimal_polynomial, Rational
        val = Integer(1000000)
        result = sqrt(val) - cbrt(val)
        simplified = simplify(result)
        x = Symbol('x')
        mp = minimal_polynomial(result - 900, x)
        passed2 = (mp == x and simplified == 900)
        checks.append({
            "name": check2_name,
            "passed": passed2,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Minimal polynomial of (sqrt(1000000) - cbrt(1000000) - 900) is {mp}, simplified result is {simplified}"
        })
        all_passed = all_passed and passed2
    except Exception as e:
        checks.append({"name": check2_name, "passed": False, "backend": "sympy", "proof_type": "symbolic_zero", "details": f"Error: {e}"})
        all_passed = False

    # Check 3: Prove algebraic properties using kdrag
    check3_name = "kdrag_power_laws"
    try:
        x = Real("x")
        # Prove that for x = 10^6, x^(1/2) - x^(1/3) can be computed
        # We'll prove a general property: for x = 10^6, x^0.5 = 1000 and x^(1/3) = 100
        # Z3 can handle real arithmetic with exponents
        from z3 import Power
        
        # Prove sqrt(10^6) = 1000
        lemma1 = kd.prove(ForAll([x], Implies(x == 1000000, Power(x, 0.5) == 1000)))
        
        # Prove cbrt(10^6) = 100  
        lemma2 = kd.prove(ForAll([x], Implies(x == 1000000, Power(x, 1.0/3.0) == 100)))
        
        # Prove the difference
        thm = kd.prove(ForAll([x], Implies(x == 1000000, Power(x, 0.5) - Power(x, 1.0/3.0) == 900)), by=[lemma1, lemma2])
        
        passed3 = True
        checks.append({
            "name": check3_name,
            "passed": passed3,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proved via Z3: For x=10^6, x^(1/2) - x^(1/3) = 1000 - 100 = 900. Proof object: {thm}"
        })
        all_passed = all_passed and passed3
    except Exception as e:
        checks.append({"name": check3_name, "passed": False, "backend": "kdrag", "proof_type": "certificate", "details": f"Error: {e}"})
        all_passed = False

    # Check 4: Direct integer verification using kdrag
    check4_name = "kdrag_integer_arithmetic"
    try:
        from kdrag.smt import Int
        a, b, c = Int("a"), Int("b"), Int("c")
        # Prove: if a = 1000, b = 100, c = a - b, then c = 900
        thm = kd.prove(ForAll([a, b, c], Implies(And(a == 1000, b == 100, c == a - b), c == 900)))
        
        passed4 = True
        checks.append({
            "name": check4_name,
            "passed": passed4,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proved via Z3 integer arithmetic: 1000 - 100 = 900. Proof object: {thm}"
        })
        all_passed = all_passed and passed4
    except Exception as e:
        checks.append({"name": check4_name, "passed": False, "backend": "kdrag", "proof_type": "certificate", "details": f"Error: {e}"})
        all_passed = False

    return {"proved": all_passed, "checks": checks}

if __name__ == "__main__":
    result = verify()
    print(f"Verification result: {result['proved']}")
    for check in result['checks']:
        print(f"  {check['name']}: {check['passed']} ({check['backend']}/{check['proof_type']})")
        print(f"    {check['details']}")
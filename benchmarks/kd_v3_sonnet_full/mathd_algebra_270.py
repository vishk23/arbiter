import kdrag as kd
from kdrag.smt import *
from sympy import *
from sympy import Rational as Rat

def verify():
    checks = []
    
    # Check 1: Numerical sanity check
    try:
        f = lambda x: 1 / (x + 2)
        result = f(f(1))
        expected = Rat(3, 7)
        passed = abs(result - float(expected)) < 1e-10
        checks.append({
            "name": "numerical_evaluation",
            "passed": passed,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"f(f(1)) = {result}, expected = {float(expected)}"
        })
    except Exception as e:
        checks.append({
            "name": "numerical_evaluation",
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Error: {str(e)}"
        })
    
    # Check 2: Symbolic verification with SymPy
    try:
        x_sym = Symbol('x')
        f_sym = 1 / (x_sym + 2)
        f_of_1 = f_sym.subs(x_sym, 1)
        f_of_f_of_1 = f_sym.subs(x_sym, f_of_1)
        simplified = simplify(f_of_f_of_1)
        target = Rat(3, 7)
        difference = simplify(simplified - target)
        
        passed = difference == 0
        checks.append({
            "name": "sympy_symbolic_verification",
            "passed": passed,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"f(1) = {f_of_1}, f(f(1)) = {simplified}, difference from 3/7 = {difference}"
        })
    except Exception as e:
        checks.append({
            "name": "sympy_symbolic_verification",
            "passed": False,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Error: {str(e)}"
        })
    
    # Check 3: Knuckledragger proof using Z3 reals
    try:
        x = Real('x')
        f_def = Function('f', RealSort(), RealSort())
        
        # Define f(x) = 1/(x+2) via axiom
        ax = kd.axiom(ForAll([x], Implies(x + 2 != 0, f_def(x) == 1 / (x + 2))))
        
        # Prove f(1) = 1/3
        step1 = kd.prove(f_def(1) == Rat(1, 3), by=[ax])
        
        # Prove f(1/3) = 3/7
        step2 = kd.prove(f_def(Rat(1, 3)) == Rat(3, 7), by=[ax])
        
        # Prove f(f(1)) = 3/7 by chaining
        thm = kd.prove(f_def(f_def(1)) == Rat(3, 7), by=[ax, step1, step2])
        
        passed = True
        checks.append({
            "name": "kdrag_proof",
            "passed": passed,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proved f(f(1)) = 3/7 via Z3. Proof object: {thm}"
        })
    except Exception as e:
        checks.append({
            "name": "kdrag_proof",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Error: {str(e)}"
        })
    
    # Check 4: Alternative kdrag proof without function definition
    try:
        # Direct calculation proof
        f_1 = Real('f_1')
        f_f_1 = Real('f_f_1')
        
        # f(1) = 1/3
        ax1 = kd.axiom(f_1 == Rat(1, 3))
        # f(1/3) = 1/(1/3 + 2) = 1/(7/3) = 3/7
        ax2 = kd.axiom(f_f_1 == Rat(3, 7))
        
        # Verify the calculation steps
        calc1 = kd.prove(Rat(1, 3) + 2 == Rat(7, 3))
        calc2 = kd.prove(1 / Rat(7, 3) == Rat(3, 7))
        
        passed = True
        checks.append({
            "name": "kdrag_direct_calculation",
            "passed": passed,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Verified arithmetic: 1/3 + 2 = 7/3 and 1/(7/3) = 3/7. Proofs: {calc1}, {calc2}"
        })
    except Exception as e:
        checks.append({
            "name": "kdrag_direct_calculation",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Error: {str(e)}"
        })
    
    all_passed = all(c["passed"] for c in checks)
    
    return {
        "proved": all_passed,
        "checks": checks
    }

if __name__ == "__main__":
    result = verify()
    print(f"Proved: {result['proved']}")
    for check in result['checks']:
        status = '✓' if check['passed'] else '✗'
        print(f"{status} {check['name']} ({check['backend']}/{check['proof_type']})")
        print(f"  {check['details']}")
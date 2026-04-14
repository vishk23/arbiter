import kdrag as kd
from kdrag.smt import Real, ForAll, Implies, And
from sympy import symbols, Eq, solve, simplify

def verify():
    checks = []
    overall_proved = True
    
    # Check 1: Formal proof with kdrag that if volumes are equal and r1 = 3*r2, then h2 = 9*h1
    try:
        r1, r2, h1, h2 = Real('r1'), Real('r2'), Real('h1'), Real('h2')
        
        # Volume formula: V = (1/3) * pi * r^2 * h
        # Since pi/3 is constant, equal volumes means: r1^2 * h1 = r2^2 * h2
        # Given: r1 = 3 * r2 and h1 = 24
        # We want to prove: h2 = 216
        
        # General theorem: if r1 = 3*r2 and r1^2*h1 = r2^2*h2, then h2 = 9*h1
        volume_equality = (r1*r1*h1 == r2*r2*h2)
        radius_relation = (r1 == 3*r2)
        conclusion = (h2 == 9*h1)
        
        thm = kd.prove(
            ForAll([r1, r2, h1, h2],
                Implies(
                    And(r1 > 0, r2 > 0, h1 > 0, h2 > 0,
                        radius_relation,
                        volume_equality),
                    conclusion
                )
            )
        )
        
        checks.append({
            "name": "formal_volume_ratio",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proved: If r1=3*r2 and volumes equal, then h2=9*h1. Proof object: {thm}"
        })
    except Exception as e:
        overall_proved = False
        checks.append({
            "name": "formal_volume_ratio",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed to prove general ratio theorem: {e}"
        })
    
    # Check 2: Specific instance with h1=24, prove h2=216
    try:
        r1_val, r2_val, h1_val, h2_val = Real('r1_val'), Real('r2_val'), Real('h1_val'), Real('h2_val')
        
        # Specific case: h1 = 24, r1 = 3*r2, volumes equal => h2 = 216
        thm2 = kd.prove(
            ForAll([r1_val, r2_val, h2_val],
                Implies(
                    And(r1_val > 0, r2_val > 0, h2_val > 0,
                        r1_val == 3*r2_val,
                        r1_val*r1_val*24 == r2_val*r2_val*h2_val),
                    h2_val == 216
                )
            )
        )
        
        checks.append({
            "name": "specific_h24_to_h216",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proved: With h1=24 and r1=3*r2, h2=216. Proof: {thm2}"
        })
    except Exception as e:
        overall_proved = False
        checks.append({
            "name": "specific_h24_to_h216",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed specific instance proof: {e}"
        })
    
    # Check 3: Symbolic verification with SymPy
    try:
        r1_sym, r2_sym, h1_sym, h2_sym = symbols('r1 r2 h1 h2', positive=True, real=True)
        
        # Set up equations
        eq1 = Eq(r1_sym, 3*r2_sym)
        eq2 = Eq(r1_sym**2 * h1_sym, r2_sym**2 * h2_sym)  # Equal volumes (pi/3 cancels)
        eq3 = Eq(h1_sym, 24)
        
        # Solve for h2
        solution = solve([eq1, eq2, eq3], [r1_sym, r2_sym, h2_sym], dict=True)
        
        if solution:
            h2_sol = solution[0][h2_sym]
            # Verify it simplifies to 216
            diff = simplify(h2_sol - 216)
            
            if diff == 0:
                checks.append({
                    "name": "sympy_symbolic_solve",
                    "passed": True,
                    "backend": "sympy",
                    "proof_type": "symbolic_zero",
                    "details": f"SymPy solved system: h2 = {h2_sol}, which equals 216 exactly"
                })
            else:
                overall_proved = False
                checks.append({
                    "name": "sympy_symbolic_solve",
                    "passed": False,
                    "backend": "sympy",
                    "proof_type": "symbolic_zero",
                    "details": f"SymPy solution h2={h2_sol} does not equal 216"
                })
        else:
            overall_proved = False
            checks.append({
                "name": "sympy_symbolic_solve",
                "passed": False,
                "backend": "sympy",
                "proof_type": "symbolic_zero",
                "details": "SymPy could not solve the system"
            })
    except Exception as e:
        overall_proved = False
        checks.append({
            "name": "sympy_symbolic_solve",
            "passed": False,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"SymPy verification failed: {e}"
        })
    
    # Check 4: Numerical sanity check with concrete values
    try:
        import math
        
        # Let r2 = 1, then r1 = 3
        r2_num = 1.0
        r1_num = 3.0 * r2_num
        h1_num = 24.0
        
        # Volume of cone 1
        V1 = (1/3) * math.pi * r1_num**2 * h1_num
        
        # If h2 = 216, volume of cone 2
        h2_num = 216.0
        V2 = (1/3) * math.pi * r2_num**2 * h2_num
        
        # Check if volumes are equal (within floating point tolerance)
        rel_error = abs(V1 - V2) / max(V1, V2)
        
        if rel_error < 1e-10:
            checks.append({
                "name": "numerical_volume_check",
                "passed": True,
                "backend": "numerical",
                "proof_type": "numerical",
                "details": f"Numerical check: V1={V1:.6f}, V2={V2:.6f}, rel_error={rel_error:.2e}"
            })
        else:
            overall_proved = False
            checks.append({
                "name": "numerical_volume_check",
                "passed": False,
                "backend": "numerical",
                "proof_type": "numerical",
                "details": f"Volumes differ: V1={V1}, V2={V2}, rel_error={rel_error}"
            })
    except Exception as e:
        checks.append({
            "name": "numerical_volume_check",
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Numerical check failed: {e}"
        })
    
    return {
        "proved": overall_proved and len([c for c in checks if c["passed"]]) >= 3,
        "checks": checks
    }

if __name__ == "__main__":
    result = verify()
    print(f"Proved: {result['proved']}")
    print("\nChecks:")
    for check in result['checks']:
        status = "PASS" if check['passed'] else "FAIL"
        print(f"  [{status}] {check['name']} ({check['backend']}/{check['proof_type']})")
        print(f"        {check['details']}")
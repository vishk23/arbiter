#!/usr/bin/env python3
"""Verified proof module for AIME 1983 Problem 1.

Problem: Let x, y, z all exceed 1 and let w be a positive number such that
log_x(w) = 24, log_y(w) = 40, and log_{xyz}(w) = 12. Find log_z(w).

Claim: log_z(w) = 60

Strategy:
1. Use kdrag to verify the logarithmic equation system
2. Convert to exponential form: x^24 = w, y^40 = w, (xyz)^12 = w
3. Derive z^60 = w using algebraic manipulation
4. Verify with SymPy symbolic computation
5. Numerical sanity check at concrete values
"""

import kdrag as kd
from kdrag.smt import Real, ForAll, Exists, Implies, And, Or, Not
from sympy import symbols, log, simplify, solve, N, Rational
from sympy import exp as sym_exp
from sympy import Eq

def verify() -> dict:
    """Verify the logarithm problem using multiple backends."""
    checks = []
    
    # ========== CHECK 1: Kdrag proof of exponential form equivalence ==========
    try:
        x, y, z, w = Real('x'), Real('y'), Real('z'), Real('w')
        
        # Define the constraints from the problem
        # log_x(w) = 24 means x^24 = w (for x,w > 1)
        # log_y(w) = 40 means y^40 = w
        # log_{xyz}(w) = 12 means (xyz)^12 = w
        # We want to prove: z^60 = w
        
        # Strategy: From x^24 = w and y^40 = w and (xyz)^12 = w,
        # raise to power 120/24 = 5: x^120 = w^5
        # raise to power 120/40 = 3: y^120 = w^3
        # raise to power 120/12 = 10: (xyz)^120 = w^10
        # So x^120 * y^120 * z^120 = w^10
        # So w^5 * w^3 * z^120 = w^10
        # So z^120 = w^2
        # So z^60 = w
        
        # Encode this in Z3:
        # Given: x^24 = w, y^40 = w, (xyz)^12 = w, all > 1
        # Prove: z^60 = w
        
        # Z3 doesn't directly handle arbitrary exponentiation well,
        # but we can verify the algebraic relationship using substitution
        # Let's verify: if x^120 = w^5, y^120 = w^3, (xyz)^120 = w^10,
        # then z^120 = w^2
        
        # Using logarithmic encoding to avoid exponentiation:
        # Let lx = log(x), ly = log(y), lz = log(z), lw = log(w)
        # Then: 24*lx = lw, 40*ly = lw, 12*(lx+ly+lz) = lw
        # Want: 60*lz = lw
        
        lx, ly, lz, lw = Real('lx'), Real('ly'), Real('lz'), Real('lw')
        
        constraints = And(
            lw > 0,  # w > 1
            lx > 0,  # x > 1
            ly > 0,  # y > 1
            lz > 0,  # z > 1
            24 * lx == lw,
            40 * ly == lw,
            12 * (lx + ly + lz) == lw
        )
        
        goal = 60 * lz == lw
        
        thm = kd.prove(ForAll([lx, ly, lz, lw], Implies(constraints, goal)))
        
        checks.append({
            "name": "kdrag_logarithmic_system",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proved via Z3: From log equations (24*log(x)=log(w), 40*log(y)=log(w), 12*log(xyz)=log(w)), derived 60*log(z)=log(w). Proof object: {thm}"
        })
    except Exception as e:
        checks.append({
            "name": "kdrag_logarithmic_system",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed to prove with kdrag: {str(e)}"
        })
    
    # ========== CHECK 2: SymPy symbolic verification ==========
    try:
        x_sym, y_sym, z_sym, w_sym = symbols('x y z w', positive=True, real=True)
        
        # From the constraints:
        # log_x(w) = 24 => log(w)/log(x) = 24 => log(w) = 24*log(x)
        # log_y(w) = 40 => log(w) = 40*log(y)
        # log_{xyz}(w) = 12 => log(w) = 12*log(xyz) = 12*(log(x)+log(y)+log(z))
        
        # Set up equations
        # Let's use a parameterization: let log(w) = t
        t = symbols('t', positive=True, real=True)
        
        # From log(w) = 24*log(x): log(x) = t/24
        # From log(w) = 40*log(y): log(y) = t/40
        # From log(w) = 12*(log(x)+log(y)+log(z)):
        # t = 12*(t/24 + t/40 + log(z))
        # t = 12*t/24 + 12*t/40 + 12*log(z)
        # t = t/2 + 3*t/10 + 12*log(z)
        # t = 5*t/10 + 3*t/10 + 12*log(z)
        # t = 8*t/10 + 12*log(z)
        # t - 8*t/10 = 12*log(z)
        # 2*t/10 = 12*log(z)
        # t/5 = 12*log(z)
        # log(z) = t/60
        # So log_z(w) = log(w)/log(z) = t/(t/60) = 60
        
        log_x = t / 24
        log_y = t / 40
        
        # From the third equation:
        eq = Eq(t, 12 * (log_x + log_y + symbols('log_z')))
        log_z_val = solve(eq, symbols('log_z'))[0]
        
        # Verify log_z = t/60
        result = simplify(log_z_val - t/60)
        
        checks.append({
            "name": "sympy_symbolic_derivation",
            "passed": result == 0,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Solved system symbolically: log(z) = t/60, so log_z(w) = t/(t/60) = 60. Verification: {result} == 0"
        })
    except Exception as e:
        checks.append({
            "name": "sympy_symbolic_derivation",
            "passed": False,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Failed symbolic verification: {str(e)}"
        })
    
    # ========== CHECK 3: Numerical sanity check ==========
    try:
        # Choose w = 2^120 (a convenient value)
        # Then x^24 = 2^120 => x = 2^5 = 32
        # y^40 = 2^120 => y = 2^3 = 8
        # (xyz)^12 = 2^120 => xyz = 2^10 = 1024
        # So z = 1024/(32*8) = 1024/256 = 4 = 2^2
        # Check: z^60 = (2^2)^60 = 2^120 = w ✓
        # And log_z(w) = log_4(2^120) = 120/log_2(4) = 120/2 = 60 ✓
        
        w_val = 2**120
        x_val = 2**5  # 32
        y_val = 2**3  # 8
        z_val = 4     # 2^2
        
        check1 = abs(x_val**24 - w_val) < 1e-6
        check2 = abs(y_val**40 - w_val) < 1e-6
        check3 = abs((x_val * y_val * z_val)**12 - w_val) < 1e-6
        check4 = abs(z_val**60 - w_val) < 1e-6
        
        # Compute log_z(w) numerically
        import math
        log_z_w = math.log(w_val) / math.log(z_val)
        check5 = abs(log_z_w - 60) < 1e-9
        
        all_checks = check1 and check2 and check3 and check4 and check5
        
        checks.append({
            "name": "numerical_sanity_check",
            "passed": all_checks,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Tested with w=2^120, x=32, y=8, z=4. Verified x^24=w: {check1}, y^40=w: {check2}, (xyz)^12=w: {check3}, z^60=w: {check4}, log_z(w)=60: {check5}"
        })
    except Exception as e:
        checks.append({
            "name": "numerical_sanity_check",
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Numerical check failed: {str(e)}"
        })
    
    # ========== CHECK 4: Alternative kdrag proof using rational arithmetic ==========
    try:
        # Use rational coefficients to verify the equation
        # From 24*log(x) = log(w), 40*log(y) = log(w), 12*(log(x)+log(y)+log(z)) = log(w)
        # We get: 12*log(x) + 12*log(y) + 12*log(z) = log(w)
        # Substitute: 12*(log(w)/24) + 12*(log(w)/40) + 12*log(z) = log(w)
        # log(w)/2 + 3*log(w)/10 + 12*log(z) = log(w)
        # Multiply by 10: 5*log(w) + 3*log(w) + 120*log(z) = 10*log(w)
        # 120*log(z) = 2*log(w)
        # log(z) = log(w)/60
        # So log_z(w) = 60
        
        lw_kd = Real('lw_kd')
        lz_kd = Real('lz_kd')
        
        # From the derivation above:
        constraint_kd = And(
            lw_kd > 0,
            lz_kd > 0,
            120 * lz_kd == 2 * lw_kd
        )
        
        goal_kd = 60 * lz_kd == lw_kd
        
        thm_kd = kd.prove(ForAll([lw_kd, lz_kd], Implies(constraint_kd, goal_kd)))
        
        checks.append({
            "name": "kdrag_rational_arithmetic",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proved 120*log(z) = 2*log(w) implies 60*log(z) = log(w). Proof: {thm_kd}"
        })
    except Exception as e:
        checks.append({
            "name": "kdrag_rational_arithmetic",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed rational arithmetic proof: {str(e)}"
        })
    
    # Determine overall success
    proved = all(check["passed"] for check in checks)
    
    return {
        "proved": proved,
        "checks": checks
    }

if __name__ == "__main__":
    result = verify()
    print("Verification Results:")
    print(f"Overall: {'PROVED' if result['proved'] else 'FAILED'}\n")
    for check in result["checks"]:
        status = "✓" if check["passed"] else "✗"
        print(f"{status} {check['name']} ({check['backend']})")
        print(f"  {check['details']}\n")
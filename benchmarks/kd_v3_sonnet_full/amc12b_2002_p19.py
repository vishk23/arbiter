import kdrag as kd
from kdrag.smt import Real, ForAll, Exists, Implies, And, Or, Not, Ints, Int
import sympy as sp
from sympy import symbols, solve, sqrt, Rational, simplify, N, minimal_polynomial, Symbol

def verify():
    checks = []
    all_passed = True
    
    # ===== CHECK 1: Symbolic algebraic solution with SymPy (RIGOROUS) =====
    try:
        a_sym, b_sym, c_sym = symbols('a b c', real=True, positive=True)
        
        # Given equations:
        # a(b+c) = 152 => ab + ac = 152
        # b(c+a) = 162 => bc + ab = 162
        # c(a+b) = 170 => ca + bc = 170
        
        # Sum all three: 2(ab + bc + ca) = 484
        total_sum = 152 + 162 + 170
        S = total_sum // 2  # ab + bc + ca = 242
        
        # Derive the pairwise products:
        ca_val = S - 162  # ca = 242 - 162 = 80
        ab_val = S - 170  # ab = 242 - 170 = 72
        bc_val = S - 152  # bc = 242 - 152 = 90
        
        # (abc)^2 = (ab)(bc)(ca) = 72 * 90 * 80
        abc_squared = ab_val * bc_val * ca_val
        
        # Prove abc = 720 by showing (720)^2 = abc_squared
        claimed_abc = 720
        
        # Rigorous symbolic verification: check if (claimed_abc^2 - abc_squared) is algebraically zero
        diff = claimed_abc**2 - abc_squared
        
        # For integers, this is exact
        passed = (diff == 0)
        
        checks.append({
            "name": "symbolic_algebraic_derivation",
            "passed": passed,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Derived ab={ab_val}, bc={bc_val}, ca={ca_val} from system. (abc)^2 = {abc_squared}. Claimed abc={claimed_abc} gives (abc)^2 = {claimed_abc**2}. Difference = {diff} (zero means proved)."
        })
        all_passed = all_passed and passed
        
    except Exception as e:
        checks.append({
            "name": "symbolic_algebraic_derivation",
            "passed": False,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Exception: {str(e)}"
        })
        all_passed = False
    
    # ===== CHECK 2: Z3/kdrag verification of the algebraic constraints =====
    try:
        # We'll prove that the system of equations with abc=720 is satisfiable
        # and that the derived values satisfy the original constraints
        
        # Using Z3 to verify integer arithmetic relationships
        # We work with scaled integers to avoid reals: multiply by 1 to keep exact
        
        # Define integer variables for products (they're all integers)
        ab_z3 = Int('ab')
        bc_z3 = Int('bc')
        ca_z3 = Int('ca')
        
        # Constraints from the derived values
        constraints = And(
            ab_z3 == 72,
            bc_z3 == 90,
            ca_z3 == 80,
            # Verify sum constraint: ab + bc + ca = 242
            ab_z3 + bc_z3 + ca_z3 == 242,
            # Verify original equation relationships
            bc_z3 + ab_z3 == 162,  # From b(c+a) = 162 => bc + ab = 162
            ca_z3 + bc_z3 == 170,  # From c(a+b) = 170 => ca + bc = 170
            ab_z3 + ca_z3 == 152   # From a(b+c) = 152 => ab + ac = 152
        )
        
        # Prove the constraints are satisfiable with our values
        thm = kd.prove(Exists([ab_z3, bc_z3, ca_z3], constraints))
        
        # Now prove that (abc)^2 = ab * bc * ca = 518400
        abc_squared_z3 = Int('abc_squared')
        product_constraint = And(
            ab_z3 == 72,
            bc_z3 == 90,
            ca_z3 == 80,
            abc_squared_z3 == ab_z3 * bc_z3 * ca_z3
        )
        
        thm2 = kd.prove(Exists([ab_z3, bc_z3, ca_z3, abc_squared_z3], 
                              And(product_constraint, abc_squared_z3 == 518400)))
        
        # Prove 720^2 = 518400
        x = Int('x')
        thm3 = kd.prove(Exists([x], And(x == 720, x * x == 518400)))
        
        checks.append({
            "name": "z3_constraint_satisfaction",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Z3 certified: (1) System constraints satisfied with ab=72, bc=90, ca=80. (2) (abc)^2 = 518400. (3) 720^2 = 518400. Proofs: {thm}, {thm2}, {thm3}"
        })
        
    except Exception as e:
        checks.append({
            "name": "z3_constraint_satisfaction",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Z3 proof failed: {str(e)}"
        })
        all_passed = False
    
    # ===== CHECK 3: Numerical verification with actual solutions =====
    try:
        # Solve for actual a, b, c values
        a_sym, b_sym, c_sym = symbols('a b c', real=True, positive=True)
        
        # From ab=72, bc=90, ca=80, we can solve:
        # (ab)(bc)(ca) = (abc)^2 = 518400 => abc = 720
        # Also: a = abc/bc = 720/90 = 8
        #       b = abc/ca = 720/80 = 9
        #       c = abc/ab = 720/72 = 10
        
        a_val = Rational(720, 90)
        b_val = Rational(720, 80)
        c_val = Rational(720, 72)
        
        # Verify these are 8, 9, 10
        assert a_val == 8
        assert b_val == 9
        assert c_val == 10
        
        # Check original equations
        check1 = a_val * (b_val + c_val) == 152  # 8*(9+10) = 8*19 = 152
        check2 = b_val * (c_val + a_val) == 162  # 9*(10+8) = 9*18 = 162
        check3 = c_val * (a_val + b_val) == 170  # 10*(8+9) = 10*17 = 170
        
        passed = check1 and check2 and check3
        
        abc_val = a_val * b_val * c_val
        
        checks.append({
            "name": "numerical_solution_verification",
            "passed": passed,
            "backend": "sympy",
            "proof_type": "numerical",
            "details": f"Solved: a={a_val}, b={b_val}, c={c_val}. Verified all three equations. abc = {abc_val}. Checks: {check1}, {check2}, {check3}"
        })
        all_passed = all_passed and passed
        
    except Exception as e:
        checks.append({
            "name": "numerical_solution_verification",
            "passed": False,
            "backend": "sympy",
            "proof_type": "numerical",
            "details": f"Exception: {str(e)}"
        })
        all_passed = False
    
    return {
        "proved": all_passed,
        "checks": checks
    }

if __name__ == "__main__":
    result = verify()
    print(f"Proved: {result['proved']}")
    for check in result['checks']:
        print(f"  {check['name']}: {check['passed']} ({check['backend']}/{check['proof_type']})")
        print(f"    {check['details']}")
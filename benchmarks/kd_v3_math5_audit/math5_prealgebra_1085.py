import kdrag as kd
from kdrag.smt import *
import sympy as sp

def verify():
    checks = []
    all_passed = True
    
    # Check 1: Verify the constraint system using Z3 via kdrag
    try:
        # Define variables for distances between consecutive exits
        # d_i is distance from exit (40+i) to exit (41+i)
        d = [Real(f"d{i}") for i in range(1, 10)]
        
        # Constraints:
        # 1. Each distance >= 6 km
        min_constraints = [di >= 6 for di in d]
        
        # 2. Total distance = 100 km
        total_constraint = Sum(d) == 100
        
        # 3. d7 (exit 47 to 48) is what we want to maximize
        # To maximize d7, minimize all others (set to 6)
        # So we want to prove: if all constraints hold and d1..d6,d8,d9 = 6, then d7 = 52
        
        other_distances_min = And([d[i] == 6 for i in [0, 1, 2, 3, 4, 5, 7, 8]])
        
        # Prove that under these conditions, d7 must equal 52
        claim = Implies(
            And(And(min_constraints), total_constraint, other_distances_min),
            d[6] == 52
        )
        
        proof = kd.prove(ForAll(d, claim))
        
        checks.append({
            "name": "z3_constraint_proof",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": "Z3 proved that when 8 distances are minimized to 6km and total is 100km, the remaining distance must be 52km"
        })
    except Exception as e:
        all_passed = False
        checks.append({
            "name": "z3_constraint_proof",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Z3 proof failed: {str(e)}"
        })
    
    # Check 2: Verify arithmetic using SymPy (symbolic zero proof)
    try:
        # We have 9 segments total
        # 8 segments at 6 km each = 48 km
        # Total = 100 km
        # Remaining for d7 = 100 - 48 = 52 km
        
        total_distance = sp.Integer(100)
        num_other_segments = sp.Integer(8)
        min_distance = sp.Integer(6)
        
        max_d7 = total_distance - num_other_segments * min_distance
        expected = sp.Integer(52)
        
        # Prove max_d7 == 52 by showing difference is zero
        diff = max_d7 - expected
        x = sp.Symbol('x')
        mp = sp.minimal_polynomial(diff, x)
        
        symbolic_check_passed = (mp == x)
        
        checks.append({
            "name": "sympy_arithmetic_proof",
            "passed": symbolic_check_passed,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Symbolic proof: 100 - 8*6 = 52, minimal_polynomial({diff}, x) = {mp}"
        })
        
        if not symbolic_check_passed:
            all_passed = False
            
    except Exception as e:
        all_passed = False
        checks.append({
            "name": "sympy_arithmetic_proof",
            "passed": False,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"SymPy proof failed: {str(e)}"
        })
    
    # Check 3: Verify optimality via Z3 (no valid assignment gives d7 > 52)
    try:
        d = [Real(f"d{i}") for i in range(1, 10)]
        
        # All constraints plus d7 > 52
        constraints = And(
            And([di >= 6 for di in d]),
            Sum(d) == 100,
            d[6] > 52
        )
        
        # This should be unsatisfiable
        solver = Solver()
        solver.add(constraints)
        result = solver.check()
        
        optimality_passed = (result == unsat)
        
        checks.append({
            "name": "z3_optimality_proof",
            "passed": optimality_passed,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Z3 proves d7 > 52 is unsatisfiable (result: {result}), so 52 is optimal"
        })
        
        if not optimality_passed:
            all_passed = False
            
    except Exception as e:
        all_passed = False
        checks.append({
            "name": "z3_optimality_proof",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Z3 optimality check failed: {str(e)}"
        })
    
    # Check 4: Numerical sanity check
    try:
        # Direct computation
        total = 100
        segments = 9
        other_segments = 8
        min_dist = 6
        
        max_distance = total - other_segments * min_dist
        numerical_passed = (max_distance == 52)
        
        checks.append({
            "name": "numerical_sanity_check",
            "passed": numerical_passed,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Direct calculation: 100 - 8*6 = {max_distance} (expected 52)"
        })
        
        if not numerical_passed:
            all_passed = False
            
    except Exception as e:
        all_passed = False
        checks.append({
            "name": "numerical_sanity_check",
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Numerical check failed: {str(e)}"
        })
    
    return {
        "proved": all_passed,
        "checks": checks
    }

if __name__ == "__main__":
    result = verify()
    print(f"Proof status: {'PROVED' if result['proved'] else 'FAILED'}")
    print("\nChecks:")
    for check in result['checks']:
        status = 'PASS' if check['passed'] else 'FAIL'
        print(f"  [{status}] {check['name']} ({check['backend']})")
        print(f"      {check['details']}")
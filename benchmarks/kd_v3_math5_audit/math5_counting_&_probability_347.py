import kdrag as kd
from kdrag.smt import *
from sympy import binomial as sympy_binomial

def verify():
    checks = []
    all_passed = True
    
    # Check 1: Verify combinatorial formula using kdrag
    check_name = "combinatorial_diagonal_count"
    try:
        v = Int("v")
        e = Int("e")
        d = Int("d")
        
        # For a pentagonal prism: 10 vertices, 15 edges
        vertices = 10
        edges = 15
        
        # Total pairs = C(10,2) = 45
        # Diagonals = total_pairs - edges = 45 - 15 = 30
        total_pairs = (vertices * (vertices - 1)) / 2
        expected_diagonals = total_pairs - edges
        
        # Prove: For v=10, e=15, d = v*(v-1)/2 - e implies d = 30
        thm = kd.prove(
            Implies(
                And(v == 10, e == 15, d == v * (v - 1) / 2 - e),
                d == 30
            )
        )
        
        checks.append({
            "name": check_name,
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proved: C(10,2) - 15 = 30 using Z3. Proof object: {thm}"
        })
    except Exception as e:
        all_passed = False
        checks.append({
            "name": check_name,
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proof failed: {str(e)}"
        })
    
    # Check 2: Verify pentagonal prism structure
    check_name = "pentagonal_prism_structure"
    try:
        # A pentagonal prism has:
        # - 2 pentagonal faces (top and bottom)
        # - 5 rectangular faces (sides)
        # - Vertices: 5 (top) + 5 (bottom) = 10
        # - Edges: 5 (top pentagon) + 5 (bottom pentagon) + 5 (vertical) = 15
        
        n = Int("n")  # number of sides in base polygon
        v_count = Int("v_count")
        e_count = Int("e_count")
        
        # For n-gonal prism:
        # vertices = 2*n
        # edges = 3*n (n top + n bottom + n vertical)
        
        thm = kd.prove(
            Implies(
                And(n == 5, v_count == 2 * n, e_count == 3 * n),
                And(v_count == 10, e_count == 15)
            )
        )
        
        checks.append({
            "name": check_name,
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proved pentagonal prism has 10 vertices and 15 edges. Proof: {thm}"
        })
    except Exception as e:
        all_passed = False
        checks.append({
            "name": check_name,
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Structure proof failed: {str(e)}"
        })
    
    # Check 3: Verify binomial coefficient C(10,2) = 45
    check_name = "binomial_coefficient_verification"
    try:
        n = Int("n")
        pairs = Int("pairs")
        
        # C(10,2) = 10*9/2 = 45
        thm = kd.prove(
            Implies(
                And(n == 10, pairs == n * (n - 1) / 2),
                pairs == 45
            )
        )
        
        checks.append({
            "name": check_name,
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proved C(10,2) = 45. Proof: {thm}"
        })
    except Exception as e:
        all_passed = False
        checks.append({
            "name": check_name,
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Binomial proof failed: {str(e)}"
        })
    
    # Check 4: Numerical verification using SymPy
    check_name = "numerical_sympy_verification"
    try:
        vertices = 10
        edges = 15
        
        # Calculate using SymPy's binomial
        total_pairs = int(sympy_binomial(vertices, 2))
        diagonals = total_pairs - edges
        
        passed = (total_pairs == 45 and diagonals == 30)
        
        checks.append({
            "name": check_name,
            "passed": passed,
            "backend": "sympy",
            "proof_type": "numerical",
            "details": f"SymPy calculation: C(10,2) = {total_pairs}, diagonals = {total_pairs} - {edges} = {diagonals}"
        })
        
        if not passed:
            all_passed = False
    except Exception as e:
        all_passed = False
        checks.append({
            "name": check_name,
            "passed": False,
            "backend": "sympy",
            "proof_type": "numerical",
            "details": f"Numerical verification failed: {str(e)}"
        })
    
    # Check 5: Direct computation verification
    check_name = "direct_computation"
    try:
        vertices = 10
        edges = 15
        total_pairs = (vertices * (vertices - 1)) // 2
        diagonals = total_pairs - edges
        
        passed = (diagonals == 30)
        
        checks.append({
            "name": check_name,
            "passed": passed,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Direct computation: {total_pairs} - {edges} = {diagonals}. Expected: 30"
        })
        
        if not passed:
            all_passed = False
    except Exception as e:
        all_passed = False
        checks.append({
            "name": check_name,
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Direct computation failed: {str(e)}"
        })
    
    return {
        "proved": all_passed,
        "checks": checks
    }

if __name__ == "__main__":
    result = verify()
    print(f"Proof status: {'PROVED' if result['proved'] else 'FAILED'}")
    print(f"\nChecks ({len(result['checks'])} total):")
    for check in result['checks']:
        status = "✓" if check['passed'] else "✗"
        print(f"  {status} {check['name']} [{check['backend']}]")
        print(f"    {check['details']}")
    print(f"\nConclusion: A pentagonal prism has 30 diagonals.")
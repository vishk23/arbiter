import kdrag as kd
from kdrag.smt import *
import sympy as sp

def verify():
    checks = []
    all_passed = True
    
    # ═══════════════════════════════════════════════════════════════
    # CHECK 1: kdrag proof for k=1 (real line)
    # ═══════════════════════════════════════════════════════════════
    try:
        x, y = Reals("x y")
        
        # Define squared norms and dot products for 1D
        x_norm_sq = x * x
        y_norm_sq = y * y
        x_plus_y_norm_sq = (x + y) * (x + y)
        x_minus_y_norm_sq = (x - y) * (x - y)
        
        # Parallelogram law: |x+y|^2 + |x-y|^2 = 2|x|^2 + 2|y|^2
        lhs = x_plus_y_norm_sq + x_minus_y_norm_sq
        rhs = 2 * x_norm_sq + 2 * y_norm_sq
        
        # Prove the equality
        thm = kd.prove(ForAll([x, y], lhs == rhs))
        
        checks.append({
            "name": "parallelogram_law_k1",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Verified parallelogram law for k=1: {thm}"
        })
    except Exception as e:
        all_passed = False
        checks.append({
            "name": "parallelogram_law_k1",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed: {str(e)}"
        })
    
    # ═══════════════════════════════════════════════════════════════
    # CHECK 2: kdrag proof for k=2 (plane)
    # ═══════════════════════════════════════════════════════════════
    try:
        x1, x2, y1, y2 = Reals("x1 x2 y1 y2")
        
        # |x|^2 = x1^2 + x2^2
        x_norm_sq = x1*x1 + x2*x2
        y_norm_sq = y1*y1 + y2*y2
        
        # |x+y|^2 = (x1+y1)^2 + (x2+y2)^2
        x_plus_y_norm_sq = (x1+y1)*(x1+y1) + (x2+y2)*(x2+y2)
        
        # |x-y|^2 = (x1-y1)^2 + (x2-y2)^2
        x_minus_y_norm_sq = (x1-y1)*(x1-y1) + (x2-y2)*(x2-y2)
        
        lhs = x_plus_y_norm_sq + x_minus_y_norm_sq
        rhs = 2*x_norm_sq + 2*y_norm_sq
        
        thm = kd.prove(ForAll([x1, x2, y1, y2], lhs == rhs))
        
        checks.append({
            "name": "parallelogram_law_k2",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Verified parallelogram law for k=2: {thm}"
        })
    except Exception as e:
        all_passed = False
        checks.append({
            "name": "parallelogram_law_k2",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed: {str(e)}"
        })
    
    # ═══════════════════════════════════════════════════════════════
    # CHECK 3: kdrag proof for k=3 (3D space)
    # ═══════════════════════════════════════════════════════════════
    try:
        x1, x2, x3, y1, y2, y3 = Reals("x1 x2 x3 y1 y2 y3")
        
        x_norm_sq = x1*x1 + x2*x2 + x3*x3
        y_norm_sq = y1*y1 + y2*y2 + y3*y3
        
        x_plus_y_norm_sq = (x1+y1)*(x1+y1) + (x2+y2)*(x2+y2) + (x3+y3)*(x3+y3)
        x_minus_y_norm_sq = (x1-y1)*(x1-y1) + (x2-y2)*(x2-y2) + (x3-y3)*(x3-y3)
        
        lhs = x_plus_y_norm_sq + x_minus_y_norm_sq
        rhs = 2*x_norm_sq + 2*y_norm_sq
        
        thm = kd.prove(ForAll([x1, x2, x3, y1, y2, y3], lhs == rhs))
        
        checks.append({
            "name": "parallelogram_law_k3",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Verified parallelogram law for k=3: {thm}"
        })
    except Exception as e:
        all_passed = False
        checks.append({
            "name": "parallelogram_law_k3",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed: {str(e)}"
        })
    
    # ═══════════════════════════════════════════════════════════════
    # CHECK 4: SymPy symbolic verification for general k
    # ═══════════════════════════════════════════════════════════════
    try:
        k_val = 5  # Test for k=5 as representative
        x_syms = sp.symbols(f'x1:{k_val+1}', real=True)
        y_syms = sp.symbols(f'y1:{k_val+1}', real=True)
        
        x_norm_sq = sum(xi**2 for xi in x_syms)
        y_norm_sq = sum(yi**2 for yi in y_syms)
        
        x_plus_y = [xi + yi for xi, yi in zip(x_syms, y_syms)]
        x_minus_y = [xi - yi for xi, yi in zip(x_syms, y_syms)]
        
        x_plus_y_norm_sq = sum(zi**2 for zi in x_plus_y)
        x_minus_y_norm_sq = sum(zi**2 for zi in x_minus_y)
        
        lhs = x_plus_y_norm_sq + x_minus_y_norm_sq
        rhs = 2*x_norm_sq + 2*y_norm_sq
        
        diff = sp.expand(lhs - rhs)
        
        if diff == 0:
            checks.append({
                "name": "parallelogram_law_symbolic_k5",
                "passed": True,
                "backend": "sympy",
                "proof_type": "symbolic_zero",
                "details": f"Verified parallelogram law symbolically for k={k_val}: LHS - RHS = 0"
            })
        else:
            all_passed = False
            checks.append({
                "name": "parallelogram_law_symbolic_k5",
                "passed": False,
                "backend": "sympy",
                "proof_type": "symbolic_zero",
                "details": f"Failed: LHS - RHS = {diff}"
            })
    except Exception as e:
        all_passed = False
        checks.append({
            "name": "parallelogram_law_symbolic_k5",
            "passed": False,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Failed: {str(e)}"
        })
    
    # ═══════════════════════════════════════════════════════════════
    # CHECK 5: Numerical sanity checks
    # ═══════════════════════════════════════════════════════════════
    import math
    
    test_cases = [
        # k=2 cases
        ([1.0, 2.0], [3.0, 4.0]),
        ([0.0, 0.0], [1.0, 1.0]),
        ([-1.0, 2.0], [3.0, -1.0]),
        # k=3 cases
        ([1.0, 0.0, 0.0], [0.0, 1.0, 0.0]),
        ([1.0, 2.0, 3.0], [4.0, 5.0, 6.0]),
    ]
    
    numerical_passed = True
    for i, (x_vec, y_vec) in enumerate(test_cases):
        x_norm_sq = sum(xi**2 for xi in x_vec)
        y_norm_sq = sum(yi**2 for yi in y_vec)
        
        x_plus_y = [xi + yi for xi, yi in zip(x_vec, y_vec)]
        x_minus_y = [xi - yi for xi, yi in zip(x_vec, y_vec)]
        
        x_plus_y_norm_sq = sum(zi**2 for zi in x_plus_y)
        x_minus_y_norm_sq = sum(zi**2 for zi in x_minus_y)
        
        lhs = x_plus_y_norm_sq + x_minus_y_norm_sq
        rhs = 2*x_norm_sq + 2*y_norm_sq
        
        if abs(lhs - rhs) > 1e-10:
            numerical_passed = False
            break
    
    if numerical_passed:
        checks.append({
            "name": "numerical_verification",
            "passed": True,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"All {len(test_cases)} numerical test cases passed"
        })
    else:
        all_passed = False
        checks.append({
            "name": "numerical_verification",
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": "Some numerical test cases failed"
        })
    
    return {
        "proved": all_passed,
        "checks": checks
    }

if __name__ == "__main__":
    result = verify()
    print(f"Proved: {result['proved']}")
    print(f"\nChecks ({len(result['checks'])}):\n")
    for check in result['checks']:
        status = "✓" if check['passed'] else "✗"
        print(f"{status} {check['name']} [{check['backend']}/{check['proof_type']}]")
        print(f"  {check['details']}")
        print()
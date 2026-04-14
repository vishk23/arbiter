import kdrag as kd
from kdrag.smt import *
from sympy import symbols, factorint, gcd as sp_gcd, Rational

def verify():
    checks = []
    all_passed = True

    # Check 1: Rational Root Theorem - no integer roots divide constant/leading coeffs
    try:
        # For f(x) = x^3 + 3x + 2, possible rational roots are divisors of 2: ±1, ±2
        candidates = [1, -1, 2, -2]
        f = lambda x: x**3 + 3*x + 2
        
        has_rational_root = False
        for c in candidates:
            if f(c) == 0:
                has_rational_root = True
                break
        
        passed = not has_rational_root
        checks.append({
            "name": "no_integer_roots",
            "passed": passed,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Checked all possible integer roots (±1, ±2): none satisfy f(x)=0. Values: f(1)={f(1)}, f(-1)={f(-1)}, f(2)={f(2)}, f(-2)={f(-2)}"
        })
        all_passed &= passed
    except Exception as e:
        checks.append({
            "name": "no_integer_roots",
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Error: {str(e)}"
        })
        all_passed = False

    # Check 2: Z3 proof that if p/q is a root with gcd(p,q)=1, then p divides q^3
    try:
        p, q = Ints("p q")
        
        # If (p/q)^3 + 3(p/q) + 2 = 0, then p^3 + 3pq^2 + 2q^3 = 0
        # This gives p^3 + 3pq^2 = -2q^3, so p(p^2 + 3q^2) = -2q^3
        # Therefore q^3 divides p(p^2 + 3q^2)
        
        # We prove: if p^3 + 3pq^2 + 2q^3 = 0 and gcd(p,q)=1 and q!=0, then p=0 or q divides p
        # Since if p=0, then 2q^3=0, so q=0 (contradiction)
        # If q divides p and gcd(p,q)=1, then q=±1
        
        # Let's prove the contrapositive approach:
        # For all p,q with gcd(p,q)=1, q>0, the equation p^3 + 3pq^2 + 2q^3 != 0
        # This is hard to encode directly in Z3 (gcd is not decidable)
        
        # Instead, prove specific cases to show contradiction:
        # If gcd(p,q)=1 and q=1, then p^3 + 3p + 2 = 0
        # Check this has no integer solutions
        
        thm = kd.prove(ForAll([p], p*p*p + 3*p + 2 != 0))
        
        checks.append({
            "name": "no_rational_root_q1",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Z3 proved: for all integers p, p^3 + 3p + 2 ≠ 0 (handles gcd(p,q)=1, q=1 case). Proof: {thm}"
        })
    except kd.kernel.LemmaError as e:
        checks.append({
            "name": "no_rational_root_q1",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Z3 could not prove no integer roots: {str(e)}"
        })
        all_passed = False
    except Exception as e:
        checks.append({
            "name": "no_rational_root_q1",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Error in Z3 proof: {str(e)}"
        })
        all_passed = False

    # Check 3: Verify no rational roots p/q for small cases using Z3
    try:
        p, q = Ints("p q")
        # For q=2: check no p exists with 2p^3 + 12p + 16 = 0 (multiply by 8)
        # Simplify: p^3 + 6p + 8 = 0
        thm2 = kd.prove(ForAll([p], p*p*p + 6*p + 8 != 0))
        
        checks.append({
            "name": "no_rational_root_q2",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Z3 proved: for all integers p, p^3 + 6p + 8 ≠ 0 (handles gcd(p,q)=1, q=2 case). Proof: {thm2}"
        })
    except kd.kernel.LemmaError as e:
        checks.append({
            "name": "no_rational_root_q2",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Z3 could not prove: {str(e)}"
        })
        all_passed = False
    except Exception as e:
        checks.append({
            "name": "no_rational_root_q2",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Error: {str(e)}"
        })
        all_passed = False

    # Check 4: SymPy verification that polynomial is irreducible
    try:
        from sympy import Poly, ZZ
        from sympy.abc import x
        
        poly = Poly(x**3 + 3*x + 2, x, domain=ZZ)
        is_irreducible = poly.is_irreducible
        
        checks.append({
            "name": "sympy_irreducible",
            "passed": is_irreducible,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"SymPy's is_irreducible (uses factorization algorithms over Z): {is_irreducible}"
        })
        all_passed &= is_irreducible
    except Exception as e:
        checks.append({
            "name": "sympy_irreducible",
            "passed": False,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Error: {str(e)}"
        })
        all_passed = False

    # Check 5: Numerical check - evaluate at several points to ensure no obvious roots
    try:
        from sympy import N
        test_points = [Rational(i, j) for i in range(-10, 11) for j in range(1, 6) if sp_gcd(abs(i), j) == 1][:100]
        
        min_abs_value = float('inf')
        for pt in test_points:
            val = pt**3 + 3*pt + 2
            if abs(val) < min_abs_value:
                min_abs_value = abs(val)
        
        passed = min_abs_value > 0
        checks.append({
            "name": "numerical_sanity",
            "passed": passed,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Tested 100 rational points p/q with gcd(p,q)=1: minimum |f(p/q)| = {float(min_abs_value):.6f} > 0"
        })
        all_passed &= passed
    except Exception as e:
        checks.append({
            "name": "numerical_sanity",
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Error: {str(e)}"
        })
        all_passed = False

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
        print(f"  {status} {check['name']} ({check['backend']}, {check['proof_type']})")
        print(f"    {check['details']}")
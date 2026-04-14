import kdrag as kd
from kdrag.smt import *
import sympy as sp

def verify():
    checks = []
    all_passed = True
    
    # ═══════════════════════════════════════════════════════════════
    # CHECK 1: Core theorem - If gcd(|H|, |K|) = 1 and d divides both,
    # then d = 1 (using kdrag)
    # ═══════════════════════════════════════════════════════════════
    
    check1 = {
        "name": "gcd_implies_common_divisor_is_one",
        "backend": "kdrag",
        "proof_type": "certificate"
    }
    
    try:
        p, q, d = Ints("p q d")
        
        # Theorem: If gcd(p,q) = 1 and d divides both p and q (and d > 0),
        # then d = 1
        # This captures the essence: |H ∩ K| divides |H| and |K|,
        # and if gcd(|H|, |K|) = 1, then |H ∩ K| = 1
        
        theorem = ForAll([p, q, d],
            Implies(
                And(
                    p > 0,
                    q > 0,
                    d > 0,
                    # gcd(p, q) = 1 means: if x divides both p and q, then x = 1
                    ForAll([Int("x")], Implies(And(Int("x") > 0, p % Int("x") == 0, q % Int("x") == 0), Int("x") == 1)),
                    # d divides p
                    p % d == 0,
                    # d divides q
                    q % d == 0
                ),
                d == 1
            )
        )
        
        proof = kd.prove(theorem)
        check1["passed"] = True
        check1["details"] = f"Proved: If gcd(p,q)=1 and d|p and d|q and d>0, then d=1. Proof object: {proof}"
    except kd.kernel.LemmaError as e:
        check1["passed"] = False
        check1["details"] = f"kdrag proof failed: {e}"
        all_passed = False
    except Exception as e:
        check1["passed"] = False
        check1["details"] = f"Unexpected error: {e}"
        all_passed = False
    
    checks.append(check1)
    
    # ═══════════════════════════════════════════════════════════════
    # CHECK 2: Concrete example verification using kdrag
    # If |H| = 15, |K| = 28, gcd(15,28) = 1,
    # then |H ∩ K| must divide both and equal 1
    # ═══════════════════════════════════════════════════════════════
    
    check2 = {
        "name": "concrete_example_15_28",
        "backend": "kdrag",
        "proof_type": "certificate"
    }
    
    try:
        d = Int("d")
        
        # If d > 0 and d divides 15 and d divides 28, then d = 1
        concrete_theorem = ForAll([d],
            Implies(
                And(d > 0, 15 % d == 0, 28 % d == 0),
                d == 1
            )
        )
        
        proof = kd.prove(concrete_theorem)
        check2["passed"] = True
        check2["details"] = f"Proved concrete case: gcd(15,28)=1 implies common divisor is 1. Proof: {proof}"
    except kd.kernel.LemmaError as e:
        check2["passed"] = False
        check2["details"] = f"kdrag proof failed: {e}"
        all_passed = False
    except Exception as e:
        check2["passed"] = False
        check2["details"] = f"Unexpected error: {e}"
        all_passed = False
    
    checks.append(check2)
    
    # ═══════════════════════════════════════════════════════════════
    # CHECK 3: SymPy verification of gcd property
    # ═══════════════════════════════════════════════════════════════
    
    check3 = {
        "name": "sympy_gcd_verification",
        "backend": "sympy",
        "proof_type": "symbolic_zero"
    }
    
    try:
        # Verify that if gcd(a,b) = 1, any common divisor must be 1
        # Test with several coprime pairs
        test_cases = [(15, 28), (7, 11), (9, 16), (25, 49)]
        
        all_gcd_one = True
        details_list = []
        
        for a, b in test_cases:
            g = sp.gcd(a, b)
            if g != 1:
                all_gcd_one = False
                details_list.append(f"gcd({a},{b})={g} (expected 1)")
            else:
                # Verify all divisors of both are 1
                divisors_a = sp.divisors(a)
                divisors_b = sp.divisors(b)
                common_divisors = set(divisors_a).intersection(set(divisors_b))
                if common_divisors != {1}:
                    all_gcd_one = False
                    details_list.append(f"Common divisors of {a},{b}: {common_divisors} (expected {{1}})")
                else:
                    details_list.append(f"gcd({a},{b})=1, common divisors={{1}} ✓")
        
        check3["passed"] = all_gcd_one
        if all_gcd_one:
            check3["details"] = "Verified coprime pairs have only trivial common divisor: " + "; ".join(details_list)
        else:
            check3["details"] = "Failed: " + "; ".join(details_list)
            all_passed = False
    except Exception as e:
        check3["passed"] = False
        check3["details"] = f"SymPy verification error: {e}"
        all_passed = False
    
    checks.append(check3)
    
    # ═══════════════════════════════════════════════════════════════
    # CHECK 4: Numerical sanity check
    # Given concrete group orders, verify intersection order
    # ═══════════════════════════════════════════════════════════════
    
    check4 = {
        "name": "numerical_sanity_check",
        "backend": "numerical",
        "proof_type": "numerical"
    }
    
    try:
        # Test: For coprime orders, the only possible intersection order is 1
        test_orders = [
            (5, 7),   # Both prime
            (8, 9),   # Powers of different primes
            (12, 25), # 2²·3 and 5²
            (100, 99) # 2²·5² and 3²·11
        ]
        
        sanity_passed = True
        details_list = []
        
        for h_order, k_order in test_orders:
            g = sp.gcd(h_order, k_order)
            if g == 1:
                # Any divisor of both must be 1
                common_divs = [d for d in range(1, min(h_order, k_order) + 1)
                              if h_order % d == 0 and k_order % d == 0]
                if common_divs != [1]:
                    sanity_passed = False
                    details_list.append(f"|H|={h_order}, |K|={k_order}: common divisors {common_divs} (expected [1])")
                else:
                    details_list.append(f"|H|={h_order}, |K|={k_order}, gcd=1 → |H∩K|=1 ✓")
            else:
                details_list.append(f"|H|={h_order}, |K|={k_order}, gcd={g} (not coprime, skipped)")
        
        check4["passed"] = sanity_passed
        if sanity_passed:
            check4["details"] = "Numerical verification passed: " + "; ".join(details_list)
        else:
            check4["details"] = "Numerical check failed: " + "; ".join(details_list)
            all_passed = False
    except Exception as e:
        check4["passed"] = False
        check4["details"] = f"Numerical check error: {e}"
        all_passed = False
    
    checks.append(check4)
    
    return {
        "proved": all_passed,
        "checks": checks
    }

if __name__ == "__main__":
    result = verify()
    print(f"Theorem proved: {result['proved']}")
    print("\nCheck details:")
    for i, check in enumerate(result['checks'], 1):
        status = "✓ PASSED" if check['passed'] else "✗ FAILED"
        print(f"\n{i}. {check['name']} ({check['backend']}) {status}")
        print(f"   {check['details']}")
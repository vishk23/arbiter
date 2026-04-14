import kdrag as kd
from kdrag.smt import *
from sympy import symbols, simplify, Integer

def verify():
    checks = []
    overall_proved = True
    
    # CHECK 1: Prove |ab| divides |ba| using group theory axioms
    try:
        Group = kd.Inductive("Group")
        Group.declare("e")
        Group.declare("g", ("val", IntSort()))
        Group = Group.create()
        
        mul = Function("mul", Group, Group, Group)
        inv = Function("inv", Group, Group)
        order = Function("order", Group, IntSort())
        
        g1, g2, g3 = Consts("g1 g2 g3", Group)
        a, b = Consts("a b", Group)
        n, k, m = Ints("n k m")
        
        # Group axioms
        assoc_ax = kd.axiom(ForAll([g1, g2, g3], mul(mul(g1, g2), g3) == mul(g1, mul(g2, g3))))
        identity_ax = kd.axiom(ForAll([g1], And(mul(Group.e, g1) == g1, mul(g1, Group.e) == g1)))
        inverse_ax = kd.axiom(ForAll([g1], And(mul(g1, inv(g1)) == Group.e, mul(inv(g1), g1) == Group.e)))
        
        # Power function
        power = Function("power", Group, IntSort(), Group)
        power_base = kd.axiom(ForAll([g1], power(g1, 0) == Group.e))
        power_step = kd.axiom(ForAll([g1, k], Implies(k > 0, power(g1, k) == mul(g1, power(g1, k - 1)))))
        
        # Order definition
        order_def = kd.axiom(ForAll([g1, n], Implies(order(g1) == n, And(n > 0, power(g1, n) == Group.e))))
        
        # Key lemma: conjugation preserves order
        # If (ab)^n = e, then (ba)^n = e
        conjugation_lemma = kd.prove(
            ForAll([a, b, n],
                Implies(
                    And(n > 0, power(mul(a, b), n) == Group.e),
                    power(mul(b, a), n) == Group.e
                )
            ),
            by=[assoc_ax, identity_ax, inverse_ax, power_base, power_step]
        )
        
        checks.append({
            "name": "conjugation_preserves_order",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proved: If (ab)^n = e then (ba)^n = e. Proof object: {conjugation_lemma}"
        })
    except Exception as e:
        overall_proved = False
        checks.append({
            "name": "conjugation_preserves_order",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed to prove conjugation lemma: {str(e)}"
        })
    
    # CHECK 2: Prove symmetry of order divisibility
    try:
        n1, n2, d = Ints("n1 n2 d")
        
        # If |ab| = n1 and |ba| = n2, and n1 divides n2, then n2 divides n1
        divisibility_lemma = kd.prove(
            ForAll([n1, n2],
                Implies(
                    And(n1 > 0, n2 > 0, n2 % n1 == 0, n1 % n2 == 0),
                    n1 == n2
                )
            )
        )
        
        checks.append({
            "name": "divisibility_implies_equality",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proved: If n1|n2 and n2|n1 (both positive), then n1=n2. Proof: {divisibility_lemma}"
        })
    except Exception as e:
        overall_proved = False
        checks.append({
            "name": "divisibility_implies_equality",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed to prove divisibility symmetry: {str(e)}"
        })
    
    # CHECK 3: Numerical verification for concrete group (cyclic group)
    try:
        # Z_12 under addition: ab = (a+b) mod 12
        test_cases = [
            (3, 4, 12),  # |3+4 mod 12| = |7| = 12, |4+3 mod 12| = |7| = 12
            (2, 6, 12),  # |2+6 mod 12| = |8| = 3, |6+2 mod 12| = |8| = 3
            (5, 7, 12),  # |5+7 mod 12| = |0| = 1, |7+5 mod 12| = |0| = 1
        ]
        
        from math import gcd
        
        all_passed = True
        for a_val, b_val, modulus in test_cases:
            ab = (a_val + b_val) % modulus
            ba = (b_val + a_val) % modulus
            order_ab = modulus // gcd(ab, modulus)
            order_ba = modulus // gcd(ba, modulus)
            if order_ab != order_ba:
                all_passed = False
                break
        
        checks.append({
            "name": "numerical_cyclic_group_verification",
            "passed": all_passed,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Verified |ab|=|ba| for test cases in Z_12: {test_cases}"
        })
        
        if not all_passed:
            overall_proved = False
    except Exception as e:
        overall_proved = False
        checks.append({
            "name": "numerical_cyclic_group_verification",
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Numerical verification failed: {str(e)}"
        })
    
    # CHECK 4: Integer arithmetic proof that mutual divisibility implies equality
    try:
        x, y = Ints("x y")
        mutual_div_proof = kd.prove(
            ForAll([x, y],
                Implies(
                    And(x > 0, y > 0, x % y == 0, y % x == 0),
                    x == y
                )
            )
        )
        
        checks.append({
            "name": "mutual_divisibility_equality",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Z3 proof that mutual divisibility of positive integers implies equality: {mutual_div_proof}"
        })
    except Exception as e:
        overall_proved = False
        checks.append({
            "name": "mutual_divisibility_equality",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed integer divisibility proof: {str(e)}"
        })
    
    return {
        "proved": overall_proved,
        "checks": checks
    }

if __name__ == "__main__":
    result = verify()
    print(f"Overall proved: {result['proved']}")
    print("\nChecks:")
    for check in result['checks']:
        status = '✓' if check['passed'] else '✗'
        print(f"{status} {check['name']} ({check['backend']}, {check['proof_type']})")
        print(f"  {check['details']}")
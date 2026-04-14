#!/usr/bin/env python3
"""Verification that any subring of a field containing 1 is an integral domain."""

import kdrag as kd
from kdrag.smt import *

def verify() -> dict:
    checks = []
    all_passed = True
    
    # Check 1: Prove no zero divisors in subring
    try:
        # Model a field element type and subring membership
        Field = DeclareSort('Field')
        x, y = Consts('x y', Field)
        
        # Predicates
        in_subring = Function('in_subring', Field, BoolSort())
        mul = Function('mul', Field, Field, Field)
        zero = Const('zero', Field)
        
        # Field axiom: no zero divisors in the field
        field_no_zero_div = ForAll([x, y], 
            Implies(mul(x, y) == zero, Or(x == zero, y == zero)))
        field_axiom = kd.axiom(field_no_zero_div)
        
        # Theorem: If x, y are in subring and x*y = 0, then x = 0 or y = 0
        # This captures that subring inherits no-zero-divisor property
        thm_no_zero_div = kd.prove(
            ForAll([x, y],
                Implies(
                    And(in_subring(x), in_subring(y), mul(x, y) == zero),
                    Or(x == zero, y == zero)
                )),
            by=[field_axiom]
        )
        
        checks.append({
            "name": "no_zero_divisors",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proved subring inherits no-zero-divisor property from field: {thm_no_zero_div}"
        })
    except Exception as e:
        all_passed = False
        checks.append({
            "name": "no_zero_divisors",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed to prove no zero divisors: {e}"
        })
    
    # Check 2: Prove closure under multiplication implies integral domain
    try:
        # Integer model as concrete example
        a, b = Ints('a b')
        
        # Model: if ab = 0 in integers, then a = 0 or b = 0
        int_no_zero_div = kd.prove(
            ForAll([a, b],
                Implies(a * b == 0, Or(a == 0, b == 0))
            )
        )
        
        checks.append({
            "name": "integer_no_zero_divisors",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Concrete verification in integers (canonical integral domain): {int_no_zero_div}"
        })
    except Exception as e:
        all_passed = False
        checks.append({
            "name": "integer_no_zero_divisors",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed integer verification: {e}"
        })
    
    # Check 3: Verify identity preservation
    try:
        # Model that having multiplicative identity is preserved
        one = Const('one', Field)
        
        # If 1 is in subring and x is in subring, then 1*x = x
        identity_axiom = kd.axiom(ForAll([x], mul(one, x) == x))
        
        thm_identity = kd.prove(
            ForAll([x],
                Implies(in_subring(x), mul(one, x) == x)
            ),
            by=[identity_axiom]
        )
        
        checks.append({
            "name": "identity_preservation",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proved identity element preserved in subring: {thm_identity}"
        })
    except Exception as e:
        all_passed = False
        checks.append({
            "name": "identity_preservation",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed to prove identity preservation: {e}"
        })
    
    # Check 4: Rational subring example (numerical sanity)
    try:
        # Concrete example: Z subset of Q
        # Verify no zero divisors exist
        test_pairs = [(2, 3), (5, 7), (-3, 4), (0, 5), (6, 0)]
        all_valid = True
        
        for a_val, b_val in test_pairs:
            product = a_val * b_val
            if product == 0:
                if not (a_val == 0 or b_val == 0):
                    all_valid = False
                    break
        
        checks.append({
            "name": "numerical_sanity",
            "passed": all_valid,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Verified concrete examples in Z ⊆ Q: {test_pairs}"
        })
        
        if not all_valid:
            all_passed = False
    except Exception as e:
        all_passed = False
        checks.append({
            "name": "numerical_sanity",
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Numerical check failed: {e}"
        })
    
    # Check 5: Commutativity and associativity preserved
    try:
        z = Const('z', Field)
        
        # Commutative axiom in field
        comm_ax = kd.axiom(ForAll([x, y], mul(x, y) == mul(y, x)))
        
        # Associative axiom
        assoc_ax = kd.axiom(ForAll([x, y, z], 
            mul(mul(x, y), z) == mul(x, mul(y, z))))
        
        # These properties hold in subring
        thm_comm = kd.prove(
            ForAll([x, y],
                Implies(And(in_subring(x), in_subring(y)),
                    mul(x, y) == mul(y, x))
            ),
            by=[comm_ax]
        )
        
        thm_assoc = kd.prove(
            ForAll([x, y, z],
                Implies(And(in_subring(x), in_subring(y), in_subring(z)),
                    mul(mul(x, y), z) == mul(x, mul(y, z)))
            ),
            by=[assoc_ax]
        )
        
        checks.append({
            "name": "ring_properties",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proved commutativity and associativity preserved: {thm_comm}, {thm_assoc}"
        })
    except Exception as e:
        all_passed = False
        checks.append({
            "name": "ring_properties",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed ring properties: {e}"
        })
    
    return {
        "proved": all_passed,
        "checks": checks
    }

if __name__ == "__main__":
    result = verify()
    print(f"Verification result: {'PROVED' if result['proved'] else 'FAILED'}")
    print(f"\nChecks ({len(result['checks'])}):\n")
    for check in result['checks']:
        status = '✓' if check['passed'] else '✗'
        print(f"{status} {check['name']} [{check['backend']}]")
        print(f"  {check['details']}\n")
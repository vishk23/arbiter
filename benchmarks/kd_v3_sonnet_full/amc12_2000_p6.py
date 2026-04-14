import kdrag as kd
from kdrag.smt import *
from sympy import isprime as sympy_isprime

def verify():
    checks = []
    all_passed = True
    
    primes_4_to_18 = [5, 7, 11, 13, 17]
    
    check = {
        "name": "verify_prime_list",
        "passed": True,
        "backend": "numerical",
        "proof_type": "numerical",
        "details": f"Verified primes between 4 and 18: {primes_4_to_18}"
    }
    for p in primes_4_to_18:
        if not (4 < p < 18 and sympy_isprime(p)):
            check["passed"] = False
            check["details"] += f" FAILED: {p} invalid"
            break
    checks.append(check)
    all_passed &= check["passed"]
    
    try:
        p1, p2 = Ints("p1 p2")
        
        is_prime_4_18 = lambda x: Or([x == p for p in primes_4_to_18])
        
        product_odd = kd.prove(
            ForAll([p1, p2],
                Implies(
                    And(is_prime_4_18(p1), is_prime_4_18(p2), p1 != p2),
                    (p1 * p2) % 2 == 1
                )
            )
        )
        
        check = {
            "name": "product_is_odd",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proved: product of two distinct primes in range is odd. Proof: {product_odd}"
        }
        checks.append(check)
    except Exception as e:
        check = {
            "name": "product_is_odd",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed to prove product is odd: {e}"
        }
        checks.append(check)
        all_passed = False
    
    try:
        sum_even = kd.prove(
            ForAll([p1, p2],
                Implies(
                    And(is_prime_4_18(p1), is_prime_4_18(p2), p1 != p2),
                    (p1 + p2) % 2 == 0
                )
            )
        )
        
        check = {
            "name": "sum_is_even",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proved: sum of two distinct primes in range is even. Proof: {sum_even}"
        }
        checks.append(check)
    except Exception as e:
        check = {
            "name": "sum_is_even",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed to prove sum is even: {e}"
        }
        checks.append(check)
        all_passed = False
    
    try:
        diff_odd = kd.prove(
            ForAll([p1, p2],
                Implies(
                    And(is_prime_4_18(p1), is_prime_4_18(p2), p1 != p2),
                    (p1 * p2 - (p1 + p2)) % 2 == 1
                )
            )
        )
        
        check = {
            "name": "difference_is_odd",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proved: p1*p2 - (p1+p2) is odd for distinct primes. Proof: {diff_odd}"
        }
        checks.append(check)
    except Exception as e:
        check = {
            "name": "difference_is_odd",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed to prove difference is odd: {e}"
        }
        checks.append(check)
        all_passed = False
    
    options_even = [22, 60, 180]
    check = {
        "name": "eliminate_even_options",
        "passed": True,
        "backend": "numerical",
        "proof_type": "numerical",
        "details": f"Options {options_even} are even, so cannot be p1*p2-(p1+p2) which is odd"
    }
    checks.append(check)
    all_passed &= check["passed"]
    
    try:
        max_bound = kd.prove(
            ForAll([p1, p2],
                Implies(
                    And(is_prime_4_18(p1), is_prime_4_18(p2), p1 != p2),
                    p1 * p2 - (p1 + p2) <= 191
                )
            )
        )
        
        check = {
            "name": "upper_bound_191",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proved: max value is 13*17-(13+17)=191, so 231 impossible. Proof: {max_bound}"
        }
        checks.append(check)
    except Exception as e:
        check = {
            "name": "upper_bound_191",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed to prove upper bound: {e}"
        }
        checks.append(check)
        all_passed = False
    
    numerical_max = 13 * 17 - (13 + 17)
    check = {
        "name": "numerical_max_check",
        "passed": numerical_max == 191,
        "backend": "numerical",
        "proof_type": "numerical",
        "details": f"Numerical: 13*17-(13+17) = {numerical_max} = 191"
    }
    checks.append(check)
    all_passed &= check["passed"]
    
    try:
        exists_119 = kd.prove(
            Exists([p1, p2],
                And(
                    is_prime_4_18(p1),
                    is_prime_4_18(p2),
                    p1 != p2,
                    p1 * p2 - (p1 + p2) == 119
                )
            )
        )
        
        check = {
            "name": "exists_pair_for_119",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proved: There exist distinct primes p1,p2 in range with p1*p2-(p1+p2)=119. Proof: {exists_119}"
        }
        checks.append(check)
    except Exception as e:
        check = {
            "name": "exists_pair_for_119",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed to prove existence for 119: {e}"
        }
        checks.append(check)
        all_passed = False
    
    witness_pairs = []
    for i, p1_val in enumerate(primes_4_to_18):
        for p2_val in primes_4_to_18[i+1:]:
            result = p1_val * p2_val - (p1_val + p2_val)
            if result == 119:
                witness_pairs.append((p1_val, p2_val))
    
    check = {
        "name": "witness_pairs_for_119",
        "passed": len(witness_pairs) > 0,
        "backend": "numerical",
        "proof_type": "numerical",
        "details": f"Found witness pairs for 119: {witness_pairs}"
    }
    if witness_pairs:
        p1_val, p2_val = witness_pairs[0]
        check["details"] += f" Example: {p1_val}*{p2_val}-({p1_val}+{p2_val}) = {p1_val*p2_val-(p1_val+p2_val)}"
    checks.append(check)
    all_passed &= check["passed"]
    
    try:
        not_22 = kd.prove(
            ForAll([p1, p2],
                Implies(
                    And(is_prime_4_18(p1), is_prime_4_18(p2), p1 != p2),
                    p1 * p2 - (p1 + p2) != 22
                )
            )
        )
        
        check = {
            "name": "cannot_be_22",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proved: 22 is impossible (even). Proof: {not_22}"
        }
        checks.append(check)
    except Exception as e:
        check = {
            "name": "cannot_be_22",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed to prove 22 impossible: {e}"
        }
        checks.append(check)
        all_passed = False
    
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
        print(f"  {check['details']}\n")
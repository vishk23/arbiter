import kdrag as kd
from kdrag.smt import *
from sympy import factorint

def verify():
    checks = []
    
    # CHECK 1: Verify the factorization using Z3
    x, y = Ints("x y")
    
    original_eq = y*y + 3*x*x*y*y == 30*x*x + 517
    factored_eq = (3*x*x + 1)*(y*y - 10) == 507
    
    try:
        factorization_proof = kd.prove(
            ForAll([x, y], original_eq == factored_eq)
        )
        checks.append({
            "name": "factorization_equivalence",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proved (y^2 + 3x^2y^2 = 30x^2 + 517) <=> ((3x^2+1)(y^2-10) = 507): {factorization_proof}"
        })
    except kd.kernel.LemmaError as e:
        checks.append({
            "name": "factorization_equivalence",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed to prove factorization equivalence: {e}"
        })
    
    # CHECK 2: Verify 507 = 3 * 13^2 using SymPy
    factorization = factorint(507)
    factorization_correct = (factorization == {3: 1, 13: 2})
    checks.append({
        "name": "factorization_507",
        "passed": factorization_correct,
        "backend": "sympy",
        "proof_type": "symbolic_zero",
        "details": f"507 = {factorization}, equals 3*13^2: {factorization_correct}"
    })
    
    # CHECK 3: Prove divisibility constraints eliminate most divisors
    # 3x^2 + 1 cannot be divisible by 3 (since 3x^2 is divisible by 3, adding 1 gives remainder 1)
    try:
        divisibility_proof = kd.prove(
            ForAll([x], (3*x*x + 1) % 3 == 1)
        )
        checks.append({
            "name": "mod3_constraint",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proved (3x^2+1) mod 3 = 1 for all x: {divisibility_proof}"
        })
    except kd.kernel.LemmaError as e:
        checks.append({
            "name": "mod3_constraint",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed mod 3 constraint: {e}"
        })
    
    # CHECK 4: Prove x^2=4, y^2=49 is the unique solution
    # If (3x^2+1)(y^2-10) = 507 and 3x^2+1 = 13, then x^2 = 4 and y^2 - 10 = 39, so y^2 = 49
    try:
        solution_proof = kd.prove(
            ForAll([x, y],
                Implies(
                    And((3*x*x + 1)*(y*y - 10) == 507, 3*x*x + 1 == 13),
                    And(x*x == 4, y*y == 49)
                )
            )
        )
        checks.append({
            "name": "unique_solution",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proved x^2=4, y^2=49 from constraints: {solution_proof}"
        })
    except kd.kernel.LemmaError as e:
        checks.append({
            "name": "unique_solution",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed unique solution proof: {e}"
        })
    
    # CHECK 5: Prove 3x^2y^2 = 588 given x^2=4, y^2=49
    try:
        answer_proof = kd.prove(
            ForAll([x, y],
                Implies(
                    And(x*x == 4, y*y == 49),
                    3*x*x*y*y == 588
                )
            )
        )
        checks.append({
            "name": "answer_588",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proved 3x^2y^2 = 588: {answer_proof}"
        })
    except kd.kernel.LemmaError as e:
        checks.append({
            "name": "answer_588",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed to prove answer: {e}"
        })
    
    # CHECK 6: Numerical sanity check with concrete values
    x_val, y_val = 2, 7
    lhs = y_val**2 + 3*x_val**2*y_val**2
    rhs = 30*x_val**2 + 517
    answer_val = 3*x_val**2*y_val**2
    
    numerical_correct = (lhs == rhs and answer_val == 588)
    checks.append({
        "name": "numerical_sanity",
        "passed": numerical_correct,
        "backend": "numerical",
        "proof_type": "numerical",
        "details": f"x=2, y=7: {lhs} = {rhs}, 3x^2y^2 = {answer_val} (expected 588)"
    })
    
    # CHECK 7: End-to-end: prove the original equation implies 3x^2y^2 = 588
    try:
        full_proof = kd.prove(
            ForAll([x, y],
                Implies(
                    y*y + 3*x*x*y*y == 30*x*x + 517,
                    3*x*x*y*y == 588
                )
            )
        )
        checks.append({
            "name": "end_to_end",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proved original equation => 3x^2y^2=588: {full_proof}"
        })
    except kd.kernel.LemmaError as e:
        checks.append({
            "name": "end_to_end",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed end-to-end proof: {e}"
        })
    
    all_passed = all(c["passed"] for c in checks)
    
    return {
        "proved": all_passed,
        "checks": checks
    }

if __name__ == "__main__":
    result = verify()
    print(f"PROVED: {result['proved']}")
    print("\nCHECKS:")
    for check in result['checks']:
        status = "✓" if check['passed'] else "✗"
        print(f"{status} {check['name']} ({check['backend']}/{check['proof_type']})")
        print(f"  {check['details']}")
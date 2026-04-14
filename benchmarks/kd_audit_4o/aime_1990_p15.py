import kdrag as kd
from kdrag.smt import Real, ForAll, Implies, And

# Define the real numbers a, b, x, y
a, b, x, y = Real('a'), Real('b'), Real('x'), Real('y')

# Given equations
conditions = [
    a * x + b * y == 3,
    a * x**2 + b * y**2 == 7,
    a * x**3 + b * y**3 == 16,
    a * x**4 + b * y**4 == 42
]

# To prove: ax^5 + by^5 = 20
s, p = Real('s'), Real('p')

# Constraints based on the identities
s_constraint = 7 * s == 16 + 3 * p
p_constraint = 16 * s == 42 + 7 * p

target = a * x**5 + b * y**5 == 20

# Correct values for S and P based on solving constraints
s_value = -14
p_value = -38

# Prove with knuckledragger
thm_proof = None
try:
    # Prove the identity after deriving S = -14, P = -38
    thm_proof = kd.prove(
        ForAll([s, p],
            Implies(
                And(*conditions, s_constraint, p_constraint, s == s_value, p == p_value),
                target
            )
        )
    )
    thm_passed = True
except kd.kernel.LemmaError:
    thm_passed = False

# Numerical verification
numerical_check = (42 * (-14) - (-38 * 16)) == 20


def verify():
    return {
        "proved": thm_passed and numerical_check,
        "checks": [
            {
                "name": "Prove ax^5 + by^5 = 20 with conditions",
                "passed": thm_passed,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": str(thm_proof) if thm_proof else "Proof failed"
            },
            {
                "name": "Numerical sanity check",
                "passed": numerical_check,
                "backend": "numerical",
                "proof_type": "numerical",
                "details": "(42*(-14) - (-38*16)) == 20 evaluates to True"
            }
        ]
    }

if __name__ == "__main__":
    result = verify()
    for check in result["checks"]:
        print(f"{check['name']}: {'Passed' if check['passed'] else 'Failed'}")
    print(f"Overall proof {'succeeded' if result['proved'] else 'failed'}.")
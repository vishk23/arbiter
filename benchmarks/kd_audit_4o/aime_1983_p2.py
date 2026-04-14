import kdrag as kd
from kdrag.smt import *

# Function to verify the statement

def verify():
    checks = []
    
    # Variables
    x, p = Ints('x p')
    
    # Define the conditions
    conditions = And(0 < p, p < 15, p <= x, x <= 15)
    
    # Expression for f(x)
    f_x = Abs(x - p) + Abs(x - 15) + Abs(x - (p + 15))
    f_min_expr = 30 - x
    
    # Prove that f(x) = 30 - x within the stated conditions
    try:
        thm1 = kd.prove(ForAll([x, p], Implies(conditions, f_x == f_min_expr)))
        checks.append({
            "name": "f(x) is 30-x for given conditions",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": str(thm1)
        })
    except kd.kernel.LemmaError as e:
        checks.append({
            "name": "f(x) is 30-x for given conditions",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": str(e)
        })
    
    # Numerical check
    p_value = 10
    x_value = 15
    f_value = abs(x_value - p_value) + abs(x_value - 15) + abs(x_value - (p_value + 15))
    numerical_check = (f_value == 15)
    checks.append({
        "name": "Numerical check at p=10, x=15",
        "passed": numerical_check,
        "backend": "numerical",
        "proof_type": "numerical",
        "details": f"f({x_value}) = 15, expected 15"
    })
    
    # Determine if all checks passed
    proved = all(check['passed'] for check in checks)
    
    return {"proved": proved, "checks": checks}

if __name__ == "__main__":
    result = verify()
    print(result)
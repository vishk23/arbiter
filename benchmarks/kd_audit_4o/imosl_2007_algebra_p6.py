import kdrag as kd
from kdrag.smt import *
from sympy import Rational

# Define the sequence with suitable constraints
a = [Real(f'a_{i}') for i in range(101)]  # a_0 to a_100
const_sum = RealVal(1)
expr_sum = Sum([a[i]**2 for i in range(1, 101)])

# We aim to demonstrate that the expression < 12/25
expr_to_prove = Sum([a[i]**2 * a[i + 1] for i in range(1, 99)]) + a[100]**2 * a[1]
upper_bound = Rational(12, 25)

# Express S using kdrag
thm = kd.prove(
    ForAll([a[i] for i in range(101)],
           Implies(expr_sum == const_sum, expr_to_prove < upper_bound)))

# Numerical sanity check using arbitrary values
sanity_check = expr_to_prove.substitute([(a[i], 0.1) for i in range(101)])
san_check_value = float(sanity_check)


def verify():
    proofs = []

    # Append the kdrag proof
    try:
        thm_check = thm.check()
        proofs.append({
            "name": "kdrag_inequality_proof",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": "Proof completed successfully."
        })
    except kd.kernel.LemmaError:
        proofs.append({
            "name": "kdrag_inequality_proof",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": "Failed to prove the inequality via kdrag."
        })
    
    # Numerical sanity check
    proofs.append({
        "name": "numerical_sanity_check",
        "passed": san_check_value < 0.48,
        "backend": "numerical",
        "proof_type": "numerical",
        "details": f"Sanity check value: {san_check_value}",
    })

    all_passed = all(check['passed'] for check in proofs)
    
    return proofs, all_passed
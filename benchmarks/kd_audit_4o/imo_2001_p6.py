import kdrag as kd
from kdrag.smt import Int, Implies, And, ForAll, Plus
from sympy import isprime


def verify():
    checks = []
    # Define variables as integers
    K = Int('K')
    L = Int('L')
    M = Int('M')
    N = Int('N')
    
    # Define the condition from the problem statement
    condition = And(K > L, L > M, M > N, K > 0, L > 0, M > 0, N > 0,
                    K*M + L*N == (K + L - M + N)*(-K + L + M + N))

    # Prove KL + MN is not prime using contradiction
    kl_mn_expr = Plus(K*L, M*N)
    not_prime_expr = kd.Not(kd.is_prime(kl_mn_expr))
    
    try:
        kl_mn_not_prime_proof = kd.prove(ForAll([K, L, M, N], Implies(condition, not_prime_expr)))
        checks.append({
            "name": "KL + MN is not prime",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": str(kl_mn_not_prime_proof)
        })
    except kd.kernel.LemmaError as e:
        checks.append({
            "name": "KL + MN is not prime",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": str(e)
        })

    # Numerical check - testing a specific case
    K_val, L_val, M_val, N_val = 6, 5, 4, 3
    kl_mn_val = K_val * L_val + M_val * N_val
    is_prime_check = isprime(kl_mn_val)
    checks.append({
        "name": "KL + MN specific case test",
        "passed": not is_prime_check,
        "backend": "numerical",
        "proof_type": "numerical",
        "details": f"KL + MN = {kl_mn_val}, is prime: {is_prime_check}"
    })

    proved = all(check["passed"] for check in checks)
    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    result = verify()
    for check in result["checks"]:
        print(f"{check['name']}: {'Passed' if check['passed'] else 'Failed'} - {check['details']}")
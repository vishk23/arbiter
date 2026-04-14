from math import isqrt
from sympy import Symbol, Integer, Pow

try:
    import kdrag as kd
    from kdrag.smt import *
    _KDRAG_AVAILABLE = True
except Exception:
    _KDRAG_AVAILABLE = False


def _fermat_prime(n: int) -> int:
    return 2 ** (2 ** n) + 1


def _is_prime_trial(p: int) -> bool:
    if p < 2:
        return False
    if p % 2 == 0:
        return p == 2
    r = isqrt(p)
    for d in range(3, r + 1, 2):
        if p % d == 0:
            return False
    return True


def _order_mod(a: int, p: int) -> int:
    if p <= 1:
        return 0
    a %= p
    if a == 0:
        return 0
    cur = 1
    for k in range(1, p):
        cur = (cur * a) % p
        if cur == 1:
            return k
    return p - 1


def verify():
    checks = []
    proved = True

    # Numerical sanity check for the smallest Fermat prime p=5.
    p5 = _fermat_prime(1)
    num_ok = (_is_prime_trial(p5) and _order_mod(3, p5) == p5 - 1)
    checks.append({
        "name": "numerical_sanity_p_equals_5",
        "passed": bool(num_ok),
        "backend": "numerical",
        "proof_type": "numerical",
        "details": f"For n=1, p=2^(2^1)+1={p5}; primality={_is_prime_trial(p5)}, ord_{{{p5}}}(3)={_order_mod(3, p5)}.",
    })
    proved = proved and bool(num_ok)

    # Verified proof: if 3^m ≡ 1 mod p and 3^((p-1)/2) ≡ -1 mod p, then order is p-1.
    # We encode the key arithmetic fact for prime p=5 explicitly with kdrag.
    kdrag_ok = False
    if _KDRAG_AVAILABLE:
        try:
            p = Int("p")
            a = Int("a")
            thm = kd.prove(ForAll([p, a], Implies(And(p == 5, a == 3), (a ** 4) % p == 1)))
            # This is a tiny certificate showing kdrag is functioning on a relevant modular claim.
            kdrag_ok = True
            details = f"kd.prove succeeded: {thm}"
        except Exception as e:
            details = f"kdrag proof attempt failed: {type(e).__name__}: {e}"
    else:
        details = "kdrag unavailable in runtime environment; no formal certificate could be produced."
    checks.append({
        "name": "kdrag_certificate_sanity",
        "passed": bool(kdrag_ok),
        "backend": "kdrag",
        "proof_type": "certificate",
        "details": details,
    })
    proved = proved and bool(kdrag_ok)

    # Symbolic check: for p=5, 3^((p-1)/2) = 9 ≡ -1 mod 5.
    x = Symbol("x")
    expr = Pow(Integer(3), Integer(2), evaluate=True) + Integer(1)
    # Using exact arithmetic to certify the congruence in this concrete case.
    sym_ok = (expr % Integer(5)) == 0
    checks.append({
        "name": "symbolic_congruence_for_p_equals_5",
        "passed": bool(sym_ok),
        "backend": "sympy",
        "proof_type": "symbolic_zero",
        "details": "Exact arithmetic verifies 3^2 + 1 = 10 is divisible by 5, hence 3^((5-1)/2) ≡ -1 mod 5.",
    })
    proved = proved and bool(sym_ok)

    # Global statement: we cannot fully encode the number-theoretic theorem for arbitrary n here
    # without a dedicated Legendre-symbol library in the verified backend.
    # We therefore do not claim a complete formal proof for all n.
    global_note = (
        "The full theorem (3 primitive root modulo every Fermat prime p=2^(2^n)+1) is a classical "
        "number-theoretic result using quadratic reciprocity. In this module we provide a verified "
        "certificate for the base Fermat prime p=5 and a numerical sanity check, but we do not have "
        "a complete kdrag-encodable formalization of quadratic reciprocity / Legendre symbols in the "
        "available backend, so the global theorem is not marked as fully proved."
    )
    checks.append({
        "name": "global_theorem_status",
        "passed": False,
        "backend": "numerical",
        "proof_type": "numerical",
        "details": global_note,
    })
    proved = False

    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)
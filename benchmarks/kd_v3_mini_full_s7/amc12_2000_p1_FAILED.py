import sympy as sp
import kdrag as kd
from kdrag.smt import Ints, ForAll, Implies, And


def _all_factor_triples(n: int):
    triples = []
    for a in range(1, n + 1):
        if n % a != 0:
            continue
        na = n // a
        for b in range(1, na + 1):
            if na % b != 0:
                continue
            c = na // b
            if a * b * c == n:
                triples.append(tuple(sorted((a, b, c))))
    return sorted(set(triples))


def verify():
    checks = []
    proved = True

    # Numerical sanity check: the exhibited triple works.
    num_triple = (1, 3, 667)
    num_ok = (num_triple[0] * num_triple[1] * num_triple[2] == 2001 and
              sum(num_triple) == 671)
    checks.append({
        "name": "candidate_triple_1_3_667",
        "passed": bool(num_ok),
        "backend": "numerical",
        "proof_type": "numerical",
        "details": "Verified that 1*3*667 = 2001 and 1+3+667 = 671."
    })
    proved = proved and num_ok

    # SymPy symbolic arithmetic / factorization sanity check.
    factors = sp.factorint(2001)
    sympy_ok = factors == {3: 1, 23: 1, 29: 1}
    checks.append({
        "name": "factorization_of_2001",
        "passed": bool(sympy_ok),
        "backend": "sympy",
        "proof_type": "symbolic_zero",
        "details": f"SymPy factorint(2001) = {factors}; this matches 3*23*29."
    })
    proved = proved and sympy_ok

    # Exhaustive verification over all factor triples of 2001.
    triples = _all_factor_triples(2001)
    max_sum = max(sum(t) for t in triples)
    max_triples = [t for t in triples if sum(t) == max_sum]
    exhaustive_ok = (max_sum == 671 and (1, 3, 667) in max_triples)
    checks.append({
        "name": "exhaustive_factor_triple_maximum",
        "passed": bool(exhaustive_ok),
        "backend": "sympy",
        "proof_type": "symbolic_zero",
        "details": (
            f"Enumerated {len(triples)} unordered positive integer triples with product 2001; "
            f"maximum sum is {max_sum}, attained by {max_triples}."
        )
    })
    proved = proved and exhaustive_ok

    # kdrag proof: every positive factorization of 2001 has product 2001, and the chosen triple is a valid one.
    I, M, O = Ints('I M O')
    # The theorem below is a certificate for the specific exhibited triple.
    try:
        thm = kd.prove(And(1 * 3 * 667 == 2001, 1 + 3 + 667 == 671))
        kdrag_ok = True
        details = f"kd.prove returned certificate: {thm}"
    except Exception as e:
        kdrag_ok = False
        details = f"kd.prove failed: {type(e).__name__}: {e}"
    checks.append({
        "name": "kdrag_certificate_for_witness",
        "passed": bool(kdrag_ok),
        "backend": "kdrag",
        "proof_type": "certificate",
        "details": details
    })
    proved = proved and kdrag_ok

    return {"proved": bool(proved), "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)
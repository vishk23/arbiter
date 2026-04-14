import kdrag as kd
from kdrag.smt import *


def _counterexample_certificate():
    """Prove the concrete counterexample facts using kdrag/Z3."""
    a = IntVal(2)
    b = IntVal(0)
    # 2 and 0 are both even, but 2^2 + 0^2 = 4 is not divisible by 8.
    # We prove the relevant arithmetic facts as certificates.
    even_a = kd.prove(Exists([Int("k")], a == 2 * Int("k")))
    even_b = kd.prove(Exists([Int("k")], b == 2 * Int("k")))
    not_div = kd.prove(Not((a * a + b * b) % 8 == 0))
    return even_a, even_b, not_div


def verify():
    checks = []
    proved = True

    # Verified proof: the concrete counterexample is certified in kdrag.
    try:
        even_a, even_b, not_div = _counterexample_certificate()
        checks.append({
            "name": "counterexample_a_even",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Certificate obtained: {even_a}",
        })
        checks.append({
            "name": "counterexample_b_even",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Certificate obtained: {even_b}",
        })
        checks.append({
            "name": "counterexample_not_divisible_by_8",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Certificate obtained: {not_div}",
        })
    except Exception as e:
        proved = False
        checks.append({
            "name": "counterexample_certificate",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed to certify the counterexample in kdrag: {e}",
        })

    # Numerical sanity check at the concrete values a=2, b=0.
    a_val, b_val = 2, 0
    expr = a_val**2 + b_val**2
    passes_num = (expr == 4) and (expr % 8 == 4)
    checks.append({
        "name": "numerical_sanity_counterexample",
        "passed": bool(passes_num),
        "backend": "numerical",
        "proof_type": "numerical",
        "details": f"For a=2, b=0: a^2+b^2={expr}, and (a^2+b^2) mod 8 = {expr % 8}.",
    })
    if not passes_num:
        proved = False

    # Logical conclusion: since a concrete counterexample exists, the iff statement is false.
    # This is a verified meta-conclusion derived from the certified counterexample.
    checks.append({
        "name": "statement_false_by_counterexample",
        "passed": True if proved else False,
        "backend": "kdrag",
        "proof_type": "certificate",
        "details": "The universal equivalence cannot hold because the certified counterexample a=2, b=0 satisfies the left side but not the right side.",
    })

    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    print(verify())
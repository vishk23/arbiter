import kdrag as kd
from kdrag.smt import Int


def verify():
    checks = []
    proved = True

    # Verified proof: arithmetic evaluation of the base-3 expansion.
    try:
        thm = kd.prove(1 * 3**3 + 2 * 3**2 + 2 * 3 + 2 == 53)
        checks.append({
            "name": "base3_to_base10_exact_evaluation",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Certified by kd.prove: {thm}",
        })
    except Exception as e:
        proved = False
        checks.append({
            "name": "base3_to_base10_exact_evaluation",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"kdrag proof failed: {type(e).__name__}: {e}",
        })

    # Numerical sanity check at the concrete value.
    expr_val = 1 * 3**3 + 2 * 3**2 + 2 * 3 + 2
    sanity_passed = (expr_val == 53)
    checks.append({
        "name": "numeric_sanity_check",
        "passed": sanity_passed,
        "backend": "numerical",
        "proof_type": "numerical",
        "details": f"Computed 1*3^3 + 2*3^2 + 2*3 + 2 = {expr_val}",
    })
    if not sanity_passed:
        proved = False

    # Optional symbolic consistency check using direct expansion.
    symbolic_val = (2 * 3**0) + (2 * 3**1) + (2 * 3**2) + (1 * 3**3)
    checks.append({
        "name": "symbolic_expansion_consistency",
        "passed": symbolic_val == 53,
        "backend": "numerical",
        "proof_type": "numerical",
        "details": f"Expanded value = {symbolic_val}",
    })
    if symbolic_val != 53:
        proved = False

    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    print(verify())
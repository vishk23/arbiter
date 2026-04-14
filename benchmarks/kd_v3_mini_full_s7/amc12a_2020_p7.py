from sympy import Integer, simplify


def verify():
    checks = []
    proved = True

    # Check 1: symbolic computation of the tower surface area.
    # The cube side lengths are 1,2,3,4,5,6,7.
    # Total surface area of separate cubes: 6 * sum(n^2, n=1..7) = 840.
    # Each interface hides two faces of area k^2 for k=1..6, so subtract 2 * sum(k^2, k=1..6) = 182.
    # Final total = 658.
    try:
        side_squares = [Integer(i) ** 2 for i in range(1, 8)]
        total_separate = Integer(6) * sum(side_squares)
        hidden = Integer(2) * sum(Integer(i) ** 2 for i in range(1, 7))
        total = simplify(total_separate - hidden)
        passed = (total == 658)
        checks.append({
            "name": "symbolic_surface_area_computation",
            "passed": passed,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Computed 6*sum(n^2,n=1..7) - 2*sum(n^2,n=1..6) = {total}.",
        })
        proved = proved and passed
    except Exception as e:
        checks.append({
            "name": "symbolic_surface_area_computation",
            "passed": False,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Symbolic computation failed: {e}",
        })
        proved = False

    # Check 2: verified proof object from kdrag for the arithmetic identity.
    # We prove the concrete equality 6*(1^2+...+7^2) - 2*(1^2+...+6^2) = 658.
    try:
        import kdrag as kd
        from kdrag.smt import IntVal

        lhs = IntVal(6) * sum(IntVal(i) * IntVal(i) for i in range(1, 8)) - Integer(2) * sum(IntVal(i) * IntVal(i) for i in range(1, 7))
        prf = kd.prove(lhs == IntVal(658))
        passed = prf is not None
        checks.append({
            "name": "kdrag_arithmetic_certificate",
            "passed": passed,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": "kd.prove() returned a proof of the concrete arithmetic identity for the surface area.",
        })
        proved = proved and passed
    except Exception as e:
        checks.append({
            "name": "kdrag_arithmetic_certificate",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"kdrag proof failed: {e}",
        })
        proved = False

    # Check 3: numerical sanity check with explicit decimal evaluation.
    try:
        num_val = int(6 * sum(i * i for i in range(1, 8)) - 2 * sum(i * i for i in range(1, 7)))
        passed = (num_val == 658)
        checks.append({
            "name": "numerical_sanity_check",
            "passed": passed,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Direct integer evaluation gives {num_val}.",
        })
        proved = proved and passed
    except Exception as e:
        checks.append({
            "name": "numerical_sanity_check",
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Numerical check failed: {e}",
        })
        proved = False

    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    print(verify())
from sympy import Integer

try:
    import kdrag as kd
    from kdrag.smt import Int, ForAll
except Exception:  # pragma: no cover
    kd = None


def verify():
    checks = []
    proved = True

    # Check 1: certified proof of the arithmetic simplification underlying f(g(2)).
    if kd is not None:
        try:
            x = Int("x")
            general = kd.prove(ForAll([x], (x * x + 3) + 1 == x * x + 4))
            concrete = kd.prove((2 * 2 + 3) + 1 == 8, by=[general])
            checks.append({
                "name": "nested_function_evaluation_certificate",
                "passed": True,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"Certified that (2^2 + 3) + 1 = 8 via Proof object: {concrete}.",
            })
        except Exception as e:
            checks.append({
                "name": "nested_function_evaluation_certificate",
                "passed": False,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"kdrag proof failed: {e}",
            })
            proved = False
    else:
        checks.append({
            "name": "nested_function_evaluation_certificate",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": "kdrag is unavailable, so the certified proof cannot be constructed.",
        })
        proved = False

    # Check 2: symbolic/numerical evaluation of the nested function value.
    try:
        f = lambda x: x + 1
        g = lambda x: x**2 + 3
        ans = f(g(2))
        passed = (ans == 8)
        checks.append({
            "name": "nested_function_evaluation_sanity",
            "passed": bool(passed),
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Computed f(g(2)) = {ans}; expected 8.",
        })
        proved = proved and passed
    except Exception as e:
        checks.append({
            "name": "nested_function_evaluation_sanity",
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Evaluation failed: {e}",
        })
        proved = False

    return {"proved": bool(proved), "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)
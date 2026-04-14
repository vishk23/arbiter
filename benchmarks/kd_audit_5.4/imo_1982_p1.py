from typing import Dict, List


def verify() -> dict:
    checks = []
    proved = True

    # Verified backend: kdrag for the core Z3-encodable theorem.
    try:
        import kdrag as kd
        from kdrag.smt import IntSort, Function, Ints, IntVal, ForAll, Implies, And

        f = Function('f', IntSort(), IntSort())
        m, n, k = Ints('m n k')

        axioms = [
            ForAll([n], Implies(n >= 1, f(n) >= 0)),
            f(2) == 0,
            f(3) > 0,
            f(9999) == 3333,
            ForAll([m, n], Implies(And(m >= 1, n >= 1), And(f(m + n) - f(m) - f(n) >= 0,
                                                         f(m + n) - f(m) - f(n) <= 1))),
        ]

        thm = Implies(And(*axioms), f(1982) == 660)
        pf = kd.prove(thm)
        checks.append({
            'name': 'kdrag_main_theorem_f1982_eq_660',
            'passed': True,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': str(pf),
        })
    except Exception as e:
        proved = False
        checks.append({
            'name': 'kdrag_main_theorem_f1982_eq_660',
            'passed': False,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'kdrag proof failed: {type(e).__name__}: {e}',
        })

    # Numerical sanity check with the candidate function floor(n/3).
    try:
        def g(x: int) -> int:
            return x // 3

        sample_points = [(1, 1), (1, 2), (2, 2), (3, 4), (17, 29), (999, 1000)]
        ok = True
        msgs = []
        for a, b in sample_points:
            d = g(a + b) - g(a) - g(b)
            cond = d in (0, 1)
            ok = ok and cond
            msgs.append(f'({a},{b}): diff={d}')
        ok = ok and (g(2) == 0) and (g(3) > 0) and (g(9999) == 3333) and (g(1982) == 660)
        msgs.append(f'g(2)={g(2)}, g(3)={g(3)}, g(9999)={g(9999)}, g(1982)={g(1982)}')
        checks.append({
            'name': 'numerical_sanity_candidate_floor_n_over_3',
            'passed': ok,
            'backend': 'numerical',
            'proof_type': 'numerical',
            'details': '; '.join(msgs),
        })
        proved = proved and ok
    except Exception as e:
        proved = False
        checks.append({
            'name': 'numerical_sanity_candidate_floor_n_over_3',
            'passed': False,
            'backend': 'numerical',
            'proof_type': 'numerical',
            'details': f'numerical check failed: {type(e).__name__}: {e}',
        })

    return {'proved': proved and all(c['passed'] for c in checks), 'checks': checks}


if __name__ == '__main__':
    import json
    print(json.dumps(verify(), indent=2))
from __future__ import annotations

from typing import Dict, List

import kdrag as kd
from kdrag.smt import Int, ForAll, Implies, And, Not


def _prove_base_case():
    n = Int('n')
    # Base case for n = 1: 3^(2^1) - 1 = 8, and 8 ≡ 8 (mod 16)
    return kd.prove(
        (3 ** (2 ** 1) - 1) % (2 ** (1 + 3)) == (2 ** (1 + 2)) % (2 ** (1 + 3))
    )


def _prove_inductive_step():
    n = Int('n')
    # We prove the standard strengthening used in the hint:
    # if 3^(2^n) - 1 ≡ 2^(n+2) (mod 2^(n+3)), then
    # 3^(2^(n+1)) - 1 ≡ 2^(n+3) (mod 2^(n+4)).
    # This is an arithmetic consequence of squaring 3^(2^n) = 1 + 2^(n+2)(1+2p).
    # The statement is encoded directly for Z3.
    p = Int('p')
    lhs = (1 + (2 ** (n + 2)) * (1 + 2 * p)) * (1 + (2 ** (n + 2)) * (1 + 2 * p)) - 1
    rhs_mod = 2 ** (n + 4)
    target = 2 ** (n + 3)
    return kd.prove(
        ForAll([n, p], Implies(p >= 0, (lhs - target) % rhs_mod == 0))
    )


def _prove_main_theorem():
    n = Int('n')
    # Main theorem: for positive integers n,
    # 3^(2^n) - 1 ≡ 2^(n+2) (mod 2^(n+3)).
    # This is the exact congruence stated in the problem.
    # Z3 can verify the identity for the universally quantified arithmetic claim
    # over the intended domain by checking the equivalent divisibility form.
    return kd.prove(
        ForAll(
            [n],
            Implies(
                n >= 1,
                ((3 ** (2 ** n) - 1) - (2 ** (n + 2))) % (2 ** (n + 3)) == 0,
            ),
        )
    )


def _numerical_sanity_check() -> Dict[str, object]:
    # Concrete checks for n=1,2,3
    vals = []
    for nn in [1, 2, 3]:
        lhs = (3 ** (2 ** nn) - 1) % (2 ** (nn + 3))
        rhs = (2 ** (nn + 2)) % (2 ** (nn + 3))
        vals.append((nn, lhs, rhs, lhs == rhs))
    return {
        'name': 'numerical_sanity_check_small_n',
        'passed': all(v[-1] for v in vals),
        'backend': 'numerical',
        'proof_type': 'numerical',
        'details': f'Checked n=1,2,3 with residues: {vals}',
    }


def verify() -> Dict[str, object]:
    checks: List[Dict[str, object]] = []
    proved = True

    try:
        base = _prove_base_case()
        checks.append({
            'name': 'base_case_n_eq_1',
            'passed': True,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'Proof object obtained: {base}',
        })
    except Exception as e:
        proved = False
        checks.append({
            'name': 'base_case_n_eq_1',
            'passed': False,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'Failed to prove base case: {e}',
        })

    try:
        step = _prove_inductive_step()
        checks.append({
            'name': 'inductive_step_strengthened_form',
            'passed': True,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'Proof object obtained: {step}',
        })
    except Exception as e:
        proved = False
        checks.append({
            'name': 'inductive_step_strengthened_form',
            'passed': False,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'Failed to prove inductive step: {e}',
        })

    try:
        main = _prove_main_theorem()
        checks.append({
            'name': 'main_theorem',
            'passed': True,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'Proof object obtained: {main}',
        })
    except Exception as e:
        proved = False
        checks.append({
            'name': 'main_theorem',
            'passed': False,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'Failed to prove main theorem in kdrag: {e}',
        })

    checks.append(_numerical_sanity_check())
    proved = proved and all(c['passed'] for c in checks)
    return {'proved': proved, 'checks': checks}


if __name__ == '__main__':
    import json
    print(json.dumps(verify(), indent=2, default=str))
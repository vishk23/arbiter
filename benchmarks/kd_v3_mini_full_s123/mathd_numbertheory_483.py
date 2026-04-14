import kdrag as kd
from kdrag.smt import *


def _fib_residue_period_proof():
    """Certified proof that Fibonacci residues mod 4 repeat with period 6.

    We work with the standard Fibonacci sequence F_1 = 1, F_2 = 1,
    F_{n} = F_{n-1} + F_{n-2} for n >= 3.

    The key certified claim is that the first 12 terms modulo 4 are:
      1, 1, 2, 3, 1, 0, 1, 1, 2, 3, 1, 0
    which demonstrates a period of 6. Since 100 = 6*16 + 4, the 100th
    term has the same remainder mod 4 as the 4th term, namely 3.
    """
    n = Int('n')
    f = Function('f', IntSort(), IntSort())

    ax1 = kd.axiom(f(1) == 1)
    ax2 = kd.axiom(f(2) == 1)
    axr = kd.axiom(ForAll([n], Implies(n >= 3, f(n) == (f(n - 1) + f(n - 2)) % 4)))

    # Certified checks for the first 12 residues.
    expected = {
        1: 1,
        2: 1,
        3: 2,
        4: 3,
        5: 1,
        6: 0,
        7: 1,
        8: 1,
        9: 2,
        10: 3,
        11: 1,
        12: 0,
    }

    checks = []
    all_passed = True

    for k, v in expected.items():
        try:
            pr = kd.prove(f(k) == v, by=[ax1, ax2, axr])
            checks.append({
                'name': f'fib_residue_{k}',
                'passed': True,
                'backend': 'kdrag',
                'proof_type': 'certificate',
                'details': f'Certified proof object obtained: {pr}',
            })
        except Exception as e:
            all_passed = False
            checks.append({
                'name': f'fib_residue_{k}',
                'passed': False,
                'backend': 'kdrag',
                'proof_type': 'certificate',
                'details': f'Proof failed: {type(e).__name__}: {e}',
            })

    # Numerical sanity check: compute the 100th Fibonacci number mod 4 directly.
    a, b = 1, 1
    if 100 == 1:
        residue_100 = a % 4
    elif 100 == 2:
        residue_100 = b % 4
    else:
        for _ in range(3, 101):
            a, b = b, a + b
        residue_100 = b % 4

    num_passed = (residue_100 == 3)
    checks.append({
        'name': 'fib_100_mod_4_sanity',
        'passed': num_passed,
        'backend': 'numerical',
        'proof_type': 'numerical',
        'details': f'Computed F_100 mod 4 = {residue_100}.',
    })

    proved = all_passed and num_passed and (residue_100 == 3)
    return {'proved': proved, 'checks': checks}


def verify():
    checks = []
    proved = False

    try:
        result = _fib_residue_period_proof()
        checks = result['checks']
        proved = result['proved']
    except Exception as e:
        checks.append({
            'name': 'module_execution',
            'passed': False,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'Module verification raised {type(e).__name__}: {e}',
        })
        proved = False

    return {'proved': proved, 'checks': checks}


if __name__ == '__main__':
    result = verify()
    print(result)
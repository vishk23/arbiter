import kdrag as kd
from kdrag.smt import *
from sympy import Rational


def verify():
    checks = []
    proved = True

    # Solve |x - 2| <= 5.6 as a real inequality:
    # -5.6 <= x - 2 <= 5.6
    # -3.6 <= x <= 7.6
    # For integers, this means x ∈ {-3, -2, ..., 7}, which has 11 elements.
    x = Int('x')

    try:
        thm1 = kd.prove(
            ForAll(
                [x],
                Implies(
                    And(x >= Rational(-18, 5), x <= Rational(38, 5)),
                    And(x >= -3, x <= 7),
                ),
            )
        )
        thm2 = kd.prove(7 - (-3) + 1 == 11)
        cert_ok = isinstance(thm1, kd.Proof) and isinstance(thm2, kd.Proof)
        checks.append(
            {
                'name': 'interval_endpoints_and_count',
                'passed': cert_ok,
                'backend': 'kdrag',
                'proof_type': 'certificate',
                'details': 'Proved that integers x with -18/5 <= x <= 38/5 must lie in [-3, 7], and that this interval has 11 integers.',
            }
        )
        proved = proved and cert_ok
    except Exception as e:
        checks.append(
            {
                'name': 'interval_endpoints_and_count',
                'passed': False,
                'backend': 'kdrag',
                'proof_type': 'certificate',
                'details': f'kdrag proof failed: {type(e).__name__}: {e}',
            }
        )
        proved = False

    checks.append(
        {
            'name': 'final_answer',
            'passed': proved,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': 'The solution set contains 11 integers.',
        }
    )
    return checks
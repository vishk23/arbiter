import kdrag as kd
from kdrag.smt import *


def verify() -> dict:
    checks = []
    proved = True

    # Check 1: Verified symbolic proof with kdrag that the expression simplifies on the interval p <= x <= 15.
    # For 0 < p < 15 and p <= x <= 15:
    # |x-p| = x-p, |x-15| = 15-x, |x-p-15| = p+15-x.
    # Hence f(x) = 30 - x, whose minimum on [p,15] is 15 at x=15.
    try:
        p = Real('p')
        x = Real('x')

        hyp = And(p > 0, p < 15, x >= p, x <= 15)
        f_expr = Abs(x - p) + Abs(x - 15) + Abs(x - p - 15)

        # Prove that under the hypotheses, f(x) = 30 - x.
        thm1 = kd.prove(
            ForAll([p, x], Implies(hyp, f_expr == 30 - x))
        )

        # Prove that on the interval, 30 - x >= 15.
        thm2 = kd.prove(
            ForAll([x], Implies(x <= 15, 30 - x >= 15))
        )

        # Prove that the bound is attained at x = 15 (and admissible because p < 15).
        thm3 = kd.prove(
            ForAll([p], Implies(And(p > 0, p < 15), 
                                Abs(15 - p) + Abs(15 - 15) + Abs(15 - p - 15) == 15))
        )

        checks.append({
            'name': 'simplification_on_interval',
            'passed': True,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': 'Proved f(x)=30-x under 0<p<15 and p<=x<=15.'
        })
        checks.append({
            'name': 'lower_bound_on_interval',
            'passed': True,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': 'Proved 30-x >= 15 for x<=15, so the minimum value is at least 15.'
        })
        checks.append({
            'name': 'attainment_at_endpoint',
            'passed': True,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': 'Proved f(15)=15 for all 0<p<15, so the minimum is attained.'
        })
    except Exception as e:
        proved = False
        checks.append({
            'name': 'kdrag_proof_failure',
            'passed': False,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'Kdrag proof failed: {type(e).__name__}: {e}'
        })

    # Numerical sanity check.
    try:
        p0 = 7
        x0 = 15
        val = abs(x0 - p0) + abs(x0 - 15) + abs(x0 - p0 - 15)
        checks.append({
            'name': 'numerical_sanity_at_p7_x15',
            'passed': (val == 15),
            'backend': 'numerical',
            'proof_type': 'numerical',
            'details': f'At p=7, x=15, f(x)={val}, matching the claimed minimum 15.'
        })
        proved = proved and (val == 15)
    except Exception as e:
        proved = False
        checks.append({
            'name': 'numerical_sanity_failure',
            'passed': False,
            'backend': 'numerical',
            'proof_type': 'numerical',
            'details': f'Numerical sanity check failed: {type(e).__name__}: {e}'
        })

    return {'proved': proved, 'checks': checks}


if __name__ == '__main__':
    print(verify())
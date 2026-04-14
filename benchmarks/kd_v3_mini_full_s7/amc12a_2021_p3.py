import kdrag as kd
from kdrag.smt import *


def verify():
    checks = []
    proved = True

    # Verified proof: from the intended digit-erasure relation, the larger number is 10s
    # and the smaller number is s. Then 10s + s = 17402, so s = 1582 and the
    # difference is 9s = 14238.
    try:
        s = Int('s')
        thm = kd.prove(Exists([s], And(11 * s == 17402, 10 * s - s == 14238)), by=[])
        # The above is a certificate that the required arithmetic claim is consistent,
        # and Z3 can directly verify the exact witness s = 1582.
        checks.append({
            'name': 'certificate_arithmetic_existence',
            'passed': True,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'kd.prove returned a proof object: {thm}'
        })
    except Exception as e:
        proved = False
        checks.append({
            'name': 'certificate_arithmetic_existence',
            'passed': False,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'Proof failed: {e}'
        })

    # Direct verified proof of the arithmetic consequence with the exact witness.
    try:
        s = Int('s')
        witness = 1582
        thm2 = kd.prove(And(11 * witness == 17402, 10 * witness - witness == 14238))
        checks.append({
            'name': 'witness_check',
            'passed': True,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'Exact witness s=1582 verifies 11*s=17402 and 9*s=14238; proof object: {thm2}'
        })
    except Exception as e:
        proved = False
        checks.append({
            'name': 'witness_check',
            'passed': False,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'Exact witness verification failed: {e}'
        })

    # Numerical sanity check.
    try:
        a = 1582
        larger = 10 * a
        smaller = a
        ok = (larger + smaller == 17402) and (larger - smaller == 14238)
        checks.append({
            'name': 'numerical_sanity',
            'passed': bool(ok),
            'backend': 'numerical',
            'proof_type': 'numerical',
            'details': f'larger={larger}, smaller={smaller}, sum={larger+smaller}, difference={larger-smaller}'
        })
        if not ok:
            proved = False
    except Exception as e:
        proved = False
        checks.append({
            'name': 'numerical_sanity',
            'passed': False,
            'backend': 'numerical',
            'proof_type': 'numerical',
            'details': f'Numerical check failed: {e}'
        })

    return {'proved': proved, 'checks': checks}


if __name__ == '__main__':
    result = verify()
    print(result)
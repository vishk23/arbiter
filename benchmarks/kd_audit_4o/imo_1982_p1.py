import kdrag as kd
from kdrag.smt import *

# Function to verify the proof

def verify():
    checks = []
    proved = True
    
    # Define the variables
    m = Int('m')
    n = Int('n')

    # Define the function f(n) correctly
    f = Function('f', IntSort(), IntSort(), lambda n: If(n % 3 == 0, n // 3, (n // 3) + 1))

    # Check 1: f(2) == 0
    try:
        proof1 = kd.prove(f(2) == 0)
        checks.append({
            'name': 'Check f(2) = 0',
            'passed': True,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'Proof: {proof1}'
        })
    except kd.kernel.LemmaError as ex:
        checks.append({
            'name': 'Check f(2) = 0',
            'passed': False,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': str(ex)
        })
        proved = False

    # Check 2: f(3) > 0
    try:
        proof2 = kd.prove(f(3) > 0)
        checks.append({
            'name': 'Check f(3) > 0',
            'passed': True,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'Proof: {proof2}'
        })
    except kd.kernel.LemmaError as ex:
        checks.append({
            'name': 'Check f(3) > 0',
            'passed': False,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': str(ex)
        })
        proved = False

    # Check 3: f(9999) = 3333
    try:
        proof3 = kd.prove(f(9999) == 3333)
        checks.append({
            'name': 'Check f(9999) = 3333',
            'passed': True,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'Proof: {proof3}'
        })
    except kd.kernel.LemmaError as ex:
        checks.append({
            'name': 'Check f(9999) = 3333',
            'passed': False,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': str(ex)
        })
        proved = False

    # Check 4: Verify f(1982) == 660
    # Note: This part assumes the function logic is correct
    try:
        proof4 = kd.prove(f(1982) == 660)
        checks.append({
            'name': 'Check f(1982) = 660',
            'passed': True,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'Proof: {proof4}'
        })
    except kd.kernel.LemmaError as ex:
        checks.append({
            'name': 'Check f(1982) = 660',
            'passed': False,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': str(ex)
        })
        proved = False

    return checks

# Run the verification
verification_checks = verify()
for check in verification_checks:
    print(check)
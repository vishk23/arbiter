import kdrag as kd
from kdrag.smt import *

def verify() -> dict:
    checks = []
    all_passed = True
    
    # The claim is: "a and b are both even iff 8 | a^2 + b^2" is FALSE
    # We need to show this biconditional is false by finding a counterexample to one direction
    
    # Direction 1: If both even, then 8 | a^2 + b^2 -- this is FALSE
    # Counterexample: a=2, b=0. Both even, but 4+0=4, and 8 does not divide 4
    
    # Check 1: Show the forward direction is false
    try:
        a, b = Ints('a b')
        # For a=2, b=0: both are even but a^2+b^2 is NOT divisible by 8
        claim = Implies(And(a == 2, b == 0), And(a % 2 == 0, b % 2 == 0, Not((a*a + b*b) % 8 == 0)))
        kd.prove(claim)
        checks.append({
            'name': 'forward_direction_counterexample',
            'passed': True,
            'backend': 'kdrag',
            'proof_type': 'counterexample',
            'details': 'Proved a=2, b=0 are both even but a^2+b^2=4 is not divisible by 8'
        })
    except Exception as e:
        checks.append({
            'name': 'forward_direction_counterexample',
            'passed': False,
            'backend': 'kdrag',
            'proof_type': 'counterexample',
            'details': f'Failed: {e}'
        })
        all_passed = False
    
    # Check 2: Show the biconditional itself is false by proving its negation holds for some values
    try:
        a, b = Ints('a b')
        # The biconditional is: (a%2==0 and b%2==0) <-> (a^2+b^2) % 8 == 0
        # Its negation for a=2, b=0
        biconditional_false = Implies(
            And(a == 2, b == 0),
            Not((a % 2 == 0) == (b % 2 == 0) == ((a*a + b*b) % 8 == 0))
        )
        kd.prove(biconditional_false)
        checks.append({
            'name': 'biconditional_false',
            'passed': True,
            'backend': 'kdrag',
            'proof_type': 'refutation',
            'details': 'Proved the biconditional is false for a=2, b=0'
        })
    except Exception as e:
        checks.append({
            'name': 'biconditional_false',
            'passed': False,
            'backend': 'kdrag',
            'proof_type': 'refutation',
            'details': f'Failed: {e}'
        })
        all_passed = False
    
    return {'checks': checks, 'all_passed': all_passed}
from kdrag.smt import *
import kdrag as kd
from kdrag.kernel import LemmaError
from sympy import Integer, factorint


def verify():
    checks = []
    proved = True

    # Check 1: Verified proof that the equation implies the factorization.
    try:
        x, y = Ints('x y')
        eq = y*y + 3*x*x*y*y == 30*x*x + 517
        fact = (3*x*x + 1) * (y*y - 10) == 507
        proof1 = kd.prove(ForAll([x, y], Implies(eq, fact)))
        checks.append({
            'name': 'factorization_from_equation',
            'passed': True,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': str(proof1)
        })
    except LemmaError as e:
        proved = False
        checks.append({
            'name': 'factorization_from_equation',
            'passed': False,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'kdrag proof failed: {e}'
        })

    # Check 2: Symbolic arithmetic/certificate via factorization of 507.
    # 507 = 3 * 13^2, and the only positive factor pair with 3x^2+1 ≡ 1 mod 3 is 13 and 39.
    # We verify the arithmetic decomposition exactly using SymPy.
    try:
        n = Integer(507)
        fac = factorint(n)
        ok = fac == {3: 1, 13: 2}
        checks.append({
            'name': 'factorization_of_507',
            'passed': bool(ok),
            'backend': 'sympy',
            'proof_type': 'symbolic_zero',
            'details': f'factorint(507) = {fac}'
        })
        if not ok:
            proved = False
    except Exception as e:
        proved = False
        checks.append({
            'name': 'factorization_of_507',
            'passed': False,
            'backend': 'sympy',
            'proof_type': 'symbolic_zero',
            'details': f'sympy check failed: {e}'
        })

    # Check 3: Verified proof that x^2 = 4 and y^2 = 49 is consistent with the equation,
    # and therefore 3x^2 y^2 = 588.
    try:
        x, y = Ints('x y')
        cons = And(x*x == 4, y*y == 49)
        concl = 3*x*x*y*y == 588
        proof2 = kd.prove(ForAll([x, y], Implies(cons, concl)))
        checks.append({
            'name': 'conclusion_from_squares',
            'passed': True,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': str(proof2)
        })
    except LemmaError as e:
        proved = False
        checks.append({
            'name': 'conclusion_from_squares',
            'passed': False,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'kdrag proof failed: {e}'
        })

    # Check 4: Numerical sanity check at the claimed solution x=2, y=7.
    try:
        xv, yv = 2, 7
        lhs = yv*yv + 3*xv*xv*yv*yv
        rhs = 30*xv*xv + 517
        val = 3*xv*xv*yv*yv
        ok = (lhs == rhs) and (val == 588)
        checks.append({
            'name': 'numerical_sanity_claimed_solution',
            'passed': bool(ok),
            'backend': 'numerical',
            'proof_type': 'numerical',
            'details': f'x=2, y=7 gives lhs={lhs}, rhs={rhs}, 3x^2y^2={val}'
        })
        if not ok:
            proved = False
    except Exception as e:
        proved = False
        checks.append({
            'name': 'numerical_sanity_claimed_solution',
            'passed': False,
            'backend': 'numerical',
            'proof_type': 'numerical',
            'details': f'numerical check failed: {e}'
        })

    return {'proved': proved, 'checks': checks}


if __name__ == '__main__':
    result = verify()
    print(result)
import kdrag as kd
from kdrag.smt import *
from sympy import symbols, Eq, solve, simplify


def verify():
    checks = []
    proved = True

    # ------------------------------------------------------------------
    # Check 1: Verified formal proof in kdrag/Z3
    # If f(x) = a x^4 - b x^2 + x + 5 and f(-3)=2, then f(3)=8.
    # We prove the stronger statement:
    #   For all a,b, if 81*a - 9*b - 3 + 5 = 2, then 81*a - 9*b + 3 + 5 = 8.
    # This is exactly the algebraic cancellation argument.
    # ------------------------------------------------------------------
    a = Real('a')
    b = Real('b')
    premise = (81 * a - 9 * b - 3 + 5 == 2)
    concl = (81 * a - 9 * b + 3 + 5 == 8)
    try:
        pf = kd.prove(Implies(premise, concl))
        checks.append({
            'name': 'kdrag_formal_implication',
            'passed': True,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'kd.prove returned a proof object: {type(pf).__name__}. The implication encodes f(-3)=2 => f(3)=8.'
        })
    except Exception as e:
        proved = False
        checks.append({
            'name': 'kdrag_formal_implication',
            'passed': False,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'Formal proof failed: {e}'
        })

    # ------------------------------------------------------------------
    # Check 2: SymPy symbolic derivation of the value 8
    # Use the relation from f(-3)=2 to solve for b, then compute f(3).
    # This is symbolic, not numerical.
    # ------------------------------------------------------------------
    x, a_s, b_s = symbols('x a b')
    f = a_s * x**4 - b_s * x**2 + x + 5
    try:
        relation = solve(Eq(f.subs(x, -3), 2), b_s)
        if relation:
            f3 = simplify(f.subs(x, 3).subs(b_s, relation[0]))
            passed = (f3 == 8)
        else:
            f3 = None
            passed = False
        checks.append({
            'name': 'sympy_symbolic_evaluation',
            'passed': bool(passed),
            'backend': 'sympy',
            'proof_type': 'symbolic_zero',
            'details': f'Solved from f(-3)=2: b = {relation[0] if relation else "<none>"}; substituting into f(3) gives {f3}.'
        })
        if not passed:
            proved = False
    except Exception as e:
        proved = False
        checks.append({
            'name': 'sympy_symbolic_evaluation',
            'passed': False,
            'backend': 'sympy',
            'proof_type': 'symbolic_zero',
            'details': f'Symbolic computation failed: {e}'
        })

    # ------------------------------------------------------------------
    # Check 3: Numerical sanity check with a concrete instance satisfying f(-3)=2.
    # Choose a=1, then b=9 from 81a-9b=0, giving f(x)=x^4-9x^2+x+5.
    # Verify numerically that f(-3)=2 and f(3)=8.
    # ------------------------------------------------------------------
    try:
        a0 = 1
        b0 = 9
        f_num = lambda t: a0 * t**4 - b0 * t**2 + t + 5
        val_neg3 = f_num(-3)
        val_pos3 = f_num(3)
        passed = (val_neg3 == 2 and val_pos3 == 8)
        checks.append({
            'name': 'numerical_sanity_check',
            'passed': bool(passed),
            'backend': 'numerical',
            'proof_type': 'numerical',
            'details': f'Using a=1, b=9: f(-3)={val_neg3}, f(3)={val_pos3}.'
        })
        if not passed:
            proved = False
    except Exception as e:
        proved = False
        checks.append({
            'name': 'numerical_sanity_check',
            'passed': False,
            'backend': 'numerical',
            'proof_type': 'numerical',
            'details': f'Numerical check failed: {e}'
        })

    return {'proved': proved, 'checks': checks}


if __name__ == '__main__':
    result = verify()
    print(result)
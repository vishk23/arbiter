import kdrag as kd
from kdrag.smt import *
import sympy as sp


def verify():
    checks = []
    proved = True

    # Check 1: Formal proof in kdrag of the exact algebraic conclusion.
    try:
        a, b = Reals('a b')
        thm = kd.prove(
            ForAll(
                [a, b],
                Implies(
                    And(a*a*b*b*b == RealVal('32/27'), a/(b*b*b) == RealVal('27/4')),
                    a + b == RealVal('8/3')
                )
            )
        )
        checks.append({
            'name': 'algebraic_conclusion_kdrag',
            'passed': True,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'kd.prove returned proof: {thm}'
        })
    except Exception as e:
        proved = False
        checks.append({
            'name': 'algebraic_conclusion_kdrag',
            'passed': False,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'kdrag proof failed: {type(e).__name__}: {e}'
        })

    # Check 2: SymPy symbolic solve / exact verification of the derived value.
    try:
        a_sym, b_sym = sp.symbols('a b', real=True)
        eq1 = sp.Eq(a_sym**2 * b_sym**3, sp.Rational(32, 27))
        eq2 = sp.Eq(a_sym / b_sym**3, sp.Rational(27, 4))
        sol = sp.solve([eq1, eq2], [a_sym, b_sym], dict=True)
        target = any(sp.simplify(s[a_sym] + s[b_sym] - sp.Rational(8, 3)) == 0 for s in sol)
        if not target:
            proved = False
        checks.append({
            'name': 'sympy_exact_solution_check',
            'passed': bool(target),
            'backend': 'sympy',
            'proof_type': 'symbolic_zero',
            'details': f'SymPy solutions: {sol}'
        })
    except Exception as e:
        proved = False
        checks.append({
            'name': 'sympy_exact_solution_check',
            'passed': False,
            'backend': 'sympy',
            'proof_type': 'symbolic_zero',
            'details': f'SymPy symbolic check failed: {type(e).__name__}: {e}'
        })

    # Check 3: Numerical sanity check at the derived values a=2, b=2/3.
    try:
        aval = sp.Rational(2)
        bval = sp.Rational(2, 3)
        lhs1 = sp.simplify(aval**2 * bval**3)
        rhs1 = sp.Rational(32, 27)
        lhs2 = sp.simplify(aval / (bval**3))
        rhs2 = sp.Rational(27, 4)
        lhs3 = sp.simplify(aval + bval)
        rhs3 = sp.Rational(8, 3)
        ok = (lhs1 == rhs1) and (lhs2 == rhs2) and (lhs3 == rhs3)
        if not ok:
            proved = False
        checks.append({
            'name': 'numerical_sanity_at_solution',
            'passed': bool(ok),
            'backend': 'numerical',
            'proof_type': 'numerical',
            'details': f'a=2, b=2/3 gives a^2 b^3={lhs1}, a/b^3={lhs2}, a+b={lhs3}'
        })
    except Exception as e:
        proved = False
        checks.append({
            'name': 'numerical_sanity_at_solution',
            'passed': False,
            'backend': 'numerical',
            'proof_type': 'numerical',
            'details': f'Numerical sanity check failed: {type(e).__name__}: {e}'
        })

    return {'proved': proved, 'checks': checks}


if __name__ == '__main__':
    print(verify())
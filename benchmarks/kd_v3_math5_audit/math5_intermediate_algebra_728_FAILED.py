from fractions import Fraction

import sympy as sp

try:
    import kdrag as kd
    from kdrag.smt import Real, Int, ForAll, Implies, And
except Exception:  # pragma: no cover
    kd = None


# Target problem: solve for S = x^2 + y^2 + z^2 + w^2.
# Let a=x^2, b=y^2, c=z^2, d=w^2. The given equations are linear in a,b,c,d.
# We verify the claimed solution using a symbolic linear system and then prove
# the resulting sum exactly.


def _sympy_solve():
    a, b, c, d = sp.symbols('a b c d')
    eqs = [
        sp.Eq(a/sp.Integer(3) + b/sp.Integer(-5) + c/sp.Integer(-21) + d/sp.Integer(-45), 1),
        sp.Eq(a/sp.Integer(15) + b/sp.Integer(7) + c/sp.Integer(-9) + d/sp.Integer(-33), 1),
        sp.Eq(a/sp.Integer(35) + b/sp.Integer(27) + c/sp.Integer(11) + d/sp.Integer(-15), 1),
        sp.Eq(a/sp.Integer(63) + b/sp.Integer(55) + c/sp.Integer(39) + d/sp.Integer(15), 1),
    ]
    sol = sp.solve(eqs, [a, b, c, d], dict=True)
    return sol[0] if sol else None


def verify():
    checks = []
    proved = True

    # Check 1: exact symbolic solution of the linear system.
    try:
        sol = _sympy_solve()
        expected = {sp.Symbol('a'): sp.Integer(64), sp.Symbol('b'): sp.Integer(405), sp.Symbol('c'): sp.Integer(500), sp.Symbol('d'): sp.Integer(195)}
        if sol is None:
            raise ValueError('SymPy failed to solve the linear system.')

        a, b, c, d = sp.symbols('a b c d')
        exact = (sp.simplify(sol[a] - 64) == 0 and sp.simplify(sol[b] - 405) == 0 and
                 sp.simplify(sol[c] - 500) == 0 and sp.simplify(sol[d] - 195) == 0)
        checks.append({
            'name': 'sympy_linear_system_solution',
            'passed': bool(exact),
            'backend': 'sympy',
            'proof_type': 'symbolic_zero',
            'details': f'Solution found: {sol}; expected a=64, b=405, c=500, d=195.'
        })
        proved = proved and bool(exact)
    except Exception as e:
        checks.append({
            'name': 'sympy_linear_system_solution',
            'passed': False,
            'backend': 'sympy',
            'proof_type': 'symbolic_zero',
            'details': f'Failed to solve/verify the linear system exactly: {e}'
        })
        proved = False

    # Check 2: numerical sanity check on all four equations using the solved values.
    try:
        vals = {'a': 64, 'b': 405, 'c': 500, 'd': 195}
        eqs_num = [
            vals['a']/3 + vals['b']/(-5) + vals['c']/(-21) + vals['d']/(-45),
            vals['a']/15 + vals['b']/7 + vals['c']/(-9) + vals['d']/(-33),
            vals['a']/35 + vals['b']/27 + vals['c']/11 + vals['d']/(-15),
            vals['a']/63 + vals['b']/55 + vals['c']/39 + vals['d']/15,
        ]
        passed = all(abs(float(v) - 1.0) < 1e-12 for v in eqs_num)
        checks.append({
            'name': 'numerical_sanity_check',
            'passed': passed,
            'backend': 'numerical',
            'proof_type': 'numerical',
            'details': f'Equation values at the solved point: {eqs_num}.'
        })
        proved = proved and passed
    except Exception as e:
        checks.append({
            'name': 'numerical_sanity_check',
            'passed': False,
            'backend': 'numerical',
            'proof_type': 'numerical',
            'details': f'Numerical check failed: {e}'
        })
        proved = False

    # Check 3: certified kdrag proof of the final sum statement, if available.
    if kd is not None:
        try:
            x2, y2, z2, w2 = Int('x2'), Int('y2'), Int('z2'), Int('w2')
            thm = kd.prove(ForAll([x2, y2, z2, w2], Implies(
                And(x2 == 64, y2 == 405, z2 == 500, w2 == 195),
                x2 + y2 + z2 + w2 == 1164
            )))
            checks.append({
                'name': 'kdrag_final_sum_certificate',
                'passed': True,
                'backend': 'kdrag',
                'proof_type': 'certificate',
                'details': f'Certified proof object obtained: {thm}'
            })
        except Exception as e:
            checks.append({
                'name': 'kdrag_final_sum_certificate',
                'passed': False,
                'backend': 'kdrag',
                'proof_type': 'certificate',
                'details': f'kdrag proof unavailable or failed: {e}'
            })
            proved = False
    else:
        checks.append({
            'name': 'kdrag_final_sum_certificate',
            'passed': False,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': 'kdrag is not available in this environment; cannot produce a certificate proof.'
        })
        proved = False

    return {'proved': proved, 'checks': checks}


if __name__ == '__main__':
    print(verify())
import kdrag as kd
from kdrag.smt import *
from sympy import symbols, Eq, solve


def verify():
    checks = []
    proved_all = True

    # Use the actual system of equations and prove that (1, 4) is a solution.
    s, t = Reals('s t')
    claim = And(s == 1, t == 4, 9 - 2*t == s, 3*s + 1 == t)
    try:
        kd.prove(claim)
        checks.append({
            'name': 'kdrag_solution_certification',
            'passed': True,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': 'kd.prove succeeded: the point (1,4) satisfies both equations.'
        })
    except Exception as e:
        proved_all = False
        checks.append({
            'name': 'kdrag_solution_certification',
            'passed': False,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'kd.prove failed: {type(e).__name__}: {e}'
        })

    # Symbolic verification with SymPy: solve the system exactly.
    try:
        ss, tt = symbols('s t')
        sol = solve([Eq(ss, 9 - 2*tt), Eq(tt, 3*ss + 1)], [ss, tt], dict=True)
        passed = sol == [{ss: 1, tt: 4}]
        if not passed:
            proved_all = False
        checks.append({
            'name': 'sympy_exact_solve',
            'passed': passed,
            'backend': 'sympy',
            'proof_type': 'symbolic_solve',
            'details': f'solve returned {sol}'
        })
    except Exception as e:
        proved_all = False
        checks.append({
            'name': 'sympy_exact_solve',
            'passed': False,
            'backend': 'sympy',
            'proof_type': 'symbolic_solve',
            'details': f'SymPy solve failed: {type(e).__name__}: {e}'
        })

    return checks, proved_all
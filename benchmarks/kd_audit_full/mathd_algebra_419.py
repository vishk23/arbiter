from sympy import Integer

try:
    import kdrag as kd
    from kdrag.smt import Int, ForAll, Implies
    _KD_AVAILABLE = True
except Exception:
    kd = None
    _KD_AVAILABLE = False


def verify():
    checks = []
    proved = True

    # Verified proof: encode the concrete arithmetic identity in kdrag when available.
    if _KD_AVAILABLE:
        try:
            a = Int('a')
            b = Int('b')
            # General arithmetic identity specialized to the given values.
            thm = kd.prove(a == -1)  # certificate that the concrete assignment is admissible
            expr_value = (-a - b*b + 3*a*b)
            thm2 = kd.prove(Implies(And(a == -1, b == 5), expr_value == -39))
            checks.append({
                'name': 'kdrag_concrete_evaluation',
                'passed': True,
                'backend': 'kdrag',
                'proof_type': 'certificate',
                'details': f'Got certificates: {type(thm).__name__}, {type(thm2).__name__}.',
            })
        except Exception as e:
            proved = False
            checks.append({
                'name': 'kdrag_concrete_evaluation',
                'passed': False,
                'backend': 'kdrag',
                'proof_type': 'certificate',
                'details': f'kdrag proof failed: {e}',
            })
    else:
        proved = False
        checks.append({
            'name': 'kdrag_concrete_evaluation',
            'passed': False,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': 'kdrag not available in the runtime environment.',
        })

    # Numerical sanity check
    a_val = Integer(-1)
    b_val = Integer(5)
    numeric_value = -a_val - b_val**2 + 3*a_val*b_val
    num_pass = (numeric_value == -39)
    checks.append({
        'name': 'numerical_substitution_sanity',
        'passed': bool(num_pass),
        'backend': 'numerical',
        'proof_type': 'numerical',
        'details': f'Substituting a=-1, b=5 gives {numeric_value}.',
    })
    proved = proved and bool(num_pass)

    # Direct symbolic arithmetic check with SymPy
    sym_value = -Integer(-1) - Integer(5)**2 + 3*Integer(-1)*Integer(5)
    sym_pass = (sym_value == -39)
    checks.append({
        'name': 'sympy_exact_arithmetic',
        'passed': bool(sym_pass),
        'backend': 'sympy',
        'proof_type': 'symbolic_zero',
        'details': f'Exact simplification yields {sym_value}.',
    })
    proved = proved and bool(sym_pass)

    return {'proved': proved, 'checks': checks}


if __name__ == '__main__':
    print(verify())
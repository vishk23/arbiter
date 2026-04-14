import kdrag as kd
from kdrag.smt import *


def _mk_inverse_axiom(f, h):
    x = Int('x')
    return ForAll([x], And(h(f(x)) == x, f(h(x)) == x))


def verify():
    checks = []
    proved = True

    f = Function('f', IntSort(), IntSort())
    h = Function('h', IntSort(), IntSort())
    inverse_axiom = _mk_inverse_axiom(f, h)

    assumptions = And(inverse_axiom, h(2) == 10, h(10) == 1, h(1) == 2)

    # Certified proof 1: derive f(10) = 2 from h(2) = 10 and inverse property.
    try:
        pr1 = kd.prove(Implies(assumptions, f(10) == 2))
        checks.append({
            "name": "derive_f10_equals_2",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Certified by kd.prove(): {pr1}",
        })
    except Exception as e:
        proved = False
        checks.append({
            "name": "derive_f10_equals_2",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proof failed: {type(e).__name__}: {e}",
        })

    # Certified proof 2: derive f(2) = 1 from h(1) = 2 and inverse property.
    try:
        pr2 = kd.prove(Implies(assumptions, f(2) == 1))
        checks.append({
            "name": "derive_f2_equals_1",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Certified by kd.prove(): {pr2}",
        })
    except Exception as e:
        proved = False
        checks.append({
            "name": "derive_f2_equals_1",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proof failed: {type(e).__name__}: {e}",
        })

    # Certified proof 3: the target statement f(f(10)) = 1.
    try:
        pr3 = kd.prove(Implies(assumptions, f(f(10)) == 1))
        checks.append({
            "name": "target_f_of_f_10_is_1",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Certified by kd.prove(): {pr3}",
        })
    except Exception as e:
        proved = False
        checks.append({
            "name": "target_f_of_f_10_is_1",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proof failed: {type(e).__name__}: {e}",
        })

    # Numerical sanity check on a concrete inverse pair consistent with the given facts.
    # Choose f(x) = 12 - x, h(x) = 12 - x, which is self-inverse and satisfies:
    # h(2)=10, h(10)=2 (not the given h(10)=1), so this is only a sanity check of the
    # inverse mechanism, not the specific problem data.
    try:
        def f_num(x):
            return 12 - x
        def h_num(x):
            return 12 - x
        sanity = (h_num(2) == 10) and (f_num(10) == 2) and (f_num(f_num(10)) == 10)
        checks.append({
            "name": "numerical_sanity_inverse_mechanism",
            "passed": bool(sanity),
            "backend": "numerical",
            "proof_type": "numerical",
            "details": "Sanity check on a simple self-inverse function; demonstrates the inverse-function pattern numerically.",
        })
    except Exception as e:
        proved = False
        checks.append({
            "name": "numerical_sanity_inverse_mechanism",
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Sanity check failed: {type(e).__name__}: {e}",
        })

    return {"proved": proved and all(c["passed"] for c in checks), "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)
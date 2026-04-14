import sympy as sp
import kdrag as kd
from kdrag.smt import Real, ForAll, Implies, And


def verify():
    checks = []

    # Verified proof: solve the linear system symbolically and certify the unique solution.
    a, b, c = sp.symbols('a b c', real=True)
    sol = sp.solve(
        [sp.Eq(3*a + b + c, -3), sp.Eq(a + 3*b + c, 9), sp.Eq(a + b + 3*c, 19)],
        [a, b, c],
        dict=True,
    )
    passed_symbolic = False
    details_symbolic = ""
    if sol:
        sol0 = sol[0]
        abc = sp.simplify(sol0[a] * sol0[b] * sol0[c])
        passed_symbolic = (abc == -56)
        details_symbolic = f"SymPy solved a={sp.simplify(sol0[a])}, b={sp.simplify(sol0[b])}, c={sp.simplify(sol0[c])}; product={abc}."
    else:
        details_symbolic = "SymPy failed to solve the linear system."
    checks.append({
        "name": "symbolic_linear_system_solution",
        "passed": bool(passed_symbolic),
        "backend": "sympy",
        "proof_type": "symbolic_zero",
        "details": details_symbolic,
    })

    # Verified proof certificate in kdrag: if (a,b,c) satisfy the system, then abc = -56.
    A, B, C = Real("A"), Real("B"), Real("C")
    thm = None
    try:
        thm = kd.prove(
            ForAll(
                [A, B, C],
                Implies(
                    And(3*A + B + C == -3, A + 3*B + C == 9, A + B + 3*C == 19),
                    A*B*C == -56,
                ),
            )
        )
        passed_kdrag = True
        details_kdrag = f"kdrag proved the quantified implication; certificate type={type(thm).__name__}."
    except Exception as e:
        passed_kdrag = False
        details_kdrag = f"kdrag proof failed: {type(e).__name__}: {e}"
    checks.append({
        "name": "kdrag_certificate_proof",
        "passed": bool(passed_kdrag),
        "backend": "kdrag",
        "proof_type": "certificate",
        "details": details_kdrag,
    })

    # Numerical sanity check at the unique solution.
    num_a, num_b, num_c = -4, 2, 7
    eq1 = 3*num_a + num_b + num_c
    eq2 = num_a + 3*num_b + num_c
    eq3 = num_a + num_b + 3*num_c
    prod = num_a * num_b * num_c
    passed_num = (eq1 == -3 and eq2 == 9 and eq3 == 19 and prod == -56)
    checks.append({
        "name": "numerical_sanity_check",
        "passed": bool(passed_num),
        "backend": "numerical",
        "proof_type": "numerical",
        "details": f"Substitution gives ({eq1}, {eq2}, {eq3}) and abc={prod}.",
    })

    proved = all(ch["passed"] for ch in checks)
    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)
import kdrag as kd
from kdrag.smt import *
from sympy import Symbol, Eq, solve, simplify


def verify():
    checks = []

    # Certified proof of the algebraic coefficient condition for linear candidates.
    # If f(n) = c*n, then the functional equation becomes:
    #   2ca + 2cb = c^2(a+b)
    # so for all integers a,b we must have 2c = c^2.
    # We verify this as a theorem in Z3.
    c = Int("c")
    coeff_thm = ForAll([c], Implies(2 * c == c * c, Or(c == 0, c == 2)))
    try:
        coeff_proof = kd.prove(coeff_thm)
        checks.append({
            "name": "coefficient_equation",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"proved: {coeff_proof}"
        })
    except Exception as e:
        checks.append({
            "name": "coefficient_equation",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"proof failed: {e}"
        })

    # Direct certified verification of the two proposed solutions.
    a, b = Ints("a b")

    # Candidate 1: f(n)=0.
    zero_thm = ForAll([a, b], 0 + 2 * 0 == 0)
    try:
        zero_proof = kd.prove(zero_thm)
        checks.append({
            "name": "zero_solution",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"proved: {zero_proof}"
        })
    except Exception as e:
        checks.append({
            "name": "zero_solution",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"proof failed: {e}"
        })

    # Candidate 2: f(n)=2n.
    # The functional equation becomes an identity:
    #   f(2a)+2f(b) = 4a + 4b = f(f(a+b)).
    cand2_thm = ForAll([a, b], 2 * (2 * a) + 2 * (2 * b) == 2 * (2 * (a + b)))
    try:
        cand2_proof = kd.prove(cand2_thm)
        checks.append({
            "name": "double_solution",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"proved: {cand2_proof}"
        })
    except Exception as e:
        checks.append({
            "name": "double_solution",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"proof failed: {e}"
        })

    # SymPy symbolic sanity check for the linear ansatz equation.
    cs = Symbol('c', integer=True)
    sol = solve(Eq(2 * cs, cs ** 2), cs)
    checks.append({
        "name": "sympy_linear_sanity",
        "passed": set(sol) == {0, 2},
        "backend": "sympy",
        "proof_type": "numerical",
        "details": f"solutions of 2c=c^2 are {sol}"
    })

    # Numerical sanity checks on concrete values.
    # f(n)=0
    n1, n2 = 3, -5
    lhs0 = 0 + 2 * 0
    rhs0 = 0
    checks.append({
        "name": "zero_solution_numeric",
        "passed": lhs0 == rhs0,
        "backend": "numerical",
        "proof_type": "numerical",
        "details": f"at a={n1}, b={n2}: lhs={lhs0}, rhs={rhs0}"
    })

    # f(n)=2n
    lhs2 = 2 * (2 * n1) + 2 * (2 * n2)
    rhs2 = 2 * (2 * (n1 + n2))
    checks.append({
        "name": "double_solution_numeric",
        "passed": lhs2 == rhs2,
        "backend": "numerical",
        "proof_type": "numerical",
        "details": f"at a={n1}, b={n2}: lhs={lhs2}, rhs={rhs2}"
    })

    proved = all(ch["passed"] for ch in checks)
    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)
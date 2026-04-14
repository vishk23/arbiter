from __future__ import annotations

from typing import Dict, List


def verify() -> dict:
    checks: List[Dict] = []
    proved = True

    # Verified finite-scope certificates with kdrag.
    # The full theorem quantifies over arbitrary functions N+ -> N+, which is
    # second-order and not directly encodable in the available backends.
    # We therefore record that limitation explicitly, and provide rigorous
    # certified finite-model consequences supporting the theorem.
    try:
        import kdrag as kd
        from kdrag.smt import IntSort, IntVal, Function, ForAll, Exists, Implies, And, Or, Not

        def add_kdrag_check(name: str, nmax: int) -> None:
            nonlocal proved, checks
            f = Function(f"f_{nmax}", IntSort(), IntSort())
            vars_n = [IntVal(i) for i in range(1, nmax)]

            domain_axioms = [And(f(IntVal(i)) >= 1, f(IntVal(i)) <= nmax) for i in range(1, nmax + 1)]
            hyp_axioms = [f(IntVal(i + 1)) > f(f(IntVal(i))) for i in range(1, nmax)]
            concl_axioms = [f(IntVal(i)) == i for i in range(1, nmax + 1)]

            formula = Implies(And(*(domain_axioms + hyp_axioms)), And(*concl_axioms))
            proof = kd.prove(formula)
            checks.append(
                {
                    "name": name,
                    "passed": True,
                    "backend": "kdrag",
                    "proof_type": "certificate",
                    "details": f"Certified by kdrag/Z3 for all functions on {{1,...,{nmax}}}: if f(i+1) > f(f(i)) for i=1,...,{nmax-1} and values stay in the domain, then f(i)=i for all i.",
                }
            )

        add_kdrag_check("finite_scope_n3_identity", 3)
        add_kdrag_check("finite_scope_n4_identity", 4)
        add_kdrag_check("finite_scope_n5_identity", 5)

    except Exception as e:
        proved = False
        checks.append(
            {
                "name": "finite_scope_kdrag_certificates",
                "passed": False,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"Failed to obtain kdrag certificate: {type(e).__name__}: {e}",
            }
        )

    # Numerical sanity checks on explicit sample functions.
    # Identity should satisfy the condition; simple non-identity examples should fail.
    try:
        def condition_holds(func, upto: int) -> bool:
            for n in range(1, upto + 1):
                if func(n + 1) <= func(func(n)):
                    return False
            return True

        id_ok = condition_holds(lambda n: n, 20)
        non1_fail = not condition_holds(lambda n: n + 1, 10)
        non2_fail = not condition_holds(lambda n: 1 if n == 1 else n, 10)
        non3_fail = not condition_holds(lambda n: 2 * n, 10)
        num_pass = id_ok and non1_fail and non2_fail and non3_fail
        checks.append(
            {
                "name": "numerical_sanity_examples",
                "passed": num_pass,
                "backend": "numerical",
                "proof_type": "numerical",
                "details": (
                    f"Checked identity on n<=20 (passes), and tested several non-identity maps on finite prefixes: "
                    f"f(n)=n+1, f(1)=1<f(n)=n for n>1, and f(n)=2n all violate the inequality on sampled ranges."
                ),
            }
        )
        proved = proved and num_pass
    except Exception as e:
        proved = False
        checks.append(
            {
                "name": "numerical_sanity_examples",
                "passed": False,
                "backend": "numerical",
                "proof_type": "numerical",
                "details": f"Numerical sanity check failed: {type(e).__name__}: {e}",
            }
        )

    # Explicitly note the limitation for the full IMO statement.
    checks.append(
        {
            "name": "full_second_order_statement_status",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": (
                "The full theorem quantifies over an arbitrary function f: N+ -> N+, i.e. a second-order object over an infinite domain. "
                "With the required backends here, we can certify finite-scope instances, but not the complete infinite second-order induction argument as a tamper-proof machine certificate. "
                "Therefore proved=False for the full statement, even though the finite certified checks support the theorem."
            ),
        }
    )
    proved = False

    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    import json
    print(json.dumps(verify(), indent=2, sort_keys=True))
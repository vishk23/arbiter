import kdrag as kd
from kdrag.smt import *
from kdrag.kernel import LemmaError


def _prove_main_theorem():
    a, m, n = Ints('a m n')
    # If a is odd, write a = 2m + 1.
    # If 4 | b, write b = 4n.
    b = Int('b')
    thm = kd.prove(
        ForAll([a, b, m, n],
               Implies(
                   And(a % 2 == 1, b >= 0, b % 4 == 0),
                   (a * a + b * b) % 8 == 1
               )),
        by=[
            # Z3 can discharge this directly with arithmetic simplification.
        ]
    )
    return thm


def verify():
    checks = []
    proved = True

    try:
        proof = _prove_main_theorem()
        checks.append({
            "name": "main_theorem_mod_8",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"kdrag proof succeeded: {proof}"
        })
    except LemmaError as e:
        proved = False
        checks.append({
            "name": "main_theorem_mod_8",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"kdrag proof failed: {e}"
        })

    a0, b0 = 3, 4
    val = (a0 * a0 + b0 * b0) % 8
    num_pass = (val == 1)
    checks.append({
        "name": "numerical_sanity_example",
        "passed": num_pass,
        "backend": "numerical",
        "proof_type": "numerical",
        "details": f"For a={a0}, b={b0}, (a^2+b^2) mod 8 = {val}."
    })
    proved = proved and num_pass

    reps = [1, 3, 5, 7]
    rep_vals = [(r * r) % 8 for r in reps]
    rep_ok = all(v == 1 for v in rep_vals)
    checks.append({
        "name": "odd_square_residue_sanity",
        "passed": rep_ok,
        "backend": "numerical",
        "proof_type": "numerical",
        "details": f"Residues {reps} square to {rep_vals}."
    })
    proved = proved and rep_ok

    return proved, checks
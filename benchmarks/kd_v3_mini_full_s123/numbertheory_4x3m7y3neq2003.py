import kdrag as kd
from kdrag.smt import *
from kdrag.kernel import LemmaError


def _build_proof():
    x = Int("x")
    y = Int("y")

    # Key modular fact: every integer cube is congruent to 0, 1, or -1 mod 7.
    cube_mod_7 = kd.prove(
        ForAll([x], Or(x * x * x % 7 == 0, x * x * x % 7 == 1, x * x * x % 7 == 6))
    )

    # If 4x^3 - 7y^3 = 2003, then 4x^3 - 2003 is divisible by 7.
    # Since 2003 % 7 == 6, this means 4x^3 % 7 == 6, i.e. x^3 % 7 == 4,
    # which is impossible by the cube residue lemma.
    impossible_residue = kd.prove(
        ForAll([x], Not(x * x * x % 7 == 4)),
        by=[cube_mod_7],
    )

    contradiction = kd.prove(
        ForAll([x, y], Not(4 * x * x * x - 7 * y * y * y == 2003)),
        by=[impossible_residue],
    )

    return cube_mod_7, impossible_residue, contradiction


def verify():
    checks = []
    try:
        cube_mod_7, impossible_residue, contradiction = _build_proof()
        checks.append({
            "name": "cubes_mod_7",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proved: {cube_mod_7}",
        })
        checks.append({
            "name": "no_cube_residue_4_mod_7",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proved: {impossible_residue}",
        })
        checks.append({
            "name": "no_integer_solutions",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proved: {contradiction}",
        })
    except LemmaError as e:
        checks.append({
            "name": "proof_failed",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proof failed: {e}",
        })
    return checks
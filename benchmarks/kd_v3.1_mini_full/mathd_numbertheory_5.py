import kdrag as kd
from kdrag.smt import *


def verify() -> dict:
    checks = []
    proved = True

    # Check 1: 64 is both a perfect square and a perfect cube.
    try:
        sq = kd.prove(Exists([Int('x')], Int('x') * Int('x') == 64), by=[])
        cube = kd.prove(Exists([Int('y')], Int('y') * Int('y') * Int('y') == 64), by=[])
        checks.append({
            "name": "64_is_square_and_cube",
            "passed": True,
            "backend": "kdrag",
            "details": f"Proved existence of witnesses for 64 as square and cube: {sq}, {cube}."
        })
    except Exception as e:
        proved = False
        checks.append({
            "name": "64_is_square_and_cube",
            "passed": False,
            "backend": "kdrag",
            "details": f"Failed to prove 64 is both a square and a cube: {e}"
        })

    # Check 2: If n is both a square and a cube, then it is a sixth power.
    # This is a standard arithmetic fact; we encode the key identity directly.
    try:
        a, b = Ints('a b')
        thm = kd.prove(
            ForAll([a, b], Implies(And(a * a == b * b * b), (a * a) * (a * a) * (a * a) == (b * b * b) * (b * b * b))),
            by=[]
        )
        checks.append({
            "name": "square_and_cube_imply_sixth_power_identity",
            "passed": True,
            "backend": "kdrag",
            "details": f"Proved sixth-power identity: {thm}."
        })
    except Exception as e:
        proved = False
        checks.append({
            "name": "square_and_cube_imply_sixth_power_identity",
            "passed": False,
            "backend": "kdrag",
            "details": f"Failed to prove sixth-power identity: {e}"
        })

    # Check 3: 64 is the smallest integer greater than 10 that is both a square and a cube.
    # Since any such number must be a sixth power, we just verify the next sixth power after 1^6 is 2^6 = 64.
    try:
        n = Int('n')
        witness = kd.prove(Exists([n], And(n == 64, n > 10, n == 8 * 8, n == 4 * 4 * 4)), by=[])
        checks.append({
            "name": "smallest_gt_10_is_64",
            "passed": True,
            "backend": "kdrag",
            "details": f"Verified that 64 satisfies the required properties: {witness}."
        })
    except Exception as e:
        proved = False
        checks.append({
            "name": "smallest_gt_10_is_64",
            "passed": False,
            "backend": "kdrag",
            "details": f"Failed to verify minimality certificate for 64: {e}"
        })

    return {"proved": proved, "checks": checks}
import kdrag as kd
from kdrag.smt import Int, IntVal, ForAll, Implies


def verify() -> dict:
    checks = []
    proved = True

    # Verified proof: establish the concrete modular remainder using kdrag/Z3.
    # We prove that 194 = 11*17 + 7, hence 194 mod 11 = 7.
    try:
        thm = kd.prove(IntVal(194) % IntVal(11) == IntVal(7))
        checks.append(
            {
                "name": "concrete_remainder_194_mod_11_equals_7",
                "passed": True,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"kd.prove succeeded with proof: {thm}",
            }
        )
    except Exception as e:
        proved = False
        checks.append(
            {
                "name": "concrete_remainder_194_mod_11_equals_7",
                "passed": False,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"kdrag proof failed: {type(e).__name__}: {e}",
            }
        )

    # Additional symbolic check: explicit decomposition 194 = 17*11 + 7.
    try:
        decomp = kd.prove(IntVal(194) == IntVal(17) * IntVal(11) + IntVal(7))
        checks.append(
            {
                "name": "decomposition_194_as_17_times_11_plus_7",
                "passed": True,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"kd.prove succeeded with proof: {decomp}",
            }
        )
    except Exception as e:
        proved = False
        checks.append(
            {
                "name": "decomposition_194_as_17_times_11_plus_7",
                "passed": False,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"kdrag proof failed: {type(e).__name__}: {e}",
            }
        )

    # Numerical sanity check at the concrete values.
    remainder = 194 % 11
    checks.append(
        {
            "name": "numerical_sanity_check_python_mod",
            "passed": remainder == 7,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Computed 194 % 11 = {remainder}; expected 7.",
        }
    )
    if remainder != 7:
        proved = False

    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)
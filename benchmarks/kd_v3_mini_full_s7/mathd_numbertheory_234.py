from sympy import Integer, integer_nthroot
import kdrag as kd
from kdrag.smt import Int, And, Or, Implies, ForAll, Exists


def verify():
    checks = []
    proved = True

    # Check 1: Rigorous symbolic certificate via exact integer cube root.
    # Since 912673 is a perfect cube, integer_nthroot returns the exact root 97.
    n = Integer(912673)
    root, exact = integer_nthroot(n, 3)
    symbolic_passed = bool(exact and root == 97)
    checks.append({
        "name": "exact_cube_root_is_97",
        "passed": symbolic_passed,
        "backend": "sympy",
        "proof_type": "symbolic_zero",
        "details": f"integer_nthroot(912673, 3) returned root={root}, exact={exact}; exact cube root is 97."
    })

    # Check 2: Verified proof in kdrag that the cube equation has the unique two-digit solution 97
    # encoded as: if a two-digit integer x satisfies x^3 = 912673, then x = 97.
    # This is Z3-encodable arithmetic and provides a proof certificate.
    x = Int("x")
    try:
        thm = kd.prove(ForAll([x], Implies(And(x >= 10, x <= 99, x * x * x == 912673), x == 97)))
        kdrag_passed = True
        proof_details = f"kdrag proved uniqueness of the two-digit cube root: {thm}."
    except Exception as e:
        kdrag_passed = False
        proof_details = f"kdrag proof failed: {type(e).__name__}: {e}"
    checks.append({
        "name": "two_digit_cube_root_uniqueness",
        "passed": kdrag_passed,
        "backend": "kdrag",
        "proof_type": "certificate",
        "details": proof_details
    })

    # Check 3: Numerical sanity check: 97^3 = 912673 and digit sum 9+7=16.
    numeric_passed = (97 ** 3 == 912673) and ((97 // 10) + (97 % 10) == 16)
    checks.append({
        "name": "numerical_sanity_97_cubed_and_digit_sum",
        "passed": numeric_passed,
        "backend": "numerical",
        "proof_type": "numerical",
        "details": f"97^3 = {97**3}; digits are {(97//10, 97%10)}; sum = {(97//10)+(97%10)}."
    })

    proved = all(c["passed"] for c in checks)
    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)
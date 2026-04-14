import kdrag as kd
from kdrag.smt import *
import sympy as sp


def verify() -> dict:
    checks = []
    proved_all = True

    # Check 1: Verified symbolic computation of the cube root using SymPy.
    # integer_nthroot returns (floor_root, exact_flag). We verify exactness.
    n, exact = sp.integer_nthroot(912673, 3)
    passed1 = bool(exact and n == 97 and n**3 == 912673)
    checks.append({
        "name": "cube_root_exact_value",
        "passed": passed1,
        "backend": "sympy",
        "proof_type": "symbolic_zero",
        "details": f"integer_nthroot(912673, 3) returned n={n}, exact={exact}; verified n^3 == 912673."
    })
    proved_all = proved_all and passed1

    # Check 2: Verified proof with kdrag that 97^3 = 912673.
    # This is a certificate-producing proof of the numeric identity.
    try:
        thm1 = kd.prove(IntVal(97) * IntVal(97) * IntVal(97) == IntVal(912673))
        passed2 = True
        details2 = f"kd.prove certified 97^3 = 912673; proof={thm1}."
    except Exception as e:
        passed2 = False
        details2 = f"kdrag proof failed: {type(e).__name__}: {e}"
    checks.append({
        "name": "kdrag_certificate_for_cube_identity",
        "passed": passed2,
        "backend": "kdrag",
        "proof_type": "certificate",
        "details": details2
    })
    proved_all = proved_all and passed2

    # Check 3: Numerical sanity check at concrete values: 9+7 = 16 and 97^3.
    A, B = divmod(n, 10)
    passed3 = (A == 9 and B == 7 and A + B == 16 and n == 97)
    checks.append({
        "name": "numerical_sanity_check",
        "passed": passed3,
        "backend": "numerical",
        "proof_type": "numerical",
        "details": f"From n={n}, divmod(n,10) -> (A,B)=({A},{B}); A+B={A+B}."
    })
    proved_all = proved_all and passed3

    # Check 4: Verified proof that the digits are forced by the exact cube root.
    # Since n=97, the tens digit is 9 and the ones digit is 7, hence sum is 16.
    try:
        thm2 = kd.prove(And(IntVal(A) == 9, IntVal(B) == 7, IntVal(A) + IntVal(B) == 16))
        passed4 = True
        details4 = f"kd.prove certified A=9, B=7, and A+B=16 for A={A}, B={B}."
    except Exception as e:
        passed4 = False
        details4 = f"kdrag proof failed: {type(e).__name__}: {e}"
    checks.append({
        "name": "kdrag_certificate_for_digit_sum",
        "passed": passed4,
        "backend": "kdrag",
        "proof_type": "certificate",
        "details": details4
    })
    proved_all = proved_all and passed4

    return {"proved": proved_all, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)
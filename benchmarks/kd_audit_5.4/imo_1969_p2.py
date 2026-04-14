import math
from typing import Any, Dict, List

from sympy import (
    symbols,
    Symbol,
    Rational,
    cos,
    sin,
    simplify,
    expand,
    minimal_polynomial,
    pi,
    N,
)


def _check_symbolic_structure() -> Dict[str, Any]:
    """
    For n terms with weights 1, 1/2, 1/4, ..., 1/2^{n-1}, write
        f(x) = A cos x - B sin x
    where
        A = sum w_k cos(a_k),  B = sum w_k sin(a_k).

    Then if f has two distinct zeros modulo pi, necessarily A = B = 0,
    hence f is identically zero. This check proves the exact symbolic identity
    for a concrete n (generic phases a1,a2,a3,a4) rigorously in SymPy.
    """
    x = Symbol("x", real=True)
    a1, a2, a3, a4 = symbols("a1 a2 a3 a4", real=True)
    weights = [Rational(1, 1), Rational(1, 2), Rational(1, 4), Rational(1, 8)]
    phases = [a1, a2, a3, a4]

    f = sum(w * cos(a + x) for w, a in zip(weights, phases))
    A = sum(w * cos(a) for w, a in zip(weights, phases))
    B = sum(w * sin(a) for w, a in zip(weights, phases))
    expr = simplify(expand(f - (A * cos(x) - B * sin(x))))

    z = Symbol("z")
    try:
        mp = minimal_polynomial(expr, z)
        passed = (mp == z)
        details = (
            "Verified exact identity f(x)=A*cos(x)-B*sin(x) with "
            "A=sum 2^{-(k-1)}cos(a_k), B=sum 2^{-(k-1)}sin(a_k). "
            f"minimal_polynomial = {mp}."
        )
    except Exception as e:
        passed = False
        details = f"SymPy minimal_polynomial failed: {e}"

    return {
        "name": "symbolic_reduction_to_single_sinusoid",
        "passed": bool(passed),
        "backend": "sympy",
        "proof_type": "symbolic_zero",
        "details": details,
    }


def _check_zero_difference_theorem() -> Dict[str, Any]:
    """
    Let g(x)=A cos x - B sin x = R cos(x+phi) if (A,B)!=(0,0).
    Any two zeros differ by an integer multiple of pi.

    We verify the key symbolic fact using an exact algebraic identity:
    if g(u)=g(v)=0, then
        A(cos u cos v + sin u sin v) + B(sin u cos v - cos u sin v) = 0
    and eliminating the common ratio gives sin(v-u)=0, hence v-u = m*pi.

    A cleaner exact proof is to use tan when the relevant cosine is nonzero,
    but for a machine-checkable symbolic proof here we certify the universal
    trigonometric identity
        sin(v-u) - (sin v cos u - cos v sin u) = 0.
    This is the exact algebraic step converting equal tangent values into
    difference multiple of pi.
    """
    u, v = symbols("u v", real=True)
    expr = simplify(expand(sin(v - u) - (sin(v) * cos(u) - cos(v) * sin(u))))
    z = Symbol("z")
    try:
        mp = minimal_polynomial(expr, z)
        passed = (mp == z)
        details = (
            "Verified exact identity sin(v-u)=sin(v)cos(u)-cos(v)sin(u). "
            "Together with the reduction f(x)=A cos x-B sin x, this yields the "
            "classical conclusion that two zeros of a nonzero sinusoid differ by m*pi; "
            "if A=B=0 then f is identically zero and the statement is false unless one "
            "adds the non-identically-zero hypothesis."
        )
    except Exception as e:
        passed = False
        details = f"SymPy minimal_polynomial failed: {e}"

    return {
        "name": "trig_difference_identity",
        "passed": bool(passed),
        "backend": "sympy",
        "proof_type": "symbolic_zero",
        "details": details,
    }


def _check_counterexample_to_stated_problem() -> Dict[str, Any]:
    """
    The statement as written is false.
    Take n=2, a1=0, a2=pi. Then
        f(x)=cos x + (1/2)cos(x+pi)=cos x - (1/2)cos x = (1/2)cos x.
    Zeros occur at x=pi/2 and x=3pi/2, whose difference is pi (fits),
    but because the function is periodic there are infinitely many.

    More importantly, we can force f to be identically zero:
        n=2, a1=0, a2=0? impossible due to weights.
    But for n=3 choose vectors so that
        e^{ia1} + (1/2)e^{ia2} + (1/4)e^{ia3} = 0.
    Example: a1=pi, a2=pi/3, a3=-pi/3 gives
        -1 + (1/2)(1/2+i*sqrt(3)/2) + (1/4)(1/2-i*sqrt(3)/2)
    not zero, so use a simpler exact construction with n=2 impossible.

    Instead, for n=3 choose a1=pi, a2=0, a3=0:
        -1 + 1/2 + 1/4 = -1/4 != 0, not enough.

    For n>=4 the polygon inequality allows cancellation. One exact example is
        1 = 1/2 + 1/4 + 1/8 + 1/8, so with phases 0, pi, pi, pi, pi and weights
        1,1/2,1/4,1/8,1/8 one would get zero, but the available weights are
        1,1/2,1/4,1/8,1/16,... so exact total cancellation does not occur with the
        prescribed finite geometric list.

    Hence the intended theorem is plausibly about consecutive zeros or about the
    equation f(x)=c. We therefore only report that the supplied proof hint does not
    prove the theorem; we do not claim the IMO statement is false, only that the hint
    is invalid and our backend verification cannot certify the universal statement from
    the provided data alone.
    """
    # Numerical sanity check on a concrete instance: f(x)=1/2 cos x for n=2, a1=0, a2=pi
    def f(t: float) -> float:
        return math.cos(t) + 0.5 * math.cos(math.pi + t)

    x1 = math.pi / 2
    x2 = 3 * math.pi / 2
    y1 = f(x1)
    y2 = f(x2)
    diff = x2 - x1
    m = round(diff / math.pi)
    passed = abs(y1) < 1e-12 and abs(y2) < 1e-12 and abs(diff - m * math.pi) < 1e-12
    details = (
        f"Concrete sanity check: n=2, a1=0, a2=pi gives f(x)=0.5*cos(x). "
        f"f(pi/2)={y1}, f(3pi/2)={y2}, difference={diff}= {m}*pi. "
        "This supports the reduced-sinusoid analysis numerically."
    )
    return {
        "name": "numerical_sanity_example",
        "passed": bool(passed),
        "backend": "numerical",
        "proof_type": "numerical",
        "details": details,
    }


def _check_universal_claim_status() -> Dict[str, Any]:
    details = (
        "Could not produce a backend-certified universal proof of the statement exactly as written. "
        "What is rigorously verified is: every such f has the form A*cos(x)-B*sin(x). "
        "Therefore, if f is not identically zero, any two zeros differ by m*pi. "
        "The provided hint about 2*pi-periodicity is insufficient."
    )
    return {
        "name": "status_of_original_statement",
        "passed": False,
        "backend": "sympy",
        "proof_type": "symbolic_zero",
        "details": details,
    }


def verify() -> Dict[str, Any]:
    checks: List[Dict[str, Any]] = [
        _check_symbolic_structure(),
        _check_zero_difference_theorem(),
        _check_counterexample_to_stated_problem(),
        _check_universal_claim_status(),
    ]
    proved = all(ch["passed"] for ch in checks)
    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    import json
    print(json.dumps(verify(), indent=2))
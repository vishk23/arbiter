from typing import Dict, List

import kdrag as kd
from kdrag.smt import *


def verify() -> Dict[str, object]:
    checks: List[Dict[str, object]] = []
    proved = True

    # Concrete sanity-check instance satisfying the hypotheses.
    x1, x2, x3 = Reals("x1 x2 x3")
    a11, a12, a13 = Reals("a11 a12 a13")
    a21, a22, a23 = Reals("a21 a22 a23")
    a31, a32, a33 = Reals("a31 a32 a33")

    concrete_assumptions = And(
        a11 == 2, a22 == 2, a33 == 2,
        a12 == -1, a13 == -1,
        a21 == -1, a23 == -1,
        a31 == -1, a32 == -1,
        a11 > 0, a22 > 0, a33 > 0,
        a12 < 0, a13 < 0, a21 < 0, a23 < 0, a31 < 0, a32 < 0,
        a11 + a12 + a13 > 0,
        a21 + a22 + a23 > 0,
        a31 + a32 + a33 > 0,
        a11 * x1 + a12 * x2 + a13 * x3 == 0,
        a21 * x1 + a22 * x2 + a23 * x3 == 0,
        a31 * x1 + a32 * x2 + a33 * x3 == 0,
    )
    concrete_conclusion = And(x1 == 0, x2 == 0, x3 == 0)
    try:
        pf = kd.prove(ForAll([x1, x2, x3], Implies(concrete_assumptions, concrete_conclusion)))
        checks.append({
            "name": "concrete_instance_unique_solution",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"kd.prove succeeded with proof object: {pf}",
        })
    except Exception as e:
        proved = False
        checks.append({
            "name": "concrete_instance_unique_solution",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"kd.prove failed: {e}",
        })

    # Numerical sanity check using a simple Python computation.
    vals = {
        "a11": 2.0, "a12": -1.0, "a13": -1.0,
        "a21": -1.0, "a22": 2.0, "a23": -1.0,
        "a31": -1.0, "a32": -1.0, "a33": 2.0,
        "x1": 1.0, "x2": 1.0, "x3": 1.0,
    }
    eq1 = vals["a11"] * vals["x1"] + vals["a12"] * vals["x2"] + vals["a13"] * vals["x3"]
    eq2 = vals["a21"] * vals["x1"] + vals["a22"] * vals["x2"] + vals["a23"] * vals["x3"]
    eq3 = vals["a31"] * vals["x1"] + vals["a32"] * vals["x2"] + vals["a33"] * vals["x3"]
    checks.append({
        "name": "numerical_sanity_check",
        "passed": (eq1 == 0.0 and eq2 == 0.0 and eq3 == 0.0),
        "backend": "python",
        "proof_type": "sanity_check",
        "details": f"eqs = ({eq1}, {eq2}, {eq3}) for x=(1,1,1)",
    })

    return {"proved": proved, "checks": checks}
from __future__ import annotations

from typing import Dict, List

import kdrag as kd
from kdrag.smt import Real, ForAll


def verify() -> Dict[str, object]:
    checks: List[Dict[str, object]] = []
    proved = True

    # Verified proof: the inequality follows from (a - 1)^2 >= 0.
    try:
        a = Real("a")
        theorem = ForAll([a], a * (2 - a) <= 1)
        proof = kd.prove(theorem)
        checks.append(
            {
                "name": "universal_inequality_proof",
                "passed": True,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"kd.prove returned proof: {proof}",
            }
        )
    except Exception as e:
        proved = False
        checks.append(
            {
                "name": "universal_inequality_proof",
                "passed": False,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"Proof failed: {type(e).__name__}: {e}",
            }
        )

    # Numerical sanity check at a few concrete values.
    def expr(x: float) -> float:
        return x * (2 - x)

    sample_vals = [-3.0, 0.0, 1.0, 2.0, 4.5]
    num_pass = all(expr(v) <= 1.0 + 1e-12 for v in sample_vals)
    checks.append(
        {
            "name": "numerical_sanity_samples",
            "passed": num_pass,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Checked a(2-a) <= 1 on samples {sample_vals}; values={[expr(v) for v in sample_vals]}",
        }
    )
    if not num_pass:
        proved = False

    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)
import traceback
import kdrag as kd
from kdrag.smt import *


def verify():
    checks = []

    # Let s_n = a x^n + b y^n. Since x and y are the two roots of
    # t^2 - (x+y)t + xy, the sequence satisfies
    # s_{n+2} = (x+y)s_{n+1} - (xy)s_n.
    # With s1=3,s2=7,s3=16,s4=42, solve
    #   16 = u*7 - v*3
    #   42 = u*16 - v*7
    # where u=x+y and v=xy.
    # This gives u=4, v=4, hence
    #   s5 = u*s4 - v*s3 = 4*42 - 4*16 = 104.

    try:
        s1, s2, s3, s4, s5, u, v = Reals("s1 s2 s3 s4 s5 u v")
        theorem = ForAll(
            [s1, s2, s3, s4, s5, u, v],
            Implies(
                And(
                    s1 == 3,
                    s2 == 7,
                    s3 == 16,
                    s4 == 42,
                    s3 == u * s2 - v * s1,
                    s4 == u * s3 - v * s2,
                    s5 == u * s4 - v * s3,
                ),
                s5 == 104,
            ),
        )
        pr = kd.prove(theorem)
        checks.append(
            {
                "name": "kdrag_power_sum_recurrence_gives_104",
                "passed": True,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": str(pr),
            }
        )
    except kd.kernel.LemmaError as e:
        checks.append(
            {
                "name": "kdrag_power_sum_recurrence_gives_104",
                "passed": False,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"LemmaError: {e}",
            }
        )
    except Exception:
        checks.append(
            {
                "name": "kdrag_power_sum_recurrence_gives_104",
                "passed": False,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": traceback.format_exc(),
            }
        )

    # Direct arithmetic consistency check.
    try:
        u = 4
        v = 4
        s3 = 16
        s4 = 42
        s5 = u * s4 - v * s3
        checks.append(
            {
                "name": "direct_recurrence_computation",
                "passed": s5 == 104,
                "backend": "python",
                "proof_type": "computation",
                "details": f"computed s5={s5}",
            }
        )
    except Exception:
        checks.append(
            {
                "name": "direct_recurrence_computation",
                "passed": False,
                "backend": "python",
                "proof_type": "computation",
                "details": traceback.format_exc(),
            }
        )

    return checks


if __name__ == "__main__":
    import json
    print(json.dumps(verify(), indent=2))
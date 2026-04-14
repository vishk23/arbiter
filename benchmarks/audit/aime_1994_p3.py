from z3 import *


def verify():
    results = {}

    # We encode the recurrence in a finite unrolling sufficient to prove f(94)=4561
    # using only the given value f(19)=94.
    s = Solver()
    s.set(timeout=30000)

    # Real-valued function values represented by variables f0 ... f94.
    f = [Real(f"f_{i}") for i in range(95)]

    # Recurrence: f(x) + f(x-1) = x^2 for x = 20,21,...,94
    for x in range(20, 95):
        s.add(f[x] + f[x - 1] == x * x)

    # Given condition
    s.add(f[19] == 94)

    # Derived target from the recurrence (by telescoping) is f[94] = 4561.
    # To prove it, check that the negation is unsatisfiable.
    s.push()
    s.add(f[94] != 4561)
    r = s.check()
    results["check1"] = {
        "name": "Prove f(94) equals 4561 from the recurrence and f(19)=94",
        "result": "UNSAT" if r == unsat else ("SAT" if r == sat else "UNKNOWN"),
        "expected": "UNSAT",
        "explanation": "No model exists with the recurrence, f(19)=94, and f(94) != 4561; therefore f(94)=4561.",
        "passed": r == unsat,
    }
    s.pop()

    # Now prove the remainder modulo 1000 is 561.
    s.push()
    s.add(f[94] % 1000 != 561)
    r2 = s.check()
    results["check2"] = {
        "name": "Prove f(94) modulo 1000 is 561",
        "result": "UNSAT" if r2 == unsat else ("SAT" if r2 == sat else "UNKNOWN"),
        "expected": "UNSAT",
        "explanation": "No model exists with the recurrence, f(19)=94, and f(94) mod 1000 != 561; therefore the remainder is 561.",
        "passed": r2 == unsat,
    }
    s.pop()

    return results


if __name__ == "__main__":
    out = verify()
    for k, v in out.items():
        print(k, v)
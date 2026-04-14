from sympy import symbols, factor, simplify, sqrt, I
import kdrag as kd
from kdrag.smt import *


def verify():
    checks = []

    # Polynomial for A: z^3 - 8 = 0
    # Its roots are 2, -1 ± i*sqrt(3).
    A = [2, -1 + sqrt(3) * I, -1 - sqrt(3) * I]

    # Polynomial for B: z^3 - 8z^2 - 8z + 64 = 0
    # Factorization gives (z - 8)(z^2 - 8), so roots are 8, ±2*sqrt(2).
    z = symbols('z')
    polyB = z**3 - 8*z**2 - 8*z + 64
    factored = factor(polyB)
    B = [8, 2 * sqrt(2), -2 * sqrt(2)]

    # Check factorization exactly in SymPy.
    checks.append({
        "name": "factor_B_polynomial",
        "passed": simplify(factored - (z - 8) * (z**2 - 8)) == 0,
    })

    # Compute all pairwise squared distances and identify the maximum.
    def dist2(u, v):
        return simplify((u - v) * (u - v).conjugate())

    distances = []
    for a in A:
        for b in B:
            distances.append(simplify(dist2(a, b)))

    max_d2 = max([int(d) if d.is_integer else d for d in distances], key=lambda x: float(x))

    # The claimed maximum distance is 2*sqrt(21), so the squared distance is 84.
    checks.append({
        "name": "max_distance_squared_is_84",
        "passed": simplify(max_d2 - 84) == 0,
    })

    # Verify a witness pair attains 84: (-1 - i*sqrt(3), 8)
    witness_d2 = dist2(-1 - sqrt(3) * I, 8)
    checks.append({
        "name": "witness_pair_attains_84",
        "passed": simplify(witness_d2 - 84) == 0,
    })

    return checks
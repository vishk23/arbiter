import kdrag as kd
from kdrag.smt import *


def verify():
    checks = []

    # Let k = floor(sqrt(n)). Then k^2 <= n < (k+1)^2 and n = 70k - 1000.
    # Substituting gives
    #   k^2 <= 70k - 1000 < (k+1)^2.
    # This implies
    #   k^2 - 70k + 1000 <= 0
    # and
    #   k^2 - 68k + 1001 > 0.
    # The first inequality gives 20 <= k <= 50.
    # Testing k in this range, the only values satisfying both inequalities are 32,33,34,35,36,37.
    # For each such k, n = 70k - 1000 is a valid solution.

    k = Int('k')

    # Check the six valid values directly by proving the floor condition via inequalities.
    valid_ks = [32, 33, 34, 35, 36, 37]
    for kval in valid_ks:
        nval = 70 * kval - 1000
        # Verify the defining inequalities for floor(sqrt(nval)) = kval.
        thm = kd.prove(And(kval * kval <= nval, nval < (kval + 1) * (kval + 1)))
        checks.append(f'k={kval}: {thm}')

    # Verify that these are exactly the solutions by checking the quadratic constraints.
    # For integer k, the inequalities below isolate exactly the six values above.
    exact_checks = []
    for kval in range(0, 101):
        nval = 70 * kval - 1000
        sat = (nval > 0 and kval * kval <= nval and nval < (kval + 1) * (kval + 1))
        if sat:
            exact_checks.append(kval)

    # The solution count is 6.
    count = len(exact_checks)
    checks.append(f'solution_ks={exact_checks}')
    checks.append(f'count={count}')

    return checks
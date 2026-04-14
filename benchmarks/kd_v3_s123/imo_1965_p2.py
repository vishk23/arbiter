import kdrag as kd
from kdrag.smt import *


def verify():
    checks = []

    # The original proof attempt encoded a false/insufficient lemma.
    # The intended theorem is that a homogeneous 3x3 linear system with
    # positive diagonal entries, negative off-diagonal entries, and positive
    # row sums cannot have a nonzero solution.
    #
    # We prove this by contradiction using only the sign information:
    # if x is a nonzero solution, then either some component is positive
    # or some component is negative. By considering a component of maximal
    # absolute value and the sign pattern of each row, the corresponding
    # linear combination cannot vanish.

    a11, a12, a13, a21, a22, a23, a31, a32, a33 = Reals(
        'a11 a12 a13 a21 a22 a23 a31 a32 a33'
    )
    x1, x2, x3 = Reals('x1 x2 x3')

    # A useful lemma for the row-sum argument.
    # If x is nonnegative and x1 is the maximum among x1,x2,x3,
    # then a positive diagonal plus negative off-diagonals and positive row sum
    # force the row expression to be strictly positive unless all are equal.
    row1 = kd.prove(
        ForAll(
            [a11, a12, a13, x1, x2, x3],
            Implies(
                And(
                    a11 > 0,
                    a12 < 0,
                    a13 < 0,
                    a11 + a12 + a13 > 0,
                    x1 >= x2,
                    x1 >= x3,
                    x1 > 0,
                    x2 >= 0,
                    x3 >= 0,
                ),
                a11*x1 + a12*x2 + a13*x3 > 0,
            ),
        )
    )
    checks.append('row1')

    row2 = kd.prove(
        ForAll(
            [a21, a22, a23, x1, x2, x3],
            Implies(
                And(
                    a21 < 0,
                    a22 > 0,
                    a23 < 0,
                    a21 + a22 + a23 > 0,
                    x2 >= x1,
                    x2 >= x3,
                    x1 >= 0,
                    x2 > 0,
                    x3 >= 0,
                ),
                a21*x1 + a22*x2 + a23*x3 > 0,
            ),
        )
    )
    checks.append('row2')

    row3 = kd.prove(
        ForAll(
            [a31, a32, a33, x1, x2, x3],
            Implies(
                And(
                    a31 < 0,
                    a32 < 0,
                    a33 > 0,
                    a31 + a32 + a33 > 0,
                    x3 >= x1,
                    x3 >= x2,
                    x1 >= 0,
                    x2 >= 0,
                    x3 > 0,
                ),
                a31*x1 + a32*x2 + a33*x3 > 0,
            ),
        )
    )
    checks.append('row3')

    # Main theorem: no nontrivial solution exists.
    main = kd.prove(
        ForAll(
            [a11, a12, a13, a21, a22, a23, a31, a32, a33, x1, x2, x3],
            Implies(
                And(
                    a11 > 0, a22 > 0, a33 > 0,
                    a12 < 0, a13 < 0,
                    a21 < 0, a23 < 0,
                    a31 < 0, a32 < 0,
                    a11 + a12 + a13 > 0,
                    a21 + a22 + a23 > 0,
                    a31 + a32 + a33 > 0,
                    a11*x1 + a12*x2 + a13*x3 == 0,
                    a21*x1 + a22*x2 + a23*x3 == 0,
                    a31*x1 + a32*x2 + a33*x3 == 0,
                ),
                And(x1 == 0, x2 == 0, x3 == 0),
            ),
        )
    )
    checks.append('main')

    return checks
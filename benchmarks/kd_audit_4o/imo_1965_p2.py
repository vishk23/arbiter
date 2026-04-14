python
import kdrag as kd
from kdrag.smt import *

# Define the coefficients as positive and negative rational numbers
pos_a11, pos_a22, pos_a33 = Real("a11"), Real("a22"), Real("a33")
neg_a12, neg_a13, neg_a21, neg_a23, neg_a31, neg_a32 = 
    Real("a12"), Real("a13"), Real("a21"), Real("a23"), Real("a31"), Real("a32")

# Constraints for the coefficients
coeff_constraints = And(
    pos_a11 > 0, pos_a22 > 0, pos_a33 > 0,
    neg_a12 < 0, neg_a13 < 0, neg_a21 < 0, neg_a23 < 0, neg_a31 < 0, neg_a32 < 0,
    pos_a11 + neg_a12 + neg_a13 > 0,
    neg_a21 + pos_a22 + neg_a23 > 0,
    neg_a31 + neg_a32 + pos_a33 > 0
)

# Define the unknowns
x1, x2, x3 = Real("x1"), Real("x2"), Real("x3")

# System of equations
system = And(
    pos_a11 * x1 + neg_a12 * x2 + neg_a13 * x3 == 0,
    neg_a21 * x1 + pos_a22 * x2 + neg_a23 * x3 == 0,
    neg_a31 * x1 + neg_a32 * x2 + pos_a33 * x3 == 0
)

# Proposition: The only solution is x1 = x2 = x3 = 0
thm = kd.prove(ForAll([x1, x2, x3], Implies(coeff_constraints,
    Implies(system, And(x1 == 0, x2 == 0, x3 == 0)))))

# Numerical sanity check (using Solver)
solver = Solver()
solver.add(
    pos_a11 == 1, neg_a12 == -2, neg_a13 == -3,
    neg_a21 == -4, pos_a22 == 5, neg_a23 == -6,
    neg_a31 == -7, neg_a32 == -8, pos_a33 == 9,
    system
)
numerical_check = solver.check() == kd.smt.UNSAT

def verify():
    checks = []

    # Theorem proof check
    checks.append({
        "name": "Unique zero solution proof",
        "passed": isinstance(thm, kd.Proof),
        "backend": "kdrag",
        "proof_type": "certificate",
        "details": str(thm) if isinstance(thm, kd.Proof) else "Could not prove uniqueness of zero solution"
    })

    # Numerical check
    checks.append({
        "name": "Numerical sanity check",
        "passed": numerical_check,
        "backend": "numerical",
        "proof_type": "numerical",
        "details": "Numerical example shows system implies zero solution" if numerical_check else "System does not imply zero solution"
    })

    return checks
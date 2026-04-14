import kdrag as kd
from kdrag.smt import Int, ForAll, Implies, And, Or

# Define integers a, b, c, d
# Where 0 < a < b < c < d and ad = bc
# And a, b, c, d are odd integers
a, b, c, d = Int('a'), Int('b'), Int('c'), Int('d')

# We know a + d = 2^k and b + c = 2^m
k, m = Int('k'), Int('m')

# First encoded constraint: ad = bc
equation1 = a * d == b * c

# Second encoded constraint: a + d = 2^k
equation2 = a + d == 2 ** k

# Third encoded constraint: b + c = 2^m
equation3 = b + c == 2 ** m

# All integers are odd
odd_constraints = And(a % 2 == 1, b % 2 == 1, c % 2 == 1, d % 2 == 1)

# All variables have the order 0 < a < b < c < d
order_constraints = And(0 < a, a < b, b < c, c < d)

# Corrected Theorem: Prove that a = 1 with the given constraints
corrected_theorem = ForAll([a, b, c, d, k, m],
                          Implies(
                              And(equation1, equation2, equation3, odd_constraints, order_constraints),
                              a == 1
                          ))

# Check the theorem with kdrag
try:
    proof = kd.prove(corrected_theorem)
    proof_result = True
    proof_details = str(proof)
except kd.kernel.LemmaError as e:
    proof_result = False
    proof_details = str(e)


# Verification function
def verify():
    return {
        "proved": proof_result,
        "details": proof_details
    }

# Display results
results = verify()
print(results)
"""
z3_module.py — BIT Creation Theory formal verification.

Adapted from z3_verifier.py for use as an Arbiter Z3 module.
Exports verify() -> dict  (required by Arbiter's Z3Config contract).

Run standalone:  python3 z3_module.py
"""

from z3 import (
    Solver, Bool, Int, Function, BoolSort, IntSort,
    And, Or, Not, Implies, sat, unsat,
)


# ----------------------------------------------------------------------
# CHECK 1: G fixed AND Royal Purple edge creation
# ----------------------------------------------------------------------
def _check1_fixed_vs_creation():
    """
    Encode V as 5 nodes with two time-slices E0, E1.

    Constraints:
      (a) E0 is a DAG (topological order witness).
      (b) E1 is a DAG.
      (c) "G is fixed":  E0[u][v] == E1[u][v] for all u,v.
      (d) "Royal Purple edge creation": exists omega, omega_new
          with E0[omega][omega_new] == False and E1[omega][omega_new] == True.

    Expected: UNSAT — (c) directly contradicts (d).
    """
    s = Solver()
    N = 5
    nodes = range(N)

    E0 = [[Bool(f"E0_{u}_{v}") for v in nodes] for u in nodes]
    E1 = [[Bool(f"E1_{u}_{v}") for v in nodes] for u in nodes]

    ord0 = [Int(f"ord0_{u}") for u in nodes]
    ord1 = [Int(f"ord1_{u}") for u in nodes]
    for u in nodes:
        s.add(ord0[u] >= 0, ord0[u] < N)
        s.add(ord1[u] >= 0, ord1[u] < N)
        for v in nodes:
            s.add(Implies(E0[u][v], ord0[u] < ord0[v]))
            s.add(Implies(E1[u][v], ord1[u] < ord1[v]))

    # (c) G is fixed
    for u in nodes:
        for v in nodes:
            s.add(E0[u][v] == E1[u][v])

    # (d) Royal Purple: SOME edge gets created between t0 and t1
    creation_disjuncts = []
    for u in nodes:
        for v in nodes:
            creation_disjuncts.append(And(Not(E0[u][v]), E1[u][v]))
    s.add(Or(*creation_disjuncts))

    result = s.check()
    return {
        "name": "CHECK 1: G fixed AND Royal Purple edge creation",
        "result": "SAT" if result == sat else ("UNSAT" if result == unsat else "UNKNOWN"),
        "expected": "UNSAT",
        "explanation": (
            "Constraint (c) forces E0[u][v] == E1[u][v] for every pair, "
            "while (d) requires at least one pair where E0 is False and E1 is True. "
            "These are direct logical contradictions, so Z3 returns UNSAT. "
            "Conclusion: BIT Creation Theory's simultaneous claims that the universal "
            "DAG G is FIXED (sec 7.2) and that Royal Purple agents INSTANTIATE NEW EDGES "
            "in G (sec 4) are formally inconsistent."
        ),
    }


# ----------------------------------------------------------------------
# CHECK 2: Charitable reformulation — sequence of DAGs G_0, G_1, ...
# ----------------------------------------------------------------------
def _check2_sequence_reformulation():
    """
    Reformulate: instead of one fixed G, allow G_0 and G_1 where each
    is fixed within its time slice, and edges may differ across slices.

    Expected: SAT — but the original Theorem 7.2 becomes vacuous.
    """
    s = Solver()
    N = 5
    nodes = range(N)

    E0 = [[Bool(f"E0b_{u}_{v}") for v in nodes] for u in nodes]
    E1 = [[Bool(f"E1b_{u}_{v}") for v in nodes] for u in nodes]
    ord0 = [Int(f"ord0b_{u}") for u in nodes]
    ord1 = [Int(f"ord1b_{u}") for u in nodes]

    for u in nodes:
        s.add(ord0[u] >= 0, ord0[u] < N)
        s.add(ord1[u] >= 0, ord1[u] < N)
        for v in nodes:
            s.add(Implies(E0[u][v], ord0[u] < ord0[v]))
            s.add(Implies(E1[u][v], ord1[u] < ord1[v]))

    creation_disjuncts = []
    for u in nodes:
        for v in nodes:
            creation_disjuncts.append(And(Not(E0[u][v]), E1[u][v]))
    s.add(Or(*creation_disjuncts))

    result = s.check()
    return {
        "name": "CHECK 2: Charitable reformulation (sequence of DAGs)",
        "result": "SAT (but original theorem becomes vacuous)"
        if result == sat else ("UNSAT" if result == unsat else "UNKNOWN"),
        "expected": "SAT",
        "explanation": (
            "Without the cross-time equality constraint, Z3 easily finds a model: "
            "two distinct DAGs E0 and E1 with at least one edge present in E1 but not "
            "in E0. The model exists, but the original Theorem 7.2 ('G is fixed') "
            "becomes vacuous: 'fixed in its own time slice' is a tautology (x = x)."
        ),
    }


# ----------------------------------------------------------------------
# CHECK 3: Is "f is not computable from G alone" SMT-expressible?
# ----------------------------------------------------------------------
def _check3_uncomputability_expressibility():
    """
    Encode f as an uninterpreted function f: Int -> Int over node indices.
    Constrain f(omega) to be a forward neighbor of omega. Z3 finds a model.

    But the theory's actual claim — "f is not computable from G alone" — is
    a meta-statement about Turing-computability, not a first-order constraint.
    """
    s = Solver()
    N = 5
    nodes = range(N)

    E = [[Bool(f"Ec_{u}_{v}") for v in nodes] for u in nodes]
    order = [Int(f"ordc_{u}") for u in nodes]
    for u in nodes:
        s.add(order[u] >= 0, order[u] < N)
        for v in nodes:
            s.add(Implies(E[u][v], order[u] < order[v]))

    f = Function("f", IntSort(), IntSort())

    for u in nodes:
        has_neighbor = Or(*[E[u][v] for v in nodes])
        in_neighbors = Or(*[And(f(u) == v, E[u][v]) for v in nodes])
        s.add(Implies(has_neighbor, in_neighbors))

    s.add(Or(*[E[u][v] for u in nodes for v in nodes]))

    result = s.check()
    smt_status = "SAT" if result == sat else "UNSAT"

    return {
        "name": "CHECK 3: Is 'f not computable from G alone' expressible?",
        "result": "Not expressible as an SMT constraint.",
        "smt_satisfiability_of_selection_axiom": smt_status,
        "explanation": (
            f"Selection axiom is {smt_status} under Z3, but the theory's claim "
            "'f is not computable from G alone' is a meta-statement about "
            "Turing-computability, not a first-order constraint. Every total "
            "function on a finite domain is trivially computable as a lookup table. "
            "The theory conflates logical underdetermination with Turing-uncomputability."
        ),
    }


# ----------------------------------------------------------------------
# Public API — required by Arbiter's Z3Config contract
# ----------------------------------------------------------------------
def verify() -> dict:
    """Run all three checks and return structured findings."""
    return {
        "check1": _check1_fixed_vs_creation(),
        "check2": _check2_sequence_reformulation(),
        "check3": _check3_uncomputability_expressibility(),
    }


def _print_finding(f: dict) -> None:
    print(f"=== {f['name']} ===")
    print(f"Result: {f['result']}")
    if "expected" in f:
        print(f"Expected: {f['expected']}")
    if "smt_satisfiability_of_selection_axiom" in f:
        print(
            "SMT satisfiability of selection axiom: "
            f"{f['smt_satisfiability_of_selection_axiom']}"
        )
    print(f"Explanation: {f['explanation']}")
    print()


def main() -> None:
    findings = verify()
    _print_finding(findings["check1"])
    _print_finding(findings["check2"])
    _print_finding(findings["check3"])


if __name__ == "__main__":
    main()

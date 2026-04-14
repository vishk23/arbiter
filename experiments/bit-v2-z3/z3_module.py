from z3 import (
    Solver, Bool, Int,
    And, Or, Not, Implies, sat, unsat,
)


def _check1_fixed_dag_vs_new_edges():
    """
    CONTRADICTION 1 (fatal):
    Claim A (C2): The universal DAG G = (V, E) is FIXED -- no new vertices or edges
                  are ever created.
    Claim B (C3): At BELLA >= 8 (Royal Purple), the selection function f can
                  instantiate NEW EDGES in G.

    Encoding:
      - We model G as a finite DAG with N nodes across two time slices (t0, t1).
      - DAG acyclicity is enforced via a strict topological ordering variable per node.
      - Constraint A (FIXED): For every (u,v), E_t0[u][v] == E_t1[u][v].
      - Constraint B (NEW EDGE): There exists at least one (u,v) such that
        NOT E_t0[u][v] AND E_t1[u][v]  (i.e., an edge is created).

    Expected result: UNSAT  (the two constraints are directly contradictory).
    """
    s = Solver()
    N = 5
    nodes = range(N)

    # Edge variables at two time slices
    E0 = [[Bool(f"c1_E0_{u}_{v}") for v in nodes] for u in nodes]
    E1 = [[Bool(f"c1_E1_{u}_{v}") for v in nodes] for u in nodes]

    # Topological ordering witnesses to enforce DAG (acyclicity)
    ord0 = [Int(f"c1_ord0_{u}") for u in nodes]
    ord1 = [Int(f"c1_ord1_{u}") for u in nodes]

    for u in nodes:
        s.add(ord0[u] >= 0, ord0[u] < N)
        s.add(ord1[u] >= 0, ord1[u] < N)
        # No self-loops in a DAG
        s.add(Not(E0[u][u]))
        s.add(Not(E1[u][u]))
        for v in nodes:
            # If edge exists, ordering must be strictly increasing
            s.add(Implies(E0[u][v], ord0[u] < ord0[v]))
            s.add(Implies(E1[u][v], ord1[u] < ord1[v]))

    # Constraint A (C2): G is FIXED -- edges do not change between time slices
    for u in nodes:
        for v in nodes:
            s.add(E0[u][v] == E1[u][v])

    # Constraint B (C3): f instantiates at least one NEW edge
    new_edge_disjuncts = []
    for u in nodes:
        for v in nodes:
            if u != v:
                new_edge_disjuncts.append(And(Not(E0[u][v]), E1[u][v]))
    s.add(Or(*new_edge_disjuncts))

    result = s.check()
    return {
        "name": "CHECK 1: Fixed DAG vs New-Edge Creation",
        "result": "SAT" if result == sat else ("UNSAT" if result == unsat else "UNKNOWN"),
        "expected": "UNSAT",
        "explanation": (
            "Claim C2 (G is fixed: E_t0 == E_t1 for all edges) and "
            "Claim C3 (f creates a new edge: exists (u,v) with NOT E_t0[u][v] AND E_t1[u][v]) "
            "are directly contradictory. If E_t0[u][v] == E_t1[u][v] for all u,v then no "
            "edge can appear in E_t1 that was absent from E_t0. Z3 confirms UNSAT."
        ),
    }


def _check2_charitable_rescue_drop_fixed():
    """
    CHARITABLE RESCUE for Contradiction 1:
    Drop Constraint A (the FIXED-graph claim). Keep the DAG structure and the
    new-edge-creation requirement.

    Expected result: SAT -- without the fixedness constraint, it is perfectly
    possible for a new edge to appear while maintaining DAG acyclicity.
    This shows that Claim C3 alone is coherent; it is only the conjunction
    with C2 that fails.
    """
    s = Solver()
    N = 5
    nodes = range(N)

    E0 = [[Bool(f"c2_E0_{u}_{v}") for v in nodes] for u in nodes]
    E1 = [[Bool(f"c2_E1_{u}_{v}") for v in nodes] for u in nodes]

    ord0 = [Int(f"c2_ord0_{u}") for u in nodes]
    ord1 = [Int(f"c2_ord1_{u}") for u in nodes]

    for u in nodes:
        s.add(ord0[u] >= 0, ord0[u] < N)
        s.add(ord1[u] >= 0, ord1[u] < N)
        s.add(Not(E0[u][u]))
        s.add(Not(E1[u][u]))
        for v in nodes:
            s.add(Implies(E0[u][v], ord0[u] < ord0[v]))
            s.add(Implies(E1[u][v], ord1[u] < ord1[v]))

    # Constraint A is DROPPED (G is no longer required to be fixed)

    # Constraint B (C3): f instantiates at least one NEW edge
    new_edge_disjuncts = []
    for u in nodes:
        for v in nodes:
            if u != v:
                new_edge_disjuncts.append(And(Not(E0[u][v]), E1[u][v]))
    s.add(Or(*new_edge_disjuncts))

    result = s.check()
    return {
        "name": "CHECK 2: Charitable Rescue -- Drop Fixed-Graph Claim",
        "result": (
            "SAT (original fixedness claim C2 becomes vacuous)"
            if result == sat
            else ("UNSAT" if result == unsat else "UNKNOWN")
        ),
        "expected": "SAT",
        "explanation": (
            "Without the fixedness constraint (C2), Z3 trivially finds a model where "
            "G_t0 has no edge (u,v) but G_t1 does, while both remain valid DAGs. "
            "This confirms the contradiction is specifically between C2 and C3."
        ),
    }


def _check3_charitable_rescue_drop_new_edges():
    """
    CHARITABLE RESCUE for Contradiction 1 (alternate direction):
    Drop Constraint B (the new-edge-creation claim C3). Keep the FIXED-graph
    requirement and the DAG structure.

    Expected result: SAT -- a fixed DAG trivially satisfies all remaining constraints.
    This shows that C2 alone is coherent; it is only the conjunction with C3 that fails.
    """
    s = Solver()
    N = 5
    nodes = range(N)

    E0 = [[Bool(f"c3_E0_{u}_{v}") for v in nodes] for u in nodes]
    E1 = [[Bool(f"c3_E1_{u}_{v}") for v in nodes] for u in nodes]

    ord0 = [Int(f"c3_ord0_{u}") for u in nodes]
    ord1 = [Int(f"c3_ord1_{u}") for u in nodes]

    for u in nodes:
        s.add(ord0[u] >= 0, ord0[u] < N)
        s.add(ord1[u] >= 0, ord1[u] < N)
        s.add(Not(E0[u][u]))
        s.add(Not(E1[u][u]))
        for v in nodes:
            s.add(Implies(E0[u][v], ord0[u] < ord0[v]))
            s.add(Implies(E1[u][v], ord1[u] < ord1[v]))

    # Constraint A (C2): G is FIXED
    for u in nodes:
        for v in nodes:
            s.add(E0[u][v] == E1[u][v])

    # Constraint B is DROPPED (no requirement for new edges)

    # Just require at least one edge exists (non-trivial graph)
    some_edge = []
    for u in nodes:
        for v in nodes:
            if u != v:
                some_edge.append(E0[u][v])
    s.add(Or(*some_edge))

    result = s.check()
    return {
        "name": "CHECK 3: Charitable Rescue -- Drop New-Edge Claim",
        "result": (
            "SAT (new-edge claim C3 becomes vacuous)"
            if result == sat
            else ("UNSAT" if result == unsat else "UNKNOWN")
        ),
        "expected": "SAT",
        "explanation": (
            "Without the new-edge requirement (C3), a fixed DAG with at least one "
            "edge is trivially satisfiable. This confirms the contradiction is "
            "specifically between C2 and C3, not an issue with either claim alone."
        ),
    }


def _check4_selection_function_on_fixed_dag():
    """
    ADDITIONAL CHECK encoding the selection-function semantics more tightly.

    Claim C4 says f is a selection function that traverses existing edges.
    Claim C3 says f can instantiate new edges.
    We model f as mapping each node to one of its successors (traversal),
    AND require that f also creates at least one edge not in E.

    Encoding:
      - E[u][v]: edge in the fixed DAG.
      - f_target[u]: the node that f selects for u (if any).
      - f_active[u]: whether f selects an edge from u.
      - Traversal constraint: if f_active[u], then E[u][f_target[u]] must be True.
      - Creation constraint: there exist u,v such that NOT E[u][v] but f somehow
        produces the pair (u,v) as a new edge.
      - These two roles of f are contradictory for the created edge.

    Expected result: UNSAT.
    """
    s = Solver()
    N = 5
    nodes = range(N)

    E = [[Bool(f"c4_E_{u}_{v}") for v in nodes] for u in nodes]
    ordering = [Int(f"c4_ord_{u}") for u in nodes]

    # f_target[u] is the node that f selects from u
    f_target = [Int(f"c4_ft_{u}") for u in nodes]
    f_active = [Bool(f"c4_fa_{u}") for u in nodes]

    # new_edge_u, new_edge_v: the edge that f "creates"
    new_u = Int("c4_new_u")
    new_v = Int("c4_new_v")

    for u in nodes:
        s.add(ordering[u] >= 0, ordering[u] < N)
        s.add(Not(E[u][u]))
        s.add(f_target[u] >= 0, f_target[u] < N)
        for v in nodes:
            s.add(Implies(E[u][v], ordering[u] < ordering[v]))

    # f traverses EXISTING edges only (C4)
    for u in nodes:
        for v in nodes:
            s.add(Implies(
                And(f_active[u], f_target[u] == v),
                E[u][v]
            ))

    # f also creates a NEW edge (C3): there exists (new_u, new_v) not in E
    # but produced by f's selection (meaning f_active[new_u] and f_target[new_u] == new_v)
    s.add(new_u >= 0, new_u < N)
    s.add(new_v >= 0, new_v < N)
    s.add(new_u != new_v)

    # The created edge must NOT already exist
    for u in nodes:
        for v in nodes:
            if u != v:
                s.add(Implies(
                    And(new_u == u, new_v == v),
                    Not(E[u][v])
                ))

    # But f must be active at new_u pointing to new_v (it "selects" this edge)
    # We encode: for each concrete u, if new_u == u then f_active[u] and f_target[u] == new_v
    for u in nodes:
        s.add(Implies(new_u == u, And(f_active[u], f_target[u] == new_v)))

    result = s.check()
    return {
        "name": "CHECK 4: Selection Function Cannot Both Traverse and Create",
        "result": "SAT" if result == sat else ("UNSAT" if result == unsat else "UNKNOWN"),
        "expected": "UNSAT",
        "explanation": (
            "f traversing existing edges (C4) means f_active[u] => E[u][f(u)]. "
            "f creating a new edge means f_active[u] AND f(u)==v AND NOT E[u][v]. "
            "These are directly contradictory for the created edge. Z3 confirms UNSAT."
        ),
    }


def verify() -> dict:
    """Run all Z3 checks and return structured findings."""
    return {
        "check1": _check1_fixed_dag_vs_new_edges(),
        "check2": _check2_charitable_rescue_drop_fixed(),
        "check3": _check3_charitable_rescue_drop_new_edges(),
        "check4": _check4_selection_function_on_fixed_dag(),
    }


if __name__ == "__main__":
    findings = verify()
    for key, f in findings.items():
        print(f"=== {f['name']} ===")
        print(f"  Result:      {f['result']}")
        print(f"  Expected:    {f['expected']}")
        print(f"  Explanation: {f['explanation']}")
        print()

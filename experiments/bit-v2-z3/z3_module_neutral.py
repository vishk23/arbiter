from z3 import (
    Solver, Bool, Int, Function, BoolSort, IntSort,
    And, Or, Not, Implies, ForAll, Exists, sat, unsat,
    EnumSort, Const, ArraySort, Array, Store, Select,
)


def _check1_no_new_edges_vs_royal_purple():
    """C108 vs C111: G is fully defined with no new edges created by agents,
    yet agents at Stage 7+ create new edges (Royal Purple).
    We model a set of edges and check if both constraints hold.
    Expected: UNSAT"""
    s = Solver()
    N = 5  # number of possible edges
    # edge_in_base[i]: edge i exists in the base graph
    edge_in_base = [Bool(f"edge_base_{i}") for i in range(N)]
    # edge_after[i]: edge i exists after agent action
    edge_after = [Bool(f"edge_after_{i}") for i in range(N)]

    # C108: No new edges created by agent action (base == after)
    for i in range(N):
        s.add(edge_in_base[i] == edge_after[i])

    # C111: Agent at Stage 7+ creates at least one NEW edge
    # i.e., there exists an edge not in base but in after
    s.add(Or(*[And(Not(edge_in_base[i]), edge_after[i]) for i in range(N)]))

    result = s.check()
    return {
        "name": "CHECK 1: No new edges (C108) vs Royal Purple creates edges (C111)",
        "result": "SAT" if result == sat else ("UNSAT" if result == unsat else "UNKNOWN"),
        "expected": "UNSAT",
        "explanation": "If base graph edges are fixed (before==after), no new edge can appear.",
    }


def _check1b_rescue_drop_immutability():
    """Charitable rescue: drop C108 (no new edges). Now C111 alone is SAT."""
    s = Solver()
    N = 5
    edge_in_base = [Bool(f"edge_base_{i}") for i in range(N)]
    edge_after = [Bool(f"edge_after_{i}") for i in range(N)]

    # Only C111: agent creates at least one new edge
    s.add(Or(*[And(Not(edge_in_base[i]), edge_after[i]) for i in range(N)]))

    result = s.check()
    return {
        "name": "CHECK 1b: Rescue - drop no-new-edges constraint",
        "result": "SAT" if result == sat else ("UNSAT" if result == unsat else "UNKNOWN"),
        "expected": "SAT",
        "explanation": "Without the immutability constraint, new edges are trivially possible.",
    }


def _check2_predefined_paths_vs_new_edges():
    """C65 vs C111: All possible paths are pre-defined (determinism)
    yet agents create new edges extending the graph.
    We model a graph where the edge set is fixed vs extended.
    Expected: UNSAT"""
    s = Solver()
    N = 6
    # predefined[i]: edge i is part of the pre-defined graph
    predefined = [Bool(f"predef_{i}") for i in range(N)]
    # exists_after[i]: edge i exists after agent action
    exists_after = [Bool(f"exists_{i}") for i in range(N)]

    # C65: All paths pre-defined means edge set is complete/fixed
    for i in range(N):
        s.add(exists_after[i] == predefined[i])

    # C111: Agent instantiates at least one edge NOT in predefined set
    s.add(Or(*[And(Not(predefined[i]), exists_after[i]) for i in range(N)]))

    result = s.check()
    return {
        "name": "CHECK 2: Pre-defined paths (C65) vs new edges (C111)",
        "result": "SAT" if result == sat else ("UNSAT" if result == unsat else "UNKNOWN"),
        "expected": "UNSAT",
        "explanation": "If exists_after == predefined for all edges, no new edge can appear.",
    }


def _check3_finite_dag_vs_asymptotic():
    """C63/C113 vs C100: Finite DAG with finite paths vs asymptotic approach.
    An asymptotic approach requires an infinite sequence of distinct values.
    A finite DAG has only finitely many nodes on any path.
    Expected: UNSAT"""
    s = Solver()
    # Model: path length is finite (bounded by N), but asymptotic approach
    # requires strictly monotone sequence converging to limit.
    # We use integers for path length and a bound.
    path_length = Int("path_length")
    num_nodes = Int("num_nodes")
    steps_needed = Int("steps_for_asymptote")

    # C63: finite DAG
    s.add(num_nodes > 0)
    s.add(num_nodes < 1000)  # finite bound

    # C113: all paths finite and terminate
    s.add(path_length > 0)
    s.add(path_length <= num_nodes)  # path can't exceed nodes in DAG

    # C100: asymptotic approach requires infinite steps
    # For a true asymptote, steps_needed must exceed any finite bound
    # We encode: steps_needed > path_length (need more steps than path allows)
    # AND steps_needed must be unbounded (greater than num_nodes)
    s.add(steps_needed > num_nodes)
    s.add(steps_needed <= path_length)  # must fit in path

    result = s.check()
    return {
        "name": "CHECK 3: Finite DAG (C63/C113) vs asymptotic approach (C100)",
        "result": "SAT" if result == sat else ("UNSAT" if result == unsat else "UNKNOWN"),
        "expected": "UNSAT",
        "explanation": "steps_needed > num_nodes >= path_length >= steps_needed is impossible.",
    }


def _check3b_rescue_drop_finiteness():
    """Charitable rescue: drop finite DAG constraint. Allow infinite paths."""
    s = Solver()
    path_length = Int("path_length")
    steps_needed = Int("steps_for_asymptote")

    # Allow unbounded path
    s.add(path_length > 0)
    s.add(steps_needed > 0)
    s.add(steps_needed <= path_length)
    s.add(steps_needed > 1000)  # need many steps for asymptote

    result = s.check()
    return {
        "name": "CHECK 3b: Rescue - drop finiteness, allow long paths",
        "result": "SAT" if result == sat else ("UNSAT" if result == unsat else "UNKNOWN"),
        "expected": "SAT",
        "explanation": "Without finite DAG bound, arbitrarily long paths are possible.",
    }


def _check4_source_and_sink_in_dag():
    """C115 vs C63: God (node 9) is both universal source (all edges originate)
    and universal sink (all paths converge) in a DAG.
    In a DAG a node with outgoing edges to all others cannot also have
    all paths leading back to it (that would require a cycle).
    Expected: UNSAT"""
    s = Solver()
    N = 4  # nodes: 0=God, 1,2,3 are other nodes
    GOD = 0
    # edge[i][j] = True means directed edge from i to j
    edge = [[Bool(f"e_{i}_{j}") for j in range(N)] for i in range(N)]

    # No self-loops (DAG)
    for i in range(N):
        s.add(Not(edge[i][i]))

    # C115 part 1: God is universal source - all edges originate from God
    # Every non-God node has an edge from God to it
    for j in range(N):
        if j != GOD:
            s.add(edge[GOD][j])

    # C115 part 2: All paths converge to God (God is universal sink)
    # Every non-God node has an edge TO God
    for i in range(N):
        if i != GOD:
            s.add(edge[i][GOD])

    # DAG: no cycles. With edges GOD->j and j->GOD, we have 2-cycles.
    # Encode acyclicity: there exists a topological ordering
    order = [Int(f"ord_{i}") for i in range(N)]
    for i in range(N):
        s.add(order[i] >= 0)
        s.add(order[i] < N)
    for i in range(N):
        for j in range(N):
            if i != j:
                s.add(Implies(edge[i][j], order[i] < order[j]))

    result = s.check()
    return {
        "name": "CHECK 4: God as both source and sink in DAG (C115 vs C63)",
        "result": "SAT" if result == sat else ("UNSAT" if result == unsat else "UNKNOWN"),
        "expected": "UNSAT",
        "explanation": "Edges GOD->j and j->GOD form cycles, violating acyclicity.",
    }


def _check4b_rescue_drop_sink():
    """Charitable rescue: God is source only, not sink. DAG is fine."""
    s = Solver()
    N = 4
    GOD = 0
    edge = [[Bool(f"e_{i}_{j}") for j in range(N)] for i in range(N)]

    for i in range(N):
        s.add(Not(edge[i][i]))

    # God is universal source only
    for j in range(N):
        if j != GOD:
            s.add(edge[GOD][j])

    # No edges back to God (drop sink requirement)
    for i in range(N):
        if i != GOD:
            s.add(Not(edge[i][GOD]))

    # Topological ordering
    order = [Int(f"ord_{i}") for i in range(N)]
    for i in range(N):
        s.add(order[i] >= 0)
        s.add(order[i] < N)
    for i in range(N):
        for j in range(N):
            if i != j:
                s.add(Implies(edge[i][j], order[i] < order[j]))

    result = s.check()
    return {
        "name": "CHECK 4b: Rescue - God as source only (drop sink)",
        "result": "SAT" if result == sat else ("UNSAT" if result == unsat else "UNKNOWN"),
        "expected": "SAT",
        "explanation": "With God as source only, a valid DAG ordering exists.",
    }


def _check5_bella_scale_range():
    """C54 vs C83-85: BELLA scale is 0-8 (complete) yet states 10,11,12 are defined.
    Expected: UNSAT"""
    s = Solver()
    max_bella = Int("max_bella_state")
    state_10 = Int("state_10")
    state_11 = Int("state_11")
    state_12 = Int("state_12")

    # C54: BELLA scale ranges from 0 to 8 as complete system
    s.add(max_bella == 8)

    # C83-85: States 10, 11, 12 are defined on the same scale
    s.add(state_10 == 10)
    s.add(state_11 == 11)
    s.add(state_12 == 12)

    # All states must be <= max_bella if the scale is complete at 8
    s.add(state_10 <= max_bella)
    s.add(state_11 <= max_bella)
    s.add(state_12 <= max_bella)

    result = s.check()
    return {
        "name": "CHECK 5: BELLA scale 0-8 complete (C54) vs states 10-12 (C83-85)",
        "result": "SAT" if result == sat else ("UNSAT" if result == unsat else "UNKNOWN"),
        "expected": "UNSAT",
        "explanation": "10, 11, 12 cannot all be <= 8.",
    }


def _check5b_rescue_extend_scale():
    """Charitable rescue: allow the scale max to be >= 12."""
    s = Solver()
    max_bella = Int("max_bella_state")
    s.add(max_bella >= 12)
    s.add(Int("s10") == 10)
    s.add(Int("s11") == 11)
    s.add(Int("s12") == 12)
    s.add(Int("s10") <= max_bella)
    s.add(Int("s11") <= max_bella)
    s.add(Int("s12") <= max_bella)

    result = s.check()
    return {
        "name": "CHECK 5b: Rescue - extend scale past 8",
        "result": "SAT" if result == sat else ("UNSAT" if result == unsat else "UNKNOWN"),
        "expected": "SAT",
        "explanation": "If the scale goes beyond 8, states 10-12 fit trivially.",
    }


def _check6_predrawn_map_vs_new_edges():
    """C48 vs C111: God already drew the map (all edges fixed)
    yet agents at Stage 7+ instantiate new edges.
    Structurally identical to checks 1/2 but from theological framing.
    Expected: UNSAT"""
    s = Solver()
    N = 5
    god_drew = [Bool(f"god_drew_{i}") for i in range(N)]
    after_agent = [Bool(f"after_agent_{i}") for i in range(N)]

    # C48: map already drawn - edges fixed
    for i in range(N):
        s.add(after_agent[i] == god_drew[i])

    # C111: agent creates new edge not in god's map
    s.add(Or(*[And(Not(god_drew[i]), after_agent[i]) for i in range(N)]))

    result = s.check()
    return {
        "name": "CHECK 6: Pre-drawn map (C48) vs agent creates edges (C111)",
        "result": "SAT" if result == sat else ("UNSAT" if result == unsat else "UNKNOWN"),
        "expected": "UNSAT",
        "explanation": "If after_agent == god_drew, no new edge can exist.",
    }


def _check7_different_origin_nodes():
    """C64 vs C115: C64 says origin is human's first moment, C115 says origin is God.
    In a DAG there is at most one universal source (node with in-degree 0 that reaches all).
    Expected: UNSAT (both cannot be THE origin if they are distinct nodes)"""
    s = Solver()
    N = 4  # 0=God, 1=human_origin, 2,3=other
    GOD = 0
    HUMAN_ORIGIN = 1

    edge = [[Bool(f"e_{i}_{j}") for j in range(N)] for i in range(N)]

    # No self-loops
    for i in range(N):
        s.add(Not(edge[i][i]))

    # Topological ordering for acyclicity
    order = [Int(f"ord_{i}") for i in range(N)]
    for i in range(N):
        s.add(order[i] >= 0)
        s.add(order[i] < N)
    for i in range(N):
        for j in range(N):
            if i != j:
                s.add(Implies(edge[i][j], order[i] < order[j]))

    # C115: God is THE origin - all edges originate from God
    # God has edges to all other nodes
    for j in range(N):
        if j != GOD:
            s.add(edge[GOD][j])
    # No edges into God (it's the source)
    for i in range(N):
        if i != GOD:
            s.add(Not(edge[i][GOD]))

    # C64: Human origin is THE origin - all edges originate from human_origin
    for j in range(N):
        if j != HUMAN_ORIGIN:
            s.add(edge[HUMAN_ORIGIN][j])
    # No edges into human_origin
    for i in range(N):
        if i != HUMAN_ORIGIN:
            s.add(Not(edge[i][HUMAN_ORIGIN]))

    result = s.check()
    return {
        "name": "CHECK 7: Human origin (C64) vs God origin (C115) in DAG",
        "result": "SAT" if result == sat else ("UNSAT" if result == unsat else "UNKNOWN"),
        "expected": "UNSAT",
        "explanation": "God must have edge to human_origin (C115) but human_origin has no incoming edges (C64). Contradiction.",
    }


def _check7b_rescue_single_origin():
    """Charitable rescue: only God is origin, human_origin is just a node."""
    s = Solver()
    N = 4
    GOD = 0
    edge = [[Bool(f"e_{i}_{j}") for j in range(N)] for i in range(N)]

    for i in range(N):
        s.add(Not(edge[i][i]))

    order = [Int(f"ord_{i}") for i in range(N)]
    for i in range(N):
        s.add(order[i] >= 0)
        s.add(order[i] < N)
    for i in range(N):
        for j in range(N):
            if i != j:
                s.add(Implies(edge[i][j], order[i] < order[j]))

    # Only God is origin
    for j in range(N):
        if j != GOD:
            s.add(edge[GOD][j])
    for i in range(N):
        if i != GOD:
            s.add(Not(edge[i][GOD]))

    result = s.check()
    return {
        "name": "CHECK 7b: Rescue - single origin (God only)",
        "result": "SAT" if result == sat else ("UNSAT" if result == unsat else "UNKNOWN"),
        "expected": "SAT",
        "explanation": "With only God as origin, DAG is well-formed.",
    }


def _check8_nondeterminism_vs_predefined():
    """C86 vs C65: Non-deterministic transitions vs all paths pre-defined.
    If all paths are pre-defined, then at each node the set of possible next
    nodes is fixed. 'Non-determinism at transition' means the agent could go
    to a successor NOT in the pre-defined set - contradiction.
    Expected: UNSAT"""
    s = Solver()
    N = 4  # nodes
    # For node 0, define which successors are pre-defined
    predef_succ = [Bool(f"predef_succ_0_{j}") for j in range(N)]
    # actual_choice: which node the agent actually transitions to
    actual_choice = Int("actual_choice")

    # C65: all transitions are within pre-defined successors
    s.add(actual_choice >= 0)
    s.add(actual_choice < N)
    # The chosen successor must be pre-defined
    for j in range(N):
        s.add(Implies(actual_choice == j, predef_succ[j]))

    # C86: non-deterministic at transition means agent can choose
    # a successor NOT in the pre-defined set
    # There exists a transition to a node that is not a pre-defined successor
    novel_choice = Int("novel_choice")
    s.add(novel_choice >= 0)
    s.add(novel_choice < N)
    for j in range(N):
        s.add(Implies(novel_choice == j, Not(predef_succ[j])))

    # The novel choice must also be a valid actual choice
    s.add(novel_choice == actual_choice)

    result = s.check()
    return {
        "name": "CHECK 8: Non-deterministic transitions (C86) vs pre-defined paths (C65)",
        "result": "SAT" if result == sat else ("UNSAT" if result == unsat else "UNKNOWN"),
        "expected": "UNSAT",
        "explanation": "A choice that is both in the pre-defined set and not in it is impossible.",
    }


def _check8b_rescue_epistemic_nondeterminism():
    """Charitable rescue: non-determinism is merely epistemic (agent doesn't know
    which pre-defined successor will be chosen, but all options are pre-defined).
    Expected: SAT"""
    s = Solver()
    N = 4
    predef_succ = [Bool(f"predef_succ_0_{j}") for j in range(N)]
    actual_choice = Int("actual_choice")
    agent_knows = [Bool(f"agent_knows_{j}") for j in range(N)]

    s.add(actual_choice >= 0)
    s.add(actual_choice < N)

    # All transitions within pre-defined set
    for j in range(N):
        s.add(Implies(actual_choice == j, predef_succ[j]))

    # At least 2 pre-defined successors (gives choice)
    s.add(Or(*[And(predef_succ[i], predef_succ[j])
               for i in range(N) for j in range(i+1, N)]))

    # Agent doesn't know which one will happen (epistemic)
    s.add(Or(*[Not(agent_knows[j]) for j in range(N)]))

    result = s.check()
    return {
        "name": "CHECK 8b: Rescue - epistemic non-determinism only",
        "result": "SAT" if result == sat else ("UNSAT" if result == unsat else "UNKNOWN"),
        "expected": "SAT",
        "explanation": "If non-determinism is just epistemic uncertainty over pre-defined successors, no contradiction.",
    }


def verify() -> dict:
    """Run all checks and return structured findings."""
    return {
        "check1": _check1_no_new_edges_vs_royal_purple(),
        "check1b": _check1b_rescue_drop_immutability(),
        "check2": _check2_predefined_paths_vs_new_edges(),
        "check3": _check3_finite_dag_vs_asymptotic(),
        "check3b": _check3b_rescue_drop_finiteness(),
        "check4": _check4_source_and_sink_in_dag(),
        "check4b": _check4b_rescue_drop_sink(),
        "check5": _check5_bella_scale_range(),
        "check5b": _check5b_rescue_extend_scale(),
        "check6": _check6_predrawn_map_vs_new_edges(),
        "check7": _check7_different_origin_nodes(),
        "check7b": _check7b_rescue_single_origin(),
        "check8": _check8_nondeterminism_vs_predefined(),
        "check8b": _check8b_rescue_epistemic_nondeterminism(),
    }


if __name__ == "__main__":
    findings = verify()
    for key, f in findings.items():
        print(f"=== {f['name']} ===")
        print(f"  Result:      {f['result']}")
        print(f"  Expected:    {f['expected']}")
        print(f"  Explanation: {f['explanation']}")
        print()

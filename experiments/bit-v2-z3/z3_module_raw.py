from z3 import (
    Solver, Bool, Int, Function, BoolSort, IntSort,
    And, Or, Not, Implies, ForAll, Exists, sat, unsat,
    Array, ArraySort, RealSort, Real, If, Distinct,
)
import json


def _check1_no_new_edges_vs_royal_purple():
    """
    C96 says G is fully defined and no new edges are created by agents.
    C98 says agents at Stage 7+ CAN create new edges (Royal Purple).
    We model: edges_fixed AND new_edge_created => UNSAT.
    """
    s = Solver()
    N = 4
    nodes = range(N)
    # G edges at time 0
    E = [[Bool(f"c1_E_{u}_{v}") for v in nodes] for u in nodes]
    # G edges at time 1 (after agent action)
    E_after = [[Bool(f"c1_Ea_{u}_{v}") for v in nodes] for u in nodes]

    # C96: G is fixed - no new edges created by agent action
    for u in nodes:
        for v in nodes:
            s.add(E[u][v] == E_after[u][v])

    # C98: Agent at Stage 7+ creates at least one new edge
    agent_stage = Int("c1_agent_stage")
    s.add(agent_stage >= 7)
    new_edge_exists = []
    for u in nodes:
        for v in nodes:
            new_edge_exists.append(And(Not(E[u][v]), E_after[u][v]))
    s.add(Or(*new_edge_exists))

    result = s.check()
    return {
        "name": "CHECK 1: No new edges (C96) vs Royal Purple edge creation (C98)",
        "result": "SAT" if result == sat else ("UNSAT" if result == unsat else "UNKNOWN"),
        "expected": "UNSAT",
        "explanation": "C96 fixes all edges; C98 requires a new edge. Jointly unsatisfiable.",
    }


def _check1b_rescue_drop_fixed():
    """
    Charitable rescue: drop C96 (edges fixed). Now agents can create edges.
    """
    s = Solver()
    N = 4
    nodes = range(N)
    E = [[Bool(f"c1b_E_{u}_{v}") for v in nodes] for u in nodes]
    E_after = [[Bool(f"c1b_Ea_{u}_{v}") for v in nodes] for u in nodes]
    # DAG constraints for both
    order = [Int(f"c1b_ord_{u}") for u in nodes]
    order_after = [Int(f"c1b_orda_{u}") for u in nodes]
    for u in nodes:
        s.add(order[u] >= 0, order[u] < N)
        s.add(order_after[u] >= 0, order_after[u] < N)
        for v in nodes:
            s.add(Implies(E[u][v], order[u] < order[v]))
            s.add(Implies(E_after[u][v], order_after[u] < order_after[v]))
    # C98 only: new edge
    new_edge_exists = []
    for u in nodes:
        for v in nodes:
            new_edge_exists.append(And(Not(E[u][v]), E_after[u][v]))
    s.add(Or(*new_edge_exists))
    result = s.check()
    return {
        "name": "CHECK 1b: Rescue - drop fixedness (C96), keep edge creation (C98)",
        "result": "SAT" if result == sat else ("UNSAT" if result == unsat else "UNKNOWN"),
        "expected": "SAT",
        "explanation": "Without the fixedness constraint, new edges can be created in a DAG.",
    }


def _check2_finite_dag_vs_asymptotic():
    """
    C54: Universe is a finite DAG.
    C90: Human BELLA state approaches 9 asymptotically but never arrives.
    Asymptotic approach requires infinitely many distinct states on the path.
    In a finite DAG, all paths are finite.
    """
    s = Solver()
    # Model: finite number of states N, a path of length K steps approaching target 9
    # For asymptotic approach, we need infinitely many distinct values approaching 9.
    # With N states, the path length is at most N.
    N = Int("c2_N")  # number of nodes
    path_len = Int("c2_path_len")  # length of asymptotic path

    s.add(N > 0)
    # C54: finite DAG => path length <= N
    s.add(path_len <= N)
    s.add(N >= 1)

    # C90: asymptotic approach requires infinitely many steps
    # We encode this as: path_len must exceed any finite bound
    # Equivalently: for the path to be asymptotic, path_len > N (contradiction with DAG)
    s.add(path_len > N)

    result = s.check()
    return {
        "name": "CHECK 2: Finite DAG (C54) vs asymptotic approach (C90)",
        "result": "SAT" if result == sat else ("UNSAT" if result == unsat else "UNKNOWN"),
        "expected": "UNSAT",
        "explanation": "Path length cannot both be <= N (finite DAG) and > N (asymptotic). UNSAT.",
    }


def _check3_finite_termination_vs_asymptotic():
    """
    C100: All paths in DAG are finite and terminate (at Omega).
    C90: Human BELLA approaches 9 but never arrives.
    If paths terminate, agent reaches terminal node. No infinite approach.
    """
    s = Solver()
    # Model with concrete path of length up to M in a DAG of size N
    N = 5
    # BELLA values along a path
    bella = [Real(f"c3_bella_{i}") for i in range(N)]
    reached_omega = Bool("c3_reached_omega")
    target = Real("c3_target")  # value 9
    s.add(target == 9)

    # C100: path terminates - last node is omega with bella value = target
    s.add(reached_omega)
    s.add(Implies(reached_omega, bella[N - 1] == target))

    # C90: bella values approach 9 but never equal 9
    for i in range(N):
        s.add(bella[i] < target)
        s.add(bella[i] >= 0)
    # Monotonically increasing toward 9
    for i in range(N - 1):
        s.add(bella[i] < bella[i + 1])

    result = s.check()
    return {
        "name": "CHECK 3: Paths terminate at Omega (C100) vs never reaches 9 (C90)",
        "result": "SAT" if result == sat else ("UNSAT" if result == unsat else "UNKNOWN"),
        "expected": "UNSAT",
        "explanation": "Terminal node has bella=9 but C90 says bella<9 always. Contradiction.",
    }


def _check3b_rescue_drop_termination():
    """
    Rescue: drop C100 (path terminates at omega=9). Keep asymptotic approach.
    """
    s = Solver()
    N = 5
    bella = [Real(f"c3b_bella_{i}") for i in range(N)]
    target = Real("c3b_target")
    s.add(target == 9)
    for i in range(N):
        s.add(bella[i] < target)
        s.add(bella[i] >= 0)
    for i in range(N - 1):
        s.add(bella[i] < bella[i + 1])
    result = s.check()
    return {
        "name": "CHECK 3b: Rescue - drop termination, keep asymptotic approach",
        "result": "SAT" if result == sat else ("UNSAT" if result == unsat else "UNKNOWN"),
        "expected": "SAT",
        "explanation": "Without forced termination at 9, increasing-but-below-9 path is satisfiable.",
    }


def _check4_human_ceiling_8_vs_states_above():
    """
    C45: Human ceiling is state 8.
    C73: State 10 (Royal Purple) is achievable by humans (C82 says exclusive to humans).
    """
    s = Solver()
    human_ceiling = Int("c4_ceiling")
    royal_purple_state = Int("c4_royal_purple")
    human_can_reach_rp = Bool("c4_human_reaches_rp")

    # C45: ceiling is 8
    s.add(human_ceiling == 8)
    # No human state exceeds ceiling
    human_state = Int("c4_human_state")
    s.add(human_state <= human_ceiling)

    # C73/C82: Royal Purple (state 10) is achievable by humans
    s.add(royal_purple_state == 10)
    s.add(human_can_reach_rp)
    s.add(Implies(human_can_reach_rp, human_state >= royal_purple_state))

    result = s.check()
    return {
        "name": "CHECK 4: Human ceiling=8 (C45) vs humans reach state 10 (C73/C82)",
        "result": "SAT" if result == sat else ("UNSAT" if result == unsat else "UNKNOWN"),
        "expected": "UNSAT",
        "explanation": "Human state <= 8 but must be >= 10. UNSAT.",
    }


def _check5_dual_peak():
    """
    C71: State 8 is peak human capability.
    C81: State 10 is peak human capability.
    Peak is unique => contradiction.
    """
    s = Solver()
    peak = Int("c5_peak")
    # C71: peak is 8
    s.add(peak == 8)
    # C81: peak is 10
    s.add(peak == 10)
    result = s.check()
    return {
        "name": "CHECK 5: State 8 is peak (C71) AND State 10 is peak (C81)",
        "result": "SAT" if result == sat else ("UNSAT" if result == unsat else "UNKNOWN"),
        "expected": "UNSAT",
        "explanation": "A single peak value cannot be both 8 and 10.",
    }


def _check5b_rescue_two_peaks():
    """
    Rescue: allow two different kinds of peak (individual vs collaborative).
    """
    s = Solver()
    individual_peak = Int("c5b_ind_peak")
    collaborative_peak = Int("c5b_collab_peak")
    s.add(individual_peak == 8)
    s.add(collaborative_peak == 10)
    s.add(individual_peak < collaborative_peak)
    result = s.check()
    return {
        "name": "CHECK 5b: Rescue - two distinct peak types",
        "result": "SAT" if result == sat else ("UNSAT" if result == unsat else "UNKNOWN"),
        "expected": "SAT",
        "explanation": "If peak is disambiguated into individual(8) and collaborative(10), no contradiction.",
    }


def _check6_determinism_vs_innovation():
    """
    C56: All possible paths pre-defined (determinism).
    C99: Innovation adds genuinely new edges to G.
    """
    s = Solver()
    N = 4
    nodes = range(N)
    E_predefined = [[Bool(f"c6_Ep_{u}_{v}") for v in nodes] for u in nodes]
    E_actual = [[Bool(f"c6_Ea_{u}_{v}") for v in nodes] for u in nodes]

    # C56: all actual edges are predefined
    for u in nodes:
        for v in nodes:
            s.add(Implies(E_actual[u][v], E_predefined[u][v]))

    # C99: at least one actual edge is NOT predefined (genuinely new)
    genuinely_new = []
    for u in nodes:
        for v in nodes:
            genuinely_new.append(And(E_actual[u][v], Not(E_predefined[u][v])))
    s.add(Or(*genuinely_new))

    result = s.check()
    return {
        "name": "CHECK 6: All paths predefined (C56) vs innovation creates new edges (C99)",
        "result": "SAT" if result == sat else ("UNSAT" if result == unsat else "UNKNOWN"),
        "expected": "UNSAT",
        "explanation": "An edge cannot be both necessarily predefined and genuinely new.",
    }


def _check7_finite_dag_vs_extension():
    """
    C54: G is a finite DAG (fixed structure).
    C98: Agents extend G by adding new edges.
    """
    s = Solver()
    edge_count_before = Int("c7_edges_before")
    edge_count_after = Int("c7_edges_after")

    # C54: G is fixed
    s.add(edge_count_before >= 0)
    s.add(edge_count_before == edge_count_after)  # fixed structure

    # C98: agent adds edges
    s.add(edge_count_after > edge_count_before)

    result = s.check()
    return {
        "name": "CHECK 7: Fixed finite DAG (C54) vs agents extend G (C98)",
        "result": "SAT" if result == sat else ("UNSAT" if result == unsat else "UNKNOWN"),
        "expected": "UNSAT",
        "explanation": "Edge count cannot be both unchanged and increased.",
    }


def _check8_acyclic_at_scale_vs_dag():
    """
    C76: Movement is 'acyclic at scale' (implying possible local cycles).
    C54: G is a DAG (no cycles at ANY scale).
    We model: a graph that has a local cycle but is 'acyclic at scale' - check if it's a DAG.
    """
    s = Solver()
    N = 4
    nodes = range(N)
    E = [[Bool(f"c8_E_{u}_{v}") for v in nodes] for u in nodes]
    order = [Int(f"c8_ord_{u}") for u in nodes]

    # DAG constraint: topological ordering exists
    for u in nodes:
        s.add(order[u] >= 0, order[u] < N)
        for v in nodes:
            s.add(Implies(E[u][v], order[u] < order[v]))

    # Local cycle exists: e.g., edge from u->v and v->u for some u,v
    local_cycle = []
    for u in nodes:
        for v in nodes:
            if u != v:
                local_cycle.append(And(E[u][v], E[v][u]))
    s.add(Or(*local_cycle))

    result = s.check()
    return {
        "name": "CHECK 8: DAG (C54) with local cycles ('acyclic at scale', C76)",
        "result": "SAT" if result == sat else ("UNSAT" if result == unsat else "UNKNOWN"),
        "expected": "UNSAT",
        "explanation": "A DAG cannot have any cycle, even a local 2-cycle. 'Acyclic at scale' contradicts strict DAG.",
    }


def _check9_dag_reachability_to_omega():
    """
    C93: G=(V,E) is a DAG of all conscious states.
    C95: Every node can reach Omega.
    We show a DAG can exist where some node cannot reach a designated terminal.
    i.e., the DAG property alone does NOT guarantee universal reachability to Omega.
    """
    s = Solver()
    N = 4
    nodes = range(N)
    omega = N - 1  # designated terminal
    E = [[Bool(f"c9_E_{u}_{v}") for v in nodes] for u in nodes]
    order = [Int(f"c9_ord_{u}") for u in nodes]

    # DAG constraint
    for u in nodes:
        s.add(order[u] >= 0, order[u] < N)
        for v in nodes:
            s.add(Implies(E[u][v], order[u] < order[v]))

    # Omega is a sink (no outgoing edges)
    for v in nodes:
        s.add(Not(E[omega][v]))

    # There exists some node that cannot reach omega
    # We encode: node 0 has no outgoing edges at all (so it can't reach omega if 0 != omega)
    source = 0
    for v in nodes:
        s.add(Not(E[source][v]))
    # source != omega
    s.add(order[source] != order[omega])

    # At least one edge exists (non-trivial graph)
    some_edge = []
    for u in nodes:
        for v in nodes:
            some_edge.append(E[u][v])
    s.add(Or(*some_edge))

    result = s.check()
    return {
        "name": "CHECK 9: DAG exists where not all nodes reach Omega (C93 vs C95)",
        "result": "SAT" if result == sat else ("UNSAT" if result == unsat else "UNKNOWN"),
        "expected": "SAT",
        "explanation": "SAT shows a DAG can exist where some node doesn't reach Omega, proving C95 doesn't follow from DAG property alone.",
    }


def _check10_determinism_vs_underdetermined_f():
    """
    C43: Free will and determinism co-present; all paths pre-defined in DAG.
    C97: Selection function f is underdetermined by G (not computable from G alone).
    If G determines all structure and f is not determined by G, the system is not fully deterministic.
    """
    s = Solver()
    # Model: a node with two outgoing edges (choice point)
    N = 3
    # node 0 -> node 1 and node 0 -> node 2 both exist
    choice_determined_by_G = Bool("c10_choice_determined")
    f_underdetermined = Bool("c10_f_underdetermined")
    system_fully_deterministic = Bool("c10_fully_deterministic")

    # C43/C56: system is fully deterministic at graph level
    s.add(system_fully_deterministic)
    # Full determinism means: given G, the path is determined
    s.add(Implies(system_fully_deterministic, choice_determined_by_G))

    # C97: f is NOT determined by G
    s.add(f_underdetermined)
    s.add(Implies(f_underdetermined, Not(choice_determined_by_G)))

    result = s.check()
    return {
        "name": "CHECK 10: Full determinism (C43/C56) vs f underdetermined by G (C97)",
        "result": "SAT" if result == sat else ("UNSAT" if result == unsat else "UNKNOWN"),
        "expected": "UNSAT",
        "explanation": "Choice cannot be both determined and underdetermined by G.",
    }


def _check10b_rescue_compatibilism():
    """
    Rescue: weaken determinism to 'all paths exist in G' but which path is taken
    is not determined by G. This is a compatibilist reading.
    """
    s = Solver()
    paths_predefined = Bool("c10b_paths_predef")
    path_selection_free = Bool("c10b_selection_free")
    # Weaker: paths exist but selection is free
    s.add(paths_predefined)
    s.add(path_selection_free)
    # No contradiction in this weaker form
    result = s.check()
    return {
        "name": "CHECK 10b: Rescue - compatibilist (paths exist, selection free)",
        "result": "SAT" if result == sat else ("UNSAT" if result == unsat else "UNKNOWN"),
        "expected": "SAT",
        "explanation": "If determinism means only that paths exist (not that selection is forced), no contradiction with f being free.",
    }


def verify() -> dict:
    """Run all checks and return structured findings."""
    results = {}
    checks = [
        ("check1", _check1_no_new_edges_vs_royal_purple),
        ("check1b", _check1b_rescue_drop_fixed),
        ("check2", _check2_finite_dag_vs_asymptotic),
        ("check3", _check3_finite_termination_vs_asymptotic),
        ("check3b", _check3b_rescue_drop_termination),
        ("check4", _check4_human_ceiling_8_vs_states_above),
        ("check5", _check5_dual_peak),
        ("check5b", _check5b_rescue_two_peaks),
        ("check6", _check6_determinism_vs_innovation),
        ("check7", _check7_finite_dag_vs_extension),
        ("check8", _check8_acyclic_at_scale_vs_dag),
        ("check9", _check9_dag_reachability_to_omega),
        ("check10", _check10_determinism_vs_underdetermined_f),
        ("check10b", _check10b_rescue_compatibilism),
    ]
    for key, fn in checks:
        results[key] = fn()
    return results


if __name__ == "__main__":
    findings = verify()
    for key, f in findings.items():
        print(f"=== {f['name']} ===")
        print(f"Result:   {f['result']}")
        print(f"Expected: {f['expected']}")
        print(f"Explanation: {f['explanation']}")
        print()

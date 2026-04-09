"""Optional Z3 structural SAT check for 'G fixed + edge creation' claims."""

from __future__ import annotations

import re


class Z3Checker:
    """Conservative SAT check using Z3.

    Tries to encode the conjunction of ``G is fixed`` and ``edges are
    created`` against a small graph and asks Z3 whether the conjunction is
    satisfiable.  If UNSAT, the claims are jointly contradictory.

    **Graceful degradation**: if Z3 is not installed the checker silently
    abstains (returns ``None``).  It also abstains when the extracted
    structural claims are not cleanly translatable into the expected
    pattern.
    """

    def check(self, structural_claims: list[str]) -> dict | None:
        """Return a violation dict if UNSAT, else ``None`` (abstain)."""
        try:
            from z3 import Bool, Int, Implies, Not, And, Or, Solver, unsat  # type: ignore[import-untyped]
        except ImportError:
            return None  # z3 not installed -- silently abstain

        joined = " ".join(c.lower() for c in structural_claims)
        asserts_fixed = bool(re.search(r"\bg\s+is\s+fixed\b", joined))
        asserts_creation = bool(
            re.search(
                r"\b(new\s+edge|add(s|ing)?\s+edges?|instantiat\w*\s+edges?|edge\s+creation)\b",
                joined,
            )
        )
        if not (asserts_fixed and asserts_creation):
            return None  # not cleanly translatable -- abstain

        # Encode a small graph (N=4 nodes) with DAG ordering constraints.
        s = Solver()
        N = 4
        E0 = [[Bool(f"v3E0_{u}_{v}") for v in range(N)] for u in range(N)]
        E1 = [[Bool(f"v3E1_{u}_{v}") for v in range(N)] for u in range(N)]
        ord0 = [Int(f"v3o0_{u}") for u in range(N)]
        ord1 = [Int(f"v3o1_{u}") for u in range(N)]

        for u in range(N):
            s.add(ord0[u] >= 0, ord0[u] < N, ord1[u] >= 0, ord1[u] < N)
            for v in range(N):
                s.add(Implies(E0[u][v], ord0[u] < ord0[v]))
                s.add(Implies(E1[u][v], ord1[u] < ord1[v]))
                s.add(E0[u][v] == E1[u][v])  # G is fixed

        # Require at least one NEW edge (present in E1 but not in E0).
        s.add(Or(*[And(Not(E0[u][v]), E1[u][v]) for u in range(N) for v in range(N)]))

        r = s.check()
        if r == unsat:
            return {
                "type": "z3_unsat",
                "note": "Structural claims 'G is fixed' + edge-creation are jointly UNSAT under Z3.",
            }
        return None

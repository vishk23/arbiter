"""Self-consistency checker across an agent's own prior claims."""

from __future__ import annotations

import re


def _normalize(s: str) -> str:
    """Lowercase, collapse whitespace."""
    return re.sub(r"\s+", " ", s.strip().lower())


class ConsistencyChecker:
    """Detect naive self-contradictions within a single agent's claim history.

    Two heuristics:
    1. **Negation flip** -- the new claim is the negation (or un-negation) of
       a prior claim.
    2. **Fixed / mutable flip** -- the new claim says "X is fixed" while a
       prior says "X is mutable" (or mentions adding edges), or vice-versa.
    """

    def check(
        self,
        agent: str,
        new_claims: list[dict],
        prior_by_agent: dict[str, list[dict]],
    ) -> list[dict]:
        """Return a list of self-contradiction violation dicts."""
        violations: list[dict] = []
        prior = prior_by_agent.get(agent, [])
        if not prior or not new_claims:
            return violations

        prior_norm: dict[str, dict] = {_normalize(c["claim"]): c for c in prior}

        for nc in new_claims:
            norm = _normalize(nc["claim"])

            # --- naive negation check ---
            flipped = _normalize(re.sub(r"\bnot\s+", "", norm))
            if f"not {norm}" in prior_norm or (flipped in prior_norm and flipped != norm):
                violations.append({
                    "type": "self_contradiction",
                    "claim": nc["claim"],
                    "note": "contradicts agent's own prior claim",
                })

            # --- fixed vs mutable direct flip ---
            if "is fixed" in norm:
                for pnorm, pclaim in prior_norm.items():
                    if "is mutable" in pnorm or "can add edges" in pnorm:
                        violations.append({
                            "type": "self_contradiction",
                            "claim": nc["claim"],
                            "conflicts_with": pclaim["claim"],
                        })
                        break

        return violations

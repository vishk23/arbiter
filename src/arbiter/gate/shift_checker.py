"""Definitional-shift detection for seed and non-seed terms."""

from __future__ import annotations

import re


class ShiftChecker:
    """Flag definitional shifts extracted by the claim extractor.

    * **Seed terms** (loaded from config) -- ANY shift is forbidden regardless
      of whether the speaker disclosed it.  Shifting a load-bearing term
      mid-debate is the rhetorical escape the gate is designed to block.
    * **Non-seed terms** -- only flagged when ``flagged_explicitly`` is False
      (i.e. the speaker silently changed the meaning).
    """

    def __init__(self, seed_terms: dict[str, str]) -> None:
        self._seed_terms = seed_terms
        self._seed_keys: set[str] = {k.strip().lower() for k in seed_terms}
        # Pre-extract parenthetical abbreviations for matching
        self._seed_abbrevs: set[str] = set()
        for k in seed_terms:
            for abbrev in re.findall(r"\(([^)]+)\)", k):
                self._seed_abbrevs.add(abbrev.strip().lower())

    def _is_seed(self, term: str) -> bool:
        t = term.strip().lower()
        if not t:
            return False
        # Exact match against seed keys
        if t in self._seed_keys:
            return True
        # Match against parenthetical abbreviations
        if t in self._seed_abbrevs:
            return True
        return False

    def check(self, shifts: list[dict]) -> list[dict]:
        """Return violation dicts for disallowed definitional shifts."""
        violations: list[dict] = []
        for s in shifts:
            term = (s.get("term") or "").strip()
            if self._is_seed(term):
                violations.append({
                    "type": "definitional_shift_on_seed_term",
                    "term": term,
                    "prior_definition": s.get("prior_definition", ""),
                    "new_definition": s.get("new_definition", ""),
                    "flagged_explicitly": s.get("flagged_explicitly", False),
                    "note": "shifting a stipulated term mid-debate is forbidden regardless of disclosure",
                })
            elif not s.get("flagged_explicitly", False):
                violations.append({
                    "type": "unflagged_definitional_shift",
                    "term": term,
                    "prior_definition": s.get("prior_definition", ""),
                    "new_definition": s.get("new_definition", ""),
                })
        return violations

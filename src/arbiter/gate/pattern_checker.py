"""Configurable regex rule engine for stipulation-violation detection."""

from __future__ import annotations

import re
from typing import List, Optional

from arbiter.config import StipulatedRule


def _matches_any(patterns: list[str], text: str) -> Optional[str]:
    """Return the first matching pattern string, or None."""
    for p in patterns:
        if re.search(p, text, re.IGNORECASE | re.DOTALL):
            return p
    return None


def _has_denial(denial_patterns: list[str], text: str) -> bool:
    """True if any denial pattern matches *text*."""
    return any(re.search(p, text, re.IGNORECASE | re.DOTALL) for p in denial_patterns)


class PatternChecker:
    """Check a turn against a list of :class:`StipulatedRule` objects.

    For each rule the checker tests whether any ``bad_patterns`` regex fires.
    If the rule also carries ``denial_patterns`` and one of those matches the
    turn text, the rule is skipped (the speaker explicitly denied the
    violating claim).
    """

    def __init__(self, rules: list[StipulatedRule]) -> None:
        self.rules = rules

    def check(self, turn_text: str) -> list[dict]:
        """Return a (possibly empty) list of violation dicts."""
        violations: list[dict] = []
        for rule in self.rules:
            # If the speaker explicitly denies the claim this rule guards,
            # skip the bad-pattern check for this rule.
            if rule.denial_patterns and _has_denial(rule.denial_patterns, turn_text):
                continue
            matched = _matches_any(rule.bad_patterns, turn_text)
            if matched:
                violations.append({
                    "type": "stipulation_violation",
                    "rule_id": rule.id,
                    "fact": rule.fact,
                    "matched_pattern": matched,
                })
        return violations

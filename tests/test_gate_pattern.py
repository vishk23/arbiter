"""Tests for T25: Gate pattern_checker with denial patterns."""

from arbiter.config import StipulatedRule
from arbiter.gate.pattern_checker import PatternChecker, _has_denial, _matches_any


class TestMatchesAny:
    def test_empty_patterns(self):
        assert _matches_any([], "any text") is None

    def test_first_match(self):
        assert _matches_any([r"foo", r"bar"], "this has foo in it") == "foo"

    def test_second_match(self):
        assert _matches_any([r"xyz", r"bar"], "this has bar in it") == "bar"

    def test_no_match(self):
        assert _matches_any([r"xyz"], "no match here") is None

    def test_case_insensitive(self):
        assert _matches_any([r"hello"], "HELLO WORLD") == "hello"

    def test_regex_pattern(self):
        assert _matches_any([r"free\s+will"], "the concept of free will") == r"free\s+will"


class TestHasDenial:
    def test_empty_patterns(self):
        assert _has_denial([], "any text") is False

    def test_denial_found(self):
        assert _has_denial([r"I deny"], "I deny this claim") is True

    def test_no_denial(self):
        assert _has_denial([r"I deny"], "I accept this claim") is False


class TestPatternChecker:
    def _rule(self, id="R1", fact="X is true", bad=None, denial=None):
        return StipulatedRule(
            id=id,
            fact=fact,
            bad_patterns=bad or [r"X is false"],
            denial_patterns=denial or [],
        )

    def test_no_violations(self):
        checker = PatternChecker([self._rule()])
        assert checker.check("Some clean text about Y") == []

    def test_single_violation(self):
        checker = PatternChecker([self._rule()])
        violations = checker.check("I believe X is false")
        assert len(violations) == 1
        assert violations[0]["type"] == "stipulation_violation"
        assert violations[0]["rule_id"] == "R1"
        assert violations[0]["fact"] == "X is true"

    def test_multiple_rules_multiple_violations(self):
        rules = [
            self._rule(id="R1", fact="A", bad=[r"not A"]),
            self._rule(id="R2", fact="B", bad=[r"not B"]),
        ]
        checker = PatternChecker(rules)
        violations = checker.check("I say not A and not B")
        assert len(violations) == 2
        assert {v["rule_id"] for v in violations} == {"R1", "R2"}

    def test_denial_blocks_violation(self):
        rule = self._rule(
            bad=[r"X is false"],
            denial=[r"although.*might seem false"],
        )
        checker = PatternChecker([rule])
        text = "X is false, although it might seem false on the surface"
        assert checker.check(text) == []

    def test_denial_does_not_block_without_match(self):
        rule = self._rule(
            bad=[r"X is false"],
            denial=[r"I explicitly deny"],
        )
        checker = PatternChecker([rule])
        violations = checker.check("X is false and I stand by it")
        assert len(violations) == 1

    def test_empty_rules(self):
        checker = PatternChecker([])
        assert checker.check("any text") == []

    def test_matched_pattern_included(self):
        checker = PatternChecker([self._rule(bad=[r"X is false", r"X cannot be"])])
        violations = checker.check("I think X cannot be true")
        assert violations[0]["matched_pattern"] == r"X cannot be"

"""Tests for T26: Gate shift_checker with seed terms."""

from arbiter.gate.shift_checker import ShiftChecker


def _shift(term="consciousness", prior="def A", new="def B", flagged=False):
    return {
        "term": term,
        "prior_definition": prior,
        "new_definition": new,
        "flagged_explicitly": flagged,
    }


class TestShiftChecker:
    def test_seed_term_shift_always_flagged(self):
        checker = ShiftChecker({"consciousness": "awareness"})
        violations = checker.check([_shift("consciousness", flagged=True)])
        assert len(violations) == 1
        assert violations[0]["type"] == "definitional_shift_on_seed_term"

    def test_seed_term_shift_unflagged(self):
        checker = ShiftChecker({"consciousness": "awareness"})
        violations = checker.check([_shift("consciousness", flagged=False)])
        assert len(violations) == 1
        assert violations[0]["type"] == "definitional_shift_on_seed_term"

    def test_non_seed_flagged_no_violation(self):
        checker = ShiftChecker({"consciousness": "awareness"})
        violations = checker.check([_shift("entropy", flagged=True)])
        assert violations == []

    def test_non_seed_unflagged_violation(self):
        checker = ShiftChecker({"consciousness": "awareness"})
        violations = checker.check([_shift("entropy", flagged=False)])
        assert len(violations) == 1
        assert violations[0]["type"] == "unflagged_definitional_shift"

    def test_case_insensitive_seed(self):
        checker = ShiftChecker({"Consciousness": "awareness"})
        violations = checker.check([_shift("CONSCIOUSNESS")])
        assert len(violations) == 1
        assert violations[0]["type"] == "definitional_shift_on_seed_term"

    def test_substring_seed_match(self):
        """'consciousness' should match seed 'conscious' via substring."""
        checker = ShiftChecker({"conscious": "aware"})
        violations = checker.check([_shift("consciousness")])
        assert len(violations) == 1
        assert violations[0]["type"] == "definitional_shift_on_seed_term"

    def test_reverse_substring_match(self):
        """Seed 'direct democracy' should match term 'democracy' via reverse substring."""
        checker = ShiftChecker({"direct democracy": "rule by people"})
        violations = checker.check([_shift("democracy")])
        assert len(violations) == 1
        assert violations[0]["type"] == "definitional_shift_on_seed_term"

    def test_empty_seed_terms(self):
        checker = ShiftChecker({})
        violations = checker.check([_shift("anything", flagged=False)])
        assert len(violations) == 1
        assert violations[0]["type"] == "unflagged_definitional_shift"

    def test_empty_shifts(self):
        checker = ShiftChecker({"consciousness": "awareness"})
        assert checker.check([]) == []

    def test_mixed_shifts(self):
        checker = ShiftChecker({"consciousness": "awareness"})
        shifts = [
            _shift("consciousness", flagged=True),   # seed: always violation
            _shift("entropy", flagged=True),          # non-seed flagged: no violation
            _shift("free will", flagged=False),       # non-seed unflagged: violation
        ]
        violations = checker.check(shifts)
        assert len(violations) == 2
        types = {v["type"] for v in violations}
        assert "definitional_shift_on_seed_term" in types
        assert "unflagged_definitional_shift" in types

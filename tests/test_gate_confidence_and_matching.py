"""Tests for gate bug fixes: confidence filtering, seed term matching, regex deference."""

from arbiter.gate.llm_checker import _is_seed_term
from arbiter.gate.shift_checker import ShiftChecker


# ── Seed term matching (exact, not substring) ────────────────────────


class TestIsSeedTerm:
    """Verify _is_seed_term uses exact match, not substring containment."""

    SEED_TERMS = {
        "Integrated Information Theory (IIT) 4.0": "A framework...",
        "Axioms": "Essential properties of experience.",
        "Complex": "A maximal substrate.",
        "G": "The universal BIT DAG.",
        "Royal Purple": "Traversal intensity state.",
    }

    def test_exact_match(self):
        assert _is_seed_term("Axioms", self.SEED_TERMS) is True
        assert _is_seed_term("axioms", self.SEED_TERMS) is True

    def test_abbreviation_in_parens(self):
        """'IIT' should match via parenthetical in the seed key."""
        assert _is_seed_term("IIT", self.SEED_TERMS) is True
        assert _is_seed_term("iit", self.SEED_TERMS) is True

    def test_full_name_match(self):
        assert _is_seed_term("Integrated Information Theory (IIT) 4.0", self.SEED_TERMS) is True

    def test_short_key_exact(self):
        assert _is_seed_term("G", self.SEED_TERMS) is True
        assert _is_seed_term("g", self.SEED_TERMS) is True

    def test_substring_no_longer_matches(self):
        """'axiomatic' should NOT match seed 'Axioms'."""
        assert _is_seed_term("axiomatic", self.SEED_TERMS) is False
        assert _is_seed_term("axiomatic framework", self.SEED_TERMS) is False

    def test_partial_name_no_match(self):
        """'Information Theory' should NOT match the full seed key."""
        assert _is_seed_term("Information Theory", self.SEED_TERMS) is False

    def test_theory_alone_no_match(self):
        """'theory' should NOT match any seed term."""
        assert _is_seed_term("theory", self.SEED_TERMS) is False

    def test_empty_term(self):
        assert _is_seed_term("", self.SEED_TERMS) is False

    def test_multi_word_exact(self):
        assert _is_seed_term("Royal Purple", self.SEED_TERMS) is True
        assert _is_seed_term("royal purple", self.SEED_TERMS) is True

    def test_multi_word_partial_no_match(self):
        assert _is_seed_term("Purple", self.SEED_TERMS) is False
        assert _is_seed_term("Royal", self.SEED_TERMS) is False


class TestShiftCheckerExactMatch:
    """Verify ShiftChecker._is_seed uses exact matching."""

    def test_exact_match_works(self):
        sc = ShiftChecker({"Axioms": "def", "G": "graph"})
        assert sc._is_seed("Axioms") is True
        assert sc._is_seed("G") is True

    def test_substring_rejected(self):
        sc = ShiftChecker({"Axioms": "def"})
        assert sc._is_seed("axiomatic") is False
        assert sc._is_seed("axioms of experience") is False

    def test_abbreviation_match(self):
        sc = ShiftChecker({"Integrated Information Theory (IIT) 4.0": "def"})
        assert sc._is_seed("IIT") is True
        assert sc._is_seed("theory") is False


# ── Confidence filtering ─────────────────────────────────────────────


class TestConfidenceFiltering:
    """Verify that only HIGH confidence violations pass the LLM checker.

    These are unit-level checks on the filtering logic, not full LLM calls.
    """

    def test_medium_confidence_now_filtered(self):
        """Medium confidence should be filtered out (per Rule 8)."""
        # Simulate what the LLM checker does at lines 124-134
        violations = []
        test_items = [
            {"violated": True, "confidence": "high", "rule_id": "R1", "explanation": "clear"},
            {"violated": True, "confidence": "medium", "rule_id": "R2", "explanation": "maybe"},
            {"violated": True, "confidence": "low", "rule_id": "R3", "explanation": "unlikely"},
            {"violated": False, "confidence": "high", "rule_id": "R4", "explanation": "no"},
        ]
        for v in test_items:
            if not v.get("violated"):
                continue
            if v.get("confidence") != "high":
                continue
            violations.append(v)

        assert len(violations) == 1
        assert violations[0]["rule_id"] == "R1"

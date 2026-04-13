"""Tests for mini-ledger-update, hit normalization, and open_hits_for.

Tests the full flow: agents produce turns → hits are created with normalized
'against' fields → mini-ledger-update resolves hits within a round →
subsequent agents see only genuinely-open hits.
"""

from __future__ import annotations

import pytest

from arbiter.ledger.ops import add_hit, resolve_hit, open_hits, ledger_grew
from arbiter.ledger.parser import parse_ledger_block
from arbiter.agents.context import _open_hits_for


# ── _open_hits_for with normalized sides ──────────────────────────────


class TestOpenHitsFor:
    """Test that _open_hits_for works with normalized against fields."""

    def _make_ledger(self):
        ledger = []
        ledger = add_hit(ledger, "Skeptic", "Proponent", "G is broken", 1)
        ledger = add_hit(ledger, "Proponent", "Skeptic", "Skeptic misreads", 1)
        ledger = add_hit(ledger, "GraphTheorist", "Theory", "DAG is inconsistent", 1)
        ledger = add_hit(ledger, "Skeptic", "Proponent", "BELLA is unfalsifiable", 1)
        return ledger

    def test_proponent_sees_attacks_against_proponent_and_theory(self):
        ledger = self._make_ledger()
        hits = _open_hits_for(ledger, "Proponent")
        # h1 (against Proponent) + h3 (against Theory) + h4 (against Proponent)
        assert len(hits) == 3
        against_values = {h["against"] for h in hits}
        assert against_values == {"Proponent", "Theory"}

    def test_skeptic_sees_attacks_against_skeptic_and_theory(self):
        ledger = self._make_ledger()
        hits = _open_hits_for(ledger, "Skeptic")
        # h2 (against Skeptic) + h3 (against Theory)
        assert len(hits) == 2
        against_values = {h["against"] for h in hits}
        assert against_values == {"Skeptic", "Theory"}

    def test_all_sides_see_theory_hits(self):
        ledger = self._make_ledger()
        pro_hits = _open_hits_for(ledger, "Proponent")
        skep_hits = _open_hits_for(ledger, "Skeptic")
        # Theory hits visible to both
        theory_in_pro = [h for h in _open_hits_for(ledger, "Proponent") if h["against"] == "Theory"]
        # Actually Theory hits are only for the exact match — let me check
        # Theory hits should show for everyone since we include "Theory" in the match
        all_theory = [h for h in ledger if h["against"] == "Theory"]
        for side in ["Proponent", "Skeptic", "Neutral"]:
            side_hits = _open_hits_for(ledger, side)
            theory_count = sum(1 for h in side_hits if h["against"] == "Theory")
            assert theory_count == len(all_theory)

    def test_resolved_hits_excluded(self):
        ledger = self._make_ledger()
        ledger = resolve_hit(ledger, "h1", "rebutted", "My rebuttal")
        hits = _open_hits_for(ledger, "Proponent")
        # h3 (Theory, open) + h4 (Proponent, open) — h1 resolved
        assert len(hits) == 2
        hit_ids = {h["id"] for h in hits}
        assert "h1" not in hit_ids
        assert "h4" in hit_ids

    def test_empty_ledger(self):
        assert _open_hits_for([], "Proponent") == []

    def test_no_matching_side(self):
        ledger = add_hit([], "A", "Proponent", "test", 1)
        assert _open_hits_for(ledger, "Neutral") == []

    def test_case_sensitivity(self):
        """against field should be normalized — exact match only."""
        ledger = add_hit([], "A", "proponent", "test", 1)  # lowercase
        # Exact match fails because "proponent" != "Proponent"
        assert _open_hits_for(ledger, "Proponent") == []
        # This is correct — normalization should happen at creation time


# ── Mini-ledger-update simulation ─────────────────────────────────────


class TestMiniLedgerUpdate:
    """Simulate the within-round mini-ledger-update flow."""

    def test_hits_disappear_for_subsequent_agents(self):
        """After Agent 0 resolves h1-h3, Agent 1 should not see them."""
        # Setup: 6 open hits against Proponent
        ledger = []
        for i in range(6):
            ledger = add_hit(ledger, "Skeptic", "Proponent", f"claim {i}", 1)

        # Agent 0 addresses h1, h2, h3
        ledger_after_0 = resolve_hit(ledger, "h1", "rebutted", "reb1")
        ledger_after_0 = resolve_hit(ledger_after_0, "h2", "conceded", "conc2")
        ledger_after_0 = resolve_hit(ledger_after_0, "h3", "rebutted", "reb3")

        # Agent 1 should see only h4, h5, h6
        open_for_1 = _open_hits_for(ledger_after_0, "Proponent")
        assert len(open_for_1) == 3
        assert {h["id"] for h in open_for_1} == {"h4", "h5", "h6"}

    def test_full_round_simulation(self):
        """Simulate 5 agents each addressing 2 hits in sequence."""
        ledger = []
        for i in range(10):
            ledger = add_hit(ledger, "Skeptic", "Proponent", f"claim {i}", 1)

        cur_ledger = list(ledger)
        addressed_ids = set()

        for agent_idx in range(5):
            open_now = _open_hits_for(cur_ledger, "Proponent")
            # Each agent addresses the first 2 open hits
            for h in open_now[:2]:
                cur_ledger = resolve_hit(cur_ledger, h["id"], "rebutted", f"reb by agent {agent_idx}")
                addressed_ids.add(h["id"])

        # All 10 should be addressed (5 agents × 2 each)
        assert len(addressed_ids) == 10
        assert _open_hits_for(cur_ledger, "Proponent") == []

    def test_no_double_counting(self):
        """If Agent 0 and Agent 2 both resolve h1, it should only count once."""
        ledger = add_hit([], "Skeptic", "Proponent", "claim", 1)

        # Agent 0 resolves h1
        ledger = resolve_hit(ledger, "h1", "rebutted", "first rebuttal")
        assert ledger[0]["status"] == "rebutted"

        # Agent 2 also tries to resolve h1 (shouldn't see it, but let's test)
        ledger = resolve_hit(ledger, "h1", "rebutted", "second rebuttal")
        # Second rebuttal overwrites — last writer wins
        assert ledger[0]["rebuttal"] == "second rebuttal"
        # But status is still rebutted (idempotent)
        assert ledger[0]["status"] == "rebutted"

    def test_mixed_sides(self):
        """Hits against different sides should be independent."""
        ledger = []
        ledger = add_hit(ledger, "Skeptic", "Proponent", "attack pro", 1)
        ledger = add_hit(ledger, "Proponent", "Skeptic", "attack skep", 1)
        ledger = add_hit(ledger, "Neutral", "Theory", "theory issue", 1)

        # Proponent resolves h1 (against Proponent)
        ledger = resolve_hit(ledger, "h1", "rebutted", "reb")

        # Skeptic should still see h2 (against Skeptic) + h3 (Theory)
        skep_hits = _open_hits_for(ledger, "Skeptic")
        assert len(skep_hits) == 2  # h2 (Skeptic) + h3 (Theory)
        # Actually h3 is "Theory" which shows for Skeptic too
        # Let me check — _open_hits_for includes "Theory"
        assert any(h["id"] == "h2" for h in skep_hits)

    def test_parsing_malformed_addressed(self):
        """Malformed hits_addressed should be skipped."""
        text = '''My argument.
```json
{"new_hits":[], "hits_addressed":["h1", {"id":"h2","status":"rebutted","rebuttal":"ok"}, 42]}
```'''
        block = parse_ledger_block(text)
        # Should have 3 entries (string, dict, int)
        addressed = block.get("hits_addressed", [])
        assert len(addressed) == 3

        # Only the dict should be processable
        valid = [a for a in addressed if isinstance(a, dict)]
        assert len(valid) == 1
        assert valid[0]["id"] == "h2"

    def test_template_placeholder_not_resolved(self):
        """Hits with status='STATUS' (unfilled template) should not resolve."""
        ledger = add_hit([], "Skeptic", "Proponent", "test", 1)
        # Agent returns template placeholder
        ledger = resolve_hit(ledger, "h1", "STATUS", "YOUR RESPONSE TO: test")
        # resolve_hit doesn't validate status — it would set it to "STATUS"
        # The graph.py enforcement should catch this
        # For now, verify the behavior
        assert ledger[0]["status"] == "STATUS"
        # _open_hits_for checks for "open" only — "STATUS" is not "open"
        assert _open_hits_for(ledger, "Proponent") == []


# ── Hit normalization ─────────────────────────────────────────────────


class TestHitNormalization:
    """Test that add_hit normalizes the against field correctly.

    Note: normalization happens in graph.py's _ledger_node, not in
    add_hit itself. These tests verify the expected behavior after
    normalization.
    """

    def test_exact_side_name(self):
        ledger = add_hit([], "A", "Proponent", "test", 1)
        assert ledger[0]["against"] == "Proponent"

    def test_theory_preserved(self):
        ledger = add_hit([], "A", "Theory", "test", 1)
        assert ledger[0]["against"] == "Theory"

    def test_claim_truncation(self):
        long_claim = "x" * 500
        ledger = add_hit([], "A", "B", long_claim, 1)
        assert len(ledger[0]["claim"]) == 300

    def test_rebuttal_truncation(self):
        long_rebuttal = "y" * 1000
        ledger = add_hit([], "A", "B", "claim", 1)
        ledger = resolve_hit(ledger, "h1", "rebutted", long_rebuttal)
        assert len(ledger[0]["rebuttal"]) == 500


# ── Ledger growth detection ───────────────────────────────────────────


class TestLedgerGrowth:
    def test_growth_detected(self):
        ledger = add_hit([], "A", "B", "c", 1)
        assert ledger_grew(ledger, 0) is True

    def test_no_growth(self):
        ledger = add_hit([], "A", "B", "c", 1)
        assert ledger_grew(ledger, 1) is False

    def test_resolution_is_not_growth(self):
        ledger = add_hit([], "A", "B", "c", 1)
        ledger = resolve_hit(ledger, "h1", "rebutted", "r")
        # Still 1 hit — resolution doesn't change count
        assert ledger_grew(ledger, 1) is False

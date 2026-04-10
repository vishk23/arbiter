"""Tests for T23: Ledger operations with gate-aware entries."""

from arbiter.ledger.ops import add_hit, resolve_hit, open_hits, ledger_grew


class TestLedgerGateAware:
    """Test ledger ops that support gate-aware transcript entries."""

    def test_add_hit_with_validity_status(self):
        """Hits should work alongside validity_status in transcript entries."""
        ledger = add_hit([], by="Proponent", against="Skeptic",
                         claim="X is true", round_idx=1)
        assert ledger[0]["status"] == "open"
        assert ledger[0]["id"] == "h1"

    def test_add_multiple_hits_sequential_ids(self):
        ledger = []
        ledger = add_hit(ledger, "P", "S", "claim 1", 1)
        ledger = add_hit(ledger, "S", "P", "claim 2", 1)
        ledger = add_hit(ledger, "P", "S", "claim 3", 2)
        assert [h["id"] for h in ledger] == ["h1", "h2", "h3"]

    def test_resolve_to_rebutted(self):
        ledger = add_hit([], "P", "S", "X is true", 1)
        ledger = resolve_hit(ledger, "h1", "rebutted", "X fails because Y")
        assert ledger[0]["status"] == "rebutted"
        assert ledger[0]["rebuttal"] == "X fails because Y"

    def test_resolve_to_conceded(self):
        ledger = add_hit([], "P", "S", "X is true", 1)
        ledger = resolve_hit(ledger, "h1", "conceded")
        assert ledger[0]["status"] == "conceded"

    def test_resolve_to_dodged(self):
        ledger = add_hit([], "P", "S", "X is true", 1)
        ledger = resolve_hit(ledger, "h1", "dodged")
        assert ledger[0]["status"] == "dodged"

    def test_resolve_nonexistent_hit(self):
        ledger = add_hit([], "P", "S", "X is true", 1)
        ledger = resolve_hit(ledger, "h99", "rebutted", "nope")
        assert ledger[0]["status"] == "open"  # unchanged

    def test_open_hits_filter_by_side(self):
        ledger = []
        ledger = add_hit(ledger, "P", "Skeptic", "claim 1", 1)
        ledger = add_hit(ledger, "S", "Proponent", "claim 2", 1)
        ledger = add_hit(ledger, "P", "Skeptic", "claim 3", 2)

        skeptic_hits = open_hits(ledger, against="Skeptic")
        assert len(skeptic_hits) == 2

        proponent_hits = open_hits(ledger, against="Proponent")
        assert len(proponent_hits) == 1

    def test_open_hits_excludes_resolved(self):
        ledger = add_hit([], "P", "S", "claim 1", 1)
        ledger = add_hit(ledger, "S", "P", "claim 2", 1)
        ledger = resolve_hit(ledger, "h1", "rebutted", "done")

        result = open_hits(ledger)
        assert len(result) == 1
        assert result[0]["id"] == "h2"

    def test_ledger_grew(self):
        ledger = add_hit([], "P", "S", "claim", 1)
        assert ledger_grew(ledger, 0) is True
        assert ledger_grew(ledger, 1) is False
        assert ledger_grew(ledger, 2) is False

    def test_claim_truncation(self):
        long_claim = "X" * 500
        ledger = add_hit([], "P", "S", long_claim, 1)
        assert len(ledger[0]["claim"]) == 300

    def test_rebuttal_truncation(self):
        long_rebuttal = "Y" * 700
        ledger = add_hit([], "P", "S", "claim", 1)
        ledger = resolve_hit(ledger, "h1", "rebutted", long_rebuttal)
        assert len(ledger[0]["rebuttal"]) == 500

    def test_immutable_pattern(self):
        """add_hit and resolve_hit should return new lists, not mutate in place."""
        original = add_hit([], "P", "S", "claim", 1)
        updated = add_hit(original, "S", "P", "claim 2", 1)
        assert len(original) == 1
        assert len(updated) == 2

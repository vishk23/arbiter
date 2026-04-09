"""Tests for T31: Export argdown format validity."""

from arbiter.export.argdown import export_argdown


def _hit(id="h1", by="Proponent", against="Skeptic", claim="Test claim",
         status="open", rebuttal="", round_landed=1):
    return {
        "id": id, "by": by, "against": against, "claim": claim,
        "status": status, "rebuttal": rebuttal, "round_landed": round_landed,
    }


class TestExportArgdown:
    def test_empty_ledger(self):
        result = export_argdown([], ["Proponent", "Skeptic"])
        assert "Empty ledger" in result

    def test_single_open_hit(self):
        ledger = [_hit(id="h1", claim="Consciousness is computable")]
        result = export_argdown(ledger, ["Proponent", "Skeptic"])
        assert "[h1]:" in result
        assert "Consciousness is computable" in result
        assert "#open" in result

    def test_rebutted_hit(self):
        ledger = [
            _hit(id="h1", by="Proponent", against="Skeptic",
                 claim="X is true", status="rebutted", rebuttal="No, X fails"),
            _hit(id="h2", by="Skeptic", against="Proponent",
                 claim="X fails because Y", rebuttal=""),
        ]
        result = export_argdown(ledger, ["Proponent", "Skeptic"])
        assert "[h1]:" in result
        assert "[h2]:" in result
        assert "#rebutted" in result

    def test_header_present(self):
        ledger = [_hit()]
        result = export_argdown(ledger, ["Proponent", "Skeptic"])
        assert "title: Argument Ledger" in result

    def test_sides_grouped(self):
        ledger = [
            _hit(id="h1", by="Proponent"),
            _hit(id="h2", by="Skeptic"),
        ]
        result = export_argdown(ledger, ["Proponent", "Skeptic"])
        assert "// --- Proponent ---" in result
        assert "// --- Skeptic ---" in result

    def test_newlines_stripped_from_claims(self):
        ledger = [_hit(claim="Line one\nLine two\nLine three")]
        result = export_argdown(ledger, ["Proponent"])
        assert "\n" not in result.split("[h1]:")[1].split("#")[0].strip()

    def test_same_side_support_relations(self):
        ledger = [
            _hit(id="h1", by="Proponent"),
            _hit(id="h2", by="Proponent"),
        ]
        result = export_argdown(ledger, ["Proponent", "Skeptic"])
        assert "[h2] + [h1]" in result

    def test_conceded_status(self):
        ledger = [_hit(status="conceded")]
        result = export_argdown(ledger, ["Proponent"])
        assert "#conceded" in result

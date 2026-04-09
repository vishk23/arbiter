"""Tests for T32: Export markdown structure."""

from arbiter.export.markdown import export_markdown


def _state(transcript=None, ledger=None, verdict=""):
    return {
        "transcript": transcript or [],
        "ledger": ledger or [],
        "formal_verdict": verdict,
    }


class TestExportMarkdown:
    def test_empty_state(self):
        result = export_markdown(_state())
        assert "# Debate Transcript" in result

    def test_config_name_in_title(self):
        result = export_markdown(_state(), config_name="Consciousness Debate")
        assert "# Debate: Consciousness Debate" in result

    def test_transcript_rounds(self):
        transcript = [
            {"agent": "Proponent", "round": 1, "text": "Opening argument."},
            {"agent": "Skeptic", "round": 1, "text": "Rebuttal."},
            {"agent": "Proponent", "round": 2, "text": "Follow up."},
        ]
        result = export_markdown(_state(transcript=transcript))
        assert "## Round 1" in result
        assert "## Round 2" in result
        assert "### Proponent" in result
        assert "### Skeptic" in result
        assert "Opening argument." in result

    def test_ledger_table(self):
        ledger = [
            {
                "id": "h1", "by": "Proponent", "against": "Skeptic",
                "claim": "Test claim", "status": "open",
            },
        ]
        result = export_markdown(_state(ledger=ledger))
        assert "## Argument Ledger" in result
        assert "| h1 " in result
        assert "| Proponent " in result

    def test_long_claim_truncation(self):
        long_claim = "X" * 200
        ledger = [
            {"id": "h1", "by": "P", "against": "S", "claim": long_claim, "status": "open"},
        ]
        result = export_markdown(_state(ledger=ledger))
        assert "..." in result
        # Should be truncated to ~120 chars
        for line in result.split("\n"):
            if "XXXX" in line:
                claim_part = line.split("|")[4].strip()
                assert len(claim_part) <= 125

    def test_verdict_section(self):
        result = export_markdown(_state(verdict="Proponent wins 24-0"))
        assert "## Formal Verdict" in result
        assert "Proponent wins 24-0" in result

    def test_no_ledger_no_table(self):
        result = export_markdown(_state())
        assert "Argument Ledger" not in result

    def test_no_verdict_no_section(self):
        result = export_markdown(_state(verdict=""))
        assert "Formal Verdict" not in result

    def test_newlines_in_claims_handled(self):
        ledger = [
            {"id": "h1", "by": "P", "against": "S",
             "claim": "Line1\nLine2", "status": "open"},
        ]
        result = export_markdown(_state(ledger=ledger))
        # Newlines should be replaced in table cells
        table_lines = [l for l in result.split("\n") if "| h1" in l]
        assert len(table_lines) == 1
        assert "\n" not in table_lines[0]

"""Tests for panel_verdict tie-breaking: scores override vote ties."""

from arbiter.judge.aggregator import aggregate


def _verdict(scores_prop, scores_skep, verdict="Proponent"):
    return {
        "scores": {
            "Proponent": {**scores_prop, "total": sum(scores_prop.values())},
            "Skeptic": {**scores_skep, "total": sum(scores_skep.values())},
        },
        "verdict": verdict,
    }


class TestPanelVerdictTiebreak:
    """Verify that tied votes are broken by mean total scores."""

    def test_vote_tie_broken_by_scores_skeptic_wins(self):
        """BIT-like scenario: 1 Proponent vote, 1 Skeptic vote, Skeptic higher scores."""
        verdicts = {
            "anthropic": _verdict(
                {"R1": 7, "R2": 4, "R3": 6, "R4": 4, "R5": 4},
                {"R1": 3, "R2": 7, "R3": 3, "R4": 5, "R5": 6},
                verdict="Proponent",
            ),
            "openai": _verdict(
                {"R1": 8, "R2": 5, "R3": 4, "R4": 4, "R5": 3},
                {"R1": 6, "R2": 7, "R3": 6, "R4": 5, "R5": 6},
                verdict="Skeptic",
            ),
        }
        result = aggregate(
            verdicts,
            ["R1", "R2", "R3", "R4", "R5"],
            ["Proponent", "Skeptic"],
        )
        # Proponent mean total: (25+24)/2 = 24.5
        # Skeptic mean total: (24+30)/2 = 27.0
        assert result["panel_verdict"] == "Skeptic"

    def test_vote_tie_broken_by_scores_proponent_wins(self):
        """Reverse: Proponent has higher scores despite split vote."""
        verdicts = {
            "j1": _verdict({"R1": 9}, {"R1": 4}, verdict="Proponent"),
            "j2": _verdict({"R1": 8}, {"R1": 5}, verdict="Skeptic"),
        }
        result = aggregate(verdicts, ["R1"], ["Proponent", "Skeptic"])
        # Proponent mean total: (9+8)/2 = 8.5
        # Skeptic mean total: (4+5)/2 = 4.5
        assert result["panel_verdict"] == "Proponent"

    def test_clear_majority_overrides_scores(self):
        """2v1 majority: majority vote wins even if minority has higher scores."""
        verdicts = {
            "j1": _verdict({"R1": 6}, {"R1": 7}, verdict="Proponent"),
            "j2": _verdict({"R1": 5}, {"R1": 8}, verdict="Proponent"),
            "j3": _verdict({"R1": 4}, {"R1": 9}, verdict="Skeptic"),
        }
        result = aggregate(verdicts, ["R1"], ["Proponent", "Skeptic"])
        # Proponent has 2 votes vs Skeptic 1 — majority wins
        assert result["panel_verdict"] == "Proponent"

    def test_iit_like_scenario(self):
        """IIT scenario: 1-1 vote tie, Skeptic wins on scores."""
        verdicts = {
            "openai": _verdict(
                {"R1": 9, "R2": 7, "R3": 6, "R4": 8, "R5": 7},
                {"R1": 7, "R2": 8, "R3": 6, "R4": 7, "R5": 8},
                verdict="Proponent",
            ),
            "anthropic": _verdict(
                {"R1": 7, "R2": 6, "R3": 4, "R4": 6, "R5": 5},
                {"R1": 6, "R2": 7, "R3": 5, "R4": 7, "R5": 6},
                verdict="Skeptic",
            ),
        }
        result = aggregate(
            verdicts,
            ["R1", "R2", "R3", "R4", "R5"],
            ["Proponent", "Skeptic"],
        )
        # Proponent mean total: (37+28)/2 = 32.5
        # Skeptic mean total: (36+31)/2 = 33.5
        assert result["panel_verdict"] == "Skeptic"

    def test_three_way_tie(self):
        """Three judges, three different verdicts — tiebreak by scores."""
        verdicts = {
            "j1": _verdict({"R1": 8}, {"R1": 5}, verdict="Proponent"),
            "j2": _verdict({"R1": 4}, {"R1": 9}, verdict="Skeptic"),
            "j3": _verdict({"R1": 6}, {"R1": 7}, verdict="Tied"),
        }
        result = aggregate(
            verdicts,
            ["R1"],
            ["Proponent", "Skeptic"],
        )
        # All 1 vote each. "Tied" isn't in sides so only Proponent/Skeptic compete.
        # Proponent mean: (8+4+6)/3 = 6.0, Skeptic mean: (5+9+7)/3 = 7.0
        assert result["panel_verdict"] == "Skeptic"

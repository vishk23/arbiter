"""Tests for T29: Judge aggregator (spread flagging, majority verdict)."""

from arbiter.judge.aggregator import aggregate


def _verdict(scores_prop, scores_skep, verdict="Proponent"):
    return {
        "scores": {
            "Proponent": {**scores_prop, "total": sum(scores_prop.values())},
            "Skeptic": {**scores_skep, "total": sum(scores_skep.values())},
        },
        "verdict": verdict,
    }


class TestAggregate:
    def test_single_judge(self):
        verdicts = {
            "judge1": _verdict({"R1": 8, "R2": 7}, {"R1": 5, "R2": 6}),
        }
        result = aggregate(verdicts, ["R1", "R2"], ["Proponent", "Skeptic"])
        assert result["panel_verdict"] == "Proponent"
        assert result["criterion_means"]["Proponent"]["R1"] == 8
        assert result["criterion_spreads"]["Proponent"]["R1"] == 0
        assert result["low_confidence_flags"] == []

    def test_two_judges_same_scores(self):
        v = _verdict({"R1": 7}, {"R1": 5})
        verdicts = {"j1": v, "j2": v}
        result = aggregate(verdicts, ["R1"], ["Proponent", "Skeptic"])
        assert result["criterion_spreads"]["Proponent"]["R1"] == 0

    def test_spread_flagging(self):
        verdicts = {
            "j1": _verdict({"R1": 9}, {"R1": 5}),
            "j2": _verdict({"R1": 4}, {"R1": 5}),
        }
        result = aggregate(
            verdicts, ["R1"], ["Proponent", "Skeptic"], spread_threshold=3
        )
        # Proponent R1 spread = 9-4 = 5 > 3
        assert len(result["low_confidence_flags"]) >= 1
        assert any("Proponent.R1" in f for f in result["low_confidence_flags"])

    def test_spread_within_threshold(self):
        verdicts = {
            "j1": _verdict({"R1": 7}, {"R1": 6}),
            "j2": _verdict({"R1": 8}, {"R1": 5}),
        }
        result = aggregate(
            verdicts, ["R1"], ["Proponent", "Skeptic"], spread_threshold=3
        )
        # Proponent R1 spread = 8-7 = 1 <= 3, Skeptic = 6-5 = 1 <= 3
        assert result["low_confidence_flags"] == []

    def test_majority_verdict_2v1(self):
        verdicts = {
            "j1": _verdict({"R1": 8}, {"R1": 5}, verdict="Proponent"),
            "j2": _verdict({"R1": 7}, {"R1": 6}, verdict="Proponent"),
            "j3": _verdict({"R1": 5}, {"R1": 8}, verdict="Skeptic"),
        }
        result = aggregate(verdicts, ["R1"], ["Proponent", "Skeptic"])
        assert result["panel_verdict"] == "Proponent"
        assert result["verdict_counts"]["Proponent"] == 2
        assert result["verdict_counts"]["Skeptic"] == 1

    def test_unanimous_verdict(self):
        verdicts = {
            "j1": _verdict({"R1": 8}, {"R1": 5}, verdict="Tied"),
            "j2": _verdict({"R1": 7}, {"R1": 6}, verdict="Tied"),
        }
        result = aggregate(verdicts, ["R1"], ["Proponent", "Skeptic"])
        assert result["panel_verdict"] == "Tied"

    def test_criterion_means(self):
        verdicts = {
            "j1": _verdict({"R1": 6, "R2": 8}, {"R1": 4, "R2": 6}),
            "j2": _verdict({"R1": 8, "R2": 6}, {"R1": 6, "R2": 8}),
        }
        result = aggregate(verdicts, ["R1", "R2"], ["Proponent", "Skeptic"])
        assert result["criterion_means"]["Proponent"]["R1"] == 7.0
        assert result["criterion_means"]["Skeptic"]["R1"] == 5.0

    def test_total_spread_not_flagged(self):
        """Total spread should never be in low_confidence_flags."""
        verdicts = {
            "j1": _verdict({"R1": 10}, {"R1": 1}),
            "j2": _verdict({"R1": 1}, {"R1": 10}),
        }
        result = aggregate(verdicts, ["R1"], ["Proponent", "Skeptic"], spread_threshold=3)
        # R1 gets flagged but total should not
        flagged_keys = [f.split(":")[0] for f in result["low_confidence_flags"]]
        assert not any("total" in k for k in flagged_keys)

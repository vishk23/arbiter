"""Tests for T28: Judge rubric dynamic model generation."""

import pytest
from pydantic import ValidationError

from arbiter.config import RubricCriterion
from arbiter.judge.rubric import build_verdict_models, rubric_description


def _criteria():
    return [
        RubricCriterion(id="R1", name="Evidence", description="Quality of evidence", min_score=0, max_score=10),
        RubricCriterion(id="R2", name="Logic", description="Logical rigour", min_score=0, max_score=10),
    ]


class TestBuildVerdictModels:
    def test_returns_two_models(self):
        SideScores, Verdict = build_verdict_models(
            _criteria(), ["Proponent", "Skeptic"], ["Proponent", "Skeptic", "Tied"]
        )
        assert SideScores is not None
        assert Verdict is not None

    def test_side_scores_has_criteria_fields(self):
        SideScores, _ = build_verdict_models(
            _criteria(), ["Proponent"], ["Proponent"]
        )
        fields = SideScores.model_fields
        assert "R1" in fields
        assert "R2" in fields
        assert "total" in fields

    def test_side_scores_validates_range(self):
        SideScores, _ = build_verdict_models(
            _criteria(), ["Proponent"], ["Proponent"]
        )
        # Valid
        SideScores(R1=5, R2=7, total=12)
        # Invalid: R1 > max (10)
        with pytest.raises(ValidationError):
            SideScores(R1=11, R2=7, total=18)
        # Invalid: negative
        with pytest.raises(ValidationError):
            SideScores(R1=-1, R2=7, total=6)

    def test_verdict_has_required_fields(self):
        _, Verdict = build_verdict_models(
            _criteria(), ["Proponent", "Skeptic"], ["Proponent", "Skeptic", "Tied"]
        )
        fields = Verdict.model_fields
        assert "scores" in fields
        assert "verdict" in fields
        assert "verdict_reasoning" in fields
        assert "key_landed_hits" in fields
        assert "key_dodged_questions" in fields

    def test_full_verdict_validation(self):
        _, Verdict = build_verdict_models(
            _criteria(), ["Proponent", "Skeptic"], ["Proponent", "Skeptic", "Tied"]
        )
        data = {
            "scores": {
                "Proponent": {"R1": 8, "R2": 7, "total": 15},
                "Skeptic": {"R1": 6, "R2": 5, "total": 11},
            },
            "verdict": "Proponent",
            "verdict_reasoning": "Better evidence.",
            "key_landed_hits": ["The consciousness argument"],
            "key_dodged_questions": ["Falsifiability"],
        }
        v = Verdict.model_validate(data)
        assert v.verdict == "Proponent"

    def test_verdict_json_schema(self):
        _, Verdict = build_verdict_models(
            _criteria(), ["Proponent", "Skeptic"], ["Proponent", "Skeptic", "Tied"]
        )
        schema = Verdict.model_json_schema()
        assert "properties" in schema
        assert "scores" in schema["properties"]


class TestRubricDescription:
    def test_contains_criteria(self):
        text = rubric_description(_criteria())
        assert "R1" in text
        assert "Evidence" in text
        assert "R2" in text
        assert "Logic" in text
        assert "[0-10]" in text

    def test_contains_total(self):
        text = rubric_description(_criteria())
        assert "total" in text
        assert "0-20" in text

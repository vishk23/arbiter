"""Tests for T27: Gate entailment_checker (mock provider)."""

from unittest.mock import MagicMock

from arbiter.config import EntailmentCheckConfig
from arbiter.gate.entailment_checker import EntailmentChecker


def _make_checker(enabled=True, system_prompt="Check violations."):
    config = EntailmentCheckConfig(
        enabled=enabled,
        provider="openai",
        system_prompt=system_prompt,
    )
    provider = MagicMock()
    return EntailmentChecker(config, provider), provider


class TestEntailmentChecker:
    def test_disabled_returns_empty(self):
        checker, _ = _make_checker(enabled=False)
        assert checker.check("any text") == []

    def test_no_system_prompt_returns_empty(self):
        checker, _ = _make_checker(system_prompt="")
        assert checker.check("any text") == []

    def test_no_violations(self):
        checker, provider = _make_checker()
        provider.call_structured.return_value = {
            "violates": [],
            "reason": "No issues",
            "confidence": "high",
        }
        assert checker.check("clean text") == []

    def test_high_confidence_violation(self):
        checker, provider = _make_checker()
        provider.call_structured.return_value = {
            "violates": ["R1", "R2"],
            "reason": "Contradicts stipulation",
            "confidence": "high",
        }
        violations = checker.check("violating text")
        assert len(violations) == 1
        assert violations[0]["type"] == "entailment_violation"
        assert violations[0]["rule_id"] == "R1,R2"
        assert violations[0]["confidence"] == "high"

    def test_medium_confidence_violation(self):
        checker, provider = _make_checker()
        provider.call_structured.return_value = {
            "violates": ["R1"],
            "reason": "Possible issue",
            "confidence": "medium",
        }
        violations = checker.check("text")
        assert len(violations) == 1

    def test_low_confidence_filtered_out(self):
        checker, provider = _make_checker()
        provider.call_structured.return_value = {
            "violates": ["R1"],
            "reason": "Maybe",
            "confidence": "low",
        }
        assert checker.check("text") == []

    def test_provider_failure_fails_open(self):
        checker, provider = _make_checker()
        provider.call_structured.side_effect = RuntimeError("API down")
        assert checker.check("text") == []

    def test_provider_called_with_correct_schema(self):
        from arbiter.schemas import EntailmentResult

        checker, provider = _make_checker()
        provider.call_structured.return_value = {
            "violates": [],
            "reason": "",
            "confidence": "low",
        }
        checker.check("test turn text")
        call_args = provider.call_structured.call_args
        assert "TURN TEXT:" in call_args.kwargs["user"]
        assert call_args.kwargs["schema"] is EntailmentResult

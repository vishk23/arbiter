"""Tests for T02: Anthropic call_structured fallback without OpenAI."""

from __future__ import annotations

import json
import sys
from unittest.mock import MagicMock, patch

import pytest

from arbiter.providers.anthropic import AnthropicProvider


class TestExtractJsonAggressive:
    """Unit tests for the aggressive JSON extraction fallback."""

    def test_clean_json(self):
        assert AnthropicProvider._extract_json_aggressive('{"a": 1}') == {"a": 1}

    def test_json_in_markdown_block(self):
        text = '```json\n{"key": "value"}\n```'
        assert AnthropicProvider._extract_json_aggressive(text) == {"key": "value"}

    def test_json_with_surrounding_text(self):
        text = 'Here is the result:\n{"name": "test", "count": 42}\nDone.'
        result = AnthropicProvider._extract_json_aggressive(text)
        assert result == {"name": "test", "count": 42}

    def test_nested_json(self):
        obj = {"outer": {"inner": [1, 2, 3]}, "flag": True}
        text = f"Response: {json.dumps(obj)} end"
        assert AnthropicProvider._extract_json_aggressive(text) == obj

    def test_no_json(self):
        assert AnthropicProvider._extract_json_aggressive("no json here") is None

    def test_invalid_json(self):
        assert AnthropicProvider._extract_json_aggressive("{broken: json}") is None


class TestCallStructuredFallback:
    """Test that call_structured doesn't crash when OpenAI is unavailable."""

    @patch.object(AnthropicProvider, "_call_impl")
    @patch.object(AnthropicProvider, "__init__", lambda self, *a, **kw: None)
    def test_regex_recovery_before_openai(self, mock_call):
        """If aggressive regex finds JSON, OpenAI is never called."""
        mock_call.return_value = 'Sure! {"name": "test", "value": 42}'
        provider = AnthropicProvider.__new__(AnthropicProvider)
        provider.model = "claude-test"
        provider.config = MagicMock()

        result = provider._call_structured_impl(
            system="test",
            user="test",
            schema={"type": "object", "properties": {"name": {"type": "string"}}},
        )
        assert result["name"] == "test"

    @patch.object(AnthropicProvider, "_call_impl")
    @patch.object(AnthropicProvider, "__init__", lambda self, *a, **kw: None)
    def test_clear_error_when_openai_missing(self, mock_call):
        """If both regex methods fail and openai is not installed, get a clear error."""
        mock_call.return_value = "This is not JSON at all, just plain text."
        provider = AnthropicProvider.__new__(AnthropicProvider)
        provider.model = "claude-test"
        provider.config = MagicMock()

        with patch.object(
            AnthropicProvider,
            "_openai_reformat",
            side_effect=ImportError("No module named 'openai'"),
        ):
            with pytest.raises(ValueError, match="OpenAI package is not installed"):
                provider._call_structured_impl(
                    system="test",
                    user="test",
                    schema={"type": "object"},
                )

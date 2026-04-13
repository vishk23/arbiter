"""Tests for Anthropic structured output via tool-use."""

from __future__ import annotations

import json
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


class TestToolUseStructuredOutput:
    """Test that call_structured uses Anthropic's tool-use for structured output."""

    @patch.object(AnthropicProvider, "__init__", lambda self, *a, **kw: None)
    def test_tool_use_extracts_input(self):
        """Tool-use response should extract the tool input as structured output."""
        provider = AnthropicProvider.__new__(AnthropicProvider)
        provider.model = "claude-test"
        provider.config = MagicMock()
        provider.config.thinking = None

        # Mock the Anthropic client to return a tool_use block
        mock_block = MagicMock()
        mock_block.type = "tool_use"
        mock_block.name = "structured_output"
        mock_block.input = {"name": "test", "value": 42}

        mock_resp = MagicMock()
        mock_resp.content = [mock_block]

        mock_client = MagicMock()
        mock_client.messages.create.return_value = mock_resp
        provider._client = mock_client

        result = provider._call_structured_impl(
            system="test", user="test",
            schema={"type": "object", "properties": {"name": {"type": "string"}}},
        )
        assert result == {"name": "test", "value": 42}

        # Verify tool_choice was set correctly
        call_kwargs = mock_client.messages.create.call_args[1]
        assert call_kwargs["tool_choice"] == {"type": "tool", "name": "structured_output"}
        assert len(call_kwargs["tools"]) == 1
        assert call_kwargs["tools"][0]["name"] == "structured_output"

    @patch.object(AnthropicProvider, "__init__", lambda self, *a, **kw: None)
    def test_fallback_to_text_extraction(self):
        """If no tool_use block, fall back to text JSON extraction."""
        provider = AnthropicProvider.__new__(AnthropicProvider)
        provider.model = "claude-test"
        provider.config = MagicMock()
        provider.config.thinking = None

        # Mock response with only text (no tool_use)
        mock_block = MagicMock()
        mock_block.type = "text"
        mock_block.text = '{"name": "fallback"}'

        mock_resp = MagicMock()
        mock_resp.content = [mock_block]

        mock_client = MagicMock()
        mock_client.messages.create.return_value = mock_resp
        provider._client = mock_client

        result = provider._call_structured_impl(
            system="test", user="test",
            schema={"type": "object"},
        )
        assert result == {"name": "fallback"}

    @patch.object(AnthropicProvider, "__init__", lambda self, *a, **kw: None)
    def test_error_when_no_json_at_all(self):
        """If neither tool_use nor extractable JSON, raise ValueError."""
        provider = AnthropicProvider.__new__(AnthropicProvider)
        provider.model = "claude-test"
        provider.config = MagicMock()
        provider.config.thinking = None

        mock_block = MagicMock()
        mock_block.type = "text"
        mock_block.text = "This is not JSON at all."

        mock_resp = MagicMock()
        mock_resp.content = [mock_block]

        mock_client = MagicMock()
        mock_client.messages.create.return_value = mock_resp
        provider._client = mock_client

        with pytest.raises(ValueError, match="tool-use structured output failed"):
            provider._call_structured_impl(
                system="test", user="test",
                schema={"type": "object"},
            )

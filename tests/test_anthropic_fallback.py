"""Tests for Anthropic structured output via tool-use."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from arbiter.providers.anthropic import AnthropicProvider


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
    def test_raises_when_no_tool_use_block(self):
        """If no tool_use block, raise ValueError (no regex fallback)."""
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

        with pytest.raises(ValueError, match="tool-use structured output failed"):
            provider._call_structured_impl(
                system="test", user="test",
                schema={"type": "object"},
            )

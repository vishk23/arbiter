"""Tests for thinking/reasoning config applied across all provider call paths.

Catches the class of bug where _call_structured_impl or _call_parsed_impl
forgets to apply thinking/reasoning config, causing the model to exhaust
output budget on thinking with nothing left for the actual response.
"""

from unittest.mock import MagicMock, patch
import pytest

from arbiter.config import ProviderConfig


# ── Anthropic ────────────────────────────────────────────────────────


class TestAnthropicThinkingConfig:
    """Verify _apply_thinking is called in all Anthropic call paths."""

    def _make_provider(self):
        config = ProviderConfig(
            model="claude-opus-4-6",
            max_tokens=4000,
            thinking={"type": "adaptive", "effort": "high"},
        )
        with patch("arbiter.providers.anthropic.AnthropicProvider._init_client"):
            from arbiter.providers.anthropic import AnthropicProvider
            p = AnthropicProvider.__new__(AnthropicProvider)
            p.config = config
            p.model = config.model
            p._client = MagicMock()
        return p

    def test_call_impl_applies_thinking(self):
        p = self._make_provider()
        # Mock the API response
        mock_block = MagicMock()
        mock_block.type = "text"
        mock_block.text = "hello"
        p._client.messages.create.return_value = MagicMock(content=[mock_block])

        p._call_impl("system", "user", max_tokens=4000)

        kwargs = p._client.messages.create.call_args[1]
        assert "thinking" in kwargs, "_call_impl must apply thinking config"
        assert kwargs["thinking"]["type"] == "adaptive"
        assert kwargs["max_tokens"] > 4000, "max_tokens must include thinking overhead"

    def test_call_structured_impl_skips_thinking(self):
        """Anthropic tool_choice mode does NOT support thinking."""
        p = self._make_provider()
        mock_block = MagicMock()
        mock_block.type = "tool_use"
        mock_block.name = "structured_output"
        mock_block.input = {"key": "value"}
        p._client.messages.create.return_value = MagicMock(content=[mock_block])

        schema = {"type": "object", "properties": {"key": {"type": "string"}}}
        p._call_structured_impl("system", "user", schema, max_tokens=16000)

        kwargs = p._client.messages.create.call_args[1]
        assert "thinking" not in kwargs, (
            "Anthropic _call_structured_impl must NOT apply thinking — "
            "API rejects thinking with tool_choice forced"
        )

    def test_call_parsed_impl_applies_thinking(self):
        """Anthropic messages.parse() DOES support thinking."""
        from pydantic import BaseModel

        class TestModel(BaseModel):
            key: str

        p = self._make_provider()
        mock_resp = MagicMock()
        mock_resp.parsed_output = TestModel(key="value")
        p._client.messages.parse.return_value = mock_resp

        p._call_parsed_impl("system", "user", TestModel, max_tokens=16000)

        kwargs = p._client.messages.parse.call_args[1]
        assert "thinking" in kwargs, (
            "Anthropic _call_parsed_impl must apply thinking — "
            "messages.parse() supports it unlike tool_choice"
        )
        assert kwargs["max_tokens"] > 16000
        assert "output_format" in kwargs

    def test_pydantic_schema_routes_to_parsed_with_thinking(self):
        """The actual hotpath: call_structured(schema=PydanticModel) must
        route to _call_parsed_impl which uses messages.parse() with thinking.
        This is what extract_claims, identify_contradictions, etc. all use."""
        from pydantic import BaseModel

        class ClaimListResult(BaseModel):
            claims: list[dict]

        p = self._make_provider()
        mock_resp = MagicMock()
        mock_resp.parsed_output = ClaimListResult(claims=[{"id": "C1", "claim": "test"}])
        p._client.messages.parse.return_value = mock_resp

        # Call through the PUBLIC API (call_structured), not the impl directly
        result = p.call_structured("system", "user", schema=ClaimListResult, max_tokens=16000)

        # Verify it went through messages.parse (not messages.create/tool_choice)
        assert p._client.messages.parse.called, "Must route to messages.parse for Pydantic schemas"
        assert not p._client.messages.create.called, "Must NOT use tool_choice for Pydantic schemas"

        kwargs = p._client.messages.parse.call_args[1]
        assert "thinking" in kwargs, "Thinking must be applied on the parsed path"
        assert kwargs["output_format"] is ClaimListResult
        assert result["claims"][0]["id"] == "C1"

    def test_no_thinking_when_config_is_none(self):
        config = ProviderConfig(model="claude-sonnet-4-6", max_tokens=4000)
        with patch("arbiter.providers.anthropic.AnthropicProvider._init_client"):
            from arbiter.providers.anthropic import AnthropicProvider
            p = AnthropicProvider.__new__(AnthropicProvider)
            p.config = config
            p.model = config.model
            p._client = MagicMock()

        mock_block = MagicMock()
        mock_block.type = "text"
        mock_block.text = "hello"
        p._client.messages.create.return_value = MagicMock(content=[mock_block])

        p._call_impl("system", "user", max_tokens=4000)

        kwargs = p._client.messages.create.call_args[1]
        assert "thinking" not in kwargs


# ── OpenAI ───────────────────────────────────────────────────────────


class TestOpenAIReasoningConfig:
    """Verify _apply_reasoning is called in all OpenAI call paths."""

    def _make_provider(self):
        config = ProviderConfig(
            model="gpt-5.4",
            max_tokens=4000,
            reasoning={"effort": "high", "overhead": 8000},
        )
        with patch("arbiter.providers.openai.OpenAIProvider._init_client"):
            from arbiter.providers.openai import OpenAIProvider
            p = OpenAIProvider.__new__(OpenAIProvider)
            p.config = config
            p.model = config.model
            p._client = MagicMock()
        return p

    def test_call_impl_applies_reasoning(self):
        p = self._make_provider()
        p._client.responses.create.return_value = MagicMock(output_text="hello")

        p._call_impl("system", "user", max_tokens=4000)

        kwargs = p._client.responses.create.call_args[1]
        assert "reasoning" in kwargs, "_call_impl must apply reasoning config"
        assert kwargs["reasoning"]["effort"] == "high"
        assert kwargs["max_output_tokens"] == 4000 + 8000

    def test_call_structured_impl_applies_reasoning(self):
        p = self._make_provider()
        p._client.responses.create.return_value = MagicMock(
            output_text='{"key": "value"}'
        )

        schema = {"type": "object", "properties": {"key": {"type": "string"}}}
        p._call_structured_impl("system", "user", schema, max_tokens=4000)

        kwargs = p._client.responses.create.call_args[1]
        assert "reasoning" in kwargs, "_call_structured_impl must apply reasoning"
        assert kwargs["max_output_tokens"] == 4000 + 8000

    def test_call_parsed_impl_applies_reasoning(self):
        from pydantic import BaseModel

        class TestModel(BaseModel):
            key: str

        p = self._make_provider()
        mock_resp = MagicMock()
        mock_resp.output_parsed = TestModel(key="value")
        p._client.responses.parse.return_value = mock_resp

        p._call_parsed_impl("system", "user", TestModel, max_tokens=4000)

        kwargs = p._client.responses.parse.call_args[1]
        assert "reasoning" in kwargs, "_call_parsed_impl must apply reasoning"
        assert kwargs["max_output_tokens"] == 4000 + 8000

    def test_no_reasoning_when_config_is_none(self):
        config = ProviderConfig(model="gpt-4o", max_tokens=4000)
        with patch("arbiter.providers.openai.OpenAIProvider._init_client"):
            from arbiter.providers.openai import OpenAIProvider
            p = OpenAIProvider.__new__(OpenAIProvider)
            p.config = config
            p.model = config.model
            p._client = MagicMock()

        p._client.responses.create.return_value = MagicMock(output_text="hello")
        p._call_impl("system", "user", max_tokens=4000)

        kwargs = p._client.responses.create.call_args[1]
        assert "reasoning" not in kwargs
        assert kwargs["max_output_tokens"] == 4000


# ── Base provider retry ──────────────────────────────────────────────


class TestRetryLogic:
    """Verify retry works for both plain and structured calls."""

    def test_call_structured_with_retry_retries(self):
        from arbiter.providers.base import BaseProvider

        class FakeProvider(BaseProvider):
            def _init_client(self, config):
                pass
            def _call_impl(self, system, user, max_tokens=4000):
                return "text"
            def _call_structured_impl(self, system, user, schema, max_tokens=4000):
                raise ValueError("transient error")

        config = ProviderConfig(model="test", max_retries=2)
        p = FakeProvider(config)

        with pytest.raises(ValueError, match="transient error"):
            p.call_structured_with_retry("sys", "user", {"type": "object"})

    def test_call_structured_with_retry_succeeds_on_second_try(self):
        from arbiter.providers.base import BaseProvider

        call_count = 0

        class FlakyProvider(BaseProvider):
            def _init_client(self, config):
                pass
            def _call_impl(self, system, user, max_tokens=4000):
                return "text"
            def _call_structured_impl(self, system, user, schema, max_tokens=4000):
                nonlocal call_count
                call_count += 1
                if call_count == 1:
                    raise ValueError("first try fails")
                return {"result": "ok"}

        config = ProviderConfig(model="test", max_retries=3)
        p = FlakyProvider(config)

        with patch("time.sleep"):  # skip actual sleep
            result = p.call_structured_with_retry("sys", "user", {"type": "object"})

        assert result == {"result": "ok"}
        assert call_count == 2

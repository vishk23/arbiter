"""Anthropic (Claude) provider."""

from __future__ import annotations

import logging
import os
from typing import TYPE_CHECKING

from arbiter.config import ProviderConfig
from arbiter.providers.base import BaseProvider

if TYPE_CHECKING:
    from pydantic import BaseModel

logger = logging.getLogger(__name__)


class AnthropicProvider(BaseProvider):
    """Provider backed by the Anthropic Messages API."""

    def _init_client(self, config: ProviderConfig) -> None:
        import anthropic

        api_key = config.api_key or os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError(
                "Anthropic API key not found. Set 'api_key' in provider config "
                "or the ANTHROPIC_API_KEY environment variable."
            )

        self._client = anthropic.Anthropic(
            api_key=api_key,
            timeout=config.timeout,
        )

    def _apply_thinking(self, kwargs: dict, max_tokens: int) -> None:
        """Apply thinking + effort config to request kwargs.

        Anthropic 4.6 supports:
        - ``thinking.type: adaptive`` (recommended) — model decides thinking depth
        - ``thinking.type: enabled`` (deprecated on 4.6) — explicit budget_tokens
        - ``effort`` param (low/medium/high/max) via thinking config — controls
          thinking depth independently of thinking type

        See: https://platform.claude.com/docs/en/build-with-claude/adaptive-thinking
        """
        if not self.config.thinking:
            return

        thinking_type = self.config.thinking.get("type", "adaptive")

        if thinking_type == "adaptive":
            kwargs["thinking"] = {"type": "adaptive"}
            overhead = self.config.thinking.get("overhead", 16000)
            kwargs["max_tokens"] = max_tokens + overhead
        else:
            # Legacy "enabled" mode (deprecated on Opus/Sonnet 4.6)
            budget = self.config.thinking.get("budget_tokens", 10000)
            kwargs["thinking"] = {"type": thinking_type, "budget_tokens": budget}
            kwargs["max_tokens"] = max_tokens + budget

        # Effort parameter (low/medium/high/max) — controls thinking depth
        # Recommended: medium for most tasks, high for complex reasoning
        effort = self.config.thinking.get("effort")
        if effort:
            kwargs.setdefault("output_config", {})["effort"] = effort

    # ── plain text call ───────────────────────────────────────────────

    def _call_impl(self, system: str, user: str, max_tokens: int = 4000) -> str:
        kwargs: dict = dict(
            model=self.model,
            max_tokens=max_tokens,
            system=system,
            messages=[{"role": "user", "content": user}],
        )

        self._apply_thinking(kwargs, max_tokens)

        resp = self._client.messages.create(**kwargs)
        text = "\n".join(
            b.text for b in resp.content if b.type == "text"
        ).strip()
        return text

    # ── structured (JSON) call ────────────────────────────────────────

    def _call_structured_impl(
        self, system: str, user: str, schema: dict, max_tokens: int = 4000
    ) -> dict:
        """Use Anthropic's tool-use as structured output.

        Defines a tool with the desired JSON schema, forces the model to
        "call" it via tool_choice, and extracts the tool input as the
        structured response. This is Anthropic's recommended approach for
        structured output — no regex, no fallbacks needed.

        See: https://platform.claude.com/docs/en/build-with-claude/structured-outputs
        """
        tool_name = "structured_output"
        tools = [{
            "name": tool_name,
            "description": "Return the structured response matching the required schema.",
            "input_schema": schema,
        }]

        kwargs: dict = {
            "model": self.model,
            "max_tokens": max_tokens,
            "system": system,
            "messages": [{"role": "user", "content": user}],
            "tools": tools,
            "tool_choice": {"type": "tool", "name": tool_name},
        }

        # NOTE: Anthropic does NOT support thinking with tool_choice forced.
        # "Thinking may not be enabled when tool_choice forces tool use."
        # So we intentionally skip _apply_thinking here. The model still
        # reasons internally; it just doesn't get extended thinking budget.

        resp = self._client.messages.create(**kwargs)

        # Extract the tool input from the response
        for block in resp.content:
            if block.type == "tool_use" and block.name == tool_name:
                return block.input  # already a dict

        # No tool_use block — this shouldn't happen with tool_choice forced
        content_types = [b.type for b in resp.content]
        logger.error(
            "Anthropic tool-use returned no tool_use block. Content types: %s",
            content_types,
        )
        raise ValueError(
            f"Anthropic tool-use structured output failed. "
            f"No tool_use block in response. Content types: {content_types}"
        )

    # ── Pydantic-native structured call (supports thinking) ──────────

    def _call_parsed_impl(
        self,
        system: str,
        user: str,
        model_class: type["BaseModel"],
        max_tokens: int = 4000,
    ) -> dict:
        """Use Anthropic's ``messages.parse(output_format=...)`` for structured output.

        Unlike ``_call_structured_impl`` (tool_choice), this approach is
        compatible with extended thinking. The API returns a ``parsed_output``
        attribute with the validated Pydantic model.
        """
        kwargs: dict = {
            "model": self.model,
            "max_tokens": max_tokens,
            "system": system,
            "messages": [{"role": "user", "content": user}],
            "output_format": model_class,
        }

        # Apply thinking — this is supported with messages.parse()
        self._apply_thinking(kwargs, max_tokens)

        resp = self._client.messages.parse(**kwargs)

        if resp.parsed_output is not None:
            return resp.parsed_output.model_dump()

        # Fallback: extract text and parse manually
        import json
        text = "\n".join(
            b.text for b in resp.content if b.type == "text"
        ).strip()
        if text:
            from arbiter.providers.base import strip_markdown_fences
            return json.loads(strip_markdown_fences(text))

        # If only thinking blocks returned, the model spent all output tokens
        # on reasoning with nothing left for the response. Log and raise with
        # actionable message so the retry loop can try again.
        content_types = [b.type for b in resp.content]
        if content_types == ["thinking"]:
            logger.warning(
                "Anthropic exhausted output budget on thinking (%d tokens). "
                "Increase max_tokens or lower thinking effort.",
                kwargs.get("max_tokens", 0),
            )
        raise ValueError(
            f"Anthropic messages.parse returned no parsed_output and no text. "
            f"Content types: {content_types}. "
            f"Try increasing max_tokens (was {kwargs.get('max_tokens', '?')})."
        )


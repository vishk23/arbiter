"""Anthropic (Claude) provider."""

from __future__ import annotations

import logging
import os



from arbiter.config import ProviderConfig
from arbiter.providers.base import BaseProvider

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

    # ── plain text call ───────────────────────────────────────────────

    def _call_impl(self, system: str, user: str, max_tokens: int = 4000) -> str:
        kwargs: dict = dict(
            model=self.model,
            max_tokens=max_tokens,
            system=system,
            messages=[{"role": "user", "content": user}],
        )

        # Extended thinking support
        # - adaptive: model decides how much to think (no budget_tokens)
        # - enabled: explicit budget_tokens allocation
        if self.config.thinking:
            thinking_type = self.config.thinking.get("type", "adaptive")
            if thinking_type == "adaptive":
                kwargs["thinking"] = {"type": "adaptive"}
                overhead = self.config.thinking.get("overhead", 16000)
                kwargs["max_tokens"] = max_tokens + overhead
            else:
                budget = self.config.thinking.get("budget_tokens", 10000)
                kwargs["thinking"] = {"type": thinking_type, "budget_tokens": budget}
                kwargs["max_tokens"] = max_tokens + budget

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


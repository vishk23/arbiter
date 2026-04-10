"""Anthropic (Claude) provider."""

from __future__ import annotations

import json
import logging
import os
import re



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
        if self.config.thinking:
            thinking_type = self.config.thinking.get("type", "adaptive")
            if thinking_type == "adaptive":
                # Adaptive thinking: no budget_tokens, model decides
                kwargs["thinking"] = {"type": "adaptive"}
                kwargs["max_tokens"] = max_tokens + 16000  # room for thinking
            else:
                # Explicit budget (legacy "enabled" mode)
                budget = self.config.thinking.get("budget_tokens", 8000)
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
        augmented_system = (
            f"{system}\n\nYou MUST respond with valid JSON matching this schema.\n"
            f"Output ONLY the JSON object, no prose before or after.\n\n"
            f"```json\n{json.dumps(schema, indent=2)}\n```"
        )
        raw = self._call_impl(augmented_system, user, max_tokens)

        # Try standard extraction (fenced block, then raw braces)
        parsed = self._extract_json(raw)
        if parsed is not None:
            return parsed

        # Try aggressive extraction (multiple attempts)
        parsed = self._extract_json_aggressive(raw)
        if parsed is not None:
            logger.info("Recovered JSON via aggressive regex extraction")
            return parsed

        # No hidden OpenAI dependency — fail with a clear error.
        # For structured output, prefer routing to OpenAI/Gemini providers
        # which have native JSON schema enforcement.
        raise ValueError(
            "Anthropic returned non-JSON. For reliable structured output, "
            "route structured calls to a provider with native JSON schema "
            "support (openai, gemini). Raw response (first 500 chars):\n"
            + raw[:500]
        )

    # ── helpers ───────────────────────────────────────────────────────

    @staticmethod
    def _extract_json(text: str) -> dict | None:
        """Try to pull a JSON object out of *text*."""
        # Try fenced code block first
        m = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
        if m:
            try:
                return json.loads(m.group(1))
            except json.JSONDecodeError:
                pass
        # Try raw braces
        m = re.search(r"\{.*\}", text, re.DOTALL)
        if m:
            try:
                return json.loads(m.group(0))
            except json.JSONDecodeError:
                pass
        return None

    @staticmethod
    def _extract_json_aggressive(text: str) -> dict | None:
        """Harder regex attempts: strip markdown, find outermost braces."""
        # Strip common markdown wrapping
        cleaned = re.sub(r"^```\w*\n?", "", text.strip(), flags=re.MULTILINE)
        cleaned = re.sub(r"\n?```\s*$", "", cleaned.strip(), flags=re.MULTILINE)

        # Find the outermost { ... } by tracking brace depth
        start = cleaned.find("{")
        if start == -1:
            return None
        depth = 0
        for i in range(start, len(cleaned)):
            if cleaned[i] == "{":
                depth += 1
            elif cleaned[i] == "}":
                depth -= 1
                if depth == 0:
                    try:
                        return json.loads(cleaned[start : i + 1])
                    except json.JSONDecodeError:
                        break
        return None


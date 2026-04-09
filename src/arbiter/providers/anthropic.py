"""Anthropic (Claude) provider."""

from __future__ import annotations

import json
import logging
import os
import re

from dotenv import load_dotenv

load_dotenv()

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

    def call(self, system: str, user: str, max_tokens: int = 4000) -> str:
        kwargs: dict = dict(
            model=self.model,
            max_tokens=max_tokens,
            system=system,
            messages=[{"role": "user", "content": user}],
        )

        # Extended thinking support
        if self.config.thinking:
            budget = self.config.thinking.get("budget_tokens", 8000)
            kwargs["thinking"] = {"type": "enabled", "budget_tokens": budget}
            kwargs["max_tokens"] = max_tokens + budget

        resp = self._client.messages.create(**kwargs)
        text = "\n".join(
            b.text for b in resp.content if b.type == "text"
        ).strip()
        return text

    # ── structured (JSON) call ────────────────────────────────────────

    def call_structured(
        self, system: str, user: str, schema: dict, max_tokens: int = 4000
    ) -> dict:
        augmented_system = (
            f"{system}\n\nYou MUST respond with valid JSON matching this schema:\n"
            f"```json\n{json.dumps(schema, indent=2)}\n```"
        )
        raw = self.call(augmented_system, user, max_tokens)

        # Try to extract JSON from the response
        parsed = self._extract_json(raw)
        if parsed is not None:
            return parsed

        # Fallback: ask OpenAI to reformat
        logger.warning("Anthropic JSON extraction failed; falling back to OpenAI reformat")
        return self._openai_reformat(raw, schema)

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
    def _openai_reformat(raw: str, schema: dict) -> dict:
        """Use OpenAI to coerce *raw* into the desired JSON schema."""
        import openai

        client = openai.OpenAI(timeout=60)
        resp = client.responses.create(
            model="gpt-4.1-nano",
            input=[
                {
                    "role": "system",
                    "content": (
                        "Reformat the following text into valid JSON matching "
                        "the provided schema. Output ONLY the JSON object."
                    ),
                },
                {
                    "role": "user",
                    "content": (
                        f"Schema:\n{json.dumps(schema, indent=2)}\n\n"
                        f"Text:\n{raw}"
                    ),
                },
            ],
            text={"format": {"type": "json_schema", "name": "reformat", "schema": schema}},
        )
        return json.loads(resp.output_text)

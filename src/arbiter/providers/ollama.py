"""Ollama (local LLM) provider."""

from __future__ import annotations

import json
import logging
import re

from arbiter.config import ProviderConfig
from arbiter.providers.base import BaseProvider

logger = logging.getLogger(__name__)


class OllamaProvider(BaseProvider):
    """Provider backed by a local Ollama instance."""

    def _init_client(self, config: ProviderConfig) -> None:
        try:
            import ollama
        except ImportError:
            raise ImportError(
                "The 'ollama' package is required for the Ollama provider. "
                "Install it with: pip install ollama"
            ) from None

        host = config.base_url or "http://localhost:11434"
        self._client = ollama.Client(host=host)

    # ── plain text call ───────────────────────────────────────────────

    def _call_impl(self, system: str, user: str, max_tokens: int = 4000) -> str:
        resp = self._client.chat(
            model=self.model,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            options={"num_predict": max_tokens},
        )
        return (resp.message.content or "").strip()

    # ── structured (JSON) call ────────────────────────────────────────

    def _call_structured_impl(
        self, system: str, user: str, schema: dict, max_tokens: int = 4000
    ) -> dict:
        augmented_system = (
            f"{system}\n\nYou MUST respond with valid JSON matching this schema:\n"
            f"```json\n{json.dumps(schema, indent=2)}\n```\n"
            "Output ONLY the JSON object, no other text."
        )
        raw = self._call_impl(augmented_system, user, max_tokens)

        # Try to parse JSON
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            pass

        # Try extracting from fenced block
        m = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", raw, re.DOTALL)
        if m:
            try:
                return json.loads(m.group(1))
            except json.JSONDecodeError:
                pass

        # Try raw braces
        m = re.search(r"\{.*\}", raw, re.DOTALL)
        if m:
            try:
                return json.loads(m.group(0))
            except json.JSONDecodeError:
                pass

        raise ValueError(
            f"Ollama response could not be parsed as JSON. Raw response:\n{raw[:500]}"
        )

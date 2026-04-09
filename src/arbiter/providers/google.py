"""Google Gemini provider."""

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


class GoogleProvider(BaseProvider):
    """Provider backed by the Google GenAI SDK (Gemini)."""

    def _init_client(self, config: ProviderConfig) -> None:
        from google import genai

        api_key = config.api_key or os.environ.get("GEMINI_API_KEY")
        if not api_key:
            raise ValueError(
                "Gemini API key not found. Set 'api_key' in provider config "
                "or the GEMINI_API_KEY environment variable."
            )

        self._client = genai.Client(api_key=api_key)

    # ── plain text call ───────────────────────────────────────────────

    def _call_impl(self, system: str, user: str, max_tokens: int = 4000) -> str:
        from google.genai import types as gtypes

        config_kwargs: dict = dict(
            system_instruction=system,
            max_output_tokens=max_tokens,
        )

        # Thinking support
        if self.config.thinking:
            level = self.config.thinking.get("thinking_level", "HIGH")
            config_kwargs["thinking_config"] = gtypes.ThinkingConfig(
                thinking_level=level
            )
            config_kwargs["max_output_tokens"] = max_tokens + 4000

        resp = self._client.models.generate_content(
            model=self.model,
            contents=user,
            config=gtypes.GenerateContentConfig(**config_kwargs),
        )
        return (resp.text or "").strip()

    # ── structured (JSON) call ────────────────────────────────────────

    def _call_structured_impl(
        self, system: str, user: str, schema: dict, max_tokens: int = 4000
    ) -> dict:
        from google.genai import types as gtypes

        config_kwargs: dict = dict(
            system_instruction=system,
            max_output_tokens=max_tokens,
            response_mime_type="application/json",
            response_schema=schema,
        )

        if self.config.thinking:
            level = self.config.thinking.get("thinking_level", "HIGH")
            config_kwargs["thinking_config"] = gtypes.ThinkingConfig(
                thinking_level=level
            )
            config_kwargs["max_output_tokens"] = max_tokens + 4000

        resp = self._client.models.generate_content(
            model=self.model,
            contents=user,
            config=gtypes.GenerateContentConfig(**config_kwargs),
        )
        text = (resp.text or "").strip()

        # Parse JSON from response
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            # Try extracting from fenced block
            m = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
            if m:
                return json.loads(m.group(1))
            m = re.search(r"\{.*\}", text, re.DOTALL)
            if m:
                return json.loads(m.group(0))
            raise

"""Google Gemini provider."""

from __future__ import annotations

import json
import logging
import os
from typing import TYPE_CHECKING

from arbiter.config import ProviderConfig
from arbiter.providers.base import BaseProvider

if TYPE_CHECKING:
    from pydantic import BaseModel

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

        # Parse JSON — response_mime_type guarantees valid JSON
        return json.loads(text)

    # ── Pydantic-native structured call ──────────────────────────────

    def _call_parsed_impl(
        self,
        system: str,
        user: str,
        model_class: type[BaseModel],
        max_tokens: int = 4000,
    ) -> dict:
        from google.genai import types as gtypes

        config_kwargs: dict = dict(
            system_instruction=system,
            max_output_tokens=max_tokens,
            response_mime_type="application/json",
            response_schema=model_class,
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

        # Try native parsed output first
        parsed = getattr(resp, "parsed", None)
        if parsed is not None:
            return parsed.model_dump()

        # Fallback: parse JSON text (response_schema guarantees JSON)
        text = (resp.text or "").strip()
        return json.loads(text)

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

    def _build_thinking_config(self, overhead: int) -> tuple[dict, int]:
        """Build Gemini thinking config and return (config_kwargs, extra_tokens).

        Gemini 2.5 uses ``thinking_budget`` (int, min 128 for pro).
        Gemini 3.x uses ``thinking_level`` (MINIMAL/LOW/MEDIUM/HIGH enum).
        """
        from google.genai import types as gtypes

        if not self.config.thinking:
            return {}, 0

        is_3x = "gemini-3" in self.model

        if is_3x:
            # Gemini 3.x: use thinking_level enum
            level_str = self.config.thinking.get("thinking_level", "HIGH")
            level_map = {
                "MINIMAL": gtypes.ThinkingLevel.MINIMAL,
                "LOW": gtypes.ThinkingLevel.LOW,
                "MEDIUM": gtypes.ThinkingLevel.MEDIUM,
                "HIGH": gtypes.ThinkingLevel.HIGH,
            }
            level = level_map.get(level_str.upper(), gtypes.ThinkingLevel.HIGH)
            return {"thinking_config": gtypes.ThinkingConfig(thinking_level=level)}, overhead
        else:
            # Gemini 2.5: use thinking_budget (int tokens)
            budget = self.config.thinking.get("thinking_budget", overhead)
            return {"thinking_config": gtypes.ThinkingConfig(thinking_budget=budget)}, budget

    # ── plain text call ───────────────────────────────────────────────

    def _call_impl(self, system: str, user: str, max_tokens: int = 4000) -> str:
        from google.genai import types as gtypes

        config_kwargs: dict = dict(
            system_instruction=system,
            max_output_tokens=max_tokens,
        )

        thinking_kwargs, extra = self._build_thinking_config(overhead=4000)
        config_kwargs.update(thinking_kwargs)
        if extra:
            config_kwargs["max_output_tokens"] = max_tokens + extra

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

        thinking_kwargs, extra = self._build_thinking_config(overhead=4000)
        config_kwargs.update(thinking_kwargs)
        if extra:
            config_kwargs["max_output_tokens"] = max_tokens + extra

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

        thinking_kwargs, extra = self._build_thinking_config(overhead=4000)
        config_kwargs.update(thinking_kwargs)
        if extra:
            config_kwargs["max_output_tokens"] = max_tokens + extra

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

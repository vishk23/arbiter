"""OpenAI provider."""

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


class OpenAIProvider(BaseProvider):
    """Provider backed by the OpenAI Responses API."""

    def _init_client(self, config: ProviderConfig) -> None:
        import openai

        api_key = config.api_key or os.environ.get("OPENAI_API_KEY")
        if not api_key:
            raise ValueError(
                "OpenAI API key not found. Set 'api_key' in provider config "
                "or the OPENAI_API_KEY environment variable."
            )

        kwargs: dict = {"api_key": api_key, "timeout": config.timeout}
        if config.base_url:
            kwargs["base_url"] = config.base_url

        self._client = openai.OpenAI(**kwargs)

    # ── plain text call ───────────────────────────────────────────────

    def _call_impl(self, system: str, user: str, max_tokens: int = 4000) -> str:
        kwargs: dict = dict(
            model=self.model,
            input=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            max_output_tokens=max_tokens,
        )

        # Reasoning effort: none/minimal/low/medium/high/xhigh
        # gpt-5.4 defaults to "none"; older gpt-5.x default to "medium"
        if self.config.reasoning:
            effort = self.config.reasoning.get("effort", "medium")
            kwargs["reasoning"] = {"effort": effort}
            overhead = self.config.reasoning.get("overhead", 8000)
            kwargs["max_output_tokens"] = max_tokens + overhead

        resp = self._client.responses.create(**kwargs)
        return (resp.output_text or "").strip()

    def _apply_reasoning(self, kwargs: dict, max_tokens: int) -> None:
        """Apply reasoning config to request kwargs (shared by all call methods)."""
        if self.config.reasoning:
            effort = self.config.reasoning.get("effort", "medium")
            kwargs["reasoning"] = {"effort": effort}
            overhead = self.config.reasoning.get("overhead", 8000)
            kwargs["max_output_tokens"] = max_tokens + overhead

    # ── structured (JSON) call ────────────────────────────────────────

    @staticmethod
    def _add_additional_properties_false(schema: dict) -> dict:
        """OpenAI strict mode requires additionalProperties: false on every object."""
        if not isinstance(schema, dict):
            return schema
        if schema.get("type") == "object":
            schema["additionalProperties"] = False
            if "required" not in schema:
                schema["required"] = list(schema.get("properties", {}).keys())
        for v in schema.values():
            if isinstance(v, dict):
                OpenAIProvider._add_additional_properties_false(v)
            elif isinstance(v, list):
                for item in v:
                    if isinstance(item, dict):
                        OpenAIProvider._add_additional_properties_false(item)
        return schema

    def _call_structured_impl(
        self, system: str, user: str, schema: dict, max_tokens: int = 4000
    ) -> dict:
        import copy
        strict_schema = self._add_additional_properties_false(copy.deepcopy(schema))

        kwargs: dict = dict(
            model=self.model,
            input=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            max_output_tokens=max_tokens,
            text={
                "format": {
                    "type": "json_schema",
                    "name": "structured_output",
                    "schema": strict_schema,
                    "strict": True,
                }
            },
        )

        self._apply_reasoning(kwargs, max_tokens)

        resp = self._client.responses.create(**kwargs)
        return json.loads(resp.output_text)

    # ── Pydantic-native structured call ──────────────────────────────

    def _call_parsed_impl(
        self,
        system: str,
        user: str,
        model_class: type[BaseModel],
        max_tokens: int = 4000,
    ) -> dict:
        kwargs: dict = dict(
            model=self.model,
            input=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            max_output_tokens=max_tokens,
            text_format=model_class,
        )

        self._apply_reasoning(kwargs, max_tokens)

        resp = self._client.responses.parse(**kwargs)
        if resp.output_parsed is not None:
            return resp.output_parsed.model_dump()
        # Fallback: parse the raw text
        return json.loads(resp.output_text)

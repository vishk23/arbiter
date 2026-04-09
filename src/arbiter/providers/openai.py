"""OpenAI provider."""

from __future__ import annotations

import json
import logging
import os

from dotenv import load_dotenv

load_dotenv()

from arbiter.config import ProviderConfig
from arbiter.providers.base import BaseProvider

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

    def call(self, system: str, user: str, max_tokens: int = 4000) -> str:
        kwargs: dict = dict(
            model=self.model,
            input=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            max_output_tokens=max_tokens,
        )

        # Reasoning effort support (for o-series models)
        if self.config.reasoning:
            effort = self.config.reasoning.get("effort", "medium")
            kwargs["reasoning"] = {"effort": effort}
            # Give extra room for reasoning overhead
            kwargs["max_output_tokens"] = max_tokens + 4000

        resp = self._client.responses.create(**kwargs)
        return (resp.output_text or "").strip()

    # ── structured (JSON) call ────────────────────────────────────────

    def call_structured(
        self, system: str, user: str, schema: dict, max_tokens: int = 4000
    ) -> dict:
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
                    "schema": schema,
                }
            },
        )

        if self.config.reasoning:
            effort = self.config.reasoning.get("effort", "medium")
            kwargs["reasoning"] = {"effort": effort}
            kwargs["max_output_tokens"] = max_tokens + 4000

        resp = self._client.responses.create(**kwargs)
        return json.loads(resp.output_text)

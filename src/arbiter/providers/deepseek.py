"""DeepSeek provider — OpenAI-compatible chat completions at api.deepseek.com.

Models:
  deepseek-chat       DeepSeek-V3.2 non-thinking ($0.28/$0.42 per MTok)
  deepseek-reasoner   DeepSeek-V3.2 thinking mode ($0.28/$0.42 per MTok)

Note: DeepSeek supports chat.completions (not OpenAI's responses API),
so this provider overrides _call_impl to use the completions endpoint.
"""

from __future__ import annotations

import json
import os

from arbiter.config import ProviderConfig
from arbiter.providers.base import BaseProvider, strip_markdown_fences

_DEFAULT_BASE_URL = "https://api.deepseek.com"


class DeepSeekProvider(BaseProvider):
    """DeepSeek provider.

    Uses the OpenAI SDK's ``chat.completions`` endpoint (not ``responses``)
    with ``base_url=https://api.deepseek.com``.

    Usage in config::

        providers:
          deepseek:
            model: deepseek-reasoner
          deepseek-fast:
            model: deepseek-chat
    """

    def _init_client(self, config: ProviderConfig) -> None:
        import openai

        api_key = config.api_key or os.environ.get("DEEPSEEK_API_KEY")
        if not api_key:
            raise ValueError(
                "DeepSeek API key not found. Set 'api_key' in provider config "
                "or the DEEPSEEK_API_KEY environment variable."
            )

        base_url = config.base_url or _DEFAULT_BASE_URL
        self._client = openai.OpenAI(
            api_key=api_key,
            base_url=base_url,
            timeout=config.timeout,
        )

    def _call_impl(self, system: str, user: str, max_tokens: int = 4000) -> str:
        resp = self._client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            max_tokens=max_tokens,
        )
        return (resp.choices[0].message.content or "").strip()

    def _call_structured_impl(
        self, system: str, user: str, schema: dict, max_tokens: int = 4000
    ) -> dict:
        augmented_system = (
            f"{system}\n\nYou MUST respond with valid JSON matching this schema:\n"
            f"```json\n{json.dumps(schema, indent=2)}\n```"
        )
        resp = self._client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": augmented_system},
                {"role": "user", "content": user},
            ],
            max_tokens=max_tokens,
            response_format={"type": "json_object"},
        )
        raw = (resp.choices[0].message.content or "").strip()
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            # Models may wrap JSON in markdown fences; strip and retry
            stripped = strip_markdown_fences(raw)
            try:
                return json.loads(stripped)
            except json.JSONDecodeError as exc:
                raise ValueError(
                    f"DeepSeek returned invalid JSON despite json_object mode: "
                    f"{raw[:300]}"
                ) from exc

"""xAI Grok provider — OpenAI-compatible API at api.x.ai."""

from __future__ import annotations

import os

from arbiter.config import ProviderConfig
from arbiter.providers.openai import OpenAIProvider

_DEFAULT_BASE_URL = "https://api.x.ai/v1"


class GrokProvider(OpenAIProvider):
    """xAI Grok provider.

    Uses the OpenAI SDK with ``base_url=https://api.x.ai/v1``.
    API key from ``config.api_key`` or ``XAI_API_KEY`` env var.

    Usage in config::

        providers:
          grok:
            model: grok-4.20-0309-reasoning
    """

    def _init_client(self, config: ProviderConfig) -> None:
        import openai

        api_key = config.api_key or os.environ.get("XAI_API_KEY")
        if not api_key:
            raise ValueError(
                "xAI API key not found. Set 'api_key' in provider config "
                "or the XAI_API_KEY environment variable."
            )

        base_url = config.base_url or _DEFAULT_BASE_URL
        self._client = openai.OpenAI(
            api_key=api_key,
            base_url=base_url,
            timeout=config.timeout,
        )

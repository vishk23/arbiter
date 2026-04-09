"""Provider registry -- lazy-load vendor SDKs on first use."""

from __future__ import annotations

import importlib
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from arbiter.config import ProviderConfig
    from arbiter.providers.base import BaseProvider

PROVIDER_REGISTRY: dict[str, str] = {
    "anthropic": "arbiter.providers.anthropic:AnthropicProvider",
    "openai": "arbiter.providers.openai:OpenAIProvider",
    "google": "arbiter.providers.google:GoogleProvider",
    "gemini": "arbiter.providers.google:GoogleProvider",  # alias
    "ollama": "arbiter.providers.ollama:OllamaProvider",
}


def get_provider(name: str, config: "ProviderConfig") -> "BaseProvider":
    """Resolve *name* to a provider class, instantiate it with *config*.

    Raises ``KeyError`` for unknown provider names.
    """
    entry = PROVIDER_REGISTRY.get(name)
    if entry is None:
        raise KeyError(
            f"Unknown provider '{name}'. "
            f"Available: {', '.join(sorted(PROVIDER_REGISTRY))}"
        )

    module_path, class_name = entry.rsplit(":", 1)
    module = importlib.import_module(module_path)
    cls = getattr(module, class_name)
    return cls(config)

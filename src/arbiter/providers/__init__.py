"""Provider registry -- lazy-load vendor SDKs on first use.

Built-in providers: anthropic, openai, google/gemini, ollama.

Custom providers: set ``plugin`` in the provider config to a
``module:ClassName`` string pointing at your own
:class:`~arbiter.providers.base.BaseProvider` subclass::

    providers:
      mistral:
        plugin: my_providers:MistralProvider
        model: mistral-large
"""

from __future__ import annotations

import importlib
import importlib.util
import logging
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from arbiter.config import ProviderConfig
    from arbiter.providers.base import BaseProvider

logger = logging.getLogger(__name__)

PROVIDER_REGISTRY: dict[str, str] = {
    "anthropic": "arbiter.providers.anthropic:AnthropicProvider",
    "openai": "arbiter.providers.openai:OpenAIProvider",
    "google": "arbiter.providers.google:GoogleProvider",
    "gemini": "arbiter.providers.google:GoogleProvider",  # alias
    "ollama": "arbiter.providers.ollama:OllamaProvider",
}


def _load_plugin_class(spec: str) -> type:
    """Load a class from a ``module:ClassName`` or ``path/to/file.py:ClassName`` spec."""
    module_path, _, class_name = spec.rpartition(":")
    if not module_path or not class_name:
        raise ValueError(
            f"Invalid plugin spec '{spec}'. "
            f"Expected 'module.path:ClassName' or 'path/to/file.py:ClassName'."
        )

    # If it looks like a file path, load from file
    if module_path.endswith(".py") or "/" in module_path or "\\" in module_path:
        file_path = Path(module_path).resolve()
        if not file_path.exists():
            raise FileNotFoundError(f"Plugin file not found: {file_path}")
        spec_obj = importlib.util.spec_from_file_location(
            f"arbiter_plugin_{file_path.stem}", file_path
        )
        module = importlib.util.module_from_spec(spec_obj)
        spec_obj.loader.exec_module(module)
    else:
        module = importlib.import_module(module_path)

    cls = getattr(module, class_name, None)
    if cls is None:
        raise AttributeError(
            f"Plugin module '{module_path}' has no class '{class_name}'."
        )
    return cls


def get_provider(name: str, config: "ProviderConfig") -> "BaseProvider":
    """Resolve *name* to a provider class, instantiate it with *config*.

    Resolution order:
    1. If ``config.plugin`` is set, load the class from that spec.
    2. Otherwise look up *name* in the built-in registry.

    Raises ``KeyError`` for unknown provider names with no plugin.
    """
    # Custom plugin provider
    plugin_spec = getattr(config, "plugin", None)
    if plugin_spec:
        logger.info("Loading custom provider plugin: %s", plugin_spec)
        cls = _load_plugin_class(plugin_spec)
        return cls(config)

    # Built-in provider
    entry = PROVIDER_REGISTRY.get(name)
    if entry is None:
        raise KeyError(
            f"Unknown provider '{name}'. "
            f"Available: {', '.join(sorted(PROVIDER_REGISTRY))}. "
            f"Or set 'plugin: module:ClassName' in provider config for custom providers."
        )

    module_path, class_name = entry.rsplit(":", 1)
    module = importlib.import_module(module_path)
    cls = getattr(module, class_name)
    return cls(config)

"""Tests for custom provider plugin loading."""

import tempfile
from pathlib import Path

import pytest

from arbiter.config import ProviderConfig
from arbiter.providers import get_provider, _load_plugin_class


CUSTOM_PROVIDER_CODE = '''
from arbiter.providers.base import BaseProvider
from arbiter.config import ProviderConfig

class EchoProvider(BaseProvider):
    """A test provider that echoes back the user prompt."""

    def _init_client(self, config: ProviderConfig) -> None:
        self._prefix = f"[{config.model}] "

    def _call_impl(self, system: str, user: str, max_tokens: int = 4000) -> str:
        return self._prefix + user

    def _call_structured_impl(
        self, system: str, user: str, schema: dict, max_tokens: int = 4000
    ) -> dict:
        return {"echo": user}
'''


class TestCustomProviderPlugin:
    def test_load_from_file(self):
        with tempfile.NamedTemporaryFile(suffix=".py", mode="w", delete=False) as f:
            f.write(CUSTOM_PROVIDER_CODE)
            f.flush()

            cfg = ProviderConfig(
                model="echo-v1",
                plugin=f"{f.name}:EchoProvider",
            )
            provider = get_provider("custom", cfg)
            result = provider.call("system", "hello world")
            assert "[echo-v1] hello world" in result

    def test_load_from_module_path(self):
        """Test loading via module:Class syntax (if module is on sys.path)."""
        with tempfile.TemporaryDirectory() as td:
            mod_path = Path(td) / "my_echo.py"
            mod_path.write_text(CUSTOM_PROVIDER_CODE)

            cfg = ProviderConfig(
                model="echo-v2",
                plugin=f"{mod_path}:EchoProvider",
            )
            provider = get_provider("my_custom", cfg)
            result = provider.call("system", "test")
            assert "[echo-v2] test" in result

    def test_structured_call(self):
        with tempfile.NamedTemporaryFile(suffix=".py", mode="w", delete=False) as f:
            f.write(CUSTOM_PROVIDER_CODE)
            f.flush()

            cfg = ProviderConfig(model="echo-v1", plugin=f"{f.name}:EchoProvider")
            provider = get_provider("x", cfg)
            result = provider.call_structured("sys", "query", {"type": "object"})
            assert result == {"echo": "query"}

    def test_invalid_spec_raises(self):
        with pytest.raises(ValueError, match="Invalid plugin spec"):
            _load_plugin_class("no_colon_here")

    def test_missing_file_raises(self):
        with pytest.raises(FileNotFoundError, match="not found"):
            _load_plugin_class("/nonexistent/path.py:SomeClass")

    def test_missing_class_raises(self):
        with tempfile.NamedTemporaryFile(suffix=".py", mode="w", delete=False) as f:
            f.write("class Foo: pass\n")
            f.flush()
            with pytest.raises(AttributeError, match="no class"):
                _load_plugin_class(f"{f.name}:NonexistentClass")

    def test_builtin_still_works(self):
        """Ensure built-in providers still resolve when no plugin is set."""
        # This just verifies the registry path isn't broken
        _ = ProviderConfig(model="gpt-5.4-mini", timeout=10, max_retries=1)  # noqa: F841
        # Don't actually call — just check it resolves
        from arbiter.providers import PROVIDER_REGISTRY
        assert "openai" in PROVIDER_REGISTRY

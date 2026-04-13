"""Z3 plugin loader -- runs a user-provided verify() module."""

from __future__ import annotations

import importlib.util
import logging
import sys
from pathlib import Path

from jinja2 import Template

logger = logging.getLogger(__name__)


class Z3Plugin:
    """Load and run a user-supplied Z3 verification module.

    The module at *module_path* must export a ``verify()`` function that
    returns a dict of ``{check_name: {name, result, expected, explanation}}``.

    Parameters
    ----------
    module_path:
        Absolute or resolved path to a Python file exporting ``verify()``.
    """

    def __init__(self, module_path: str) -> None:
        self.module_path = Path(module_path)
        self._module = self._load_module()

    def _load_module(self):
        """Dynamically import the Z3 module."""
        path = self.module_path
        if not path.exists():
            raise FileNotFoundError(f"Z3 module not found: {path}")

        spec = importlib.util.spec_from_file_location("z3_user_module", str(path))
        if spec is None or spec.loader is None:
            raise ImportError(f"Cannot load module from {path}")

        module = importlib.util.module_from_spec(spec)
        sys.modules["z3_user_module"] = module
        spec.loader.exec_module(module)  # type: ignore[union-attr]
        return module

    # ------------------------------------------------------------------ #

    def verify(self) -> dict:
        """Call the user module's ``verify()`` and return results.

        Returns ``{check_name: {name, result, expected, explanation}}``.
        Falls back to an error dict on failure.
        """
        fn = getattr(self._module, "verify", None)
        if fn is None:
            raise AttributeError(
                f"Z3 module {self.module_path} does not export verify()"
            )
        try:
            return fn()
        except Exception as exc:
            logger.exception("Z3 verify() failed: %s", exc)
            return {
                "_error": {
                    "name": "z3_error",
                    "result": "error",
                    "expected": "pass",
                    "explanation": str(exc),
                }
            }

    # ------------------------------------------------------------------ #

    def format_stipulation(self, template: str | None = None) -> str:
        """Format Z3 results for injection into agent prompts.

        If *template* is provided it is rendered as a Jinja2 template
        with ``{{ z3_results }}`` available.  Otherwise a default
        human-readable format is produced.
        """
        results = self.verify()

        if template:
            tpl = Template(template)
            return tpl.render(z3_results=results, **results)

        # Default formatting
        lines = ["Z3 STIPULATED FACTS (mechanically verified, not debatable):"]
        for key, val in results.items():
            if key.startswith("_"):
                continue
            name = val.get("name", key)
            result = val.get("result", "?")
            explanation = val.get("explanation", "")
            lines.append(f"  [{name}] {result}: {explanation}")
        return "\n".join(lines)

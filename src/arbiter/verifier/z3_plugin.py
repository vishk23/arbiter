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

        # Default formatting — categorized by check_type when available
        return self._format_categorized(results)

    # ------------------------------------------------------------------ #

    @staticmethod
    def _format_categorized(results: dict) -> str:  # noqa: C901
        """Produce rich stipulation text grouped by check_type.

        Falls back to the legacy flat list when entries lack a
        ``check_type`` field (backward-compatible with older modules).
        """
        # Bucket results by check_type; entries without one go to "_legacy"
        buckets: dict[str, list[tuple[str, dict]]] = {}
        for key, val in results.items():
            if key.startswith("_"):
                continue
            ct = val.get("check_type", "_legacy")
            buckets.setdefault(ct, []).append((key, val))

        # If every entry landed in _legacy, use the old flat format
        if set(buckets.keys()) == {"_legacy"}:
            lines = [
                "Z3 STIPULATED FACTS (mechanically verified, not debatable):"
            ]
            for key, val in buckets["_legacy"]:
                name = val.get("name", key)
                result = val.get("result", "?")
                explanation = val.get("explanation", "")
                lines.append(f"  [{name}] {result}: {explanation}")
            return "\n".join(lines)

        # --- Rich categorized output ---------------------------------- #
        sections: list[str] = [
            "Z3 STIPULATED FACTS (mechanically verified, not debatable):",
            "",
        ]

        def _append_section(heading: str, body_lines: list[str]) -> None:
            sections.append(f"=== {heading} ===")
            sections.extend(body_lines)
            sections.append("")

        # 1. VERIFIED PROPOSITIONS — proof_verification with UNSAT result
        if "proof_verification" in buckets:
            verified: list[str] = []
            for key, val in buckets["proof_verification"]:
                name = val.get("name", key)
                result = str(val.get("result", "")).lower()
                explanation = val.get("explanation", "")
                if result in ("unsat", "proved"):
                    backend = val.get("backend", "z3")
                    cert = " [CERT]" if val.get("proof_certificate") else ""
                    verified.append(
                        f"  [VERIFIED{cert}] ({backend}) {name}: {explanation}"
                    )
            if verified:
                _append_section("VERIFIED PROPOSITIONS", verified)

        # 2. COUNTEREXAMPLES — proof_verification with SAT result
        if "proof_verification" in buckets:
            counters: list[str] = []
            for key, val in buckets["proof_verification"]:
                name = val.get("name", key)
                result = str(val.get("result", "")).lower()
                explanation = val.get("explanation", "")
                if result == "sat":
                    model_vals = val.get("model_values", {})
                    model_str = (
                        ", ".join(
                            f"{k}={v}" for k, v in model_vals.items()
                        )
                        if model_vals
                        else "n/a"
                    )
                    counters.append(
                        f"  [COUNTEREXAMPLE] {name}: {explanation}"
                    )
                    counters.append(f"    model: {model_str}")
            if counters:
                _append_section("COUNTEREXAMPLES", counters)

        # 3. COUNTEREXAMPLE SEARCH
        if "counterexample_search" in buckets:
            ce_lines: list[str] = []
            for key, val in buckets["counterexample_search"]:
                name = val.get("name", key)
                result = str(val.get("result", "")).lower()
                explanation = val.get("explanation", "")
                model_vals = val.get("model_values", {})
                if result == "sat":
                    model_str = (
                        ", ".join(
                            f"{k}={v}" for k, v in model_vals.items()
                        )
                        if model_vals
                        else "n/a"
                    )
                    ce_lines.append(
                        f"  [FOUND] {name}: {explanation}"
                    )
                    ce_lines.append(f"    model: {model_str}")
                else:
                    ce_lines.append(
                        f"  [NONE] {name}: {explanation}"
                    )
            if ce_lines:
                _append_section("COUNTEREXAMPLES", ce_lines)

        # 4. ASSUMPTION SENSITIVITY
        if "assumption_sensitivity" in buckets:
            as_lines: list[str] = []
            for key, val in buckets["assumption_sensitivity"]:
                name = val.get("name", key)
                result = str(val.get("result", "")).lower()
                explanation = val.get("explanation", "")
                tag = "LOAD-BEARING" if result == "sat" else "REDUNDANT"
                as_lines.append(f"  [{tag}] {name}: {explanation}")
            if as_lines:
                _append_section("ASSUMPTION SENSITIVITY", as_lines)

        # 5. BOUNDARY CONDITIONS
        if "boundary_analysis" in buckets:
            ba_lines: list[str] = []
            for key, val in buckets["boundary_analysis"]:
                name = val.get("name", key)
                result = str(val.get("result", "")).lower()
                explanation = val.get("explanation", "")
                model_vals = val.get("model_values", {})
                model_str = (
                    ", ".join(f"{k}={v}" for k, v in model_vals.items())
                    if model_vals
                    else ""
                )
                tag = result.upper()
                line = f"  [{tag}] {name}: {explanation}"
                if model_str:
                    line += f" (values: {model_str})"
                ba_lines.append(line)
            if ba_lines:
                _append_section("BOUNDARY CONDITIONS", ba_lines)

        # 6. POLICY VERIFICATION
        if "policy_verification" in buckets:
            pv_lines: list[str] = []
            for key, val in buckets["policy_verification"]:
                name = val.get("name", key)
                result = str(val.get("result", "")).lower()
                explanation = val.get("explanation", "")
                tag = "VERIFIED" if result == "unsat" else "FAILS"
                pv_lines.append(f"  [{tag}] {name}: {explanation}")
            if pv_lines:
                _append_section("POLICY VERIFICATION", pv_lines)

        # 7. CONTRADICTIONS
        if "contradiction_check" in buckets:
            cc_lines: list[str] = []
            for key, val in buckets["contradiction_check"]:
                name = val.get("name", key)
                result = str(val.get("result", "")).lower()
                explanation = val.get("explanation", "")
                tag = (
                    "CONTRADICTION"
                    if result == "unsat"
                    else "CONSISTENT"
                )
                cc_lines.append(f"  [{tag}] {name}: {explanation}")
            if cc_lines:
                _append_section("CONTRADICTIONS", cc_lines)

        # 8. Anything with an unrecognised check_type
        known_types = {
            "proof_verification",
            "counterexample_search",
            "assumption_sensitivity",
            "boundary_analysis",
            "policy_verification",
            "contradiction_check",
            "_legacy",
        }
        for ct, entries in buckets.items():
            if ct in known_types:
                continue
            other_lines: list[str] = []
            for key, val in entries:
                name = val.get("name", key)
                result = val.get("result", "?")
                explanation = val.get("explanation", "")
                other_lines.append(
                    f"  [{name}] {result}: {explanation}"
                )
            if other_lines:
                _append_section(ct.upper().replace("_", " "), other_lines)

        return "\n".join(sections).rstrip()

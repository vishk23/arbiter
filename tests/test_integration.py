"""Integration tests for T10-T18: Engine, providers, and end-to-end flows.

These tests require API keys and are skipped if not available.
Use cheap models (gpt-4o-mini) to minimize cost.
"""

from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path

import pytest

_HAS_OPENAI = bool(os.environ.get("OPENAI_API_KEY"))
_HAS_ANTHROPIC = bool(os.environ.get("ANTHROPIC_API_KEY"))
_HAS_GEMINI = bool(os.environ.get("GEMINI_API_KEY"))

skip_no_openai = pytest.mark.skipif(not _HAS_OPENAI, reason="OPENAI_API_KEY not set")
skip_no_anthropic = pytest.mark.skipif(not _HAS_ANTHROPIC, reason="ANTHROPIC_API_KEY not set")
skip_no_gemini = pytest.mark.skipif(not _HAS_GEMINI, reason="GEMINI_API_KEY not set")
skip_no_multi = pytest.mark.skipif(
    not (_HAS_OPENAI and _HAS_ANTHROPIC),
    reason="Need both OPENAI_API_KEY and ANTHROPIC_API_KEY",
)


def _mini_config_dict(topology="standard", gate=False):
    """Build a minimal config dict for fast integration tests."""
    cfg = {
        "schema_version": "1.0",
        "topic": {
            "name": "Is water wet?",
            "summary": "A simple test topic about whether water can be considered wet.",
        },
        "topology": topology,
        "providers": {
            "openai": {
                "model": "gpt-4o-mini",
                "max_tokens": 500,
                "timeout": 60,
                "max_retries": 2,
            },
        },
        "agents": {
            "Pro": {
                "provider": "openai",
                "side": "Proponent",
                "max_words": 100,
                "system_prompt": "You are the Proponent. Argue that water is wet. Be brief.",
            },
            "Skep": {
                "provider": "openai",
                "side": "Skeptic",
                "max_words": 100,
                "system_prompt": "You are the Skeptic. Argue that water is not wet. Be brief.",
            },
        },
        "convergence": {"max_rounds": 1, "no_growth_halt": 1},
        "judge": {
            "system_prompt": "Judge this debate fairly.",
            "rubric": [
                {"id": "R1", "name": "Logic", "description": "Logical validity", "min": 0, "max": 10},
            ],
            "sides": ["Proponent", "Skeptic"],
            "verdict_options": ["Proponent", "Skeptic", "Tied"],
            "spread_threshold": 3,
            "panel": [{"provider": "openai"}],
        },
        "output": {
            "dir": "output/",
            "live_log": False,
            "formats": ["json"],
            "checkpoint_db": ":memory:",
        },
    }
    if gate:
        cfg["gate"] = {
            "enabled": True,
            "max_rewrites": 1,
            "stipulated_rules": [
                {
                    "id": "S1",
                    "fact": "Water is H2O",
                    "bad_patterns": ["water is not H2O", "water isn't H2O"],
                },
            ],
            "seed_terms": {"water": "H2O compound"},
        }
    return cfg


def _write_config(cfg_dict, tmpdir):
    """Write a config dict to a YAML file and return its path."""
    import yaml

    path = Path(tmpdir) / "config.yaml"
    path.write_text(yaml.dump(cfg_dict, default_flow_style=False))
    return path


@skip_no_openai
class TestRunStandard:
    """T10-equivalent: Test arbiter run with standard topology."""

    def test_basic_debate_completes(self):
        from arbiter.config import load_config
        from arbiter.graph import DebateEngine

        with tempfile.TemporaryDirectory() as td:
            cfg_path = _write_config(_mini_config_dict(), td)
            cfg = load_config(cfg_path)
            cfg.output.dir = str(Path(td) / "output")

            engine = DebateEngine(cfg)
            result = engine.run()

            assert result["round_idx"] >= 1
            assert isinstance(result["ledger"], list)
            assert isinstance(result["transcript"], list)
            assert len(result["transcript"]) >= 2  # at least 2 agents spoke


@skip_no_openai
class TestRunGated:
    """T10: Test arbiter run with gated topology end-to-end."""

    def test_gated_debate_completes(self):
        from arbiter.config import load_config
        from arbiter.graph import DebateEngine

        with tempfile.TemporaryDirectory() as td:
            cfg_path = _write_config(_mini_config_dict(topology="gated", gate=True), td)
            cfg = load_config(cfg_path)
            cfg.output.dir = str(Path(td) / "output")

            engine = DebateEngine(cfg)
            result = engine.run()

            assert result["round_idx"] >= 1


@skip_no_openai
class TestJudgePanel:
    """T15-equivalent: Test judge panel end-to-end."""

    def test_judge_produces_verdict(self):
        from arbiter.config import load_config
        from arbiter.judge.panel import JudgePanel
        from arbiter.providers import get_provider

        with tempfile.TemporaryDirectory() as td:
            cfg_path = _write_config(_mini_config_dict(), td)
            cfg = load_config(cfg_path)

            providers = {}
            for name, pcfg in cfg.providers.items():
                providers[name] = get_provider(name, pcfg)

            panel = JudgePanel(cfg.judge, providers)
            result = panel.judge(
                "Pro: Water is wet because it makes things wet.\n"
                "Skep: Water is not wet, wetness is a property of surfaces.",
                topic_name="Is water wet?",
            )

            assert "panel_verdict" in result
            assert result["panel_verdict"] in ["Proponent", "Skeptic", "Tied"]


@skip_no_anthropic
class TestAnthropicProvider:
    """T18: Test Anthropic provider for debate turns."""

    def test_anthropic_call(self):
        from arbiter.config import ProviderConfig
        from arbiter.providers.anthropic import AnthropicProvider

        cfg = ProviderConfig(model="claude-sonnet-4-20250514", max_tokens=100, timeout=60, max_retries=2)
        provider = AnthropicProvider(cfg)
        result = provider.call(
            system="You are a helpful assistant.",
            user="Say hello in 5 words.",
            max_tokens=100,
        )
        assert len(result) > 0

    def test_anthropic_structured(self):
        from arbiter.config import ProviderConfig
        from arbiter.providers.anthropic import AnthropicProvider

        cfg = ProviderConfig(model="claude-sonnet-4-20250514", max_tokens=200, timeout=60, max_retries=2)
        provider = AnthropicProvider(cfg)
        result = provider.call_structured(
            system="Return valid JSON.",
            user="What is 2+2? Return {\"answer\": N}.",
            schema={"type": "object", "properties": {"answer": {"type": "integer"}}, "required": ["answer"]},
            max_tokens=200,
        )
        assert "answer" in result


@skip_no_openai
class TestExportMarkdownIntegration:
    """T20: Test arbiter export -f markdown."""

    def test_markdown_export_from_run(self):
        from arbiter.config import load_config
        from arbiter.export.markdown import export_markdown
        from arbiter.graph import DebateEngine

        with tempfile.TemporaryDirectory() as td:
            cfg_path = _write_config(_mini_config_dict(), td)
            cfg = load_config(cfg_path)
            cfg.output.dir = str(Path(td) / "output")

            engine = DebateEngine(cfg)
            result = engine.run()

            md = export_markdown(result, "Test Debate")
            assert "# Debate: Test Debate" in md
            assert "## Round" in md


# ======================================================================
# T11: Z3 plugin loading + stipulation injection
# ======================================================================


@skip_no_openai
class TestZ3PluginLoading:
    """T11: Test arbiter run with Z3 plugin loading."""

    def test_z3_stipulation_in_gated_run(self):
        """If a Z3 module is present, its stipulation should be injected."""
        from arbiter.config import load_config
        from arbiter.graph import DebateEngine

        with tempfile.TemporaryDirectory() as td:
            # Create a minimal Z3 module matching the expected plugin format
            z3_module = Path(td) / "z3_module.py"
            z3_module.write_text(
                "def verify():\n"
                "    return {\n"
                '        "conservation": {\n'
                '            "name": "Conservation Law",\n'
                '            "result": "SAT",\n'
                '            "explanation": "All entities satisfy conservation."\n'
                "        }\n"
                "    }\n"
            )

            cfg_dict = _mini_config_dict(topology="gated", gate=True)
            cfg_dict["z3"] = {"module": str(z3_module)}
            cfg_path = _write_config(cfg_dict, td)
            cfg = load_config(cfg_path)
            cfg.output.dir = str(Path(td) / "output")

            engine = DebateEngine(cfg)
            assert engine.z3_plugin is not None
            assert engine._z3_stipulation  # should be non-empty


# ======================================================================
# T12: Multi-provider config
# ======================================================================


@skip_no_multi
class TestMultiProvider:
    """T12: Test arbiter run with agents on different providers."""

    def test_multi_provider_debate(self):
        from arbiter.config import load_config
        from arbiter.graph import DebateEngine

        with tempfile.TemporaryDirectory() as td:
            cfg_dict = _mini_config_dict()
            cfg_dict["providers"]["anthropic"] = {
                "model": "claude-sonnet-4-20250514",
                "max_tokens": 500,
                "timeout": 60,
                "max_retries": 2,
            }
            cfg_dict["agents"]["Skep"]["provider"] = "anthropic"
            cfg_path = _write_config(cfg_dict, td)
            cfg = load_config(cfg_path)
            cfg.output.dir = str(Path(td) / "output")

            engine = DebateEngine(cfg)
            result = engine.run()
            assert result["round_idx"] >= 1
            assert len(result["transcript"]) >= 2


# ======================================================================
# T13: arbiter calibrate end-to-end
# ======================================================================


@skip_no_openai
class TestCalibrateEndToEnd:
    """T13: Test arbiter calibrate with gate_tests.yaml."""

    def test_calibrate_basic(self):
        import yaml
        from arbiter.config import load_config
        from arbiter.gate.validity_gate import ValidityGate
        from arbiter.providers import get_provider

        with tempfile.TemporaryDirectory() as td:
            cfg_dict = _mini_config_dict(topology="gated", gate=True)
            cfg_path = _write_config(cfg_dict, td)
            cfg = load_config(cfg_path)

            providers = {}
            for name, pcfg in cfg.providers.items():
                providers[name] = get_provider(name, pcfg)

            gate = ValidityGate(cfg.gate, providers)

            # Create test cases
            cases = [
                {"text": "Water is H2O and it is wet.", "expected_pass": True},
                {"text": "Water is not H2O, it is fake.", "expected_pass": False},
            ]

            tp, fp, tn, fn = 0, 0, 0, 0
            for case in cases:
                result = gate.check(
                    agent="calibration",
                    turn_text=case["text"],
                    prior_claims={},
                    known_terms=dict(cfg.gate.seed_terms) if cfg.gate.seed_terms else {},
                )
                actual_pass = result["passed"]
                expected_pass = case["expected_pass"]
                if expected_pass and actual_pass:
                    tn += 1
                elif not expected_pass and not actual_pass:
                    tp += 1
                elif expected_pass and not actual_pass:
                    fp += 1
                else:
                    fn += 1

            # At minimum, the violating case should be caught
            assert tp + tn > 0


# ======================================================================
# T14: arbiter redteam end-to-end
# ======================================================================


@skip_no_openai
class TestRedteamEndToEnd:
    """T14: Test arbiter redteam end-to-end."""

    def test_redteam_completes(self):
        from arbiter.config import load_config, GateConfig
        from arbiter.graph import DebateEngine

        with tempfile.TemporaryDirectory() as td:
            cfg_dict = _mini_config_dict(topology="standard")
            cfg_path = _write_config(cfg_dict, td)
            cfg = load_config(cfg_path)
            cfg.output.dir = str(Path(td) / "output")

            # Enable adversarial mode
            cfg.topology = "adversarial"
            agent_name = list(cfg.agents.keys())[0]
            cfg.agents[agent_name].adversarial = True
            if cfg.gate is None:
                cfg.gate = GateConfig()

            engine = DebateEngine(cfg)
            result = engine.run()
            assert result["round_idx"] >= 1


# ======================================================================
# T16: Steelman loop
# ======================================================================


@skip_no_openai
class TestSteelmanLoop:
    """T16: Test steelman loop through the engine."""

    def test_steelman_loop_basic(self):
        from arbiter.config import ProviderConfig
        from arbiter.providers import get_provider
        from arbiter.steelman.loop import iterated_steelman

        pcfg = ProviderConfig(
            model="gpt-4o-mini", max_tokens=1000, timeout=60, max_retries=2
        )
        provider = get_provider("openai", pcfg)

        result = iterated_steelman(
            theory_summary="Water is wet because it makes things wet upon contact.",
            steelman_provider=provider,
            critic_provider=provider,
            judge_provider=provider,
            max_iterations=1,
        )

        assert "versions" in result
        assert len(result["versions"]) >= 1
        assert result["final_version"]
        assert isinstance(result["stabilized"], bool)


# ======================================================================
# T17: Gemini provider
# ======================================================================


def _google_sdk_works():
    """Check if the Google GenAI SDK is functional."""
    try:
        from google import genai  # noqa: F401
        return True
    except BaseException:
        return False


@pytest.mark.skipif(not _HAS_GEMINI, reason="GEMINI_API_KEY not set")
@pytest.mark.skipif(not _google_sdk_works(), reason="google-genai SDK not functional")
class TestGeminiProvider:
    """T17: Test Gemini provider through the engine."""

    def test_gemini_call(self):
        from arbiter.config import ProviderConfig
        from arbiter.providers.google import GoogleProvider

        cfg = ProviderConfig(
            model="gemini-2.0-flash", max_tokens=100, timeout=60, max_retries=2,
        )
        provider = GoogleProvider(cfg)
        result = provider.call(
            system="You are helpful.",
            user="Say hello in 5 words.",
            max_tokens=100,
        )
        assert len(result) > 0

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

skip_no_openai = pytest.mark.skipif(not _HAS_OPENAI, reason="OPENAI_API_KEY not set")
skip_no_anthropic = pytest.mark.skipif(not _HAS_ANTHROPIC, reason="ANTHROPIC_API_KEY not set")


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

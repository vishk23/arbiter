"""Tests for T24: Generated config.yaml validates through the engine."""

import tempfile
from pathlib import Path


from arbiter.config import load_config
from arbiter.init.config_writer import write_config


class TestGeneratedConfigValidation:
    """Ensure configs produced by write_config parse correctly."""

    def _write_and_load(self, **overrides):
        defaults = dict(
            topic_name="Test Topic",
            topic_summary="A test summary about the theory.",
            counter_thesis="The theory is wrong.",
            privileged_context={},
            topology="standard",
            providers_config={
                "openai": {"model": "gpt-5.4-mini", "max_tokens": 4000, "timeout": 180, "max_retries": 6},
            },
            agents={
                "Proponent": {
                    "provider": "openai",
                    "side": "Proponent",
                    "max_words": 500,
                    "system_prompt": "You are the proponent.",
                },
                "Skeptic": {
                    "provider": "openai",
                    "side": "Skeptic",
                    "max_words": 500,
                    "system_prompt": "You are the skeptic.",
                },
            },
            gate_rules=None,
            z3_module_path=None,
            rubric=[{"id": "R1", "name": "Evidence", "description": "Evidence quality", "min": 0, "max": 10}],
            judge_panel=[{"provider": "openai"}],
            sources_dir=None,
            convergence={"max_rounds": 6, "no_growth_halt": 2},
            steelman=None,
        )
        defaults.update(overrides)

        with tempfile.TemporaryDirectory() as td:
            out = str(Path(td) / "config.yaml")
            path = write_config(output_path=out, **defaults)
            return load_config(Path(path))

    def test_standard_topology(self):
        cfg = self._write_and_load(topology="standard")
        assert cfg.topology == "standard"
        assert "Proponent" in cfg.agents
        assert "Skeptic" in cfg.agents

    def test_gated_topology_with_gate(self):
        cfg = self._write_and_load(
            topology="gated",
            gate_rules={
                "max_rewrites": 2,
                "stipulated_rules": [
                    {"id": "S1", "fact": "X is true", "bad_patterns": ["X is false"]},
                ],
                "seed_terms": {"X": "a real thing"},
            },
        )
        assert cfg.topology == "gated"
        assert cfg.gate is not None
        assert cfg.gate.enabled is True

    def test_multi_provider(self):
        cfg = self._write_and_load(
            providers_config={
                "openai": {"model": "gpt-5.4-mini", "max_tokens": 4000, "timeout": 180, "max_retries": 6},
                "anthropic": {"model": "claude-sonnet-4-20250514", "max_tokens": 4000, "timeout": 180, "max_retries": 6},
            },
            agents={
                "Proponent": {"provider": "openai", "side": "Proponent", "max_words": 500, "system_prompt": "P"},
                "Skeptic": {"provider": "anthropic", "side": "Skeptic", "max_words": 500, "system_prompt": "S"},
            },
            judge_panel=[{"provider": "openai"}, {"provider": "anthropic"}],
        )
        assert "openai" in cfg.providers
        assert "anthropic" in cfg.providers

    def test_with_steelman(self):
        cfg = self._write_and_load(
            steelman={
                "enabled": True,
                "max_iterations": 4,
                "steelman_provider": "openai",
                "critic_provider": "openai",
                "judge_provider": "openai",
            },
        )
        assert cfg.steelman is not None
        assert cfg.steelman.enabled is True

    def test_with_privileged_context(self):
        cfg = self._write_and_load(
            privileged_context={"Skeptic": "Secret counter-evidence here."},
        )
        assert cfg.topic.privileged_context.get("Skeptic") == "Secret counter-evidence here."

    def test_section_comments_preserved(self):
        """Comments should not break YAML parsing."""
        with tempfile.TemporaryDirectory() as td:
            out = str(Path(td) / "config.yaml")
            write_config(
                output_path=out,
                topic_name="Test",
                topic_summary="Sum.",
                counter_thesis=None,
                privileged_context={},
                topology="standard",
                providers_config={"openai": {"model": "gpt-5.4-mini", "max_tokens": 4000, "timeout": 180, "max_retries": 6}},
                agents={
                    "Proponent": {"provider": "openai", "side": "Proponent", "max_words": 500, "system_prompt": "P"},
                    "Skeptic": {"provider": "openai", "side": "Skeptic", "max_words": 500, "system_prompt": "S"},
                },
                gate_rules=None,
                z3_module_path=None,
                rubric=[{"id": "R1", "name": "E", "description": "D", "min": 0, "max": 10}],
                judge_panel=[{"provider": "openai"}],
                sources_dir=None,
                convergence={"max_rounds": 6, "no_growth_halt": 2},
                steelman=None,
            )
            text = Path(out).read_text()
            assert text.count("#") > 5, "Comments should be present in generated config"
            # Should still parse
            cfg = load_config(Path(out))
            assert cfg.topic.name == "Test"

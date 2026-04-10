"""Tests for T07: Jinja2 template rendering in context builder."""

from __future__ import annotations

import pytest

from arbiter.agents.context import ContextBuilder
from arbiter.config import AgentConfig, ArbiterConfig, ProviderConfig, TopicConfig


def _make_config(
    topic_name: str = "BIT Creation Theory",
    topic_summary: str = "A theory about consciousness.",
    counter_thesis: str = "Consciousness is reducible to computation.",
    agents: dict | None = None,
) -> ArbiterConfig:
    """Build a minimal ArbiterConfig for testing."""
    topic = TopicConfig(
        name=topic_name,
        summary=topic_summary,
        counter_thesis=counter_thesis,
    )
    if agents is None:
        agents = {
            "Proponent": AgentConfig(
                provider="openai",
                side="Proponent",
                system_prompt=(
                    "You are the PROPONENT of {{ topic.name }}. "
                    "{{ z3_stipulation }} Defend the theory."
                ),
            ),
            "Skeptic": AgentConfig(
                provider="openai",
                side="Skeptic",
                system_prompt=(
                    "You are the SKEPTIC. {{ z3_stipulation }} "
                    "Challenge {{ topic.name }} rigorously."
                ),
            ),
        }
    return ArbiterConfig(
        topic=topic,
        providers={"openai": ProviderConfig(model="gpt-4o")},
        agents=agents,
        judge={"rubric": [], "panel": [{"provider": "openai"}]},
    )


class TestRenderSystemPrompt:
    """Verify that {{ topic.name }} and {{ z3_stipulation }} are rendered."""

    def test_topic_name_rendered(self):
        cfg = _make_config(topic_name="Quantum Gravity")
        builder = ContextBuilder(cfg)
        result = builder.render_system_prompt(
            cfg.agents["Proponent"].system_prompt
        )
        assert "Quantum Gravity" in result
        assert "{{ topic.name }}" not in result

    def test_z3_stipulation_rendered(self):
        cfg = _make_config()
        builder = ContextBuilder(cfg)
        z3 = "All entities must satisfy P(x) AND Q(x)."
        result = builder.render_system_prompt(
            cfg.agents["Proponent"].system_prompt, z3_stipulation=z3
        )
        assert z3 in result
        assert "{{ z3_stipulation }}" not in result

    def test_empty_z3_stipulation(self):
        cfg = _make_config()
        builder = ContextBuilder(cfg)
        result = builder.render_system_prompt(
            cfg.agents["Proponent"].system_prompt, z3_stipulation=""
        )
        assert "{{ z3_stipulation }}" not in result
        assert "{{ " not in result

    def test_counter_thesis_rendered(self):
        cfg = _make_config(counter_thesis="The theory is wrong.")
        builder = ContextBuilder(cfg)
        prompt = "Counter: {{ counter_thesis }}"
        result = builder.render_system_prompt(prompt)
        assert result == "Counter: The theory is wrong."

    def test_topic_summary_accessible(self):
        cfg = _make_config(topic_summary="Detailed summary here.")
        builder = ContextBuilder(cfg)
        result = builder.render_system_prompt("Summary: {{ topic.summary }}")
        assert result == "Summary: Detailed summary here."

    def test_no_literal_template_strings(self):
        """Ensure no {{ ... }} remain after rendering any generated prompt."""
        cfg = _make_config(topic_name="Test Theory")
        builder = ContextBuilder(cfg)
        z3 = "UNSAT constraint"

        for agent_name, agent_cfg in cfg.agents.items():
            rendered = builder.render_system_prompt(
                agent_cfg.system_prompt, z3_stipulation=z3
            )
            assert "{{" not in rendered, (
                f"Agent {agent_name} has unrendered template: {rendered}"
            )

    def test_prompt_without_templates(self):
        """Plain prompts (no Jinja2 variables) pass through unchanged."""
        cfg = _make_config()
        builder = ContextBuilder(cfg)
        plain = "You are a debate agent. Be rigorous."
        assert builder.render_system_prompt(plain) == plain

    def test_json_braces_not_mangled(self):
        """Single braces (like JSON examples) are not altered by Jinja2."""
        cfg = _make_config()
        builder = ContextBuilder(cfg)
        prompt = '{{ topic.name }}: output {"key": "value"}'
        result = builder.render_system_prompt(prompt)
        assert '{"key": "value"}' in result


class TestContextBuild:
    """Verify the full user-prompt assembly."""

    def test_build_includes_topic(self):
        cfg = _make_config(topic_name="Free Will")
        builder = ContextBuilder(cfg)
        state = {
            "round_idx": 1,
            "transcript": [],
            "ledger": [],
            "judge_signals": {},
        }
        result = builder.build("Proponent", state)
        assert "TOPIC: Free Will" in result

    def test_build_includes_round(self):
        cfg = _make_config()
        builder = ContextBuilder(cfg)
        state = {
            "round_idx": 3,
            "transcript": [],
            "ledger": [],
            "judge_signals": {},
        }
        result = builder.build("Proponent", state)
        assert "ROUND: 3" in result

"""Tests for T22: Verify all built-in agent prompts are valid Jinja2."""

import pytest
from jinja2 import Template

from arbiter.config import TopicConfig


# All known built-in prompt templates from agent_designer.py fallback agents
BUILTIN_PROMPTS = [
    "You are the PROPONENT of {{ topic.name }}. {{ z3_stipulation }} Defend the theory.",
    "You are the SKEPTIC. {{ z3_stipulation }} Challenge {{ topic.name }} rigorously.",
    (
        "You are the STEELMAN. {{ z3_stipulation }} "
        "Build the BEST possible reformulation of {{ topic.name }} "
        "that preserves its substantive insights while fixing the formal problems."
    ),
    (
        "You are an INDEPENDENT GENERALIST. {{ z3_stipulation }} "
        "Take no side. After each round, identify the single sloppiest argument."
    ),
    # Template config prompts (from cli.py)
    "You are the PROPONENT of {{ topic.name }}. Defend the position.",
    "You are the SKEPTIC. Challenge the theory rigorously.",
]


class TestBuiltinPromptsValidJinja:
    @pytest.mark.parametrize("prompt", BUILTIN_PROMPTS)
    def test_parses_as_jinja2(self, prompt):
        """Each prompt should parse without TemplateSyntaxError."""
        Template(prompt)

    @pytest.mark.parametrize("prompt", BUILTIN_PROMPTS)
    def test_renders_without_error(self, prompt):
        """Each prompt should render cleanly with standard context."""
        topic = TopicConfig(name="BIT Theory", summary="A theory.")
        tpl = Template(prompt)
        result = tpl.render(
            topic=topic,
            z3_stipulation="All claims must satisfy P(x).",
            counter_thesis="The theory is wrong.",
        )
        assert "{{" not in result, f"Unrendered template found: {result}"

    @pytest.mark.parametrize("prompt", BUILTIN_PROMPTS)
    def test_renders_with_empty_z3(self, prompt):
        """Prompts should work even when z3_stipulation is empty."""
        topic = TopicConfig(name="Test", summary="Summary.")
        tpl = Template(prompt)
        result = tpl.render(
            topic=topic,
            z3_stipulation="",
            counter_thesis="",
        )
        assert "{{" not in result


class TestStrayBraceDetection:
    """Ensure no prompts have mismatched or stray Jinja2 braces."""

    @pytest.mark.parametrize("prompt", BUILTIN_PROMPTS)
    def test_no_stray_braces(self, prompt):
        """Count {{ and }} — they should be balanced."""
        opens = prompt.count("{{")
        closes = prompt.count("}}")
        assert opens == closes, (
            f"Unbalanced braces: {opens} opens vs {closes} closes in: {prompt[:80]}"
        )

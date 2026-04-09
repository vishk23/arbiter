"""Per-turn context builder -- assembles the user prompt for each agent."""

from __future__ import annotations

from typing import TYPE_CHECKING, List

from jinja2 import Template

if TYPE_CHECKING:
    from arbiter.config import ArbiterConfig
    from arbiter.retrieval.retriever import Retriever
    from arbiter.state import DebateState, Hit


def _open_hits_for(ledger: "List[Hit]", agent_side: str) -> "List[Hit]":
    """Return open ledger hits that target *agent_side* or 'Theory'."""
    return [
        h
        for h in ledger
        if h["status"] == "open"
        and h["against"] in (agent_side, "Theory")
    ]


class ContextBuilder:
    """Assemble the complete user-prompt context for a single agent turn.

    Combines: topic summary, counter-thesis, Z3 stipulation,
    privileged context, open hits, judge signals, retrieved sources,
    and round number.

    The agent's ``system_prompt`` is rendered as a Jinja2 template with
    variables ``{{ topic.name }}``, ``{{ topic.summary }}``,
    ``{{ counter_thesis }}``, and ``{{ z3_stipulation }}``.
    """

    def __init__(
        self,
        config: "ArbiterConfig",
        retriever: "Retriever | None" = None,
    ) -> None:
        self.config = config
        self.retriever = retriever

    # ------------------------------------------------------------------ #

    def render_system_prompt(
        self, raw_prompt: str, z3_stipulation: str = ""
    ) -> str:
        """Render a Jinja2-templated system prompt."""
        tpl = Template(raw_prompt)
        return tpl.render(
            topic=self.config.topic,
            counter_thesis=self.config.topic.counter_thesis or "",
            z3_stipulation=z3_stipulation,
        )

    # ------------------------------------------------------------------ #

    def build(
        self,
        agent_name: str,
        state: "DebateState",
        z3_stipulation: str = "",
    ) -> str:
        """Return the full user-prompt context string for *agent_name*.

        Parameters
        ----------
        agent_name:
            Key into ``config.agents``.
        state:
            Current debate state.
        z3_stipulation:
            Formatted Z3 verification results to inject (empty when
            ``config.topology == 'standard'``).
        """
        topic = self.config.topic
        agent_cfg = self.config.agents[agent_name]
        parts: list[str] = []

        # 1. Topic summary
        parts.append(f"TOPIC: {topic.name}\n\n{topic.summary}")

        # 2. Counter-thesis (if any)
        if topic.counter_thesis:
            parts.append(f"COUNTER-THESIS:\n{topic.counter_thesis}")

        # 3. Z3 stipulation (for gated / adversarial topologies)
        if z3_stipulation:
            parts.append(f"Z3 STIPULATED FACTS:\n{z3_stipulation}")

        # 4. Privileged context (keyed by side)
        priv = topic.privileged_context.get(agent_cfg.side)
        if priv:
            parts.append(f"PRIVILEGED CONTEXT (only {agent_cfg.side} sees this):\n{priv}")

        # 5. Open hits this agent must address
        open_hits = _open_hits_for(state["ledger"], agent_cfg.side)
        if open_hits:
            hit_lines = "\n".join(
                f"  [{h['id']}] {h['by']}: {h['claim']}" for h in open_hits
            )
            parts.append(
                "OPEN HITS YOU MUST ADDRESS BEFORE INTRODUCING NEW MATERIAL:\n"
                + hit_lines
            )

        # 6. Judge signals
        signal = state.get("judge_signals", {}).get(agent_name)
        if signal:
            parts.append(f"JUDGE SIGNAL FOR YOU: {signal}")

        # 7. Retrieved sources
        if self.retriever is not None:
            query = f"{topic.name} {agent_name}"
            k_local = 2
            k_web = 2
            if self.config.retrieval:
                if self.config.retrieval.local:
                    k_local = self.config.retrieval.local.k
                if self.config.retrieval.web:
                    k_web = self.config.retrieval.web.k
            sources = self.retriever.retrieve(query, k_local=k_local, k_web=k_web)
            if sources and sources != "[no sources available]":
                parts.append(sources)

        # 8. Instructions
        parts.append(
            f"Speak as {agent_name}. Maximum {agent_cfg.max_words} words. "
            f"End with a JSON block:\n"
            '```json\n{"new_hits":[{"against":"...","claim":"..."}],'
            '"hits_addressed":[{"id":"h1","status":"rebutted|conceded|dodged",'
            '"rebuttal":"..."}]}\n```'
        )

        # 9. Round number
        parts.append(f"ROUND: {state['round_idx']}")

        return "\n\n".join(parts)

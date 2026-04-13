"""Per-turn context builder -- assembles the user prompt for each agent."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING, List

from jinja2 import Template

if TYPE_CHECKING:
    from arbiter.config import ArbiterConfig
    from arbiter.retrieval.retriever import Retriever
    from arbiter.state import DebateState, Hit


def _open_hits_for(ledger: "List[Hit]", agent_side: str) -> "List[Hit]":
    """Return open ledger hits targeting *agent_side*.

    Hit ``against`` fields are normalized at creation time (in graph.py's
    _ledger_node) to known side names, so exact matching works reliably.
    Also includes hits against 'Theory' for all sides.
    """
    return [
        h for h in ledger
        if h["status"] == "open"
        and h.get("against", "") in (agent_side, "Theory")
    ]


def _prefill_json_template(open_hits: "List[Hit]", max_hits: int = 5) -> str:
    """Build a pre-filled JSON template with actual hit IDs.

    Instead of a generic placeholder, the agent gets a fill-in-the-blanks
    template with real hit IDs and claims, dramatically reducing cognitive
    load and increasing compliance.
    """
    recent = sorted(open_hits, key=lambda h: h["round_landed"], reverse=True)[:max_hits]
    prefilled = []
    for h in recent:
        claim_preview = h["claim"][:80] + ("..." if len(h["claim"]) > 80 else "")
        prefilled.append({
            "id": h["id"],
            "status": "STATUS",
            "rebuttal": f"YOUR RESPONSE TO: {claim_preview} (by {h['by']})",
        })

    template = {
        "new_hits": [{"against": "...", "claim": "..."}],
        "hits_addressed": prefilled,
    }
    formatted = json.dumps(template, indent=2)
    # Add instructions as comments-like text above the JSON
    return (
        "Replace each STATUS with one of: rebutted, conceded, dodged\n"
        "Replace each \"YOUR RESPONSE TO: ...\" with your one-sentence response.\n"
        "You may add more new_hits but do NOT remove the hits_addressed entries.\n\n"
        f"```json\n{formatted}\n```"
    )


class ContextBuilder:
    """Assemble the complete user-prompt context for a single agent turn.

    Design: open hits and the JSON template are placed at the ABSOLUTE END
    of the context to exploit LLM recency bias (highest attention position).

    Order: topic → thesis → Z3 → privileged → signals → sources → round
    → **open hits + pre-filled JSON template** (last = most attended).
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

        Open hits and the JSON template are placed LAST to exploit
        recency bias for maximum compliance.

        The open-hits list naturally shrinks within a round as earlier
        agents resolve hits (mini-ledger-update in graph.py). No rotation
        needed — each agent sees only genuinely-open hits.
        """
        topic = self.config.topic
        agent_cfg = self.config.agents[agent_name]
        parts: list[str] = []
        open_hits = _open_hits_for(state["ledger"], agent_cfg.side)

        # ── Early context (background info) ────────────────────────────

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
            parts.append(
                f"PRIVILEGED CONTEXT (only {agent_cfg.side} sees this):\n{priv}"
            )

        # 5. Judge signals
        signal = state.get("judge_signals", {}).get(agent_name)
        if signal:
            parts.append(f"JUDGE SIGNAL FOR YOU: {signal}")

        # 6. Retrieved sources
        if self.retriever is not None:
            query = f"{topic.name} {agent_name}"
            k_local = 2
            k_web = 2
            if self.config.retrieval:
                if self.config.retrieval.local:
                    k_local = self.config.retrieval.local.k
                if self.config.retrieval.web:
                    k_web = self.config.retrieval.web.k
            sources = self.retriever.retrieve(
                query, k_local=k_local, k_web=k_web
            )
            if sources and sources != "[no sources available]":
                parts.append(sources)

        # 7. Round number
        parts.append(f"ROUND: {state['round_idx']}")

        # ── End of context (highest attention) ─────────────────────────

        # 8. Open hits + pre-filled JSON template (LAST for recency bias)
        required = min(3, len(open_hits)) if open_hits else 0

        sides = ", ".join(
            sorted({a.side for a in self.config.agents.values()})
        )

        if open_hits and required > 0:
            parts.append(
                f"Speak as {agent_name}. Maximum {agent_cfg.max_words} words.\n\n"
                f"CRITICAL — RESPOND TO OPEN HITS FIRST:\n"
                f"There are {len(open_hits)} unaddressed arguments against your side. "
                f"You MUST respond to at least {required} of them in your JSON block below. "
                f"Judges will PENALIZE you for ignoring opponent arguments.\n\n"
                f"Then make your new arguments. For new_hits, use \"against\": one of: {sides}\n\n"
                f"End your response with this JSON block (fill in STATUS and YOUR RESPONSE):\n\n"
                + _prefill_json_template(open_hits, max_hits=required)
            )
        else:
            sides = ", ".join(
                sorted({a.side for a in self.config.agents.values()})
            )
            parts.append(
                f"Speak as {agent_name}. Maximum {agent_cfg.max_words} words.\n"
                f"End with a JSON block:\n"
                f'```json\n{{"new_hits":[{{"against":"SIDE_NAME","claim":"..."}}],'
                f'"hits_addressed":[]}}\n```\n'
                f'For "against", use one of: {sides}'
            )

        return "\n\n".join(parts)

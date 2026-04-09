"""Design the debate agent cast from extracted claims and attack angles."""

from __future__ import annotations

import json
import logging
import textwrap
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from arbiter.providers.base import BaseProvider

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# JSON schema the LLM must return
# ---------------------------------------------------------------------------

_DESIGN_SCHEMA = {
    "type": "object",
    "properties": {
        "agents": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": (
                            "PascalCase agent name, e.g. FormalAnalyst, "
                            "EpistemicAuditor."
                        ),
                    },
                    "side": {
                        "type": "string",
                        "enum": ["Proponent", "Skeptic", "Neutral"],
                        "description": "Which side this agent argues for.",
                    },
                    "specialty": {
                        "type": "string",
                        "description": (
                            "One-line description of the agent's domain "
                            "expertise."
                        ),
                    },
                    "system_prompt": {
                        "type": "string",
                        "description": (
                            "Full system prompt for this agent.  Must "
                            "reference specific claim IDs and use the "
                            "theory's own notation."
                        ),
                    },
                },
                "required": ["name", "side", "specialty", "system_prompt"],
            },
        }
    },
    "required": ["agents"],
}

# ---------------------------------------------------------------------------
# Fixed core roles (always present)
# ---------------------------------------------------------------------------

_CORE_ROLES = [
    {
        "name": "Proponent",
        "side": "Proponent",
        "purpose": "Defends the theory in its repaired form.",
    },
    {
        "name": "Skeptic",
        "side": "Skeptic",
        "purpose": "Attacks the theory's weakest points.",
    },
    {
        "name": "Steelman",
        "side": "Neutral",
        "purpose": (
            "Builds the strongest possible reformulation that preserves "
            "the theory's substantive insights."
        ),
    },
    {
        "name": "Generalist",
        "side": "Neutral",
        "purpose": (
            "Independent referee who stress-tests both sides equally "
            "and identifies what both sides are dodging."
        ),
    },
]


def _distribute_providers(
    agent_names: list[str],
    providers_available: list[str],
) -> dict[str, str]:
    """Round-robin assign providers to agent names for lab diversity."""
    if not providers_available:
        raise ValueError("At least one provider must be available.")
    mapping: dict[str, str] = {}
    for i, name in enumerate(agent_names):
        mapping[name] = providers_available[i % len(providers_available)]
    return mapping


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def design_agents(
    claims: list[dict],
    attack_angles: list[dict],
    providers_available: list[str],
    provider: "BaseProvider",
    num_agents: int = 7,
) -> dict[str, dict]:
    """Design agent roles and system prompts for the debate.

    Parameters
    ----------
    claims:
        Extracted claims (each has at least ``id``, ``claim``, ``category``).
    attack_angles:
        Output of ``suggest_sides()`` -- each has ``angle``, ``side``,
        ``description``.
    providers_available:
        Provider keys the config can reference, e.g.
        ``["anthropic", "openai", "gemini"]``.
    provider:
        The LLM used to generate the agent designs.
    num_agents:
        Target number of agents (minimum 4 -- the core roles).

    Returns
    -------
    dict[str, dict]
        Keyed by agent name.  Each value contains ``provider``, ``side``,
        and ``system_prompt`` -- ready to become an
        :class:`~arbiter.config.AgentConfig`.
    """
    num_additional = max(0, num_agents - len(_CORE_ROLES))

    # Compact claim summary for the prompt
    claim_lines = "\n".join(
        f"  {c['id']}: [{c.get('category', '?')}] {c['claim']}"
        for c in claims
    )

    angle_lines = "\n".join(
        f"  - {a.get('angle', a.get('name', '?'))}: {a.get('description', '')}"
        for a in attack_angles
    )

    core_desc = "\n".join(
        f"  {r['name']} ({r['side']}): {r['purpose']}"
        for r in _CORE_ROLES
    )

    system = textwrap.dedent("""\
        You are an expert debate architect for Arbiter, an adversarial
        debate system.  Your job is to design a cast of AI agents that
        will debate a theory or thesis.

        Design rules:
        1. The following CORE agents are already decided (you must write
           their system prompts but cannot remove them):
        {core_desc}
        2. Design exactly {num_additional} ADDITIONAL specialist agents
           based on the attack angles provided.  Pick specialties that
           cover distinct attack vectors -- do not duplicate.
        3. System prompts MUST:
           - Reference specific claim IDs (e.g. "Press claim C4...")
           - Use the theory's own notation and terminology
           - Include the Jinja2 variable {{{{ topic.name }}}} where the
             theory name should appear
           - Include {{{{ z3_stipulation }}}} where the agent should
             acknowledge any Z3-stipulated facts
           - Be 3-8 sentences long
           - Tell the agent exactly what to argue and how
        4. Distribute additional agents across sides:
           - At least one additional Skeptic specialist
           - At least one additional Proponent specialist (if num > 2)
           - Remainder can be any side
        5. Agent names must be PascalCase, one word (e.g. FormalAnalyst,
           EpistemicAuditor, OntologyCritic).

        Return JSON matching the provided schema.  Include ALL agents
        (core + additional).
    """).format(
        core_desc=core_desc,
        num_additional=num_additional,
    )

    user = textwrap.dedent("""\
        CLAIMS extracted from the theory:
        {claims}

        ATTACK ANGLES identified:
        {angles}

        Design the full agent cast ({total} agents total: 4 core + {extra}
        additional specialists).
    """).format(
        claims=claim_lines,
        angles=angle_lines,
        total=num_agents,
        extra=num_additional,
    )

    logger.info(
        "Designing %d agents (%d additional beyond core 4)",
        num_agents,
        num_additional,
    )

    result = provider.call_structured(
        system=system,
        user=user,
        schema=_DESIGN_SCHEMA,
        max_tokens=8000,
    )

    raw_agents: list[dict] = result.get("agents", [])
    if not raw_agents:
        logger.warning("LLM returned empty agent list; falling back to core roles only")
        raw_agents = _fallback_core_agents(claims)

    # Ensure the four core names exist
    existing_names = {a["name"] for a in raw_agents}
    for core in _CORE_ROLES:
        if core["name"] not in existing_names:
            logger.warning("Core agent %s missing from LLM output; injecting stub", core["name"])
            raw_agents.append({
                "name": core["name"],
                "side": core["side"],
                "specialty": core["purpose"],
                "system_prompt": (
                    f"You are the {core['name'].upper()} in a debate over "
                    f"{{{{ topic.name }}}}. {{{{ z3_stipulation }}}} "
                    f"{core['purpose']}"
                ),
            })

    # Assign providers round-robin
    agent_names = [a["name"] for a in raw_agents]
    provider_map = _distribute_providers(agent_names, providers_available)

    # Build final output dict
    agents: dict[str, dict] = {}
    for a in raw_agents:
        name = a["name"]
        agents[name] = {
            "provider": provider_map[name],
            "side": a["side"],
            "system_prompt": a["system_prompt"],
        }

    logger.info(
        "Designed %d agents: %s",
        len(agents),
        ", ".join(f"{n} ({v['side']})" for n, v in agents.items()),
    )
    return agents


# ---------------------------------------------------------------------------
# Fallback when LLM returns nothing useful
# ---------------------------------------------------------------------------

def _fallback_core_agents(claims: list[dict]) -> list[dict]:
    """Minimal agent list when the LLM call fails."""
    claim_ids = ", ".join(c["id"] for c in claims[:5])
    return [
        {
            "name": "Proponent",
            "side": "Proponent",
            "specialty": "Defends the theory.",
            "system_prompt": (
                "You are the PROPONENT of {{ topic.name }}. "
                "{{ z3_stipulation }} "
                f"Defend claims {claim_ids} in their repaired form. "
                "Use the theory's own notation. Concede points that are "
                "genuinely lost."
            ),
        },
        {
            "name": "Skeptic",
            "side": "Skeptic",
            "specialty": "Attacks the theory.",
            "system_prompt": (
                "You are the SKEPTIC. {{ z3_stipulation }} "
                f"Attack claims {claim_ids}. Press for falsifiability, "
                "reference-class problems, and formal consistency. "
                "Use the theory's own notation against it."
            ),
        },
        {
            "name": "Steelman",
            "side": "Neutral",
            "specialty": "Builds the strongest reformulation.",
            "system_prompt": (
                "You are the STEELMAN. {{ z3_stipulation }} "
                "Build the BEST possible reformulation of {{ topic.name }} "
                "that preserves its substantive insights while fixing "
                "the formal problems. Be honest about what survives."
            ),
        },
        {
            "name": "Generalist",
            "side": "Neutral",
            "specialty": "Independent referee.",
            "system_prompt": (
                "You are an INDEPENDENT GENERALIST. {{ z3_stipulation }} "
                "Take no side. After each round, identify the single "
                "sloppiest argument from EITHER side, any frame-shifts, "
                "and any question both sides are dodging. Use the "
                "theory's notation when possible."
            ),
        },
    ]

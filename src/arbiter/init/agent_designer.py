"""Design the debate agent cast from extracted claims and attack angles."""

from __future__ import annotations

import logging
import textwrap
from typing import TYPE_CHECKING

from arbiter.schemas import AgentDesignResult

if TYPE_CHECKING:
    from arbiter.providers.base import BaseProvider

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# JSON schema the LLM must return
# ---------------------------------------------------------------------------

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
    agents: list[dict],
    providers_available: list[str],
) -> dict[str, str]:
    """Side-balanced provider assignment for lab diversity.

    Ensures each debate *side* has agents from multiple providers (when
    possible), so no side is a monoculture of one lab's biases.
    """
    if not providers_available:
        raise ValueError("At least one provider must be available.")
    if len(providers_available) == 1:
        return {a["name"]: providers_available[0] for a in agents}

    # Group agents by side
    by_side: dict[str, list[str]] = {}
    for a in agents:
        by_side.setdefault(a["side"], []).append(a["name"])

    mapping: dict[str, str] = {}
    # For each side, round-robin across providers independently
    for side, names in by_side.items():
        for i, name in enumerate(names):
            mapping[name] = providers_available[i % len(providers_available)]

    return mapping


def _format_key_terms_for_prompt(key_terms: dict[str, str]) -> str:
    """Format key terms dict into a readable block for the LLM prompt."""
    if not key_terms:
        return "  (none extracted)"
    lines = []
    for term, defn in list(key_terms.items())[:20]:
        lines.append(f"  {term}: {defn}")
    return "\n".join(lines)


def _format_theses_for_prompt(theses: list[dict]) -> str:
    """Format consolidated theses into a readable block."""
    if not theses:
        return "  (none available)"
    lines = []
    for t in theses:
        sub = ", ".join(t.get("sub_claims", [])[:8])
        notation = ", ".join(t.get("key_notation", [])[:6])
        lines.append(
            f"  {t['id']} [{t.get('category', '?')}] (claims: {sub})"
            f"\n    Thesis: {t['thesis']}"
            f"\n    Key notation: {notation}"
            f"\n    Quote: \"{t.get('quote', '')[:150]}\""
        )
    return "\n".join(lines)


def _format_contradictions_for_prompt(contradictions: list[dict]) -> str:
    """Format contradictions into a readable block."""
    if not contradictions:
        return "  (none found)"
    lines = []
    for c in contradictions[:10]:
        lines.append(
            f"  {c['claim_a']} vs {c['claim_b']} [{c.get('severity', '?')}]:"
            f" {c['contradiction'][:200]}"
        )
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def design_agents(
    claims: list[dict],
    attack_angles: list[dict],
    providers_available: list[str] | dict,
    provider: "BaseProvider",
    num_agents: int = 7,
    *,
    consolidated_theses: list[dict] | None = None,
    key_terms: dict[str, str] | None = None,
    contradictions: list[dict] | None = None,
    counter_thesis: str | None = None,
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
        ``["anthropic", "openai", "gemini"]`` or a dict keyed by name.
    provider:
        The LLM used to generate the agent designs.
    num_agents:
        Target number of agents (minimum 4 -- the core roles).
    consolidated_theses:
        Output of ``consolidate_claims()`` (optional but recommended).
    key_terms:
        Glossary of key terms extracted from the theory.
    contradictions:
        Identified contradictions between claims.
    counter_thesis:
        The main counter-thesis a Skeptic would advance.

    Returns
    -------
    dict[str, dict]
        Keyed by agent name.  Each value contains ``provider``, ``side``,
        and ``system_prompt`` -- ready to become an
        :class:`~arbiter.config.AgentConfig`.
    """
    # Normalize providers_available to a list of names
    if isinstance(providers_available, dict):
        provider_names_list = list(providers_available.keys())
    else:
        provider_names_list = list(providers_available)

    num_additional = max(0, num_agents - len(_CORE_ROLES))

    # Compact claim summary for the prompt
    claim_lines = "\n".join(
        f"  {c['id']}: [{c.get('category', '?')}] {c['claim']}"
        for c in claims[:30]
    )

    angle_lines = "\n".join(
        f"  - {a.get('angle', a.get('name', '?'))}: {a.get('description', '')}"
        for a in attack_angles
    )

    core_desc = "\n".join(
        f"  {r['name']} ({r['side']}): {r['purpose']}"
        for r in _CORE_ROLES
    )

    # Build rich context blocks
    theses_block = _format_theses_for_prompt(consolidated_theses or [])
    terms_block = _format_key_terms_for_prompt(key_terms or {})
    contra_block = _format_contradictions_for_prompt(contradictions or [])

    # Example notation for the LLM to use in prompts
    example_notation = ""
    if key_terms:
        sample_terms = list(key_terms.items())[:5]
        example_notation = "\n".join(
            f"    - Use \"{t}\" to mean: {d[:100]}"
            for t, d in sample_terms
        )

    # Counter-thesis instruction
    counter_thesis_instruction = ""
    if counter_thesis:
        counter_thesis_instruction = textwrap.dedent(f"""\

        COUNTER-THESIS (the strongest opposing position):
        {counter_thesis}

        The Skeptic agent's system prompt MUST be seeded with this
        counter-thesis.  The Skeptic should use it as their primary
        line of attack.
        """)

    system = textwrap.dedent("""\
        You are an expert debate architect for Arbiter, an adversarial
        debate system.  Your job is to design a cast of AI agents that
        will debate a theory or thesis at EXPERT level.

        Design rules:
        1. The following CORE agents are already decided (you must write
           their system prompts but cannot remove them):
        {core_desc}
        2. Design exactly {num_additional} ADDITIONAL specialist agents
           based on the attack angles and contradictions provided.  Each
           specialist must have:
           - A specific ACADEMIC DOMAIN (e.g., "causal inference
             specialist", "formal ontology auditor", "empirical
             methodology critic") -- not generic labels like "analyst"
           - System prompts that reference the theory's OWN notation
             and terminology using the key terms provided below
           - Instructions to cite specific claim IDs and thesis IDs
           - Instructions to use formal notation when engaging the theory
        3. System prompts MUST:
           - Reference specific claim IDs (e.g. "Press claim C4...")
             and thesis IDs (e.g. "Challenge thesis T2...")
           - Use the theory's own notation and terminology from the
             KEY TERMS below:
        {example_notation}
           - Include the Jinja2 variable {{{{ topic.name }}}} where the
             theory name should appear
           - Include {{{{ z3_stipulation }}}} where the agent should
             acknowledge any Z3-stipulated facts
           - Be 4-10 sentences long
           - Tell the agent exactly what to argue, which claims to
             target, what notation to use, and how to engage at the
             theory's own level of discourse
           - Reference specific contradictions when relevant
        4. PROPONENT prompt must:
           - Defend the theory using its OWN framework and notation
           - Concede genuinely lost points explicitly
           - Attempt to repair contradictions rather than deny them
        5. SKEPTIC prompt must:
           - Be the main attacker, seeded with the counter-thesis if available
           - Target the most severe contradictions first
           - Use the theory's notation AGAINST the theory
        6. STEELMAN prompt must:
           - Rescue the theory by identifying which claims can be
             DROPPED to save the rest
           - Build the strongest reformulation that preserves
             substantive insights while fixing formal problems
        7. GENERALIST prompt must:
           - Take no side; stress-test BOTH sides equally
           - After each round, identify the sloppiest argument from
             either side, any frame-shifts or equivocations, and any
             question both sides are dodging
        8. Distribute additional agents across sides:
           - At least one additional Skeptic specialist
           - At least one additional Proponent specialist (if num > 2)
           - Remainder can be any side
        9. Agent names must be PascalCase, one word (e.g. FormalAnalyst,
           EpistemicAuditor, OntologyCritic).
        10. CRITICAL — UNCITED BUT RELEVANT FIELDS: The theory may use
           concepts from academic traditions it does NOT explicitly cite.
           You MUST identify these and design specialists for them.
           Examples: a theory using "synchronicity" or "archetypal
           convergence" without citing Jung still needs a Jungian
           psychology specialist; a theory using DAG notation without
           citing Pearl still needs a causal inference specialist; a
           theory making consciousness claims without citing Tononi/IIT
           still needs a consciousness studies specialist.
           Ask yourself: "What expert, reading this theory, would
           immediately recognize concepts from their field being used
           (correctly or incorrectly) WITHOUT attribution?" Design an
           agent for each such expert.
        {counter_thesis_instruction}
        Return JSON matching the provided schema.  Include ALL agents
        (core + additional).
    """).format(
        core_desc=core_desc,
        num_additional=num_additional,
        example_notation=example_notation or "    (no key terms extracted)",
        counter_thesis_instruction=counter_thesis_instruction,
    )

    user = textwrap.dedent("""\
        CONSOLIDATED THESES (core arguments grouped from claims):
        {theses}

        KEY TERMS AND NOTATION:
        {terms}

        IDENTIFIED CONTRADICTIONS:
        {contradictions}

        RAW CLAIMS (for reference):
        {claims}

        ATTACK ANGLES identified:
        {angles}

        Design the full agent cast ({total} agents total: 4 core + {extra}
        additional specialists).  Each agent's system prompt must use the
        theory's own terminology from the KEY TERMS above.
    """).format(
        theses=theses_block,
        terms=terms_block,
        contradictions=contra_block,
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
        schema=AgentDesignResult,
        max_tokens=8000,
    )

    raw_agents: list[dict] = result.get("agents", [])
    if not raw_agents:
        logger.warning("LLM returned empty agent list; falling back to core roles only")
        raw_agents = _fallback_core_agents(claims, key_terms, counter_thesis)

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

    # Assign providers — side-balanced across labs
    provider_map = _distribute_providers(raw_agents, provider_names_list)

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

def _fallback_core_agents(
    claims: list[dict],
    key_terms: dict[str, str] | None = None,
    counter_thesis: str | None = None,
) -> list[dict]:
    """Minimal agent list when the LLM call fails."""
    claim_ids = ", ".join(c["id"] for c in claims[:5])

    # Build notation instruction from key terms
    notation_hint = ""
    if key_terms:
        sample = list(key_terms.items())[:3]
        notation_hint = (
            " Use the theory's notation: "
            + ", ".join(f'"{t}" ({d[:50]}...)' for t, d in sample)
            + "."
        )

    counter_hint = ""
    if counter_thesis:
        counter_hint = (
            f" Your primary line of attack: {counter_thesis[:200]}."
        )

    return [
        {
            "name": "Proponent",
            "side": "Proponent",
            "specialty": "Defends the theory using its own framework.",
            "system_prompt": (
                "You are the PROPONENT of {{ topic.name }}. "
                "{{ z3_stipulation }} "
                f"Defend claims {claim_ids} in their repaired form. "
                f"{notation_hint} "
                "Concede points that are genuinely lost. When a "
                "contradiction is stipulated, adopt a repair path "
                "rather than denying the contradiction."
            ),
        },
        {
            "name": "Skeptic",
            "side": "Skeptic",
            "specialty": "Attacks the theory using its own notation against it.",
            "system_prompt": (
                "You are the SKEPTIC. {{ z3_stipulation }} "
                f"Attack claims {claim_ids}. Press for falsifiability, "
                "reference-class problems, and formal consistency. "
                f"{notation_hint} "
                "Use the theory's own notation against it."
                f"{counter_hint}"
            ),
        },
        {
            "name": "Steelman",
            "side": "Neutral",
            "specialty": "Builds the strongest reformulation by dropping weak claims.",
            "system_prompt": (
                "You are the STEELMAN. {{ z3_stipulation }} "
                "Build the BEST possible reformulation of {{ topic.name }} "
                "that preserves its substantive insights while fixing "
                "the formal problems. Identify which claims should be "
                "DROPPED to save the rest. Be honest about what survives."
                f"{notation_hint}"
            ),
        },
        {
            "name": "Generalist",
            "side": "Neutral",
            "specialty": "Independent referee who catches dodged questions.",
            "system_prompt": (
                "You are an INDEPENDENT GENERALIST. {{ z3_stipulation }} "
                "Take no side. After each round, identify the single "
                "sloppiest argument from EITHER side, any frame-shifts "
                "or equivocations, and any question both sides are "
                "dodging. Use the theory's notation when possible."
                f"{notation_hint}"
            ),
        },
    ]

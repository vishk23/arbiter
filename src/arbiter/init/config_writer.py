"""Assemble pipeline outputs into a complete Arbiter YAML config file."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

import yaml

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# YAML helpers
# ---------------------------------------------------------------------------

class _LiteralStr(str):
    """Marker type so the YAML dumper uses block-literal style (|)."""


def _literal_representer(dumper: yaml.Dumper, data: _LiteralStr) -> Any:
    return dumper.represent_scalar("tag:yaml.org,2002:str", data, style="|")


yaml.add_representer(_LiteralStr, _literal_representer)


def _literalise(obj: Any) -> Any:
    """Recursively convert multi-line strings to _LiteralStr for YAML output."""
    if isinstance(obj, dict):
        return {k: _literalise(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_literalise(v) for v in obj]
    if isinstance(obj, str) and "\n" in obj:
        return _LiteralStr(obj)
    return obj


# ---------------------------------------------------------------------------
# Config assembly
# ---------------------------------------------------------------------------

def write_config(
    output_path: str,
    topic_name: str,
    topic_summary: str,
    counter_thesis: str | None,
    privileged_context: dict[str, str],
    topology: str,
    providers_config: dict,       # {name: {model, thinking, reasoning, ...}}
    agents: dict,                 # from agent_designer
    gate_rules: dict | None,      # from gate_builder
    z3_module_path: str | None,
    rubric: list[dict],           # from rubric_builder
    judge_panel: list[dict],      # [{provider: "anthropic"}, ...]
    sources_dir: str | None,
    convergence: dict | None,
    steelman: dict | None,
) -> str:
    """Write a complete arbiter config YAML file.

    Returns the path written.
    """
    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)

    # -- topic ---------------------------------------------------------------
    topic: dict[str, Any] = {
        "name": topic_name,
        "summary": topic_summary,
    }
    if counter_thesis:
        topic["counter_thesis"] = counter_thesis
    if privileged_context:
        topic["privileged_context"] = privileged_context

    # -- providers -----------------------------------------------------------
    providers: dict[str, Any] = {}
    for name, pcfg in providers_config.items():
        entry: dict[str, Any] = {"model": pcfg["model"]}
        entry["max_tokens"] = pcfg.get("max_tokens", 4000)
        entry["timeout"] = pcfg.get("timeout", 180)
        entry["max_retries"] = pcfg.get("max_retries", 6)
        if pcfg.get("thinking"):
            entry["thinking"] = pcfg["thinking"]
        if pcfg.get("reasoning"):
            entry["reasoning"] = pcfg["reasoning"]
        if pcfg.get("base_url"):
            entry["base_url"] = pcfg["base_url"]
        providers[name] = entry

    # -- agents --------------------------------------------------------------
    agents_section: dict[str, Any] = {}
    for aname, acfg in agents.items():
        agents_section[aname] = {
            "provider": acfg["provider"],
            "side": acfg["side"],
            "max_words": acfg.get("max_words", 500),
            "system_prompt": acfg["system_prompt"],
        }
        if acfg.get("adversarial"):
            agents_section[aname]["adversarial"] = True

    # -- convergence ---------------------------------------------------------
    conv = convergence or {"max_rounds": 6, "no_growth_halt": 2}

    # -- judge ---------------------------------------------------------------
    # Build rubric entries using min/max keys expected by the schema
    rubric_entries = []
    for r in rubric:
        entry = {
            "id": r["id"],
            "name": r["name"],
            "description": r["description"],
            "min": r.get("min", r.get("min_score", 0)),
            "max": r.get("max", r.get("max_score", 10)),
        }
        rubric_entries.append(entry)

    # Collect unique sides from agents
    sides = sorted({a["side"] for a in agents.values() if a["side"] != "Neutral"})
    if not sides:
        sides = ["Proponent", "Skeptic"]

    judge: dict[str, Any] = {
        "system_prompt": (
            f"You are an expert judge evaluating a multi-agent debate on "
            f"{topic_name}.\n"
            f"Apply the rubric mechanically. Reward precise engagement with "
            f"the subject matter, arguments that survive rebuttal, and honest "
            f"concession. Penalize dodging, equivocation, and appeals to "
            f"authority.\n"
        ),
        "rubric": rubric_entries,
        "sides": sides,
        "verdict_options": sides + ["Tied"],
        "spread_threshold": 3,
        "panel": judge_panel,
        "mid_debate": {
            "enabled": True,
            "provider": "anthropic-fast" if "anthropic-fast" in providers_config else (
                judge_panel[0]["provider"] if judge_panel else "openai"
            ),
        },
    }

    # -- auto-create specialized provider variants ──────────────────────
    # Each task gets the right model tier. Users can override in YAML.
    if "openai" in providers_config:
        if "openai-pro" not in providers_config:
            # Pro: judges + steelman critic (needs maximum precision)
            providers_config["openai-pro"] = {
                "model": "gpt-5.4-pro",
                "max_tokens": 4000,
                "timeout": 180,
                "max_retries": 6,
            }
        if "openai-gate" not in providers_config:
            # Mini: gate checker (classification, cheap)
            providers_config["openai-gate"] = {
                "model": "gpt-5.4-mini",
                "max_tokens": 4000,
                "timeout": 60,
                "max_retries": 3,
            }
    if "anthropic" in providers_config and "anthropic-fast" not in providers_config:
        # Sonnet: mid-debate judge (fast + smart, runs every round)
        providers_config["anthropic-fast"] = {
            "model": "claude-sonnet-4-6",
            "max_tokens": 4000,
            "timeout": 120,
            "max_retries": 6,
        }

    # -- gate ----------------------------------------------------------------
    gate: dict[str, Any] | None = None
    if gate_rules and topology in ("gated", "adversarial"):
        gate_provider = "openai-gate" if "openai-gate" in providers_config else (
            list(providers_config.keys())[0] if providers_config else "openai"
        )

        gate_provider = "openai-gate" if "openai-gate" in providers_config else (
            list(providers_config.keys())[0] if providers_config else "openai"
        )
        gate = {
            "enabled": True,
            "primary": "llm",
            "llm_checker_provider": gate_provider,
            "max_rewrites": gate_rules.get("max_rewrites", 2),
        }
        if gate_rules.get("extraction_provider"):
            gate["extraction_provider"] = gate_rules["extraction_provider"]
        if gate_rules.get("stipulated_rules"):
            gate["stipulated_rules"] = gate_rules["stipulated_rules"]
        if gate_rules.get("seed_terms"):
            gate["seed_terms"] = gate_rules["seed_terms"]
        # Smart default: always enable entailment check if gate is active.
        # The LLM semantic backstop catches paraphrased violations that regex misses.
        if gate_rules.get("entailment_check"):
            pass  # user/pipeline provided explicit config — use it
        else:
            # Auto-enable with the first available provider
            first_provider = list(providers_config.keys())[0] if providers_config else "openai"
            gate["entailment_check"] = {
                "enabled": True,
                "provider": first_provider,
            }
        if gate_rules.get("entailment_check"):
            gate["entailment_check"] = gate_rules["entailment_check"]

    # -- z3 ------------------------------------------------------------------
    z3: dict[str, Any] | None = None
    if z3_module_path:
        # Store a relative path from the config file location
        z3_abs = Path(z3_module_path).resolve()
        config_dir = out.resolve().parent
        try:
            z3_rel = z3_abs.relative_to(config_dir)
        except ValueError:
            z3_rel = z3_abs
        z3 = {"module": str(z3_rel)}

    # -- steelman ------------------------------------------------------------
    steel: dict[str, Any] | None = None
    if steelman:
        steel = steelman

    # -- retrieval -----------------------------------------------------------
    retrieval: dict[str, Any] | None = None
    if sources_dir:
        sources_abs = Path(sources_dir).resolve()
        config_dir = out.resolve().parent
        try:
            sources_rel = sources_abs.relative_to(config_dir)
        except ValueError:
            sources_rel = sources_abs
        retrieval = {"local": {"sources_dir": str(sources_rel), "k": 2}}

    # -- output --------------------------------------------------------------
    output_section = {
        "dir": "output/",
        "live_log": True,
        "formats": ["json", "markdown"],
        "checkpoint_db": "checkpoints.sqlite",
    }

    # -- assemble root -------------------------------------------------------
    config: dict[str, Any] = {
        "schema_version": "1.0",
        "topic": topic,
        "topology": topology,
        "providers": providers,
        "agents": agents_section,
        "convergence": conv,
    }
    if gate:
        config["gate"] = gate
    if z3:
        config["z3"] = z3
    config["judge"] = judge
    if steel:
        config["steelman"] = steel
    if retrieval:
        config["retrieval"] = retrieval
    config["output"] = output_section

    # -- write ---------------------------------------------------------------
    config = _literalise(config)

    yaml_text = yaml.dump(
        config,
        default_flow_style=False,
        sort_keys=False,
        allow_unicode=True,
        width=100,
    )
    yaml_text = _inject_section_comments(yaml_text)
    out.write_text(yaml_text)
    logger.info("Config written to %s", out)
    return str(out)


# ---------------------------------------------------------------------------
# Section comments
# ---------------------------------------------------------------------------

_SECTION_COMMENTS: dict[str, str] = {
    "schema_version": "Arbiter config schema version. Do not change.",
    "topic": (
        "Topic under debate.\n"
        "# - name: short label shown in transcripts and exports\n"
        "# - summary: 2-4 paragraph description of the position\n"
        "# - counter_thesis: the strongest opposing position\n"
        "# - privileged_context: per-side info only that side sees"
    ),
    "topology": (
        "Debate topology. Values: standard | gated | adversarial\n"
        "# - standard: agents debate freely, no validity gate\n"
        "# - gated: each turn passes through the 5-layer validity gate\n"
        "# - adversarial: gated + one agent in red-team mode"
    ),
    "providers": (
        "LLM providers. Each key is a provider name referenced by agents/judge.\n"
        "# Supported: openai, anthropic, google (Gemini), ollama (local)\n"
        "# - model: model identifier (e.g. gpt-5.4-mini, claude-sonnet-4-6)\n"
        "# - max_tokens: max output tokens per call\n"
        "# - timeout: seconds before a call times out\n"
        "# - max_retries: retry count with exponential backoff\n"
        "# - thinking: {budget_tokens: N} for Anthropic extended thinking\n"
        "# - reasoning: {effort: low|medium|high} for OpenAI o-series"
    ),
    "agents": (
        "Debate agents. Each key is the agent's display name.\n"
        "# - provider: which provider key to use for this agent\n"
        "# - side: Proponent | Skeptic | Neutral\n"
        "# - max_words: word limit per turn\n"
        "# - system_prompt: Jinja2 template. Available variables:\n"
        "#     {{ topic.name }}, {{ topic.summary }}, {{ counter_thesis }},\n"
        "#     {{ z3_stipulation }} (injected when topology is gated)"
    ),
    "convergence": (
        "When to stop the debate.\n"
        "# - max_rounds: hard cap on number of rounds\n"
        "# - no_growth_halt: stop if the ledger doesn't grow for N rounds"
    ),
    "gate": (
        "Validity gate (only for gated/adversarial topologies).\n"
        "# Checks each agent turn for: pattern violations, consistency,\n"
        "# topic drift, Z3 stipulation compliance, and entailment.\n"
        "# - max_rewrites: how many times an agent can retry a failed turn\n"
        "# - stipulated_rules: formal constraints agents must obey\n"
        "# - seed_terms: key terms with definitions for shift detection\n"
        "# - entailment_check: LLM-based semantic backstop"
    ),
    "z3": (
        "Z3 SMT verifier module.\n"
        "# - module: path to auto-generated Python file with Z3 constraints\n"
        "# The module is loaded at runtime and its verify() function is\n"
        "# called to check formal consistency of extracted claims."
    ),
    "judge": (
        "Judge panel configuration.\n"
        "# - system_prompt: instructions for the judge LLM\n"
        "# - rubric: scoring criteria (id, name, description, min, max)\n"
        "# - sides: which sides to score\n"
        "# - verdict_options: possible verdicts\n"
        "# - spread_threshold: flag if scores diverge by more than this\n"
        "# - panel: list of {provider: name} for multi-provider judging\n"
        "# - mid_debate: enable mid-debate judge signals to agents"
    ),
    "steelman": (
        "Steelman loop: iteratively strengthens the losing side's argument.\n"
        "# - max_iterations: cap on steelman refinement rounds\n"
        "# - steelman_provider: provider for generating steelman\n"
        "# - critic_provider: provider for critiquing the steelman\n"
        "# - judge_provider: provider for judging improvement"
    ),
    "retrieval": (
        "Source retrieval for grounding agent arguments.\n"
        "# - local.sources_dir: directory of source documents (TF-IDF indexed)\n"
        "# - local.k: number of local sources to retrieve per turn\n"
        "# - web.provider: web search provider (e.g. tavily)\n"
        "# - web.k: number of web results per turn"
    ),
    "output": (
        "Output configuration.\n"
        "# - dir: directory for debate output files\n"
        "# - live_log: print agent turns to console during the debate\n"
        "# - formats: output formats (json, markdown)\n"
        "# - checkpoint_db: SQLite file for crash recovery checkpoints"
    ),
}


def _inject_section_comments(yaml_text: str) -> str:
    """Insert descriptive comments above each top-level YAML section."""
    lines = yaml_text.split("\n")
    result: list[str] = []
    for line in lines:
        # Check if this line is a top-level key (no leading whitespace)
        if line and not line[0].isspace() and ":" in line:
            key = line.split(":")[0].strip()
            comment = _SECTION_COMMENTS.get(key)
            if comment:
                if result:
                    result.append("")  # blank line before section
                for cline in comment.split("\n"):
                    if cline.startswith("#"):
                        result.append(cline)
                    else:
                        result.append(f"# {cline}")
        result.append(line)
    return "\n".join(result)

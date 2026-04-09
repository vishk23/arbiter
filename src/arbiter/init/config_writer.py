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
            "provider": judge_panel[0]["provider"] if judge_panel else "openai",
        },
    }

    # -- gate ----------------------------------------------------------------
    gate: dict[str, Any] | None = None
    if gate_rules and topology in ("gated", "adversarial"):
        gate = {
            "enabled": True,
            "max_rewrites": gate_rules.get("max_rewrites", 2),
        }
        if gate_rules.get("extraction_provider"):
            gate["extraction_provider"] = gate_rules["extraction_provider"]
        if gate_rules.get("stipulated_rules"):
            gate["stipulated_rules"] = gate_rules["stipulated_rules"]
        if gate_rules.get("seed_terms"):
            gate["seed_terms"] = gate_rules["seed_terms"]
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
    out.write_text(yaml_text)
    logger.info("Config written to %s", out)
    return str(out)

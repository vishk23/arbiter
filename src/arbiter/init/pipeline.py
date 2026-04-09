"""Main orchestrator for the agentic init pipeline."""

from __future__ import annotations

import logging
import textwrap
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import TYPE_CHECKING, Any

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm, Prompt
from rich.table import Table

if TYPE_CHECKING:
    from arbiter.providers.base import BaseProvider

logger = logging.getLogger(__name__)
console = Console()


# ---------------------------------------------------------------------------
# LLM helper for topic generation (no PDF)
# ---------------------------------------------------------------------------

_TOPIC_SCHEMA = {
    "type": "object",
    "properties": {
        "name": {"type": "string", "description": "Short name for the topic."},
        "summary": {
            "type": "string",
            "description": (
                "2-4 paragraph summary of the theory or position, "
                "including its key claims and structure."
            ),
        },
        "counter_thesis": {
            "type": "string",
            "description": (
                "The strongest opposing position — what a Skeptic would argue."
            ),
        },
    },
    "required": ["name", "summary", "counter_thesis"],
}

_TOPIC_SYSTEM = textwrap.dedent("""\
    You are a research assistant helping set up a structured multi-agent
    debate.  Given a topic description, produce:
    1. A concise name
    2. A thorough summary of the position to be debated (2-4 paragraphs)
    3. The strongest counter-thesis a Skeptic would advance

    Be precise and intellectually rigorous.
""")


def _generate_topic(topic_text: str, provider: "BaseProvider") -> dict:
    """Use the LLM to flesh out a topic string into name/summary/counter."""
    result = provider.call_structured(
        system=_TOPIC_SYSTEM,
        user=f"Topic to debate:\n\n{topic_text}",
        schema=_TOPIC_SCHEMA,
        max_tokens=4000,
    )
    return result


# ---------------------------------------------------------------------------
# Default provider / rubric / agent configs
# ---------------------------------------------------------------------------

_DEFAULT_RUBRIC = [
    {
        "id": "evidence",
        "name": "Evidence Quality",
        "description": "Strength and relevance of cited evidence.",
        "min": 0,
        "max": 10,
    },
    {
        "id": "logic",
        "name": "Logical Rigour",
        "description": "Validity of logical inferences.",
        "min": 0,
        "max": 10,
    },
    {
        "id": "engagement",
        "name": "Engagement",
        "description": "How well each side addresses the other's arguments.",
        "min": 0,
        "max": 10,
    },
    {
        "id": "falsifiability",
        "name": "Falsifiability",
        "description": "Were claims advanced that are in principle falsifiable?",
        "min": 0,
        "max": 10,
    },
    {
        "id": "concession",
        "name": "Concession Honesty",
        "description": "Were genuinely-landed points conceded?",
        "min": 0,
        "max": 10,
    },
]

_DEFAULT_AGENTS: dict[str, dict[str, Any]] = {
    "Proponent": {
        "provider": "openai",
        "side": "Proponent",
        "max_words": 500,
        "system_prompt": (
            "You are the PROPONENT. Defend the position rigorously.\n"
            "Engage critics on their own terms. Concede landed hits explicitly.\n"
        ),
    },
    "Skeptic": {
        "provider": "openai",
        "side": "Skeptic",
        "max_words": 500,
        "system_prompt": (
            "You are the SKEPTIC. Challenge the theory rigorously.\n"
            "Cite primary sources. Press on falsifiability and evidence.\n"
        ),
    },
}


def _make_provider(
    provider_name: str,
    provider_model: str,
) -> "BaseProvider":
    """Instantiate a provider for the init pipeline calls."""
    from arbiter.config import ProviderConfig
    from arbiter.providers import get_provider

    # Auto-detect model-specific features
    thinking = None
    reasoning = None
    if "opus" in provider_model or "claude" in provider_model:
        thinking = {"type": "enabled", "budget_tokens": 8000}
    if "gpt-5" in provider_model or "gpt-4o" in provider_model:
        reasoning = {"effort": "high"}
    if "gemini" in provider_model:
        thinking = {"thinking_level": "HIGH"}

    pcfg = ProviderConfig(
        model=provider_model,
        max_tokens=4000,
        timeout=180,
        max_retries=6,
        thinking=thinking,
        reasoning=reasoning,
    )
    return get_provider(provider_name, pcfg)


def _make_providers_from_spec(spec: str) -> dict[str, "BaseProvider"]:
    """Parse a provider spec string into named providers.

    Formats:
        "openai:gpt-5"                → {"default": OpenAIProvider(gpt-5)}
        "openai:gpt-5,anthropic:claude-opus-4-5,gemini:gemini-3.1-pro-preview"
            → {"openai": ..., "anthropic": ..., "gemini": ...}
    """
    providers: dict[str, "BaseProvider"] = {}
    for part in spec.split(","):
        part = part.strip()
        if ":" in part:
            name, model = part.split(":", 1)
        else:
            name, model = part, ""
        if not model:
            # Default models per provider
            defaults = {
                "openai": "gpt-5",
                "anthropic": "claude-opus-4-5",
                "gemini": "gemini-3.1-pro-preview",
                "google": "gemini-3.1-pro-preview",
                "ollama": "llama3:70b",
            }
            model = defaults.get(name, name)
        providers[name] = _make_provider(name, model)
    return providers


# ---------------------------------------------------------------------------
# Interactive helpers
# ---------------------------------------------------------------------------

def _show_claims(claims: list[dict], limit: int = 5) -> None:
    """Print a Rich table of claims."""
    table = Table(title=f"Extracted Claims (showing {min(limit, len(claims))} of {len(claims)})")
    table.add_column("ID", style="bold cyan", no_wrap=True)
    table.add_column("Category", style="magenta")
    table.add_column("Formal", justify="center")
    table.add_column("Claim")
    for c in claims[:limit]:
        table.add_row(
            c["id"],
            c.get("category", "?"),
            "[green]Yes[/green]" if c.get("is_formal") else "No",
            c["claim"][:120] + ("..." if len(c["claim"]) > 120 else ""),
        )
    console.print(table)


def _show_contradictions(contradictions: list[dict], limit: int = 5) -> None:
    table = Table(title=f"Potential Contradictions ({len(contradictions)} found)")
    table.add_column("Claims", style="bold cyan", no_wrap=True)
    table.add_column("Severity", style="magenta")
    table.add_column("Z3?", justify="center")
    table.add_column("Description")
    for c in contradictions[:limit]:
        table.add_row(
            f'{c["claim_a"]} <> {c["claim_b"]}',
            c.get("severity", "?"),
            "[green]Yes[/green]" if c.get("z3_encodable") else "No",
            c["contradiction"][:120] + ("..." if len(c["contradiction"]) > 120 else ""),
        )
    console.print(table)


def _show_agents(agents: dict[str, dict]) -> None:
    table = Table(title=f"Proposed Agent Cast ({len(agents)} agents)")
    table.add_column("Name", style="bold cyan")
    table.add_column("Side", style="magenta")
    table.add_column("Provider")
    table.add_column("Role Hint")
    for name, acfg in agents.items():
        prompt_hint = acfg.get("system_prompt", "")[:80]
        table.add_row(
            name,
            acfg.get("side", "?"),
            acfg.get("provider", "?"),
            prompt_hint + ("..." if len(acfg.get("system_prompt", "")) > 80 else ""),
        )
    console.print(table)


# ---------------------------------------------------------------------------
# Pipeline
# ---------------------------------------------------------------------------

def run_init(
    from_pdf: str | None = None,
    topic: str | None = None,
    output_dir: str = ".",
    provider_name: str = "openai",
    provider_model: str = "gpt-5",
    providers_spec: str | None = None,
    interactive: bool = True,
) -> str:
    """Run the full agentic init pipeline.

    Parameters
    ----------
    providers_spec:
        Comma-separated provider:model pairs for multi-provider init.
        e.g. "openai:gpt-5,anthropic:claude-opus-4-5,gemini:gemini-3.1-pro-preview"
        When set, pipeline steps are distributed across providers for quality.
        Falls back to provider_name:provider_model if not set.

    Flow:
    1. Get topic (from PDF, from argument, or ask interactively)
    2. Extract claims
    3. Identify contradictions + key terms + attack angles
    4. Show user the findings, ask for confirmation
    5. In parallel: Z3 module, agent design, gate rules, rubric, sources
    6. Assemble config
    7. Self-test (run gate calibration if gate was generated)
    8. Print summary and path to config

    Returns path to generated config.yaml
    """
    from arbiter.init.config_writer import write_config

    out_dir = Path(output_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    console.print(
        Panel(
            "[bold]Arbiter Init Pipeline[/bold]\n"
            "Generating a complete debate configuration.",
            border_style="blue",
        )
    )

    # ── 1. Obtain providers ─────────────────────────────────────────────
    if providers_spec:
        init_providers = _make_providers_from_spec(providers_spec)
        provider_names_list = list(init_providers.keys())
        console.print(f"\n[dim]Using providers:[/dim] [bold]{', '.join(f'{k} ({v.model})' for k, v in init_providers.items())}[/bold]")
        # Primary provider for single-provider calls
        provider = list(init_providers.values())[0]
        # Distribute roles: claim extraction = first, Z3 = second (or first), agents = third, etc.
        provider_for_claims = init_providers.get("openai") or provider
        provider_for_z3 = init_providers.get("anthropic") or provider
        provider_for_agents = init_providers.get("gemini") or init_providers.get("openai") or provider
        provider_for_gate = init_providers.get("openai") or provider
        provider_for_rubric = init_providers.get("gemini") or provider
        provider_for_sources = provider  # cheapest task
    else:
        console.print(f"\n[dim]Using provider:[/dim] [bold]{provider_name}[/bold] ({provider_model})")
        provider = _make_provider(provider_name, provider_model)
        init_providers = {provider_name: provider}
        provider_names_list = [provider_name]
        provider_for_claims = provider
        provider_for_z3 = provider
        provider_for_agents = provider
        provider_for_gate = provider
        provider_for_rubric = provider
        provider_for_sources = provider

    # ── 2. Get topic text ───────────────────────────────────────────────
    source_text: str | None = None
    topic_name: str = ""
    topic_summary: str = ""
    counter_thesis: str | None = None

    if from_pdf:
        console.print(f"\n[bold blue]Step 1:[/bold blue] Reading PDF: {from_pdf}")
        from arbiter.init.pdf_reader import read_pdf

        source_text = read_pdf(from_pdf)
        console.print(f"  Extracted {len(source_text):,} characters from PDF.")
    elif topic:
        console.print(f"\n[bold blue]Step 1:[/bold blue] Generating topic summary from description")
        with console.status("[bold green]Thinking...[/bold green]"):
            topic_info = _generate_topic(topic, provider)
        topic_name = topic_info.get("name", topic)
        topic_summary = topic_info.get("summary", topic)
        counter_thesis = topic_info.get("counter_thesis")
        console.print(f"  Topic: [bold]{topic_name}[/bold]")
        console.print(f"  Summary: {topic_summary[:200]}...")
        if counter_thesis:
            console.print(f"  Counter-thesis: {counter_thesis[:200]}...")
    else:
        # Interactive: ask the user
        if interactive:
            topic_input = Prompt.ask(
                "\n[bold]Describe the topic to debate[/bold]"
            )
            console.print(f"\n[bold blue]Step 1:[/bold blue] Generating topic summary")
            with console.status("[bold green]Thinking...[/bold green]"):
                topic_info = _generate_topic(topic_input, provider)
            topic_name = topic_info.get("name", topic_input)
            topic_summary = topic_info.get("summary", topic_input)
            counter_thesis = topic_info.get("counter_thesis")
            console.print(f"  Topic: [bold]{topic_name}[/bold]")
        else:
            console.print("[red]Error: --topic or --from-pdf is required in non-interactive mode.[/red]")
            raise SystemExit(1)

    # ── 3. Extract claims ───────────────────────────────────────────────
    claims: list[dict] = []
    if source_text:
        console.print(f"\n[bold blue]Step 2:[/bold blue] Extracting claims from source text")
        from arbiter.init.pdf_reader import extract_claims

        with console.status("[bold green]Extracting claims...[/bold green]"):
            claims = extract_claims(source_text, provider_for_claims)
        console.print(f"  Found [bold]{len(claims)}[/bold] claims.")

        # Derive topic info from the first few claims if from PDF
        if not topic_name:
            # Use the LLM to name the topic from the claims
            with console.status("[bold green]Summarising topic...[/bold green]"):
                claims_text = "\n".join(
                    f'{c["id"]}: {c["claim"]}' for c in claims[:15]
                )
                topic_info = _generate_topic(
                    f"A document with these claims:\n{claims_text}",
                    provider,
                )
            topic_name = topic_info.get("name", "Unnamed Topic")
            topic_summary = topic_info.get("summary", "")
            counter_thesis = topic_info.get("counter_thesis")
            console.print(f"  Inferred topic: [bold]{topic_name}[/bold]")
    elif topic_name:
        # No source text but we have a topic -- generate synthetic claims
        console.print(f"\n[bold blue]Step 2:[/bold blue] Generating claims from topic description")
        from arbiter.init.pdf_reader import extract_claims

        with console.status("[bold green]Generating claims...[/bold green]"):
            claims = extract_claims(topic_summary, provider)
        console.print(f"  Generated [bold]{len(claims)}[/bold] claims.")

    # ── Interactive: show claims ────────────────────────────────────────
    if claims and interactive:
        _show_claims(claims)
        choice = Prompt.ask(
            "  [bold]Continue[/bold] / [bold]Show all[/bold] / [bold]Edit[/bold]?",
            choices=["continue", "show all", "edit", "c", "s", "e"],
            default="continue",
        )
        if choice in ("show all", "s"):
            _show_claims(claims, limit=len(claims))
            Prompt.ask("  Press Enter to continue")
        elif choice in ("edit", "e"):
            console.print(
                "  [dim]Claim editing is not yet implemented. "
                "You can edit the generated config.yaml after init.[/dim]"
            )

    # ── 4. Analysis: contradictions, key terms, attack angles ───────────
    contradictions: list[dict] = []
    key_terms: dict[str, str] = {}
    sides_info: dict = {"proponent_claims": [], "attack_angles": []}

    if claims:
        console.print(f"\n[bold blue]Step 3:[/bold blue] Analysing claims (contradictions, key terms, attack angles)")
        from arbiter.init.claim_extractor import (
            identify_contradictions,
            identify_key_terms,
            suggest_sides,
        )

        # Run all three in parallel
        with console.status("[bold green]Analysing...[/bold green]"):
            with ThreadPoolExecutor(max_workers=3) as pool:
                fut_contra = pool.submit(identify_contradictions, claims, provider_for_z3)
                fut_terms = pool.submit(identify_key_terms, claims, provider_for_gate)
                fut_sides = pool.submit(suggest_sides, claims, provider_for_agents)

                contradictions = fut_contra.result()
                key_terms = fut_terms.result()
                sides_info = fut_sides.result()

        console.print(f"  Contradictions: [bold]{len(contradictions)}[/bold]")
        console.print(f"  Key terms: [bold]{len(key_terms)}[/bold]")
        console.print(f"  Attack angles: [bold]{len(sides_info.get('attack_angles', []))}[/bold]")

    # ── Interactive: show contradictions ─────────────────────────────────
    use_z3 = False
    if contradictions and interactive:
        _show_contradictions(contradictions)
        z3_encodable = [c for c in contradictions if c.get("z3_encodable")]
        if z3_encodable:
            use_z3 = Confirm.ask(
                f"  {len(z3_encodable)} contradiction(s) are Z3-encodable. Generate Z3 module?",
                default=True,
            )
        else:
            console.print("  [dim]No Z3-encodable contradictions found. Skipping Z3.[/dim]")
    elif contradictions:
        # Non-interactive: auto-generate Z3 if encodable contradictions exist
        z3_encodable = [c for c in contradictions if c.get("z3_encodable")]
        use_z3 = bool(z3_encodable)

    # ── 5. Determine topology ───────────────────────────────────────────
    has_formal = any(c.get("is_formal") for c in claims) if claims else False
    topology = "standard"
    if contradictions and (use_z3 or has_formal):
        topology = "gated"
    elif contradictions:
        topology = "gated"

    if interactive and claims:
        console.print(f"\n  Suggested topology: [bold]{topology}[/bold]")
        topo_choice = Prompt.ask(
            "  Topology",
            choices=["standard", "gated", "adversarial"],
            default=topology,
        )
        topology = topo_choice

    # ── 6. Parallel generation: Z3, agents, gate, rubric, sources ───────
    console.print(f"\n[bold blue]Step 4:[/bold blue] Generating debate components")

    z3_module_path: str | None = None
    agents_result: dict[str, dict] = {}
    gate_rules: dict | None = None
    rubric: list[dict] = _DEFAULT_RUBRIC
    sources_path: str | None = None

    attack_angles = sides_info.get("attack_angles", [])

    # Build providers_config from all available init providers
    providers_config: dict[str, dict[str, Any]] = {}
    for pname, prov in init_providers.items():
        cfg = prov.config if hasattr(prov, "config") else None
        providers_config[pname] = {
            "model": prov.model,
            "max_tokens": cfg.max_tokens if cfg else 4000,
            "timeout": cfg.timeout if cfg else 180,
            "max_retries": cfg.max_retries if cfg else 6,
        }
        if cfg and cfg.thinking:
            providers_config[pname]["thinking"] = cfg.thinking
        if cfg and cfg.reasoning:
            providers_config[pname]["reasoning"] = cfg.reasoning

    futures: dict[str, Any] = {}
    with console.status("[bold green]Building config components...[/bold green]"):
        with ThreadPoolExecutor(max_workers=5) as pool:

            # Z3 module
            if use_z3:
                def _gen_z3() -> dict | None:
                    try:
                        from arbiter.init.z3_generator import generate_z3_module
                        z3_out = str(out_dir / "z3_module.py")
                        return generate_z3_module(
                            contradictions, claims, provider_for_z3, z3_out,
                        )
                    except Exception as exc:
                        logger.warning("Z3 generation failed: %s", exc)
                        return None

                futures["z3"] = pool.submit(_gen_z3)

            # Agent design
            def _gen_agents() -> dict:
                try:
                    from arbiter.init.agent_designer import design_agents
                    return design_agents(
                        claims,
                        attack_angles,
                        providers_config,
                        provider_for_agents,
                        num_agents=max(4, len(attack_angles) + 2),
                    )
                except Exception as exc:
                    logger.warning("Agent design failed, using defaults: %s", exc)
                    return {}

            futures["agents"] = pool.submit(_gen_agents)

            # Gate rules
            if topology in ("gated", "adversarial"):
                def _gen_gate() -> dict | None:
                    try:
                        from arbiter.init.gate_builder import generate_gate_rules
                        return generate_gate_rules(
                            contradictions, key_terms, provider_for_gate,
                        )
                    except Exception as exc:
                        logger.warning("Gate generation failed: %s", exc)
                        return None

                futures["gate"] = pool.submit(_gen_gate)

            # Rubric
            def _gen_rubric() -> list[dict]:
                try:
                    from arbiter.init.rubric_builder import design_rubric
                    return design_rubric(claims, attack_angles, provider_for_rubric)
                except Exception as exc:
                    logger.warning("Rubric generation failed, using defaults: %s", exc)
                    return _DEFAULT_RUBRIC

            futures["rubric"] = pool.submit(_gen_rubric)

            # Sources
            def _gen_sources() -> str | None:
                try:
                    from arbiter.init.source_finder import find_sources
                    src_dir = str(out_dir / "sources")
                    paths = find_sources(
                        claims, key_terms, src_dir, provider_for_sources,
                        web_searcher=None,
                    )
                    return src_dir if paths else None
                except Exception as exc:
                    logger.warning("Source finding failed (Tavily unavailable?): %s", exc)
                    return None

            futures["sources"] = pool.submit(_gen_sources)

        # Collect results
        for name, fut in futures.items():
            try:
                result = fut.result()
            except Exception as exc:
                logger.warning("Future '%s' raised: %s", name, exc)
                result = None

            if name == "z3" and result:
                z3_module_path = str(out_dir / "z3_module.py")
            elif name == "agents" and result:
                agents_result = result
            elif name == "gate":
                gate_rules = result
            elif name == "rubric" and result:
                rubric = result
            elif name == "sources":
                sources_path = result

    # Fall back to defaults if agent design produced nothing
    if not agents_result:
        agents_result = dict(_DEFAULT_AGENTS)
        # Update provider references
        for acfg in agents_result.values():
            acfg["provider"] = provider_name

    # If Z3 failed, downgrade to standard if no gate rules either
    if topology == "gated" and not gate_rules and not z3_module_path:
        console.print(
            "  [yellow]No gate rules or Z3 module generated. "
            "Falling back to standard topology.[/yellow]"
        )
        topology = "standard"

    # Ensure all agent provider refs exist in providers_config
    for acfg in agents_result.values():
        pname = acfg.get("provider", provider_name)
        if pname not in providers_config:
            providers_config[pname] = {
                "model": provider_model,
                "max_tokens": 4000,
                "timeout": 180,
                "max_retries": 6,
            }

    # ── Interactive: show agents ────────────────────────────────────────
    if interactive:
        _show_agents(agents_result)
        choice = Prompt.ask(
            "  [bold]Continue[/bold] / [bold]Edit[/bold]?",
            choices=["continue", "edit", "c", "e"],
            default="continue",
        )
        if choice in ("edit", "e"):
            console.print(
                "  [dim]Agent editing is not yet implemented. "
                "Edit the generated config.yaml after init.[/dim]"
            )

    # ── 7. Build judge panel from available providers ───────────────────
    judge_panel = [{"provider": p} for p in providers_config]

    # ── 8. Steelman config ──────────────────────────────────────────────
    steelman: dict | None = None
    provider_names = list(providers_config.keys())
    if len(provider_names) >= 2:
        steelman = {
            "enabled": True,
            "max_iterations": 4,
            "steelman_provider": provider_names[0],
            "critic_provider": provider_names[-1],
            "judge_provider": provider_names[0],
        }
    else:
        steelman = {
            "enabled": True,
            "max_iterations": 4,
            "steelman_provider": provider_names[0],
            "critic_provider": provider_names[0],
            "judge_provider": provider_names[0],
        }

    # ── 9. Privileged context ───────────────────────────────────────────
    privileged_context: dict[str, str] = {}
    if counter_thesis:
        # Give the Skeptic the counter-thesis as privileged context
        privileged_context["Skeptic"] = (
            f"PRIVILEGED CONTEXT (only Skeptic sees this):\n\n"
            f"Counter-thesis: {counter_thesis}\n"
        )

    # ── 10. Write config ────────────────────────────────────────────────
    config_path = str(out_dir / "config.yaml")
    console.print(f"\n[bold blue]Step 5:[/bold blue] Writing config")

    config_path = write_config(
        output_path=config_path,
        topic_name=topic_name,
        topic_summary=topic_summary,
        counter_thesis=counter_thesis,
        privileged_context=privileged_context,
        topology=topology,
        providers_config=providers_config,
        agents=agents_result,
        gate_rules=gate_rules,
        z3_module_path=z3_module_path,
        rubric=rubric,
        judge_panel=judge_panel,
        sources_dir=sources_path,
        convergence={"max_rounds": 6, "no_growth_halt": 2},
        steelman=steelman,
    )

    # ── 11. Self-test: validate the config we just wrote ────────────────
    console.print(f"\n[bold blue]Step 6:[/bold blue] Validating generated config")
    try:
        from arbiter.config import load_config

        load_config(Path(config_path))
        console.print("  [green]Config validation passed.[/green]")
    except Exception as exc:
        console.print(f"  [yellow]Config validation warning: {exc}[/yellow]")
        console.print(
            "  [dim]The config may need manual adjustments. "
            "Check provider references and agent settings.[/dim]"
        )

    # ── 12. Summary ─────────────────────────────────────────────────────
    console.print()
    summary_table = Table(title="Init Summary", border_style="green")
    summary_table.add_column("Item", style="bold")
    summary_table.add_column("Value")
    summary_table.add_row("Topic", topic_name)
    summary_table.add_row("Topology", topology)
    summary_table.add_row("Claims extracted", str(len(claims)))
    summary_table.add_row("Contradictions", str(len(contradictions)))
    summary_table.add_row("Agents", str(len(agents_result)))
    summary_table.add_row("Z3 module", z3_module_path or "None")
    summary_table.add_row("Gate rules", "Yes" if gate_rules else "No")
    summary_table.add_row("Sources dir", sources_path or "None")
    summary_table.add_row("Config path", config_path)
    console.print(summary_table)

    console.print(
        f"\n[green bold]Config written to {config_path}[/green bold]"
    )
    console.print(
        f"Run with: [bold]arbiter run {config_path}[/bold]\n"
    )

    return config_path

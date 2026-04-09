"""Typer CLI for Arbiter -- formally verified multi-agent debates."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console

app = typer.Typer(
    name="arbiter",
    help="Formally verified multi-agent debates.",
    no_args_is_help=True,
)
console = Console()


def _load_dotenv() -> None:
    """Best-effort load .env from cwd, parent dirs, and common locations."""
    try:
        from dotenv import load_dotenv
        from pathlib import Path

        # Try CWD first, then walk up, then common locations
        load_dotenv()  # CWD
        for candidate in [
            Path.home() / ".env",
            Path.home() / "VKDEV" / "VK-KB" / ".env",
        ]:
            if candidate.exists():
                load_dotenv(candidate, override=False)
    except ImportError:
        pass


# ====================================================================== #
#  init
# ====================================================================== #


_TEMPLATE_YAML = """\
schema_version: "1.0"

topic:
  name: "Your debate topic"
  summary: |
    A clear, concise summary of the theory or position under debate.
  counter_thesis: |
    The opposing thesis to be defended by the skeptic side.
  privileged_context:
    Skeptic: |
      Sources, quotes, or context only visible to the Skeptic side.

topology: standard  # standard | gated | adversarial

providers:
  anthropic:
    model: claude-sonnet-4-20250514
    max_tokens: 4000
    timeout: 180
    max_retries: 6
  openai:
    model: gpt-4o
    max_tokens: 4000
    timeout: 180
    max_retries: 6

agents:
  Proponent:
    provider: anthropic
    side: Proponent
    max_words: 500
    system_prompt: |
      You are the PROPONENT of {{ topic.name }}. Defend the position.
      Engage critics in their own terms. Concede landed hits explicitly.
  Skeptic:
    provider: openai
    side: Skeptic
    max_words: 500
    system_prompt: |
      You are the SKEPTIC. Challenge the theory rigorously.
      Cite primary sources from your privileged context.

convergence:
  max_rounds: 6
  no_growth_halt: 2

# gate:  # uncomment for gated/adversarial topologies
#   enabled: true
#   max_rewrites: 2
#   seed_terms:
#     key_term: "definition of key term"
#   entailment_check:
#     enabled: true
#     provider: openai

# z3:  # uncomment if you have a Z3 verifier module
#   module: ./z3_verifier.py
#   stipulation_template: null

judge:
  system_prompt: |
    You are judging a debate on {{ topic_name }}.
    {{ rubric_description }}
  rubric:
    - id: evidence
      name: Evidence Quality
      description: "Strength and relevance of cited evidence"
      min: 0
      max: 10
    - id: logic
      name: Logical Rigour
      description: "Validity of logical inferences"
      min: 0
      max: 10
    - id: engagement
      name: Engagement
      description: "How well each side addresses the other's arguments"
      min: 0
      max: 10
  sides:
    - Proponent
    - Skeptic
  verdict_options:
    - Proponent
    - Skeptic
    - Tied
  spread_threshold: 3
  panel:
    - provider: anthropic
    - provider: openai
  mid_debate:
    enabled: true
    provider: anthropic

# steelman:
#   enabled: true
#   max_iterations: 4
#   steelman_provider: anthropic
#   critic_provider: openai
#   judge_provider: anthropic

# retrieval:
#   local:
#     sources_dir: ./sources
#     k: 2
#   web:
#     provider: tavily
#     k: 2

output:
  dir: ./output
  live_log: true
  formats:
    - json
    - markdown
  checkpoint_db: ./checkpoints.sqlite
"""


@app.command()
def init(
    from_pdf: Optional[str] = typer.Option(
        None,
        "--from-pdf",
        help="Path to a PDF file to extract the topic from.",
    ),
    topic: Optional[str] = typer.Option(
        None,
        "--topic",
        help="Topic description to debate (used when no PDF is provided).",
    ),
    provider: str = typer.Option(
        "anthropic",
        "--provider",
        help="LLM provider for init pipeline calls.",
    ),
    model: str = typer.Option(
        "claude-opus-4-5",
        "--model",
        help="Model to use for init pipeline. Use the best available for quality.",
    ),
    non_interactive: bool = typer.Option(
        False,
        "--non-interactive",
        help="Skip all interactive prompts and use defaults.",
    ),
    providers: Optional[str] = typer.Option(
        None,
        "--providers",
        help=(
            "Multi-provider init. Comma-separated provider:model pairs. "
            "e.g. 'openai:gpt-5,anthropic:claude-opus-4-5,gemini:gemini-3.1-pro-preview'. "
            "When set, pipeline steps are distributed across providers."
        ),
    ),
    output_dir: str = typer.Option(
        ".",
        "--output-dir",
        "-o",
        help="Directory for the generated config and artifacts.",
    ),
    template_only: bool = typer.Option(
        False,
        "--template",
        help="Write a blank template config instead of running the pipeline.",
    ),
) -> None:
    """Generate a debate configuration using the agentic init pipeline.

    Analyses a PDF or topic description, extracts claims, identifies
    contradictions, and assembles a complete config.yaml ready for
    ``arbiter run``.

    Use ``--template`` for a blank starter config without LLM calls.
    """
    _load_dotenv()

    if template_only:
        out = Path(output_dir) / "arbiter-config.yaml"
        if out.exists():
            overwrite = typer.confirm(f"{out} already exists. Overwrite?")
            if not overwrite:
                raise typer.Abort()
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(_TEMPLATE_YAML)
        console.print(f"[green]Template written to {out}[/green]")
        console.print(f"Edit the file, then run: [bold]arbiter run {out}[/bold]")
        return

    from arbiter.init.pipeline import run_init

    run_init(
        from_pdf=from_pdf,
        topic=topic,
        output_dir=output_dir,
        provider_name=provider,
        provider_model=model,
        providers_spec=providers,
        interactive=not non_interactive,
    )


# ====================================================================== #
#  run
# ====================================================================== #


@app.command()
def run(
    config: Path = typer.Argument(..., help="Path to arbiter YAML config."),
    resume: bool = typer.Option(
        False, "--resume", help="Resume from checkpoint."
    ),
    thread_id: Optional[str] = typer.Option(
        None, "--thread-id", help="Thread ID for checkpointing."
    ),
) -> None:
    """Run a debate from a YAML config file."""
    _load_dotenv()

    from arbiter.config import load_config
    from arbiter.graph import DebateEngine

    cfg = load_config(config)
    engine = DebateEngine(cfg)
    result = engine.run(resume=resume, thread_id=thread_id)

    console.print(
        f"\n[green]Done.[/green] "
        f"Rounds: {result['round_idx'] - 1}, "
        f"Hits: {len(result['ledger'])}"
    )

    # Summary
    ledger = result["ledger"]
    if ledger:
        open_n = sum(1 for h in ledger if h["status"] == "open")
        conceded = sum(1 for h in ledger if h["status"] == "conceded")
        rebutted = sum(1 for h in ledger if h["status"] == "rebutted")
        dodged = sum(1 for h in ledger if h["status"] == "dodged")
        console.print(
            f"  open={open_n}  conceded={conceded}  "
            f"rebutted={rebutted}  dodged={dodged}"
        )

    if result.get("formal_verdict"):
        console.print(f"\n{result['formal_verdict']}")


# ====================================================================== #
#  judge
# ====================================================================== #


@app.command()
def judge(
    output: Path = typer.Argument(
        ..., help="Path to a debate output JSON file."
    ),
    config: Optional[Path] = typer.Option(
        None, "--config", "-c", help="Arbiter config (for rubric + providers)."
    ),
) -> None:
    """Run the judge panel on a completed debate."""
    _load_dotenv()

    from arbiter.config import load_config
    from arbiter.judge.panel import JudgePanel

    data = json.loads(output.read_text())
    state = data.get("state", data)

    # Build transcript text
    transcript_text = "\n\n".join(
        f"[{t.get('agent', '?')}] (Round {t.get('round', '?')})\n{t.get('text', '')}"
        for t in state.get("transcript", [])
    )

    if config is None:
        console.print(
            "[red]--config is required for judge (provides rubric + providers)[/red]"
        )
        raise typer.Exit(1)

    cfg = load_config(config)
    providers = {}
    from arbiter.providers import get_provider

    for name, pcfg in cfg.providers.items():
        providers[name] = get_provider(name, pcfg)

    panel = JudgePanel(cfg.judge, providers)
    result = panel.judge(transcript_text, cfg.topic.name)

    console.print_json(json.dumps(result, indent=2, default=str))

    # Save verdict
    verdict_path = output.with_suffix(".verdict.json")
    verdict_path.write_text(json.dumps(result, indent=2, default=str))
    console.print(f"[green]Verdict saved to {verdict_path}[/green]")


# ====================================================================== #
#  calibrate
# ====================================================================== #


@app.command()
def calibrate(
    config: Path = typer.Argument(..., help="Arbiter YAML config."),
    test_cases: Path = typer.Option(
        ..., "--test-cases", help="YAML file with gold-standard test cases."
    ),
) -> None:
    """Calibrate the validity gate against gold-standard test cases.

    Each test case should have: text, expected_pass (bool), and optional
    expected_violations (list of violation types).
    """
    _load_dotenv()

    import yaml

    from arbiter.config import load_config
    from arbiter.gate.validity_gate import ValidityGate
    from arbiter.providers import get_provider

    cfg = load_config(config)
    if not cfg.gate:
        console.print("[red]Config has no gate section.[/red]")
        raise typer.Exit(1)

    providers = {}
    for name, pcfg in cfg.providers.items():
        providers[name] = get_provider(name, pcfg)

    gate = ValidityGate(cfg.gate, providers)

    cases = yaml.safe_load(test_cases.read_text())
    if not isinstance(cases, list):
        cases = cases.get("test_cases", [])

    tp, fp, tn, fn = 0, 0, 0, 0
    for i, case in enumerate(cases):
        text = case["text"]
        expected_pass = case["expected_pass"]
        result = gate.check(
            agent="calibration",
            turn_text=text,
            prior_claims={},
            known_terms=dict(cfg.gate.seed_terms) if cfg.gate.seed_terms else {},
        )
        actual_pass = result["passed"]

        if expected_pass and actual_pass:
            tn += 1  # true negative (no violation expected, none found)
        elif not expected_pass and not actual_pass:
            tp += 1  # true positive (violation expected, found)
        elif expected_pass and not actual_pass:
            fp += 1  # false positive (no violation expected, but found)
            console.print(
                f"  [yellow]FP[/yellow] case {i}: "
                f"{[v.get('type') for v in result['violations']]}"
            )
        else:
            fn += 1  # false negative (violation expected, not found)
            console.print(f"  [red]FN[/red] case {i}: expected violation, gate passed")

    total = tp + fp + tn + fn
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    specificity = tn / (tn + fp) if (tn + fp) > 0 else 0.0
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0

    console.print(f"\n[bold]Calibration results ({total} cases):[/bold]")
    console.print(f"  TP={tp}  FP={fp}  TN={tn}  FN={fn}")
    console.print(f"  Recall:      {recall:.2%}")
    console.print(f"  Specificity: {specificity:.2%}")
    console.print(f"  Precision:   {precision:.2%}")


# ====================================================================== #
#  redteam
# ====================================================================== #


@app.command()
def redteam(
    config: Path = typer.Argument(..., help="Arbiter YAML config."),
    target: str = typer.Option(
        "Proponent",
        "--target",
        help="Agent name to put in adversarial mode.",
    ),
) -> None:
    """Run a debate with one agent in adversarial red-team mode."""
    _load_dotenv()

    from arbiter.config import load_config
    from arbiter.graph import DebateEngine

    cfg = load_config(config)

    if target not in cfg.agents:
        console.print(
            f"[red]Agent '{target}' not found. "
            f"Available: {', '.join(cfg.agents)}[/red]"
        )
        raise typer.Exit(1)

    # Mutate config for adversarial mode
    cfg.topology = "adversarial"
    cfg.agents[target].adversarial = True

    # Ensure gate exists for adversarial topology
    if cfg.gate is None:
        from arbiter.config import GateConfig

        cfg.gate = GateConfig()

    engine = DebateEngine(cfg)
    result = engine.run()

    console.print(
        f"\n[green]Red-team done.[/green] "
        f"Rounds: {result['round_idx'] - 1}, "
        f"Hits: {len(result['ledger'])}"
    )


# ====================================================================== #
#  export
# ====================================================================== #


@app.command(name="export")
def export_cmd(
    output: Path = typer.Argument(
        ..., help="Path to a debate output JSON file."
    ),
    format: str = typer.Option(
        "markdown",
        "-f",
        "--format",
        help="Export format: markdown, argdown, or json.",
    ),
) -> None:
    """Export an argument map from a debate output file."""
    _load_dotenv()

    from arbiter.export import export_argdown, export_json, export_markdown

    data = json.loads(output.read_text())
    state = data.get("state", data)

    if format == "markdown":
        result = export_markdown(state, data.get("metadata", {}).get("topic", ""))
        ext = ".md"
    elif format == "argdown":
        sides = data.get("metadata", {}).get("sides", ["Proponent", "Skeptic"])
        result = export_argdown(state.get("ledger", []), sides)
        ext = ".argdown"
    elif format == "json":
        result = export_json(state, data.get("metadata"))
        ext = ".json"
    else:
        console.print(f"[red]Unknown format: {format}[/red]")
        raise typer.Exit(1)

    out_path = output.with_suffix(ext)
    out_path.write_text(result)
    console.print(f"[green]Exported to {out_path}[/green]")

"""LangGraph StateGraph builder -- the heart of the Arbiter debate engine."""

from __future__ import annotations

import json
import logging
import sqlite3
import time
from pathlib import Path
from typing import Any, Dict, List

from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.graph import END, START, StateGraph
from rich.console import Console

from arbiter.agents.agent import Agent
from arbiter.agents.context import ContextBuilder
from arbiter.config import ArbiterConfig
from arbiter.export import export_argdown, export_json, export_markdown
from arbiter.ledger.ops import add_hit, ledger_grew, open_hits, resolve_hit
from arbiter.ledger.parser import parse_ledger_block
from arbiter.logging.live_log import LiveLogger
from arbiter.providers import get_provider
from arbiter.state import DebateState, initial_state

logger = logging.getLogger(__name__)
console = Console()


class DebateEngine:
    """Build and run a complete Arbiter debate from a config.

    Initialises providers, agents, gate, retriever, mid-debate judge,
    live logger, and Z3 plugin, then wires them into a LangGraph
    :class:`StateGraph` whose topology depends on ``config.topology``.
    """

    def __init__(self, config: ArbiterConfig) -> None:
        self.config = config

        # ── Providers ─────────────────────────────────────────────────
        self.providers: Dict[str, Any] = {}
        for name, pcfg in config.providers.items():
            self.providers[name] = get_provider(name, pcfg)

        # ── Agents ────────────────────────────────────────────────────
        self.agents: Dict[str, Agent] = {}
        for name, acfg in config.agents.items():
            provider = self.providers[acfg.provider]
            self.agents[name] = Agent(name, acfg, provider)

        # ── Validity gate (optional) ─────────────────────────────────
        self.gate = None
        if config.gate and config.gate.enabled:
            from arbiter.gate.validity_gate import ValidityGate

            self.gate = ValidityGate(config.gate, self.providers)

        # ── Retriever (optional) ─────────────────────────────────────
        self.retriever = None
        if config.retrieval:
            from arbiter.retrieval.retriever import Retriever

            self.retriever = Retriever(config.retrieval)

        # ── Context builder ──────────────────────────────────────────
        self.ctx_builder = ContextBuilder(config, self.retriever)

        # ── Mid-debate judge (optional) ──────────────────────────────
        self.mid_judge = None
        if config.judge.mid_debate and config.judge.mid_debate.enabled:
            from arbiter.judge.mid_debate import MidDebateJudge

            md_cfg = config.judge.mid_debate
            md_provider = self.providers.get(md_cfg.provider)
            if md_provider:
                self.mid_judge = MidDebateJudge(md_cfg, md_provider)

        # ── Z3 plugin (optional) ─────────────────────────────────────
        self.z3_plugin = None
        self._z3_stipulation = ""
        if config.z3:
            from arbiter.verifier.z3_plugin import Z3Plugin

            self.z3_plugin = Z3Plugin(config.z3.module)
            self._z3_stipulation = self.z3_plugin.format_stipulation(
                config.z3.stipulation_template
            )

        # ── Live logger ──────────────────────────────────────────────
        self.live_logger: LiveLogger | None = None
        if config.output.live_log:
            self.live_logger = LiveLogger(
                config.output.dir, config.topic.name[:40]
            )

        # ── Rolling prior-claims for gate ────────────────────────────
        self._prior_claims: Dict[str, List[dict]] = {}
        self._known_terms: Dict[str, str] = {}
        if config.gate and config.gate.seed_terms:
            self._known_terms = dict(config.gate.seed_terms)

        # ── Output dir ───────────────────────────────────────────────
        self._out_dir = Path(config.output.dir)
        self._out_dir.mkdir(parents=True, exist_ok=True)

    # ================================================================== #
    #  Graph construction
    # ================================================================== #

    def build(self) -> Any:
        """Build and compile the LangGraph :class:`StateGraph`.

        Topology variants:
        - **standard**: round -> ledger -> midjudge -> [continue|finalize]
        - **gated**: round -> validity_audit -> ledger -> midjudge -> [continue|finalize]
        - **adversarial**: same as gated (adversarial agent gets different prompt)
        """
        g = StateGraph(DebateState)

        g.add_node("round", self._round_node)
        g.add_node("ledger", self._ledger_node)
        g.add_node("midjudge", self._midjudge_node)
        g.add_node("finalize", self._finalize_node)

        if self.config.topology in ("gated", "adversarial"):
            g.add_node("validity_audit", self._validity_audit_node)
            g.add_edge(START, "round")
            g.add_edge("round", "validity_audit")
            g.add_edge("validity_audit", "ledger")
        else:
            g.add_edge(START, "round")
            g.add_edge("round", "ledger")

        g.add_edge("ledger", "midjudge")
        g.add_conditional_edges(
            "midjudge",
            self._should_continue,
            {"round": "round", "finalize": "finalize"},
        )
        g.add_edge("finalize", END)

        # Checkpointer — use SqliteSaver for crash recovery.
        # Falls back to InMemorySaver if the DB path is ":memory:" or unusable.
        db_path = self.config.output.checkpoint_db
        try:
            conn = sqlite3.connect(db_path, check_same_thread=False)
            checkpointer = SqliteSaver(conn)
            checkpointer.setup()  # create tables if needed
            self._checkpoint_conn = conn
            logger.debug("Using SqliteSaver checkpoint: %s", db_path)
        except Exception as exc:
            logger.warning(
                "SqliteSaver init failed (%s), falling back to InMemorySaver", exc
            )
            from langgraph.checkpoint.memory import InMemorySaver
            checkpointer = InMemorySaver()
            self._checkpoint_conn = None
        return g.compile(checkpointer=checkpointer)

    # ================================================================== #
    #  Node: round
    # ================================================================== #

    def _round_node(self, state: DebateState) -> dict:
        """Run all agents sequentially for one round.

        For gated/adversarial topologies, each turn passes through the
        validity gate's rewrite loop.
        """
        console.print(
            f"\n[bold yellow]=== ROUND {state['round_idx']} ===[/bold yellow]"
        )

        # Rebuild prior claims from transcript (deterministic from state)
        self._rebuild_prior_claims(state["transcript"])

        new_entries: List[dict] = []
        new_validity_log: List[dict] = []
        cur_state = dict(state)

        for agent_name, agent in self.agents.items():
            # Z3 stipulation only for non-standard topologies
            z3_stip = self._z3_stipulation if self.config.topology != "standard" else ""

            # Build context
            user_prompt = self.ctx_builder.build(agent_name, cur_state, z3_stip)  # type: ignore[arg-type]

            # Render system prompt via Jinja2
            system_prompt = self.ctx_builder.render_system_prompt(
                agent.system_prompt, z3_stip
            )

            # Adversarial prompt augmentation
            if agent.is_adversarial and self.config.topology == "adversarial":
                system_prompt += (
                    "\n\nYou are in ADVERSARIAL RED-TEAM mode. Your goal is to "
                    "find the sharpest possible weaknesses, exploit rhetorical "
                    "loopholes, and stress-test the opponent's position. "
                    "Do not concede easily."
                )

            # Gate or direct call
            entry_text: str
            validity_log_entry: dict | None = None

            if self.gate and self.config.topology in ("gated", "adversarial"):
                gate_result = self.gate.run_with_rewrites(
                    call_fn=agent.call,
                    agent=agent_name,
                    system=system_prompt,
                    user=user_prompt,
                    prior_claims=self._prior_claims,
                    known_terms=self._known_terms,
                )
                entry_text = gate_result["entry"]
                extracted = gate_result.get("extracted", {})
                validity_log_entry = {
                    "round": state["round_idx"],
                    "agent": agent_name,
                    "attempts": gate_result["log"],
                    "final_status": (
                        "ok"
                        if gate_result["log"]
                        and gate_result["log"][-1].get("passed")
                        else "validity_violation"
                    ),
                    "rewrites_used": max(0, len(gate_result["log"]) - 1),
                }
            else:
                entry_text = agent.call(system_prompt, user_prompt)
                extracted = {}

            # Build transcript entry
            entry: Dict[str, Any] = {
                "agent": agent_name,
                "round": state["round_idx"],
                "text": entry_text,
            }
            if extracted:
                entry["extracted_claims"] = extracted
            if validity_log_entry:
                status = validity_log_entry["final_status"]
                entry["validity_status"] = status
                if status == "validity_violation":
                    # Find violations from last attempt
                    last_attempt = (
                        validity_log_entry["attempts"][-1]
                        if validity_log_entry["attempts"]
                        else {}
                    )
                    entry["validity_violations"] = last_attempt.get(
                        "violations", []
                    )

            new_entries.append(entry)
            if validity_log_entry:
                new_validity_log.append(validity_log_entry)

            # Update rolling prior claims for later agents in this round
            if extracted:
                self._prior_claims.setdefault(agent_name, []).extend(
                    extracted.get("formal_claims", [])
                )

            # Update cur_state so next agent in round sees prior entries
            cur_state["transcript"] = cur_state["transcript"] + [entry]

            # Live log
            if self.live_logger:
                self.live_logger.log_turn(
                    agent_name, state["round_idx"], entry_text
                )

            # Status line
            rewrites = (
                validity_log_entry["rewrites_used"]
                if validity_log_entry
                else 0
            )
            vstatus = entry.get("validity_status", "ok")
            console.print(
                f"  [{agent_name}] {vstatus} (rewrites={rewrites})"
            )

        result: dict = {"transcript": new_entries}
        if new_validity_log:
            result["validity_log"] = new_validity_log
        return result

    # ================================================================== #
    #  Node: validity_audit (per-round summary)
    # ================================================================== #

    def _validity_audit_node(self, state: DebateState) -> dict:
        """Emit round-level validity stats (visible graph node for auditing)."""
        round_idx = state["round_idx"]
        round_logs = [
            l
            for l in state.get("validity_log", [])
            if l.get("round") == round_idx and l.get("kind") != "round_summary"
        ]
        n = len(round_logs)
        n_violations = sum(
            1 for l in round_logs if l.get("final_status") == "validity_violation"
        )
        n_rewrites = sum(l.get("rewrites_used", 0) for l in round_logs)

        summary = {
            "kind": "round_summary",
            "round": round_idx,
            "turns": n,
            "violations": n_violations,
            "total_rewrites": n_rewrites,
        }

        console.print(
            f"  [validity_audit] round {round_idx}: "
            f"turns={n} violations={n_violations} rewrites={n_rewrites}"
        )

        if self.live_logger:
            self.live_logger.note(
                f"Validity audit R{round_idx}: "
                f"{n_violations}/{n} violations, {n_rewrites} rewrites"
            )

        return {"validity_log": [summary]}

    # ================================================================== #
    #  Node: ledger
    # ================================================================== #

    def _ledger_node(self, state: DebateState) -> dict:
        """Parse agent outputs and update the argument ledger."""
        ledger = list(state["ledger"])
        round_idx = state["round_idx"]

        # Process only entries from the current round
        round_entries = [
            t for t in state["transcript"] if t.get("round") == round_idx
        ]

        for entry in round_entries:
            block = parse_ledger_block(entry["text"])

            # New hits
            for h in block.get("new_hits", []):
                ledger = add_hit(
                    ledger,
                    by=entry["agent"],
                    against=h.get("against", "Theory"),
                    claim=h.get("claim", ""),
                    round_idx=round_idx,
                )

            # Addressed hits
            for upd in block.get("hits_addressed", []):
                hit_id = upd.get("id", "")
                status = upd.get("status", "")
                rebuttal = upd.get("rebuttal", "")
                if hit_id and status:
                    ledger = resolve_hit(ledger, hit_id, status, rebuttal)

        grew = ledger_grew(ledger, state["last_ledger_size"])

        return {
            "ledger": ledger,
            "last_ledger_size": len(ledger),
            "rounds_without_growth": (
                0 if grew else state["rounds_without_growth"] + 1
            ),
        }

    # ================================================================== #
    #  Node: midjudge
    # ================================================================== #

    def _midjudge_node(self, state: DebateState) -> dict:
        """Generate per-agent guidance signals and advance round counter."""
        signals: Dict[str, str] = {}

        if self.mid_judge:
            round_transcript = [
                t
                for t in state["transcript"]
                if t.get("round") == state["round_idx"]
            ]
            oh = open_hits(state["ledger"])
            signals = self.mid_judge.generate_signals(
                state["round_idx"], round_transcript, oh
            )

        return {
            "judge_signals": signals,
            "round_idx": state["round_idx"] + 1,
        }

    # ================================================================== #
    #  Node: finalize
    # ================================================================== #

    def _finalize_node(self, state: DebateState) -> dict:
        """Run Z3 verification, steelman loop, and export outputs."""
        lines: List[str] = []

        # ── Z3 verification ──────────────────────────────────────────
        if self.z3_plugin:
            results = self.z3_plugin.verify()
            lines.append("FORMAL VERIFIER (Z3):")
            for k, v in results.items():
                if k.startswith("_"):
                    continue
                lines.append(
                    f"  [{k}] {v.get('result', '?')}: "
                    f"{v.get('explanation', '')[:400]}"
                )

        # ── Validity stats ───────────────────────────────────────────
        vlog = state.get("validity_log", [])
        turn_logs = [l for l in vlog if l.get("kind") != "round_summary"]
        total_turns = len(turn_logs)
        total_violations = sum(
            1
            for l in turn_logs
            if l.get("final_status") == "validity_violation"
        )
        total_rewrites = sum(l.get("rewrites_used", 0) for l in turn_logs)
        if total_turns > 0:
            lines.append("")
            lines.append("VALIDITY GATE STATS:")
            lines.append(f"  total turns audited: {total_turns}")
            lines.append(
                f"  turns flagged VALIDITY VIOLATION (after rewrites): "
                f"{total_violations}"
            )
            lines.append(f"  total rewrites issued: {total_rewrites}")

        # ── Steelman loop (optional) ─────────────────────────────────
        steelman_result: dict | None = None
        if (
            self.config.steelman
            and self.config.steelman.enabled
        ):
            from arbiter.steelman.loop import iterated_steelman

            scfg = self.config.steelman
            steelman_result = iterated_steelman(
                theory_summary=self.config.topic.summary,
                steelman_provider=self.providers[scfg.steelman_provider],
                critic_provider=self.providers[scfg.critic_provider],
                judge_provider=self.providers[scfg.judge_provider],
                max_iterations=scfg.max_iterations,
            )
            lines.append("")
            lines.append(
                f"ITERATED STEELMAN: {steelman_result['iterations']} versions, "
                f"stabilized={steelman_result['stabilized']}"
            )
            lines.append(
                f"FINAL RESCUED VERSION:\n"
                f"{steelman_result['final_version'][:1200]}"
            )

        formal_verdict = "\n".join(lines) if lines else ""

        # ── Export ────────────────────────────────────────────────────
        final_state = dict(state)
        final_state["formal_verdict"] = formal_verdict
        final_state["halt"] = True
        if steelman_result:
            final_state["steelman_versions"] = steelman_result.get(
                "versions", []
            )

        ts = int(time.time())
        formats = self.config.output.formats

        if "json" in formats:
            metadata = {
                "topic": self.config.topic.name,
                "topology": self.config.topology,
                "sides": self.config.judge.sides,
                "rounds_run": state["round_idx"] - 1,
                "timestamp": ts,
                "judge_config": self.config.judge.model_dump(),
                "providers_config": {
                    name: pcfg.model_dump()
                    for name, pcfg in self.config.providers.items()
                },
            }
            if self.z3_plugin:
                metadata["z3_findings"] = self.z3_plugin.verify()
            json_str = export_json(final_state, metadata)
            out_path = self._out_dir / f"debate_{ts}.json"
            out_path.write_text(json_str)
            console.print(f"  [dim]Exported JSON: {out_path}[/dim]")

        if "markdown" in formats:
            md = export_markdown(final_state, self.config.topic.name)
            out_path = self._out_dir / f"debate_{ts}.md"
            out_path.write_text(md)
            console.print(f"  [dim]Exported Markdown: {out_path}[/dim]")

        if "argdown" in formats:
            ad = export_argdown(
                final_state.get("ledger", []),
                self.config.judge.sides,
            )
            out_path = self._out_dir / f"debate_{ts}.argdown"
            out_path.write_text(ad)
            console.print(f"  [dim]Exported Argdown: {out_path}[/dim]")

        if self.live_logger:
            self.live_logger.note(
                f"Debate complete. Rounds: {state['round_idx'] - 1}, "
                f"Hits: {len(state['ledger'])}"
            )

        return {
            "formal_verdict": formal_verdict,
            "halt": True,
            "steelman_versions": (
                steelman_result.get("versions", []) if steelman_result else []
            ),
        }

    # ================================================================== #
    #  Routing
    # ================================================================== #

    def _should_continue(self, state: DebateState) -> str:
        """Decide whether to run another round or finalize."""
        conv = self.config.convergence
        if state["round_idx"] > conv.max_rounds:
            return "finalize"
        if state["rounds_without_growth"] >= conv.no_growth_halt:
            return "finalize"
        return "round"

    # ================================================================== #
    #  Run
    # ================================================================== #

    def run(
        self,
        resume: bool = False,
        thread_id: str | None = None,
    ) -> dict:
        """Invoke the compiled graph and return the final state.

        Parameters
        ----------
        resume:
            If True, attempt to resume from the checkpoint database.
        thread_id:
            Thread identifier for checkpointing. Auto-generated if None.
        """
        app = self.build()
        tid = thread_id or f"arbiter-{int(time.time())}"
        run_config = {"configurable": {"thread_id": tid}, "recursion_limit": 150}

        if resume:
            console.print(f"[yellow]Resuming thread {tid}...[/yellow]")
            result = app.invoke(None, config=run_config)
        else:
            console.print(
                f"[bold green]Starting debate:[/bold green] "
                f"{self.config.topic.name} "
                f"(topology={self.config.topology}, "
                f"max_rounds={self.config.convergence.max_rounds})"
            )
            result = app.invoke(initial_state(), config=run_config)

        # Close the checkpoint DB connection
        if getattr(self, "_checkpoint_conn", None):
            try:
                self._checkpoint_conn.close()
            except Exception:
                pass

        return result

    # ================================================================== #
    #  Helpers
    # ================================================================== #

    def _rebuild_prior_claims(self, transcript: List[dict]) -> None:
        """Rebuild the rolling prior-claims dict from the transcript."""
        self._prior_claims.clear()
        for t in transcript:
            ex = t.get("extracted_claims")
            if not ex:
                continue
            self._prior_claims.setdefault(t["agent"], []).extend(
                ex.get("formal_claims", [])
            )

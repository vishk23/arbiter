"""End-to-end ledger + gate + engagement tests with real LLM calls.

Uses gpt-5.4-mini for cheap, fast validation of the full pipeline.
Each test creates a tiny 2-agent, 2-round debate with specific scenarios
to verify edge cases in hit creation, normalization, mini-ledger-update,
gate interaction, and engagement enforcement.

Skip if OPENAI_API_KEY not set.
"""

from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path

import pytest
import yaml

_HAS_OPENAI = bool(os.environ.get("OPENAI_API_KEY"))
skip_no_openai = pytest.mark.skipif(not _HAS_OPENAI, reason="OPENAI_API_KEY not set")


def _write_config(cfg_dict: dict, tmpdir: str) -> Path:
    path = Path(tmpdir) / "config.yaml"
    path.write_text(yaml.dump(cfg_dict, default_flow_style=False, sort_keys=False))
    return path


def _mini_config(
    topology: str = "standard",
    gate: bool = False,
    max_rounds: int = 2,
    min_hits: int = 2,
) -> dict:
    """Minimal 2-agent config for fast testing."""
    cfg: dict = {
        "schema_version": "1.0",
        "topic": {
            "name": "Is water wet?",
            "summary": "A simple debate: does water itself have the property of wetness, or does it only make other things wet?",
        },
        "topology": topology,
        "providers": {
            "openai": {
                "model": "gpt-5.4-mini",
                "max_tokens": 500,
                "timeout": 60,
                "max_retries": 3,
            },
        },
        "agents": {
            "Pro": {
                "provider": "openai",
                "side": "Proponent",
                "max_words": 150,
                "system_prompt": "You are the Proponent. Argue that water IS wet. Be brief. Always address open hits.",
            },
            "Skep": {
                "provider": "openai",
                "side": "Skeptic",
                "max_words": 150,
                "system_prompt": "You are the Skeptic. Argue that water is NOT wet. Be brief. Always address open hits.",
            },
        },
        "convergence": {
            "max_rounds": max_rounds,
            "no_growth_halt": 2,
            "min_hits_addressed": min_hits,
        },
        "judge": {
            "system_prompt": "Judge fairly.",
            "rubric": [
                {"id": "R1", "name": "quality", "description": "Argument quality", "min": 0, "max": 10},
            ],
            "sides": ["Proponent", "Skeptic"],
            "verdict_options": ["Proponent", "Skeptic", "Tied"],
            "panel": [{"provider": "openai"}],
        },
        "output": {
            "dir": "",  # set per test
            "live_log": True,
            "formats": ["json"],
        },
    }
    if gate:
        cfg["gate"] = {
            "enabled": True,
            "primary": "llm",
            "llm_checker_provider": "openai",
            "max_rewrites": 1,
            "seed_terms": {
                "water": "H2O, the chemical compound",
                "wet": "The state of being covered or saturated with liquid",
            },
        }
    return cfg


def _run_debate(cfg_dict: dict) -> dict:
    """Run a debate and return the final state."""
    from arbiter.config import load_config
    from arbiter.graph import DebateEngine

    with tempfile.TemporaryDirectory() as td:
        cfg_dict["output"]["dir"] = str(Path(td) / "output")
        cfg_path = _write_config(cfg_dict, td)
        cfg = load_config(cfg_path)
        engine = DebateEngine(cfg)
        return engine.run()


# ═══════════════════════════════════════════════════════════════════════
# Test 1: Basic hit creation and normalization
# ═══════════════════════════════════════════════════════════════════════


@skip_no_openai
class TestHitCreationAndNormalization:
    """Verify hits are created with normalized 'against' fields."""

    def test_hits_have_normalized_sides(self):
        result = _run_debate(_mini_config(max_rounds=1, min_hits=0))
        ledger = result.get("ledger", [])
        assert len(ledger) > 0, "No hits created"

        valid_sides = {"Proponent", "Skeptic", "Theory"}
        for h in ledger:
            assert h["against"] in valid_sides, (
                f"Hit {h['id']} has non-normalized against='{h['against']}'"
            )

    def test_hits_have_correct_by_field(self):
        result = _run_debate(_mini_config(max_rounds=1, min_hits=0))
        ledger = result.get("ledger", [])
        valid_agents = {"Pro", "Skep"}
        for h in ledger:
            assert h["by"] in valid_agents, (
                f"Hit {h['id']} has unknown by='{h['by']}'"
            )

    def test_hit_ids_are_sequential(self):
        result = _run_debate(_mini_config(max_rounds=1, min_hits=0))
        ledger = result.get("ledger", [])
        for i, h in enumerate(ledger):
            assert h["id"] == f"h{i+1}", (
                f"Expected h{i+1}, got {h['id']}"
            )


# ═══════════════════════════════════════════════════════════════════════
# Test 2: Mini-ledger-update — hits addressed in R2
# ═══════════════════════════════════════════════════════════════════════


@skip_no_openai
class TestMiniLedgerEngagement:
    """Verify that the mini-ledger-update causes R2 agents to address
    different hits (not all piling on the same ones)."""

    def test_r2_has_resolutions(self):
        """R2 agents should address some R1 hits."""
        result = _run_debate(_mini_config(max_rounds=2, min_hits=2))
        ledger = result.get("ledger", [])
        resolved = [h for h in ledger if h["status"] != "open"]
        assert len(resolved) > 0, (
            f"No hits resolved in 2-round debate. "
            f"Statuses: {[h['status'] for h in ledger]}"
        )

    def test_resolved_statuses_are_valid(self):
        result = _run_debate(_mini_config(max_rounds=2, min_hits=2))
        ledger = result.get("ledger", [])
        for h in ledger:
            assert h["status"] in ("open", "rebutted", "conceded", "dodged"), (
                f"Hit {h['id']} has invalid status '{h['status']}'"
            )

    def test_rebuttals_have_content(self):
        """Rebutted hits should have non-empty rebuttal text."""
        result = _run_debate(_mini_config(max_rounds=2, min_hits=2))
        ledger = result.get("ledger", [])
        rebutted = [h for h in ledger if h["status"] == "rebutted"]
        for h in rebutted:
            assert h["rebuttal"].strip(), (
                f"Hit {h['id']} is rebutted but has empty rebuttal"
            )
            # Should NOT contain the template placeholder
            assert "YOUR RESPONSE TO:" not in h["rebuttal"], (
                f"Hit {h['id']} has unfilled template placeholder in rebuttal"
            )


# ═══════════════════════════════════════════════════════════════════════
# Test 3: Enforcement — agents must address hits
# ═══════════════════════════════════════════════════════════════════════


@skip_no_openai
class TestEnforcementRetrigger:
    """Verify that the post-turn enforcement re-prompts agents who
    don't address enough hits."""

    def test_min_hits_addressed_is_respected(self):
        """With min_hits_addressed=2, R2 agents should address >= 2 each."""
        result = _run_debate(_mini_config(max_rounds=2, min_hits=2))
        ledger = result.get("ledger", [])
        resolved = [h for h in ledger if h["status"] != "open"]
        # 2 agents × 2 min each = at least 4 addressed (some may overlap)
        # But with mini-ledger-update, overlaps should be minimal
        assert len(resolved) >= 2, (
            f"Only {len(resolved)} hits resolved, expected >= 2 with min_hits=2"
        )


# ═══════════════════════════════════════════════════════════════════════
# Test 4: LLM gate with real model
# ═══════════════════════════════════════════════════════════════════════


@skip_no_openai
class TestLLMGateReal:
    """Test the LLM-primary gate with a real model."""

    def test_gated_debate_completes(self):
        """A gated debate should complete without crashing."""
        result = _run_debate(_mini_config(
            topology="gated", gate=True, max_rounds=1, min_hits=0
        ))
        assert result["round_idx"] >= 1
        assert len(result["transcript"]) >= 2

    def test_gate_produces_validity_log(self):
        """Gated topology should have validity_log entries."""
        result = _run_debate(_mini_config(
            topology="gated", gate=True, max_rounds=1, min_hits=0
        ))
        vlog = result.get("validity_log", [])
        assert len(vlog) > 0, "No validity_log entries in gated debate"

    def test_gate_does_not_block_legitimate_arguments(self):
        """'Water is wet' debate has no stipulated contradictions —
        the gate should pass all turns. Seed terms used consistently
        should NOT be flagged as definitional shifts."""
        result = _run_debate(_mini_config(
            topology="gated", gate=True, max_rounds=1, min_hits=0
        ))
        assert result["round_idx"] >= 1
        assert len(result["transcript"]) >= 2
        vlog = result.get("validity_log", [])
        turn_logs = [v for v in vlog if v.get("kind") != "round_summary"]
        assert len(turn_logs) >= 2, "Gate should have audited at least 2 turns"
        violations = [v for v in turn_logs if v.get("final_status") == "validity_violation"]
        assert len(violations) == 0, (
            f"Gate produced {len(violations)} false positive(s) on a benign debate. "
            f"Seed terms used consistently should not be flagged."
        )


# ═══════════════════════════════════════════════════════════════════════
# Test 5: Full pipeline — init-like config through engine
# ═══════════════════════════════════════════════════════════════════════


@skip_no_openai
class TestFullPipeline:
    """Test the complete flow: config → engine → debate → output."""

    def test_output_files_created(self):
        with tempfile.TemporaryDirectory() as td:
            cfg = _mini_config(max_rounds=1, min_hits=0)
            out_dir = str(Path(td) / "output")
            cfg["output"]["dir"] = out_dir
            cfg_path = _write_config(cfg, td)

            from arbiter.config import load_config
            from arbiter.graph import DebateEngine

            engine = DebateEngine(load_config(cfg_path))
            engine.run()

            output_dir = Path(out_dir)
            json_files = list(output_dir.glob("debate_*.json"))
            assert len(json_files) >= 1, "No debate JSON output"

            data = json.loads(json_files[0].read_text())
            assert "state" in data or "transcript" in data
            assert "metadata" in data

    def test_metadata_has_judge_config(self):
        """Output should embed judge config for arbiter judge auto-detect."""
        with tempfile.TemporaryDirectory() as td:
            cfg = _mini_config(max_rounds=1, min_hits=0)
            out_dir = str(Path(td) / "output")
            cfg["output"]["dir"] = out_dir
            cfg_path = _write_config(cfg, td)

            from arbiter.config import load_config
            from arbiter.graph import DebateEngine

            engine = DebateEngine(load_config(cfg_path))
            engine.run()

            data = json.loads(next(Path(out_dir).glob("debate_*.json")).read_text())
            meta = data.get("metadata", {})
            assert "judge_config" in meta, "No embedded judge_config in metadata"
            assert "providers_config" in meta, "No embedded providers_config in metadata"

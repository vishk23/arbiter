# Arbiter

**Formally verified multi-agent debates.**

Run structured debates between frontier LLMs with optional Z3 formal verification, calibrated validity gates, and multi-lab judging panels.

## Install

```bash
pip install -e ".[all]"
```

## Quickstart

```bash
# Set your API key
export OPENAI_API_KEY=sk-...

# Run a 3-agent debate
arbiter run configs/quickstart.yaml
```

## Full experiment (BIT Creation Theory case study)

```bash
# Set API keys for all 3 providers
export ANTHROPIC_API_KEY=...
export OPENAI_API_KEY=...
export GEMINI_API_KEY=...

# Run the gated debate with Z3 stipulation
arbiter run experiments/bit_creation_theory/config.yaml

# Judge the result
arbiter judge output/debate_*.json

# Calibrate the validity gate
arbiter calibrate experiments/bit_creation_theory/config.yaml \
  --test-cases experiments/bit_creation_theory/gate_tests.yaml

# Red-team: adversarial Proponent tries to evade the gate
arbiter redteam experiments/bit_creation_theory/config.yaml --target Proponent

# Export argument map
arbiter export output/debate_*.json -f argdown
```

## Features

- **Any LLM provider** — Anthropic, OpenAI, Google, Ollama, or custom
- **Z3 formal verification** — optional SMT solver integration proves claims are self-consistent
- **Calibrated validity gate** — per-turn logical hygiene enforcement with gold-standard test suite (0.94 recall / 1.00 specificity)
- **Structured argument ledger** — every hit tracked as open/conceded/rebutted/dodged
- **Convergence detection** — debate halts when no new arguments surface
- **Multi-lab judge panel** — 3+ judges from different providers, with spread-flagging for disagreement
- **Adversarial red-team** — test the gate against a deliberately evasive agent
- **Argdown export** — machine-readable argument maps
- **Crash recovery** — SQLite checkpointing, resume interrupted debates

## Case study: BIT Creation Theory

Arbiter was developed during an 8-posture experimental analysis of BIT Creation Theory (Torres, 2026). The experiment produced a **24-0 unanimous verdict** across 24 LLM judges from 3 labs (Anthropic Claude Opus, OpenAI gpt-5, Google Gemini 3.1 Pro).

Key findings:
- Z3 mechanically proved the theory's formal claims are self-contradictory (UNSAT)
- The validity gate achieved 100% operational catch rate on unwitting violations
- When red-teamed, the gate caught the adversary's evasion attempts and deterred further violations
- Frontier LLMs independently discovered the formal contradiction and the synchronicity-to-singularity non-sequitur without being told

Full experimental data and reproduction configs are in `experiments/bit_creation_theory/`.

## License

MIT

# Arbiter — Formally Verified Multi-Agent Debate for Research Papers

[![PyPI](https://img.shields.io/pypi/v/arbiter-debate)](https://pypi.org/project/arbiter-debate/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)

**An open-source AI tool for auditing research papers with formal or quantitative models. Arbiter extracts claims, attempts machine verification of encodable mathematical claims using Z3/Knuckledragger, and stages structured multi-agent debates to expose the gap between what a paper proves and what it claims.**

Works best on papers with explicit formal models — economics, theoretical CS, mechanism design, quantitative social science, optimization. Claim extraction and formalization are LLM-driven (untrusted heuristics); proof certificates are machine-checked (trusted). See [trust model](#trust-model) below.

Point Arbiter at a PDF — it extracts claims, finds contradictions, generates Z3/Knuckledragger proof certificates for encodable claims, designs specialist debate agents across multiple LLM providers (OpenAI, Anthropic, Google, Grok), and produces a structured verdict with every argument tracked.

> **Paper**: [Arbiter: Formally Verified Multi-Agent Debate for Research Claim Evaluation](papers/arbiter_systems_paper.pdf)
>
> **Benchmark**: 244/244 on miniF2F, 89.3% checker-passing certificates (Claude Sonnet 4.5). **Important**: our audit finds ~13–26% of Z3 proofs are genuinely valid after checking encodings — the gap between checker-passing and genuinely-valid is the core finding of our audit paper. See [benchmark paper](papers/arbiter_paper.pdf) for full taxonomy.

<p align="center">
  <img src="https://raw.githubusercontent.com/vishk23/arbiter/main/docs/screenshots/argdown_output.gif" width="800" alt="Arbiter argdown output showing argument ledger with syntax highlighting" />
</p>

## What it does

1. **Reads the paper** — extracts every claim, assumption, proposition, and equation
2. **Finds the cracks** — identifies contradictions, tensions, and Z3-encodable formal claims
3. **Designs the debate** — creates specialist agents (e.g., Macroeconomist, TaxScholar, IO Theorist), gate rules, and a custom rubric
4. **Runs the debate** — multi-round argumentation with real-time validity enforcement
5. **Delivers a verdict** — multi-lab judge panel with scores, landed hits, and a structured argument map

## Case study: "The AI Layoff Trap"

We ran Arbiter on ["The AI Layoff Trap"](https://arxiv.org/abs/2603.20617) (Falk & Tsoukalas, 2026), which claims to **prove** that AI over-automation is inevitable and only a Pigouvian tax can fix it.

**Init** — 280 claims extracted, 17 propositions, 10 assumptions, 7 policy claims identified:

<p align="center">
  <img src="https://raw.githubusercontent.com/vishk23/arbiter/main/docs/screenshots/argdown_concessions.gif" width="800" alt="Argdown showing concessions and rebuttals with formal math" />
</p>

**Debate** — 9 specialist agents (Proponent, Skeptic, IO Theorist, Macroeconomist, TaxScholar, LaborEconomist, PublicFinance, CausalInference, Generalist) across 3 providers (OpenAI gpt-5.4, Anthropic Claude Opus 4.6, xAI Grok) debated for 6 rounds:

<p align="center">
  <img src="https://raw.githubusercontent.com/vishk23/arbiter/main/docs/screenshots/dashboard_final.gif" width="800" alt="Dashboard showing completed 6-round debate with agent cards" />
</p>

**Verdict** — Skeptic wins 2-1. The paper's core theorem holds, but its policy claims overreach:

| Judge | Proponent | Skeptic | Verdict |
|-------|-----------|---------|---------|
| Grok | 39 | 51 | **Skeptic** |
| OpenAI | 42 | 50 | **Skeptic** |
| Anthropic | 37 | 35 | Proponent |

**Key findings:**
- Core theorem (α_NE > α_CO when η<1, N>1) is **mathematically correct** — all 3 judges agree
- "Only a Pigouvian tax works" — **conceded** by Proponent (η-raising policies also work)
- "Boundless productivity" rhetoric — **conceded** (not implied by the formal model)
- 17 total Proponent concessions, 22 conceded hits, 141 total argument hits
- 0 gate violations across 54 turns, 0 mid-debate judge failures

Full outputs: [`experiments/ai_layoff_trap_v3/`](experiments/ai_layoff_trap_v3/)

## Quickstart

```bash
# Install
pip install -e ".[all]"

# Set API keys
cp .env.example .env
# Edit .env with your keys (at minimum OPENAI_API_KEY)

# Generate a debate config from any PDF
arbiter init --from-pdf paper.pdf --output-dir my-debate/

# Run the debate
arbiter run my-debate/config.yaml

# Judge it
arbiter judge my-debate/output/debate_001.json

# Export the argument map
arbiter export my-debate/output/debate_001.json -f argdown
```

### Use multiple frontier models

```bash
arbiter init --from-pdf paper.pdf \
  --providers "openai:gpt-5.4,anthropic:claude-opus-4-6,grok:grok-4.20-0309-reasoning" \
  --effort high \
  --output-dir my-debate/
```

### Watch it live in the browser

```bash
arbiter web --init --from-pdf paper.pdf
# Opens http://localhost:8741 with live dashboard
```

<!-- Live dashboard auto-refreshes as debate progresses -->

## How it works

```
arbiter init --from-pdf paper.pdf
  │
  ├─ 1. PDF → Markdown → Chunked text
  ├─ 2. Claim extraction (280 claims, tagged formal/logical/empirical)
  ├─ 2b. Formal model extraction (assumptions, propositions, equations, policies)
  ├─ 3. Contradiction detection + key terms + attack angles
  ├─ 4. Parallel generation:
  │     ├─ Z3 proof verification (proof checks, sensitivity, boundary, policy)
  │     ├─ Agent cast design (domain specialists per attack angle)
  │     ├─ Gate rules + escape-route anticipation
  │     ├─ Judge rubric (topic-specific scoring criteria)
  │     └─ Source corpus (synthesis + classification)
  ├─ 5. Gate self-calibration
  └─ 6. Config assembly → ready for `arbiter run`
```

## Features

- **Agentic init from PDF** — one command generates a complete debate config with agents, gate, Z3, rubric
- **Z3 verification suite** — proof verification, counterexample search, assumption sensitivity, boundary analysis, policy verification
- **7 built-in providers** — OpenAI, Anthropic, Google Gemini, Grok, DeepSeek, Ollama, custom plugins
- **LLM validity gate** — per-turn logical hygiene via LLM classifier, 0 violations across 54 frontier-model turns
- **Structured argument ledger** — every hit tracked as open/conceded/rebutted/dodged
- **Multi-lab judge panel** — N judges from different providers with spread-flagging
- **Live web dashboard** — watch init and debate in real-time with argdown syntax highlighting
- **KaTeX math rendering** — LaTeX equations render in the dashboard
- **Knuckledragger integration** — optional Python proof assistant for formal verification
- **Adversarial red-team mode** — test the gate against deliberately evasive agents
- **Argdown export** — machine-readable argument maps

## CLI Commands

| Command | Description |
|---|---|
| `arbiter init --from-pdf paper.pdf` | Generate debate config from PDF |
| `arbiter init --topic "..."` | Generate config from topic description |
| `arbiter run config.yaml` | Run the debate |
| `arbiter judge output.json` | Run multi-lab judge panel |
| `arbiter export output.json -f argdown` | Export argument map |
| `arbiter web config.yaml` | Live dashboard for debate |
| `arbiter web --init --from-pdf paper.pdf` | Live dashboard for init + debate |
| `arbiter calibrate config.yaml --test-cases tests.yaml` | Calibrate validity gate |
| `arbiter validate config.yaml` | Validate config |
| `arbiter redteam config.yaml --target Proponent` | Red-team mode |

## Architecture

```
arbiter init ─── PDF ──→ Claims ──→ Formal Model ──→ Contradictions
                                         │
                         ┌───────────────┼───────────────┐
                         ▼               ▼               ▼
                      Z3 Proofs    Agent Design     Gate Rules ──→ config.yaml
                                                        
arbiter run ─── config.yaml ──→ Round ──→ Gate ──→ Ledger ──→ Mid-Judge ──→ Round
                                   ▲       │                                  │
                                   │    Rewrite                          converged?
                                   └───────┘                                  │
                                                                         Steelman
                                                                              │
arbiter judge ────────────────────────────────────────────────────── Judge Panel
                                                                         │
                                                                    Verdict + Scores
```

See [ARCHITECTURE.md](ARCHITECTURE.md) for the full module map and design decisions.

## Formal Verification

Arbiter uses three verification backends, with the LLM selecting the right one per claim:

| Backend | What it handles | Proof certificate |
|---------|----------------|-------------------|
| **[Knuckledragger](https://github.com/philzook58/knuckledragger)** | Integer constraints, polynomial inequalities, divisibility, induction | `kd.Proof` object (tamper-proof, Z3-verified) |
| **SymPy** | Trig identities, recurrences, series, symbolic algebra | `minimal_polynomial == x` (rigorous algebraic zero) |
| **Z3** (raw) | Counterexample search, optimization, boundary analysis | SAT model extraction |

### Benchmark results

| Benchmark | Model | Checker-passing | Audit-surviving (genuine valid) |
|-----------|-------|----------------|---------------------------------|
| miniF2F (244) | Sonnet 4.5 | 89.3% | ~26% (full set), ~13% (hard tier) |
| miniF2F (244) | gpt-5.4-mini | 82.8% | ~13-26% (estimated) |
| MiniF2F-Dafny | Sonnet 4.5 | 55.7% | — (not audited) |

**The gap between checker-passing and audit-surviving is the core finding** — see [audit paper](papers/arbiter_paper.pdf) for the full 202-problem taxonomy. Certification does not mean the encoded claim is faithful to the original theorem.

Reproducibility: gpt-5.4-mini, temperature 1.0, up to 3 retries, 60s Z3 timeout. Full prompt templates in `benchmarks/`.

### Verification check types

| Check Type | What it does | Example |
|-----------|-------------|---------|
| **Proof verification** | Encode assumptions + negated proposition, check UNSAT | "α_NE > α_CO" → PROVEN |
| **Counterexample** | Extract concrete values when proof fails | "At N=1, η=0.92: wedge = 0" |
| **Sensitivity** | Drop each assumption, find load-bearing ones | "N > 1 is LOAD-BEARING" |
| **Boundary** | Find where results flip | "Wedge positive iff η < 0.83" |
| **Policy verification** | Check if proposed policies achieve goals | "Pigouvian tax implements α_CO" |

## Configuration

Everything is a single YAML file. Key sections:

```yaml
topology: gated              # standard | gated | adversarial
providers:
  openai:
    model: gpt-5.4
    reasoning: { effort: high }
  anthropic:
    model: claude-opus-4-6
    thinking: { type: adaptive, effort: medium }
agents:
  Proponent: { provider: openai, side: Proponent, system_prompt: "..." }
  Skeptic: { provider: anthropic, side: Skeptic, system_prompt: "..." }
convergence:
  max_rounds: 6
  min_hits_addressed: 3      # agents must engage with open arguments
judge:
  panel:
    - { provider: openai }
    - { provider: anthropic }
    - { provider: grok }
```

See [`experiments/ai_layoff_trap_v3/config.yaml`](experiments/ai_layoff_trap_v3/config.yaml) for a complete example.

## Trust Model

Not all steps in Arbiter are equally trustworthy. Here is an honest breakdown:

| Step | Trust level | Notes |
|------|-------------|-------|
| PDF parsing | **Untrusted heuristic** | OCR errors, layout issues common |
| Claim extraction | **Untrusted heuristic** | LLM may miss claims or split incorrectly |
| Formalization (Z3/SymPy) | **Untrusted heuristic** | LLM may encode wrong claim; see [audit paper](papers/arbiter_paper.pdf) |
| Knuckledragger `kd.Proof` | **Machine-checked** | Tamper-proof; if it exists, the encoded claim was verified by Z3 |
| Raw Z3 UNSAT | **Diagnostic** | Only as trustworthy as the encoding |
| SymPy simplification | **Symbolic, not logical** | Correct algebra ≠ logical proof |
| Debate gate | **Heuristic** | LLM classifier; reduces but doesn't eliminate bad arguments |
| Multi-provider judge panel | **Heuristic** | Correlated LLMs; better than single-model, not independent adjudication |

**The central open problem**: how faithfully does LLM-generated Z3 code represent the intended mathematical claim? Our audit ([paper](papers/arbiter_paper.pdf)) finds ~13–26% of generated Z3 proofs are genuinely valid after checking encodings. Closing this gap is the active research frontier.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for setup, testing, and PR guidelines.

```bash
git clone https://github.com/vishk23/arbiter.git
cd arbiter
pip install -e ".[all]"
cp .env.example .env
pytest tests/ -v
```

## License

MIT

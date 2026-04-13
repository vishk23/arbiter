# Arbiter Architecture

## Overview

Arbiter has two main flows: **init** (setup-time, generates config from a PDF) and **runtime** (executes the debate from config).

```
┌─────────────────────────────────────────────────────────────────────┐
│  arbiter init --from-pdf paper.pdf                                  │
│                                                                     │
│  PDF → Claims → Contradictions → [parallel] → Config.yaml           │
│                                  ├─ Z3 module                       │
│                                  ├─ Agent design                    │
│                                  ├─ Gate rules                      │
│                                  ├─ Rubric                          │
│                                  └─ Sources                         │
└─────────────────────────────────┬───────────────────────────────────┘
                                  │ config.yaml
                                  ▼
┌─────────────────────────────────────────────────────────────────────┐
│  arbiter run config.yaml                                            │
│                                                                     │
│  ┌─────┐    ┌──────────┐    ┌────────┐    ┌──────────┐             │
│  │round├───►│validity  ├───►│ledger  ├───►│midjudge  │             │
│  │     │    │audit     │    │update  │    │signals   │             │
│  └──┬──┘    └──────────┘    └────────┘    └────┬─────┘             │
│     │                                          │                    │
│     │         ┌────────────────────────┐       │                    │
│     └─────────┤ continue? ◄────────────┘       │                    │
│               │  round_idx > max_rounds?       │                    │
│               │  ledger stopped growing?        │                    │
│               └──────────┬─────────────┘       │                    │
│                          │ finalize                                  │
│                          ▼                                           │
│               ┌──────────────────┐                                  │
│               │ Z3 verify        │                                  │
│               │ Steelman loop    │                                  │
│               │ Export JSON/MD   │                                  │
│               └──────────────────┘                                  │
└─────────────────────────────────────────────────────────────────────┘
                                  │ output.json
                                  ▼
┌─────────────────────────────────────────────────────────────────────┐
│  arbiter judge output.json                                          │
│                                                                     │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐                             │
│  │Anthropic│  │ OpenAI  │  │ Gemini  │  → Aggregate → Verdict      │
│  │ judge   │  │ judge   │  │ judge   │    (majority + spreads)      │
│  └─────────┘  └─────────┘  └─────────┘                             │
└─────────────────────────────────────────────────────────────────────┘
```

## Module Map

```
src/arbiter/
├── cli.py              CLI entry point (Typer, 12 commands)
├── config.py           Pydantic models + TokenBudgets + YAML loader
├── schemas.py          23 Pydantic models for all structured LLM outputs
├── state.py            DebateState + Hit TypedDicts
├── graph.py            LangGraph StateGraph builder (DebateEngine)
│
├── providers/          LLM provider abstraction (7 built-in + custom plugin)
│   ├── base.py         BaseProvider ABC + Pydantic dispatch + retry
│   ├── anthropic.py    Adaptive thinking + effort + tool-use structured output
│   ├── openai.py       Reasoning effort + responses.parse (native Pydantic)
│   ├── google.py       ThinkingLevel (3.x) / thinking_budget (2.5) + native Pydantic
│   ├── grok.py         xAI Grok (extends OpenAI, reasoning support)
│   ├── deepseek.py     DeepSeek chat/reasoner (chat completions API)
│   └── ollama.py       Local models (format="json")
│
├── agents/             Agent turn management
│   ├── agent.py        Agent = provider + role + prompt
│   └── context.py      Per-turn prompt assembly (recency-biased)
│
├── ledger/             Argument tracking
│   ├── ops.py          add_hit, resolve_hit, open_hits (immutable)
│   └── parser.py       JSON block extraction from agent output
│
├── gate/               Validity enforcement (LLM-primary + optional layers)
│   ├── validity_gate.py    Orchestrator (LLM + regex + Z3 in parallel)
│   ├── llm_checker.py     Primary LLM classifier (ViolationResult schema)
│   ├── pattern_checker.py  Regex rules (additive)
│   ├── consistency_checker.py  Self-contradiction detection
│   ├── shift_checker.py    Definitional shift detection
│   ├── entailment_checker.py  LLM semantic backstop (legacy regex mode)
│   └── z3_checker.py      Structural SAT check
│
├── judge/              Verdict generation
│   ├── panel.py        Multi-provider panel
│   ├── rubric.py       Dynamic Pydantic model from config criteria
│   ├── mid_debate.py   Per-agent guidance signals
│   └── aggregator.py   Score means + spread flagging
│
├── verifier/           Formal verification
│   └── z3_plugin.py    Load user's Z3 module via importlib
│
├── retrieval/          Optional RAG
│   ├── local_index.py  TF-IDF corpus search
│   ├── web_search.py   Tavily web search
│   └── retriever.py    Combined interface
│
├── steelman/           Theory rescue
│   └── loop.py         Iterated steelman-critic loop
│
├── export/             Output formats
│   ├── argdown.py      Ledger → Argdown markup
│   ├── markdown.py     Transcript → readable markdown
│   └── json_export.py  Full state JSON
│
├── logging/            Live output
│   └── live_log.py     Per-turn file append + Rich console
│
└── init/               Agentic setup pipeline
    ├── pipeline.py     Main orchestrator (parallel phases + --skip-calibration)
    ├── pdf_reader.py   PDF → markdown → claims
    ├── claim_extractor.py  Claims → contradictions + terms + angles
    ├── z3_generator.py     Contradictions → Z3 Python module
    ├── gate_builder.py     Contradictions → gate rules + calibration (parallel)
    ├── agent_designer.py   Claims → specialist agent cast
    ├── rubric_builder.py   Claims → judge rubric criteria
    ├── source_finder.py    Topic → web corpus + classification (parallel queries)
    └── config_writer.py    Assemble everything → YAML
```

## Data Flow: One Debate Turn

```
State (entering round)
  │
  ├─ context.py: build prompt
  │   ├─ topic + thesis + Z3 stipulation + privileged context
  │   ├─ judge signals from last round
  │   ├─ retrieved sources (optional network I/O)
  │   ├─ round number
  │   └─ open hits + pre-filled JSON template (LAST for recency bias)
  │
  ├─ provider: LLM call (system + user prompt → response text)
  │
  ├─ [if gated] gate: check response (LLM-primary mode)
  │   ├─ [parallel] LLM classifier (violations + shifts)
  │   ├─ [parallel] extract formal claims (LLM call)
  │   ├─ regex patterns (additive, instant)
  │   ├─ Z3 structural check (from extracted claims)
  │   ├─ deduplicate violations
  │   └─ if violation: rewrite loop (up to max_rewrites)
  │
  ├─ [ledger enforcement] check hits_addressed count
  │   └─ if insufficient: re-prompt once
  │
  ├─ parser: extract JSON block from response
  │   ├─ new_hits → add to ledger
  │   └─ hits_addressed → resolve existing hits
  │
  └─ transcript: append entry
```

## Key Design Decisions

### Pre-filled JSON Template (Ledger Engagement)
Agents receive a fill-in-the-blanks JSON template with ACTUAL hit IDs
instead of a placeholder. Combined with end-of-context placement (recency
bias) and post-turn enforcement, this achieved 73% engagement (up from 0%).

### Side-Balanced Provider Distribution
Each debate side gets agents from multiple LLM providers, preventing
monoculture bias. If all Skeptic agents are OpenAI, the verdict might
reflect OpenAI's biases rather than argument quality.

### Validity Gate as Deterrence
The gate's value is behavioral steering, not just violation detection.
In adversarial testing, the gate caught 2 evasion attempts in R2, after
which the adversary abandoned evasion entirely (100% deterrence).

### Z3 as Optional Plugin
Z3 constraints are loaded from a user-provided Python module, not
hardcoded. This keeps the engine general-purpose while allowing
mechanical formal verification when the theory has checkable claims.

### Smart Defaults
Users who don't configure get: 3-judge panel, entailment check enabled,
ledger enforcement on, side-balanced providers. Power users can tune
everything via YAML.

## Parallelization

| Location | What runs in parallel | Savings |
|---|---|---|
| Judge panel | All judges (ThreadPoolExecutor) | 6-10s/debate |
| Gate per-turn | LLM check + claim extraction | ~2-3s/turn × 35 turns |
| Gate calibration | All test case checks | 12-18s/init |
| Source finder | Query processing | 3-8s/init |
| Init Phase A | Escape routes + source download | 5-10s/init |
| Init Phase B | Z3 + agents + gate + rubric + context | 10-20s/init |

Agent turns within a round remain sequential (each agent needs prior entries).

## Known Technical Debt

### DebateEngine is a God Object (graph.py)
Manages: provider init, agent init, gate init, context building,
ledger updates, mid-debate judging, Z3 verification, steelman loops,
export, checkpointing, and logging. Should be split into:
ProviderFactory, LedgerManager, ExportManager, CheckpointManager.

### Init Pipeline Duplicates Runtime Logic
`init/pipeline.py` reimplements provider initialization with its own
`_make_provider()` function. Changes to provider init must be made in
two places. Should share a factory with `graph.py`.

### State Type Safety
`DebateState` is a TypedDict (type hints only, not enforced at runtime).
A missing key causes a runtime KeyError, not a validation error.
Upgrading to Pydantic would add safety but requires custom LangGraph
serialization (LangGraph recommends TypedDict).

### Ledger JSON Parsing
`ledger/parser.py` uses regex to extract JSON from agent prose output.
This is intentional (agents produce mixed text + JSON), but silent
failure on malformed JSON could be improved with schema validation.

### Naming Inconsistencies
Mixed use of: `hit_id` vs `id`, `agent` vs `agent_name`,
`round_idx` vs `round`, `entry_text` vs `text`. Not broken,
but friction for contributors.

## Resolved Technical Debt

- **Magic numbers**: All `max_tokens` values use `TokenBudgets` tiers (small/medium/large/xl), configurable via YAML.
- **Regex fallbacks in providers**: Removed from Anthropic, Google, DeepSeek. Providers use native structured output.
- **Dict schemas**: All 21 replaced with Pydantic models in `schemas.py`. Provider-native parsing (OpenAI `responses.parse`, Anthropic tool-use, Gemini `response_schema`).
- **LLM gate replaced regex**: LLM-primary gate achieves 100% recall/specificity vs 94% with regex. Regex kept as additive layer.

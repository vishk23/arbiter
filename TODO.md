# Arbiter TODO

Comprehensive list of bugs, improvements, and missing features.
Prioritized by impact. Check off as completed.

---

## P0 — Bugs that will bite users

- [x] **T01** Rich spinners hide all output during API calls. Users see nothing for 5+ minutes. Replace `console.status()` with elapsed-time progress bars. Print "Calling {provider} ({model})..." before each call and "Response received ({N} chars, {T}s)" after.
- [x] **T02** Anthropic `call_structured` silently depends on OpenAI for the reformat fallback. If user only has Anthropic key, fallback crashes with ImportError. Fix: catch ImportError, try regex-only, raise clear error if both fail.
- [x] **T03** No `--verbose` / `--debug` flag anywhere in the CLI. When things go wrong there's no way to see what's happening. Add global `--verbose` option that enables DEBUG logging + prints every API call start/end.
- [x] **T04** InMemorySaver doesn't survive crashes. README says "crash recovery" but it's a lie. Fix: properly integrate SqliteSaver (requires async context in newer LangGraph) or use a sync-compatible checkpoint backend.
- [x] **T05** Config writer doesn't add section comments. Generated 751-line YAML has zero guidance. Add inline comments to every section header explaining what it does and what values are valid.
- [x] **T06** `arbiter init` interactive mode untested. The `Prompt.ask()` / `Confirm.ask()` paths might crash. Test all interactive flows.
- [x] **T07** Jinja2 template rendering unverified. Agent prompts contain `{{ topic.name }}` and `{{ z3_stipulation }}` but context builder rendering hasn't been tested. If broken, agents see literal template strings.
- [x] **T08** Gate test cases not saved to disk during init. Auto-generated tests exist only in memory. `arbiter calibrate` can't use them later. Fix: write `gate_tests.yaml` alongside `config.yaml`.
- [x] **T09** `arbiter judge` requires `--config` flag. Should auto-detect rubric from output JSON metadata, or embed rubric in output at debate completion.

## P1 — Testing gaps

- [x] **T10** Test `arbiter run` with gated topology end-to-end (currently running as integration test).
- [x] **T11** Test `arbiter run` with Z3 plugin loading and stipulation injection.
- [x] **T12** Test `arbiter run` with multi-provider config (agents on different providers).
- [x] **T13** Test `arbiter calibrate` end-to-end with gate_tests.yaml.
- [x] **T14** Test `arbiter redteam` end-to-end.
- [x] **T15** Test mid-debate judge signals fire and route back to agents.
- [x] **T16** Test steelman loop through the engine `_finalize_node`.
- [x] **T17** Test Gemini provider through the engine (worked in old code, untested in Arbiter).
- [x] **T18** Test Anthropic provider for debate turns (only tested for init calls so far).
- [x] **T19** Test `arbiter init` interactive mode (all Prompt/Confirm paths).
- [x] **T20** Test `arbiter export -f markdown` (only argdown tested).
- [x] **T21** Test Jinja2 template rendering in context builder with real Z3 stipulation.
- [x] **T22** Verify all 11 BIT agent prompts are valid Jinja2 (no stray braces).
- [x] **T23** Test ledger update node with gate-aware transcript entries (validity_status, extracted_claims fields).
- [x] **T24** Test that generated config.yaml from init actually runs through the engine without errors.
- [x] **T25** Add tests for gate pattern_checker with denial patterns.
- [x] **T26** Add tests for gate shift_checker with seed terms.
- [x] **T27** Add tests for gate entailment_checker (mock provider).
- [x] **T28** Add tests for judge rubric dynamic model generation.
- [x] **T29** Add tests for judge aggregator (spread flagging, majority verdict).
- [x] **T30** Add tests for retrieval local_index (TF-IDF + fallback).
- [x] **T31** Add tests for export argdown format validity.
- [x] **T32** Add tests for export markdown structure.

## P2 — DX improvements

- [x] **T33** Add `--effort` flag to `arbiter init` CLI for controlling reasoning effort (low/medium/high).
- [ ] **T34** Add cost estimation: `arbiter estimate config.yaml` counts expected tokens per round and estimates $/run for each provider.
- [ ] **T35** Add `arbiter diff output1.json output2.json` to compare two debate runs (ledger diff, score diff, which arguments appeared/disappeared).
- [ ] **T36** Add `arbiter status` command that checks if a debate is running (via checkpoint/PID file) and shows progress.
- [ ] **T37** Streaming output during debates — show agent text as it generates, not just after the full call.
- [x] **T38** Auto-version debate outputs (debate_001.json, debate_002.json) instead of timestamp-only naming.
- [ ] **T39** `arbiter init` should save intermediate results (claims, contradictions, theses) so a failed init can resume from the last checkpoint.
- [x] **T40** Add config YAML linting/validation command: `arbiter validate config.yaml` with helpful error messages.
- [x] **T41** Add `arbiter show-rubric config.yaml` to display the judge rubric as a formatted table.
- [x] **T42** Embed the config + rubric in the debate output JSON so `arbiter judge` doesn't need `--config`.

## P3 — Architecture improvements

- [x] **T43** Custom provider plugin system. `plugin: module:ClassName` in provider config. Supports Mistral, Cohere, Together, etc.
- [x] **T44** LLM-primary gate replaced regex as primary checker. 100% recall/specificity vs 94% with regex. Catches paraphrases natively.
- [ ] **T45** Configurable graph topology via YAML. Power users define custom debate flows (e.g. "3 rounds parallel critique → 2 rounds head-to-head → steelman"). Currently limited to 3 presets.
- [x] **T46** Parallel execution: judge panel, gate checks (LLM + extraction), calibration test cases, source queries all run in parallel. Agent turns remain sequential (state dependency).
- [ ] **T47** Proper SqliteSaver integration for crash recovery with async LangGraph. Or use langgraph-checkpoint-postgres for production deployments.
- [ ] **T48** Webhook / callback system. Notify external services (Slack, Discord, webhook URL) when debate completes or gate fires.

## P4 — Content & documentation

- [ ] **T49** Write proper documentation (not just README). Sphinx or MkDocs with: quickstart tutorial, config reference, architecture guide, API reference.
- [ ] **T50** Architecture diagram (Mermaid) showing the LangGraph state machine, data flow, and component relationships.
- [ ] **T51** Add a second case study config (e.g. IIT consciousness, climate sensitivity, a contested arXiv paper) to prove generality.
- [ ] **T52** CONTRIBUTING.md with development setup, code style, PR guidelines.
- [x] **T53** GitHub Actions CI: run pytest on push, lint with ruff. (.github/workflows/ci.yml)
- [ ] **T54** Publish to PyPI as `arbiter-debate`.
- [ ] **T55** Write a technical blog post / arXiv paper: "Arbiter: Formally Verified Multi-Agent Debates with Calibrated Validity Gates."
- [ ] **T56** Record a demo video / GIF showing the full `init → run → judge → export` pipeline.
- [ ] **T57** Update `experiments/bit_creation_theory/` configs to use the new Arbiter engine (currently reference old debate-repos code).

## P5 — Nice to have

- [ ] **T58** Web UI (Streamlit or Gradio) for non-technical users: upload PDF, configure agents visually, watch debate live, see argument map.
- [ ] **T59** LangSmith / Langfuse tracing integration for debugging LLM calls.
- [ ] **T60** Docker container for reproducible environment.
- [ ] **T61** Ollama provider end-to-end test with a local model.
- [ ] **T62** Support for image/figure extraction from PDFs (some theories include diagrams that are relevant to claims).
- [ ] **T63** Debate tournament mode: multiple theories debated against each other in a bracket.
- [ ] **T64** Human-in-the-loop: allow a human to take one agent's seat and argue against AI agents.
- [ ] **T65** Rate limiting / budget caps: abort if API spend exceeds $X.

---

## Completed

- [x] Core engine (LangGraph state machine with convergence)
- [x] Provider abstraction (7 built-in: Anthropic, OpenAI, Google, Grok, DeepSeek, Ollama + custom plugin)
- [x] Pydantic-first structured output (23 models in schemas.py, provider-native parsing)
- [x] LLM-primary validity gate (100% recall/specificity, replaces regex as primary)
- [x] Gate self-calibration in init pipeline (optional via --skip-calibration)
- [x] Multi-lab judge panel with spread flagging (parallel execution)
- [x] Structured argument ledger (Hit objects + mini-ledger-update between agents)
- [x] Agentic init from PDF (pymupdf4llm → claims → Z3 → agents → gate → config)
- [x] Multi-provider init with distributed pipeline steps
- [x] Side-balanced provider assignment
- [x] Configurable token budgets (TokenBudgets: small/medium/large/xl, YAML-configurable)
- [x] Provider thinking/reasoning support (Anthropic adaptive+effort, OpenAI reasoning effort, Gemini 2.5/3.x)
- [x] Parallel execution (judge panel, gate checks, calibration, source queries)
- [x] Uncited-but-relevant-fields detection in agent designer
- [x] Escape-route anticipation in gate builder
- [x] Source classification (counter-evidence vs supports-theory)
- [x] Privileged context assembly (asymmetric info per side)
- [x] CLI: init, run, judge, calibrate, redteam, export, add-agent, remove-agent, list-agents, validate, show-rubric
- [x] Argdown export
- [x] Live transcript logging
- [x] BIT Creation Theory case study (8 postures, 24-0 verdict)
- [x] Z3 verifier (auto-generated, finds UNSAT independently)
- [x] 173 unit tests + 26 Pydantic integration tests + 28 LLM gate tests
- [x] pyproject.toml with all optional dependencies
- [x] README + ARCHITECTURE.md
- [x] GitHub Actions CI (lint + unit tests on push)
- [x] MIT LICENSE

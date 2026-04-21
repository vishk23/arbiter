# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.0] — 2026-04-21

Case-study expansion and verification-audit release.

### Added

- **Three N=3 case studies with full transcripts and analysis** in `experiments/`:
  - `ai_layoff_trap_v3/` — Falk & Tsoukalas, *The AI Layoff Trap* (arXiv:2603.20617). 9 agents, 141 hits, 17 Proponent concessions, Skeptic 2–1.
  - `llm_self_improvement_limits/` — Zenil, *On the Limits of Self-Improving in Large Language Models* (arXiv:2601.05280). 11 agents, 168 hits, 13 Proponent concessions, Skeptic 3–0. FATAL contradiction C43 vs C126 auto-flagged at init.
  - `agi_safety_impossibility/` — Panigrahy & Sharan, *Limitations on Safe, Trusted, Artificial General Intelligence* (arXiv:2509.21654). 10 agents, 132 hits, 9 Proponent concessions, split panel.
- `ANALYSIS.md` per case study: init summary, debate stats, what survived, what fell (with named hit IDs), MVP agents, key arguments, per-judge rubric breakdowns, and verdict summaries (~1,500 lines total).
- **Verification-audit paper** (`papers/arbiter_paper.pdf`, 11 pages): full audit of all 202 proved miniF2F results plus 54-certificate FormalMATH audit. Reported 82.8% solve rate → 13.5% audit-surviving. Failure taxonomy with 7 categories; decomposition-bottleneck hypothesis.
- **Systems paper** (`papers/arbiter_systems_paper.pdf`, 15 pages): PDF-to-verdict pipeline, three case studies with cross-case-pattern analysis (policy exclusivity / scope generalization / definition mismatch), gated-topology design, multi-provider judge panel, ablation.
- CHANGELOG.md (this file).

### Changed

- README: added three-overreach-types table, highlights section naming specific debate artifacts (C43/C126 flag, VerificationScholar Trust-as-epistemic-access, DivergenceCritic RLHF decomposition), and "What the debate output is useful for (and not)" section. Case-study section now links real arXiv preprints and notes concessions are pipeline outputs, not claims about author beliefs.
- Gate-violation framing in README corrected: "0 admitted violations" across 54 turns on Layoff Trap, with 8 rewrites before admission (gate precludes violations from entering the transcript by design).

### Fixed

- Paper B bibliography: replaced `[Author redacted for blind review]` placeholders with real citations (Zenil 2601.05280; Panigrahy & Sharan 2509.21654).
- Paper A cross-references Paper B's Z3-encodable stipulations to contextualize the 74.3% invalidity finding downstream.

### Known limitations

- All three case studies are single runs; variance across random seeds has not been measured.
- No domain-expert adjudication of debate transcripts; specialist arguments (Hotelling countermodel, RLHF structural separation, Trust-as-epistemic-access) are LLM-generated and may reflect competent rhetoric rather than validated insight.
- Ablation (V-only / D-only / V+D / LLM-Judge) remains N=1 on the Layoff Trap; treated as qualitative pilot.
- Anthropic judge ruled for Proponent in all three debates while OpenAI and Grok leaned Skeptic; cross-provider disagreement is reported transparently but not resolved.
- Verification backend audit-surviving rate is 13.5% on miniF2F and 7.4% on FormalMATH (certificate audit). Stipulations used in the case-study debates are "machine-checked under our encoding," not independently verified.

## [0.1.1] — 2026-04-14

### Fixed

- PyPI package rendering: README images use absolute GitHub raw URLs so they display on pypi.org.
- `pyproject.toml`: moved dependencies out of the `[project.urls]` section.

## [0.1.0] — 2026-04-14

Initial public release.

### Added

- PDF-to-verdict pipeline: `arbiter init --from-pdf`, `arbiter run`, `arbiter judge`, `arbiter export`.
- Multi-agent debate engine with 5-layer validity gate (LLM-checked).
- Z3/Knuckledragger/SymPy verification backends with tamper-proof `Proof` objects.
- Seven provider integrations: OpenAI, Anthropic, Google Gemini, Grok, DeepSeek, Ollama, custom plugins.
- Live web dashboard with argdown syntax highlighting and KaTeX math rendering.
- Adversarial red-team mode; argdown export; multi-lab judge panel.

[0.2.0]: https://github.com/vishk23/arbiter/releases/tag/v0.2.0
[0.1.1]: https://github.com/vishk23/arbiter/releases/tag/v0.1.1
[0.1.0]: https://github.com/vishk23/arbiter/releases/tag/v0.1.0

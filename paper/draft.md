# Arbiter: Formally Verified Multi-Agent Debates with Calibrated Validity Gates

**Authors:** [Your name], with Claude Opus 4.6

**Abstract**

We present Arbiter, an open-source framework for running structured multi-agent debates between frontier LLMs with optional formal verification via Z3 SMT solving. Arbiter introduces three novel contributions to AI-assisted deliberation: (1) a per-turn validity gate that mechanically enforces logical consistency, with a gold-standard calibration methodology achieving 0.94 recall and 1.00 specificity; (2) an agentic pipeline that reads a PDF, extracts formal claims, auto-generates Z3 constraints, and produces a debate-ready configuration; and (3) an adversarial red-team posture that measures the gate's deterrence effect under deliberate evasion. In our case study analyzing BIT Creation Theory (Torres, 2026), the system produced a 24-0 unanimous verdict across 24 LLM judges from three independent labs, with the Z3 solver mechanically proving 11 of the theory's formal claims to be internally contradictory (UNSAT). The validity gate achieved 100% operational catch rate on unwitting violations and successfully deterred a deliberately adversarial agent after two early catches. The agentic init pipeline independently discovered six contradictions that eight hours of manual expert analysis had missed. Arbiter is pip-installable, provider-agnostic, and fully configurable via YAML.

---

## 1. Introduction

Multi-agent debate has emerged as a promising approach for improving the factuality and reasoning of large language models (Du et al., 2023; Liang et al., 2023; Zhang et al., 2026). The core insight is that multiple LLM agents arguing opposing positions can surface errors that a single model would miss, producing more calibrated and accurate conclusions than independent sampling.

However, existing debate frameworks suffer from a fundamental limitation: **they have no mechanism to ensure that the arguments themselves are logically valid.** An eloquent LLM can defend a formally contradictory position by rephrasing the contradiction in ways that sound consistent, shifting definitions mid-debate without acknowledgment, or appealing to complexity when logic fails. Without mechanical enforcement of logical hygiene, debate outcomes reflect rhetorical skill rather than argument quality.

This paper introduces Arbiter, a framework that addresses this gap by integrating formal verification into the multi-agent debate loop. Our key contributions:

1. **A calibrated validity gate** that checks every debate turn against stipulated logical facts, with a gold-standard test methodology that measures the gate's recall and specificity before trusting its verdicts (Section 4).

2. **Z3 SMT integration** as an optional plugin that mechanically proves whether a theory's formal claims are self-consistent, with findings injected into the debate as stipulated facts that agents cannot contest (Section 3).

3. **An adversarial red-team posture** where one agent is explicitly instructed to evade the gate, measuring the gate's robustness under deliberate attack (Section 5).

4. **An agentic init pipeline** that reads a PDF, extracts claims, identifies contradictions, generates Z3 constraints, designs specialist agent roles, and produces a complete debate configuration — matching or exceeding the quality of manual expert setup (Section 6).

5. **A structured argument ledger** that tracks every claim as a typed object (open/conceded/rebutted/dodged), enabling convergence detection and Argdown export for argument mapping (Section 3).

We evaluate Arbiter on a case study analyzing BIT Creation Theory (Torres, 2026), a 23-page interdisciplinary framework claiming to reconcile free will and determinism via directed acyclic graphs. Across eight experimental conditions varying the presence of Z3 stipulation, user-provided counter-thesis, and validity gate, the system produced a unanimous 24-0 Skeptic verdict from judges spanning three independent LLM providers (Anthropic, OpenAI, Google).

## 2. Related Work

**Multi-agent debate.** Du et al. (2023) demonstrated that multi-agent debate improves factuality and reasoning over single-model inference. Liang et al. (2023) introduced the Multi-Agent Debate (MAD) framework with a moderator-based halting mechanism. Zhang et al. (2026) proposed Agent4Debate with specialized Searcher/Analyzer/Writer/Reviewer roles. DebateCV (2025) applied debate to claim verification. These frameworks treat agent output as text; none enforce logical consistency mechanically.

**LLMs and formal methods.** The integration of LLMs with formal verification is an active research direction. The Fusion Roadmap (2024) outlined a bidirectional framework where LLMs generate formal specifications and formal methods verify LLM outputs. Solver-Aided Verification (2026) encodes tool-use policies as SMT constraints and checks agent actions prior to execution — the closest technical comparator to our validity gate, though applied to tool calls rather than debate turns. SAT-LLM (2026) couples SMT solvers with LLMs for inconsistency detection with F1 of 0.91. Emergent Formal Verification (2026) observed that autonomous AI ecosystems independently discover Z3-based safety checks across domains.

**Argumentation frameworks.** Dung's abstract argumentation frameworks (1995) formalize attack and support relations between arguments. Argdown provides a markup language for argument mapping. Our structured argument ledger draws on this tradition, applying it to LLM-generated debate turns with typed hit-tracking (open/conceded/rebutted/dodged).

Arbiter is, to our knowledge, the first system to combine SMT-based formal verification, calibrated per-turn validity gates, and multi-lab judging panels into a configurable debate framework with an agentic setup pipeline.

## 3. System Architecture

### 3.1 Overview

Arbiter is a Python package (`pip install arbiter-debate`) built on LangGraph (LangChain, 2024) for state machine orchestration. A debate is defined by a single YAML configuration file specifying: the topic and claims under debate, the agent cast (any number, any LLM provider), convergence conditions, optional Z3 constraints, optional validity gate rules, judge panel composition, and output formats.

The debate proceeds as a LangGraph state machine:

```
START → round → [validity_audit] → ledger_update → mid_debate_judge
          ↑                                              ↓
          └──────────── continue? ──────────────── finalize → END
```

Three topology presets are available:
- **Standard:** No gate, no Z3. Agents debate freely.
- **Gated:** Validity gate active. Every turn is checked; violations trigger rewrites.
- **Adversarial:** One agent is instructed to deliberately evade the gate.

### 3.2 Argument Ledger

Every agent turn must end with a structured JSON block declaring new "hits" (claims landed against the opposing side) and addressing open hits from previous rounds. Each hit is a typed object:

```
Hit = {id, by, against, claim, status, rebuttal, round_landed}
status ∈ {open, conceded, rebutted, dodged}
```

The ledger enables: (a) convergence detection — the debate halts when no new hits appear for N consecutive rounds; (b) accountability — agents must address open hits before introducing new material; (c) export — the ledger maps directly to Argdown argument maps.

### 3.3 Z3 SMT Plugin

Arbiter loads a user-provided Python module exporting a `verify()` function that encodes the theory's formal claims as Z3 constraints. The module is executed at debate initialization; its findings are formatted into a stipulation block injected into agent contexts (for gated/adversarial topologies) and into the gate's rule set.

The plugin interface is minimal:

```python
def verify() -> dict[str, CheckResult]:
    # CheckResult = {name, result, expected, explanation}
```

In our case study, the auto-generated Z3 module produced 15 checks, 11 of which returned UNSAT — mechanically proving the theory's formal claims are self-contradictory.

### 3.4 Multi-Lab Judge Panel

After debate completion, a panel of N judges from configurable LLM providers scores the transcript against a rubric. The rubric criteria are defined in YAML (any number, any names, any score ranges). Scores are aggregated with per-criterion spread flagging: if judges disagree by more than a configurable threshold, the criterion is marked low-confidence.

The panel verdict is the majority vote. Our case study used three judges (Anthropic Claude Opus 4.5, OpenAI gpt-5, Google Gemini 3.1 Pro) with five criteria (notation fidelity, argument survival, concession honesty, falsifiability, synchronicity handling).

## 4. The Validity Gate

### 4.1 Architecture

The validity gate is a five-layer checking pipeline applied to every agent turn in gated/adversarial topologies:

1. **Pattern matching:** Configurable regex rules check for known contradiction patterns (e.g., simultaneous assertion of "G is fixed" and "edges can be added"). Denial-aware: if the agent explicitly negates the claim (e.g., "not the creation of a new edge"), the rule is skipped.

2. **Self-consistency:** Checks the agent's current claims against its own prior claims for direct verbal contradictions (e.g., "G is fixed" in round 1, "G is mutable" in round 3).

3. **Definitional shift detection:** Flags when a key term (from a configurable seed-term list) is used with a different meaning than previously established. Any shift on a seed term is a violation regardless of whether the agent acknowledges it.

4. **Z3 structural check:** For structural claims about graph properties, encodes them as Z3 constraints and checks satisfiability against the stipulated facts. Abstains (returns no violation) when claims cannot be cleanly translated to SMT-LIB.

5. **LLM entailment check:** A semantic backstop using a separate LLM call to detect paraphrased violations that regex misses. Only fires when the cheaper checks above don't already trigger. Only flags medium/high confidence results.

When a violation is detected, the agent receives a rejection notice listing specific failures and is asked to rewrite (up to `max_rewrites` attempts, default 2). If all rewrites fail, the turn is kept but tagged as `validity_violation`, visible to judges.

### 4.2 Calibration Methodology

We introduce a gold-standard calibration methodology for validity gates:

1. **Construct test cases:** For each gate rule, hand-craft (or auto-generate) positive cases (should trigger) and negative cases (should not trigger), including paraphrased and edge-case variants.

2. **Measure recall and specificity:** Run all test cases through the gate. Compute:
   - Recall = (TP + 0.5 × PARTIAL) / total_positive
   - Specificity = TN / total_negative

3. **Iterate:** If recall < threshold, identify failing patterns, regenerate, and re-test.

In our case study, the gate achieved 0.94 weighted recall and 1.00 specificity after three iterations of pattern refinement (from 0.61 initial recall). The auto-generated gate from the init pipeline achieved 100% recall after two self-calibration iterations.

### 4.3 Operational Results

We measured the gate's operational performance across three conditions:

| Condition | Violations caught | Total drafts | Catch rate | Interpretation |
|---|---|---|---|---|
| **v3 (stipulated)** | 0 | 42 | N/A | Agents comply with Z3 stipulation |
| **v3-blind (gate only)** | 6 | 47 | 6/6 = 100% | Gate catches all unwitting violations |
| **v3-adversarial** | 2 | 8 (adversary) | 2/2 attempts | Gate deters adversary after R2 |

The v3-blind result is the key finding: without being told about the Z3 contradiction, agents naturally made 6 violating claims across 47 turns. The gate caught all 6. The 4 affected agents successfully rewrote clean versions after receiving rejection notices; the remaining 2 exhausted their rewrite budget and were tagged.

## 5. Adversarial Red-Teaming

### 5.1 Design

In the adversarial posture, the Proponent agent receives an explicit instruction to defend the theory "by any rhetorical means available" while knowing the gate's rules. It is told the Z3 stipulations and instructed to try paraphrase, definitional gymnastics, and "two-modes" framings to smuggle violations past the gate.

### 5.2 Results

The adversary attempted to violate Z3-1 (G fixed + edge creation) twice in Round 2. Both attempts were caught — the first by the regex pattern checker, the second by the LLM entailment check. After Round 2, the adversary abandoned evasion entirely and adopted a legitimate defense strategy ("perspectival projection," "metatheoretic accessibility function") for Rounds 3-6.

**The gate functions as a deterrence mechanism, not just a filter.** Its value is behavioral steering: early catches force the adversary to find valid arguments, which improves debate quality rather than simply blocking turns. The adversary's post-deterrence arguments were substantively more interesting than its evasion attempts.

## 6. Agentic Init Pipeline

### 6.1 Motivation

Manual setup of a formally verified debate requires domain expertise in the theory under analysis, familiarity with Z3/SMT-LIB, and careful prompt engineering for specialist agents. This process took approximately eight hours in our initial case study. Arbiter's agentic init pipeline automates this process.

### 6.2 Pipeline

```
arbiter init --from-pdf paper.pdf
```

The pipeline proceeds in six phases:

1. **PDF extraction:** PyMuPDF4LLM converts the PDF to LLM-ready markdown.
2. **Claim extraction:** An LLM extracts all claims as structured objects (category, formality flag, dependencies, supporting quotes). The BIT case study yielded 140 claims.
3. **Analysis:** In parallel: contradiction detection (27 found), key term extraction (37 terms), attack angle identification (8 angles). Claims are consolidated into core theses (9).
4. **Escape-route anticipation:** For each contradiction, the LLM predicts defender evasion strategies, generating patterns to catch them.
5. **Parallel generation:** Z3 constraint module (auto-generated and self-tested), agent cast (10 specialists with domain-specific prompts), gate rules (18 rules with auto-calibration), judge rubric (6 topic-specific criteria), source corpus (web search + classification as counter-evidence vs. supporting).
6. **Assembly and validation:** Config YAML written and validated against the Pydantic schema.

### 6.3 Quality Comparison

| Dimension | Manual (8 hours) | Agentic init (25 min) |
|---|---|---|
| Claims extracted | 7 (curated) | 140 → 9 theses |
| Contradictions | 3 | **27** |
| Z3 checks (UNSAT) | 3 | **11** |
| New contradictions found | — | **6 that manual missed** |
| Agents | 7 | **10** (with uncited-field detection) |
| Gate recall | 0.94 (3 iterations) | **1.00** (auto-calibrated) |
| Rubric criteria | 5 (2 generic) | **6** (all topic-specific) |

The agentic pipeline found six contradictions that eight hours of manual analysis missed, including: flow state double-assignment (BELLA 6 and 10), finite termination vs. asymptotic approach, attractor vs. unreachable omega, and BELLA range inconsistency (0-8 vs. States 10-12).

## 7. Case Study: BIT Creation Theory

### 7.1 The Theory

BIT Creation Theory (Torres, 2026) is a 23-page framework claiming that free will and determinism are "co-present structural properties" of a directed acyclic graph (DAG). The theory introduces the BIT (Briana Isabella Torres unit) as "the smallest quantum of conscious experience," a BELLA Scalar System mapping developmental states 0-12, and a "Royal Purple" creation event where agents instantiate new edges in the DAG. The author identifies herself as "the Singularity" — the irreducible BIT unit of the system.

### 7.2 Experimental Design

We ran eight debate variants in a 2×2×2 design:

| Variable | Values |
|---|---|
| Z3 stipulation | Stipulated to agents / Not stipulated |
| User counter-thesis | Provided ("synchronicity ≠ singularity") / Not provided |
| Validity gate | Active / Inactive |

Plus two additional conditions: adversarial (gate active, Proponent tries to evade) and blind (gate active, agents unaware of Z3).

### 7.3 Results

**Unanimous verdict.** Across all eight conditions, the Skeptic won 24-0 (24 judges, zero dissents).

| Condition | Z3 | Thesis | Gate | Skeptic | Proponent | Confidence |
|---|---|---|---|---|---|---|
| v2.5 | ✓ | ✓ | — | **44.0** | **32.0** | HIGH |
| v3 | ✓ | ✓ | ✓ | 42.0 | 30.0 | HIGH |
| v3-blind | — | ✓ | ✓ | 42.0 | 20.0 | LOW |
| naive | — | — | — | 40.3 | 20.7 | LOW |
| v2-nz | — | ✓ | — | 40.0 | 17.0 | LOW |
| v2 | — | ✓ | — | 39.7 | 20.3 | LOW |
| v2.5-neutral | ✓ | — | — | 39.0 | 20.0 | LOW |
| v3-adversarial | — | ✓ | ✓* | 38.7 | 15.0 | LOW |

*Gate active with adversarial Proponent.

**Key finding: Z3 stipulation helps both sides.** The Proponent scores 32 (stipulated) vs. 17-21 (not stipulated) because stipulation forces them onto defensible ground. The Skeptic also scores higher (44 vs. 38-40) because they can focus on substantive arguments instead of relitigating the formal contradiction. The highest-quality debate (v2.5) has both stipulation and a user-provided counter-thesis.

**The adversarial Proponent scored worst (15.0).** Trying to evade the gate produced incoherent arguments that judges penalized heavily.

### 7.4 Independent Discovery

In the naive condition (no Z3, no user thesis), frontier LLMs from three different labs independently discovered both the formal contradiction (Section 7.3 Step 1 vs. Step 3) and the synchronicity-to-singularity non-sequitur without being prompted. This finding has implications for debate-as-alignment: frontier models can surface genuine logical errors in novel theories without human guidance.

## 8. Limitations

1. **Single case study.** Arbiter has been validated on one theory. Generality across domains (science, policy, philosophy) requires further evaluation.

2. **Gate recall is not 100% on adversarial paraphrases.** The LLM entailment check catches most evasions but a sufficiently creative adversary might find phrasings that pass. The gate's value is deterrence, not guaranteed enforcement.

3. **Cost.** A full debate with 11 agents × 6 rounds × frontier models costs approximately $50-100 in API fees. The init pipeline adds $10-30.

4. **Speed.** The gated topology is slow (~22 min/turn with high-effort entailment checks). Medium-effort settings reduce this to ~8 min/turn with acceptable quality.

5. **LLM judge bias.** Despite multi-lab panels, all LLM judges share training-data biases. The spread-flagging mechanism detects inter-judge disagreement but cannot detect systematic bias shared across all models.

## 9. Conclusion

Arbiter demonstrates that formal verification can be meaningfully integrated into multi-agent LLM debates. The calibrated validity gate provides mechanical enforcement of logical hygiene with measurable recall and specificity. The adversarial red-team posture shows the gate functions as a behavioral steering mechanism that improves debate quality. The agentic init pipeline makes the system accessible to non-experts by automating the setup process from a single PDF input.

Our case study produced a definitive, unanimous verdict on a novel theory — but more importantly, it produced that verdict through a process whose logical hygiene can be independently audited. The Z3 findings are mechanically certified. The gate's catch rate is empirically measured. The judge panel's agreement level is quantified per criterion. This auditability is what distinguishes Arbiter from existing debate frameworks that rely on LLM judgment alone.

Arbiter is available at https://github.com/vishk23/arbiter under the MIT license.

---

## References

- Du, Y., Li, S., Torralba, A., Tenenbaum, J.B., & Mordatch, I. (2023). Improving Factuality and Reasoning in Language Models through Multiagent Debate. ICML 2024.
- Dung, P.M. (1995). On the Acceptability of Arguments and its Fundamental Role in Nonmonotonic Reasoning, Logic Programming and n-Person Games. Artificial Intelligence, 77(2).
- Irving, G., Christiano, P., & Amodei, D. (2018). AI Safety via Debate. arXiv:1805.00899.
- LangChain. (2024). LangGraph: Build resilient language agents as graphs.
- Liang, T., He, Z., Jiao, W., et al. (2023). Encouraging Divergent Thinking in Large Language Models through Multi-Agent Debate. arXiv:2305.19118.
- Torres, B.I. (2026). BIT Creation Theory: Free Will Within a Deterministic DAG Structure. Framework Paper v6.1.
- Zhang, Y., et al. (2026). Agent4Debate: Dynamic Multi-Agent Framework for Competitive Debate. ICASSP 2026.
- Solver-Aided Verification of Policy Compliance in Tool-Augmented LLM Agents. (2026). arXiv:2603.20449.
- Emergent Formal Verification: How an Autonomous AI Ecosystem Independently Discovered SMT-Based Safety. (2026). arXiv:2603.21149.
- The Fusion of Large Language Models and Formal Methods for Trustworthy AI Agents: A Roadmap. (2024). arXiv:2412.06512.

#!/usr/bin/env python3
"""Get peer review feedback on the full project (papers + repo) from GPT and Grok."""
from __future__ import annotations

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

ROOT = Path(__file__).resolve().parent.parent

PAPER_REVIEW_PROMPT = """\
You are a senior AI/ML researcher reviewing a paper submission. Give brutally honest, \
specific peer review feedback. Structure your review as:

## Summary (2-3 sentences)
What the paper claims to do and what it actually demonstrates.

## Strengths
Bullet points — what genuinely holds up.

## Weaknesses
Bullet points — the most serious problems a reviewer would raise. Be specific: \
cite exact claims, sections, or numbers that are wrong, overclaiming, or unsupported.

## Verdict
One of: Accept / Minor Revision / Major Revision / Reject — with 1-sentence reason.

## Suggested Title
Propose a better title if the current one is overclaiming or misleading, or say "Keep as-is."

Be direct. Do not soften criticism."""

REPO_REVIEW_PROMPT = """\
You are a senior software engineer and AI researcher evaluating an open-source research \
project for credibility, technical merit, and impact potential.

The project is called Arbiter — a system that reads academic papers (PDF), extracts \
formal mathematical claims, verifies them using Z3/Knuckledragger, then runs a \
multi-agent debate to evaluate the gap between what a paper proves and what it claims.

Review the README and repo structure below. Structure your feedback as:

## First Impression
What a developer sees when they land on the repo. Is it compelling?

## Technical Credibility
Does the project appear technically sound? What raises red flags?

## Novelty Assessment
Is the core idea genuinely novel or incremental?

## Weaknesses / Red Flags
What would make an experienced engineer or researcher skeptical?

## What Would Make This Stronger
Concrete, specific suggestions.

## Overall Rating
1-10 for: (a) technical merit, (b) presentation/polish, (c) impact potential

Be direct and honest. This person wants real feedback, not encouragement."""


def load_readme() -> str:
    return (ROOT / "README.md").read_text()


def load_repo_structure() -> str:
    """Get a tree-like view of the repo."""
    lines = []
    skip = {'.git', '__pycache__', '.pytest_cache', 'node_modules', '*.egg-info',
            '.venv', 'venv', 'dist', 'build', '.mypy_cache'}
    for p in sorted(ROOT.rglob('*')):
        if any(s in str(p) for s in skip):
            continue
        if p.is_file():
            rel = str(p.relative_to(ROOT))
            lines.append(rel)
    return '\n'.join(lines[:150])


def load_paper(tex_path: str) -> str:
    return (ROOT / tex_path).read_text()


def get_provider(name: str, model: str):
    from arbiter.config import ProviderConfig
    if name == "openai":
        from arbiter.providers.openai import OpenAIProvider
        config = ProviderConfig(
            name="openai", model=model,
            api_key=os.environ.get("OPENAI_API_KEY"),
            reasoning={"effort": "high", "overhead": 10000},
        )
        return OpenAIProvider(config)
    elif name == "grok":
        from arbiter.providers.grok import GrokProvider
        config = ProviderConfig(
            name="grok", model=model,
            api_key=os.environ.get("XAI_API_KEY"),
            base_url="https://api.x.ai/v1",
        )
        return GrokProvider(config)
    raise ValueError(f"Unknown provider: {name}")


def run_review(provider_name: str, model: str, system: str, user: str) -> str:
    p = get_provider(provider_name, model)
    return p.call_with_retry(system, user, max_tokens=3000)


def section(title: str):
    print(f"\n{'='*70}")
    print(f"  {title}")
    print('='*70)


def main():
    reviewers = [
        ("openai", "gpt-5.4"),
        ("grok",   "grok-4.20-0309-reasoning"),
    ]

    readme = load_readme()
    structure = load_repo_structure()
    paper_a = load_paper("papers/arbiter_paper.tex")
    paper_b = load_paper("papers/arbiter_systems_paper.tex")

    all_results = {}

    # ── Repo + README review ──────────────────────────────────────────
    section("REPO & README REVIEW")
    repo_user = f"README:\n\n{readme}\n\nREPO STRUCTURE:\n\n{structure}"
    all_results["repo"] = {}
    for provider_name, model in reviewers:
        print(f"\n--- {provider_name.upper()} ({model}) ---\n")
        try:
            review = run_review(provider_name, model, REPO_REVIEW_PROMPT, repo_user)
            print(review)
            all_results["repo"][f"{provider_name}_{model}"] = review
        except Exception as e:
            print(f"[ERROR: {e}]")
            all_results["repo"][f"{provider_name}_{model}"] = str(e)

    # ── Paper A review ───────────────────────────────────────────────
    section("PAPER A: Z3 AUDIT PAPER")
    all_results["paper_a"] = {}
    for provider_name, model in reviewers:
        print(f"\n--- {provider_name.upper()} ({model}) ---\n")
        try:
            review = run_review(provider_name, model, PAPER_REVIEW_PROMPT,
                                f"Review this paper:\n\n{paper_a}")
            print(review)
            all_results["paper_a"][f"{provider_name}_{model}"] = review
        except Exception as e:
            print(f"[ERROR: {e}]")
            all_results["paper_a"][f"{provider_name}_{model}"] = str(e)

    # ── Paper B review ───────────────────────────────────────────────
    section("PAPER B: ARBITER SYSTEMS PAPER")
    all_results["paper_b"] = {}
    for provider_name, model in reviewers:
        print(f"\n--- {provider_name.upper()} ({model}) ---\n")
        try:
            review = run_review(provider_name, model, PAPER_REVIEW_PROMPT,
                                f"Review this paper:\n\n{paper_b}")
            print(review)
            all_results["paper_b"][f"{provider_name}_{model}"] = review
        except Exception as e:
            print(f"[ERROR: {e}]")
            all_results["paper_b"][f"{provider_name}_{model}"] = str(e)

    # ── Save ─────────────────────────────────────────────────────────
    import json
    out = ROOT / "benchmarks" / "peer_review_results.json"
    out.write_text(json.dumps(all_results, indent=2))
    print(f"\n\nAll reviews saved to {out}")


if __name__ == "__main__":
    main()

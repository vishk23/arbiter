#!/usr/bin/env python3
"""LLM-as-judge baseline for ablation study.

Single LLM call to evaluate a paper — no debate, no verification.
This is the control condition showing what a naive LLM judge produces.

Usage:
    python benchmarks/llm_judge_baseline.py --paper experiments/ai_layoff_trap_v3/ --model gpt-5.4
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from benchmarks.minif2f_bench import get_provider
from arbiter.config import TokenBudgets

import logging
logging.basicConfig(level=logging.INFO)

_B = TokenBudgets()

JUDGE_SYSTEM = """\
You are an expert academic reviewer evaluating a research paper. Your task is to
identify claims that overreach beyond the paper's formal results.

For each claim you evaluate, report:
1. The claim (quote or paraphrase)
2. Whether it is SUPPORTED by the paper's formal model, PARTIALLY supported, or UNSUPPORTED
3. If unsupported: what specific formal gap exists
4. Confidence: high/medium/low

Also provide:
- Overall verdict: Does the paper's core theorem hold?
- Number of overreach instances (claims extending beyond the math)
- Key weaknesses in the paper's argumentation

Be rigorous and specific. Do not accept rhetorical claims as proven.
Return your analysis as JSON with keys: verdict, overreach_count, claims (list), weaknesses (list).
"""


def run_baseline(paper_dir: str, model: str) -> dict:
    """Run single-LLM judge on a paper."""
    provider = get_provider(model)

    # Load the paper summary from config
    config_path = os.path.join(paper_dir, "config.yaml")
    import yaml
    with open(config_path) as f:
        config = yaml.safe_load(f)

    topic = config.get("topic", {})
    summary = topic.get("summary", "")
    counter = topic.get("counter_thesis", "")

    # Load claims if available from init
    claims_text = ""
    init_html = os.path.join(paper_dir, "live_init.html")
    if os.path.exists(init_html):
        with open(init_html) as f:
            html = f.read()
        # Extract text content (crude but works)
        import re
        claims_text = re.sub(r'<[^>]+>', '', html)[:5000]

    user_prompt = (
        f"PAPER: {topic.get('name', 'Unknown')}\n\n"
        f"SUMMARY:\n{summary[:2000]}\n\n"
        f"COUNTER-THESIS:\n{counter[:1000]}\n\n"
        f"EXTRACTED CLAIMS (first 5000 chars):\n{claims_text[:5000]}\n\n"
        "Evaluate this paper. Identify all claims that overreach beyond the formal model. "
        "Return JSON with: verdict, overreach_count, claims (list of {claim, status, gap, confidence}), "
        "weaknesses (list of strings)."
    )

    print(f"Running LLM-judge baseline with {model}...")
    response = provider.call_with_retry(JUDGE_SYSTEM, user_prompt, max_tokens=_B.xl)

    return {
        "model": model,
        "paper": topic.get("name", "Unknown"),
        "response": response if isinstance(response, str) else str(response),
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


def main():
    parser = argparse.ArgumentParser(description="LLM-judge baseline")
    parser.add_argument("--paper", required=True, help="Path to experiment directory")
    parser.add_argument("--model", default="gpt-5.4", help="Model to use as judge")
    parser.add_argument("--output", default=None)
    args = parser.parse_args()

    result = run_baseline(args.paper, args.model)

    if not args.output:
        args.output = f"benchmarks/llm_judge_baseline_{args.model}.json"

    os.makedirs(os.path.dirname(args.output) or ".", exist_ok=True)
    with open(args.output, "w") as f:
        json.dump(result, f, indent=2)

    print(f"\nSaved to {args.output}")
    print(f"\nResponse preview:\n{result['response'][:500]}")


if __name__ == "__main__":
    main()

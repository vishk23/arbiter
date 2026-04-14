#!/usr/bin/env python3
"""Audit FormalMATH proofs: does the certificate prove the theorem or a trivial lemma?"""
from __future__ import annotations
import json, os, sys, subprocess
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from benchmarks.minif2f_bench import get_provider
from arbiter.providers.base import strip_markdown_fences

CLASSIFIER_PROMPT = """\
You are auditing a formal proof. Given:
1. A math PROBLEM statement
2. Generated Python CODE that claims to prove it
3. The EXECUTION OUTPUT

Classify the proof into ONE category:

- VALID: The kd.prove() or minimal_polynomial certificate actually proves the core mathematical claim
- TRIVIAL_CERTIFICATE: kd.prove() proves a tautology or trivial arithmetic (e.g., "x <= x", "n > 0 → 2n > 0") while the real work is done by numerical computation
- PARTIAL: Proves a sub-result but not the full theorem
- NUMERICAL_ONLY: No formal certificate; only numerical/brute-force verification
- WRONG: Proves something unrelated to the problem
- CRASH: Code doesn't run

Return JSON: {"category": "...", "what_certificate_proves": "...", "what_problem_asks": "...", "reason": "..."}
"""


def audit_one(problem_stmt, code, output, provider):
    user = f"PROBLEM:\n{problem_stmt[:500]}\n\nCODE:\n{code[:2000]}\n\nOUTPUT:\n{output[:1000]}"
    try:
        resp = provider.call_with_retry(CLASSIFIER_PROMPT, user, max_tokens=500)
        text = resp if isinstance(resp, str) else str(resp)
        text = strip_markdown_fences(text)
        return json.loads(text)
    except:
        return {"category": "parse_error"}


def main():
    from datasets import load_dataset
    ds = load_dataset('SphereLab/FormalMATH-All')['train']
    stmt_map = {row['theorem_names']: row['refined_statement'] for row in ds}

    provider = get_provider("gpt-5.4-mini")
    audit_dir = "benchmarks/formalmath_audit"

    results = []
    cats = {}

    proved_files = [f for f in os.listdir(audit_dir)
                    if f.endswith('.py') and 'FAILED' not in f]

    print(f"Auditing {len(proved_files)} proved FormalMATH results...")

    for i, fname in enumerate(sorted(proved_files), 1):
        name = fname.replace('.py', '')
        code_path = os.path.join(audit_dir, fname)
        out_path = os.path.join(audit_dir, name + '.out')

        with open(code_path) as f:
            code = f.read()
        output = ""
        if os.path.exists(out_path):
            with open(out_path) as f:
                output = f.read()

        stmt = stmt_map.get(name, "Unknown problem")

        print(f"[{i}/{len(proved_files)}] {name}...", end=" ", flush=True)
        result = audit_one(stmt, code, output, provider)
        cat = result.get("category", "unknown")
        cats[cat] = cats.get(cat, 0) + 1
        results.append({"id": name, **result})
        print(cat)

    print(f"\n{'='*50}")
    print("AUDIT RESULTS:")
    for cat, count in sorted(cats.items(), key=lambda x: -x[1]):
        pct = count / len(results) * 100
        print(f"  {cat}: {count} ({pct:.1f}%)")

    valid = cats.get("VALID", 0)
    print(f"\nGenuinely valid: {valid}/{len(results)} ({valid/len(results)*100:.1f}%)")

    with open("benchmarks/formalmath_audit_results.json", "w") as f:
        json.dump({"n": len(results), "categories": cats, "results": results}, f, indent=2)
    print("Saved to benchmarks/formalmath_audit_results.json")


if __name__ == "__main__":
    main()

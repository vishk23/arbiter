"""Live HTML argument map with auto-refresh.

Writes a self-contained HTML file that auto-refreshes every 5s.
Can be called during init (claims/contradictions) or debate (ledger).
Open in browser to watch the debate build in real time.
"""

from __future__ import annotations

import html as _html
from pathlib import Path


def _syntax_highlight_argdown(escaped_html: str) -> str:
    """Apply CSS classes to argdown syntax in pre-escaped HTML."""
    import re
    text = escaped_html

    # Comments: // ...
    text = re.sub(
        r'^(// .*)$',
        r'<span class="ad-comment">\1</span>',
        text, flags=re.MULTILINE,
    )
    # Section headers: === ... ===
    text = re.sub(
        r'^(===.*)$',
        r'<span class="ad-section">\1</span>',
        text, flags=re.MULTILINE,
    )
    # Statements: [id]: text
    text = re.sub(
        r'\[([^\]]+)\]:',
        r'<span class="ad-statement">[\1]:</span>',
        text,
    )
    # Arguments: <id>: text
    text = re.sub(
        r'&lt;([^&]+)&gt;:',
        r'<span class="ad-argument">&lt;\1&gt;:</span>',
        text,
    )
    # Support relations: + [id]
    text = re.sub(
        r'(\s+)\+ \[([^\]]+)\]',
        r'\1<span class="ad-relation-support">+ [\2]</span>',
        text,
    )
    # Attack relations: - <id>
    text = re.sub(
        r'(\s+)- &lt;([^&]+)&gt;',
        r'\1<span class="ad-relation-attack">- &lt;\2&gt;</span>',
        text,
    )
    # Tags: #word
    text = re.sub(
        r'#(\w+)',
        r'<span class="ad-tag">#\1</span>',
        text,
    )
    return text


def write_live_html(
    path: Path,
    topic: str,
    stage: str,
    body: str,
) -> None:
    """Write a self-refreshing HTML page.

    Parameters
    ----------
    path: where to write the HTML file
    topic: debate topic name
    stage: e.g. "Init — Claims", "Round 2", "Judge Verdict"
    body: the main content (argdown, claim list, etc.) — will be escaped
    """
    escaped = _html.escape(body, quote=False)
    # Syntax-highlight argdown: color statements, arguments, tags, comments
    highlighted = _syntax_highlight_argdown(escaped)
    path.write_text(f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>Arbiter — {_html.escape(topic)}</title>
  <meta http-equiv="refresh" content="5">
  <style>
    body {{ font-family: 'SF Mono', 'Fira Code', monospace; margin: 0; padding: 2rem; background: #0d1117; color: #c9d1d9; }}
    h1 {{ color: #58a6ff; font-size: 1.3rem; margin: 0 0 0.3rem 0; }}
    .stage {{ color: #8b949e; font-size: 0.9rem; margin-bottom: 1.5rem; border-bottom: 1px solid #21262d; padding-bottom: 0.8rem; }}
    .content {{ background: #161b22; border: 1px solid #30363d; border-radius: 6px; padding: 1.2rem; overflow: auto; max-height: 85vh; }}
    pre {{ white-space: pre-wrap; font-size: 0.82rem; line-height: 1.6; margin: 0; }}
    /* Argdown syntax highlighting */
    .ad-statement {{ color: #7ee787; font-weight: bold; }}
    .ad-argument {{ color: #ff7b72; font-weight: bold; }}
    .ad-tag {{ color: #d2a8ff; font-style: italic; }}
    .ad-comment {{ color: #8b949e; font-style: italic; }}
    .ad-relation-support {{ color: #3fb950; }}
    .ad-relation-attack {{ color: #f85149; }}
    .ad-section {{ color: #58a6ff; font-weight: bold; font-size: 0.95rem; }}
  </style>
</head>
<body>
  <h1>Arbiter — {_html.escape(topic)}</h1>
  <div class="stage">{_html.escape(stage)} · auto-refreshes every 5s</div>
  <div class="content"><pre>{highlighted}</pre></div>
</body>
</html>""")


def format_claims_view(claims: list[dict], contradictions: list[dict] | None = None, key_terms: dict | None = None) -> str:
    """Format claims + contradictions for the live HTML view."""
    lines = []

    if claims:
        lines.append(f"=== CLAIMS ({len(claims)}) ===\n")
        for c in claims:
            formal = " [FORMAL]" if c.get("is_formal") else ""
            cat = c.get("category", "")
            lines.append(f"  {c['id']}: {c['claim'][:120]}")
            lines.append(f"       [{cat}]{formal}")
            if c.get("depends_on"):
                lines.append(f"       depends: {', '.join(c['depends_on'])}")
            lines.append("")

    if contradictions:
        lines.append(f"\n=== CONTRADICTIONS ({len(contradictions)}) ===\n")
        for c in contradictions:
            sev = c.get("severity", "?")
            z3 = " [Z3-encodable]" if c.get("z3_encodable") else ""
            lines.append(f"  [{sev.upper()}]{z3}")
            lines.append(f"    A: {c.get('claim_a', '')[:100]}")
            lines.append(f"    B: {c.get('claim_b', '')[:100]}")
            lines.append(f"    → {c.get('contradiction', '')[:120]}")
            lines.append("")

    if key_terms:
        lines.append(f"\n=== KEY TERMS ({len(key_terms)}) ===\n")
        for term, defn in key_terms.items():
            lines.append(f"  {term}: {defn[:100]}")

    return "\n".join(lines)


def format_init_argdown(claims: list[dict], contradictions: list[dict] | None = None) -> str:
    """Format claims + contradictions as argdown notation."""
    lines = ["===", "title: Init — Claims & Contradictions", "===", ""]

    if claims:
        lines.append("// === Claims ===")
        lines.append("")
        for c in claims:
            cat = c.get("category", "other")
            formal = " #formal" if c.get("is_formal") else ""
            claim_text = c.get("claim", "").replace("\n", " ").strip()[:150]
            lines.append(f"[{c['id']}]: {claim_text} #{cat}{formal}")
            # Show dependencies
            for dep in c.get("depends_on", []):
                lines.append(f"  + [{dep}]")
            lines.append("")

    if contradictions:
        lines.append("// === Contradictions ===")
        lines.append("")
        for i, c in enumerate(contradictions):
            sev = c.get("severity", "?")
            z3 = " #z3" if c.get("z3_encodable") else ""
            desc = c.get("contradiction", "").replace("\n", " ").strip()[:150]
            lines.append(f"<contra_{i+1}>: {desc} #{sev}{z3}")
            # Link to claims if we can identify them
            a = c.get("claim_a", "")[:80]
            b = c.get("claim_b", "")[:80]
            lines.append(f"  // A: {a}")
            lines.append(f"  // B: {b}")
            lines.append("")

    return "\n".join(lines)


def format_agents_view(agents: dict, gate_rules: dict | None = None, rubric: list[dict] | None = None) -> str:
    """Format agent cast + gate + rubric for the live HTML view."""
    lines = []

    if agents:
        lines.append(f"=== AGENT CAST ({len(agents)}) ===\n")
        for name, cfg in agents.items():
            lines.append(f"  {name}")
            lines.append(f"    side: {cfg.get('side', '?')} | provider: {cfg.get('provider', '?')}")
            prompt = cfg.get("system_prompt", "")[:150]
            lines.append(f"    prompt: {prompt}...")
            lines.append("")

    if gate_rules and gate_rules.get("stipulated_rules"):
        rules = gate_rules["stipulated_rules"]
        lines.append(f"\n=== GATE RULES ({len(rules)}) ===\n")
        for r in rules:
            lines.append(f"  [{r.get('id', '?')}] {r.get('fact', '')[:120]}")
            lines.append("")

    if rubric:
        lines.append(f"\n=== RUBRIC ({len(rubric)} criteria) ===\n")
        for r in rubric:
            lines.append(f"  {r.get('id', '?')}: {r.get('name', '?')}")
            lines.append(f"    {r.get('description', '')[:120]}")
            lines.append("")

    return "\n".join(lines)

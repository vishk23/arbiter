"""Tests for the argument ledger."""

from arbiter.ledger.ops import add_hit, resolve_hit, open_hits, ledger_grew
from arbiter.ledger.parser import parse_ledger_block


def test_add_hit():
    ledger = []
    ledger = add_hit(ledger, by="Skeptic", against="Theory", claim="G is inconsistent", round_idx=1)
    assert len(ledger) == 1
    assert ledger[0]["by"] == "Skeptic"
    assert ledger[0]["status"] == "open"


def test_resolve_hit():
    ledger = add_hit([], by="Skeptic", against="Theory", claim="test", round_idx=1)
    hit_id = ledger[0]["id"]
    ledger = resolve_hit(ledger, hit_id, "rebutted", "Proponent's rebuttal here")
    assert ledger[0]["status"] == "rebutted"
    assert ledger[0]["rebuttal"] == "Proponent's rebuttal here"


def test_open_hits_filter():
    ledger = add_hit([], by="Skeptic", against="Proponent", claim="c1", round_idx=1)
    ledger = add_hit(ledger, by="Skeptic", against="Theory", claim="c2", round_idx=1)
    ledger = resolve_hit(ledger, ledger[0]["id"], "conceded", "fair point")

    all_open = open_hits(ledger)
    assert len(all_open) == 1
    assert all_open[0]["claim"] == "c2"

    pro_open = open_hits(ledger, against="Proponent")
    assert len(pro_open) == 0  # was conceded


def test_ledger_grew():
    ledger = add_hit([], by="A", against="B", claim="c", round_idx=1)
    assert ledger_grew(ledger, 0) is True
    assert ledger_grew(ledger, 1) is False


def test_parse_ledger_block_valid():
    text = '''Here is my argument.
```json
{"new_hits":[{"against":"Theory","claim":"G is broken"}],"hits_addressed":[]}
```
'''
    result = parse_ledger_block(text)
    assert len(result["new_hits"]) == 1
    assert result["new_hits"][0]["claim"] == "G is broken"


def test_parse_ledger_block_missing():
    result = parse_ledger_block("No JSON here at all.")
    assert result["new_hits"] == []
    assert result["hits_addressed"] == []


def test_parse_ledger_block_malformed():
    text = '```json\n{broken json\n```'
    result = parse_ledger_block(text)
    assert result["new_hits"] == []

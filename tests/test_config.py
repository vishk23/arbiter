"""Tests for config loading and validation."""


import pytest

from arbiter.config import ArbiterConfig, load_config


def test_quickstart_config_loads(quickstart_config):
    cfg = load_config(quickstart_config)
    assert cfg.topic.name
    assert len(cfg.agents) >= 2
    assert len(cfg.providers) >= 1
    assert cfg.topology == "standard"


def test_bit_config_loads(bit_config):
    cfg = load_config(bit_config)
    assert cfg.topic.name
    assert len(cfg.agents) >= 5
    assert cfg.topology == "gated"
    assert cfg.z3 is not None
    assert cfg.gate is not None
    assert cfg.gate.enabled


def test_provider_ref_validation():
    """Agent referencing non-existent provider should fail."""
    raw = {
        "topic": {"name": "Test", "summary": "Test summary"},
        "providers": {"openai": {"model": "gpt-5.4-mini"}},
        "agents": {
            "A1": {"provider": "nonexistent", "side": "Proponent", "system_prompt": "test"},
        },
        "judge": {
            "rubric": [{"id": "R1", "name": "test", "description": "test"}],
            "panel": [{"provider": "openai"}],
        },
    }
    with pytest.raises(ValueError, match="undefined provider"):
        ArbiterConfig.model_validate(raw)


def test_minimal_valid_config():
    """Minimal config that should pass validation."""
    raw = {
        "topic": {"name": "Test", "summary": "A test debate"},
        "providers": {"openai": {"model": "gpt-5.4-mini"}},
        "agents": {
            "Pro": {"provider": "openai", "side": "Proponent", "system_prompt": "Defend."},
            "Con": {"provider": "openai", "side": "Skeptic", "system_prompt": "Attack."},
        },
        "judge": {
            "rubric": [{"id": "R1", "name": "quality", "description": "Argument quality"}],
            "panel": [{"provider": "openai"}],
        },
    }
    cfg = ArbiterConfig.model_validate(raw)
    assert cfg.topology == "gated"  # prod default
    assert cfg.gate is not None  # auto-created for gated topology
    assert len(cfg.agents) == 2


def test_gated_topology_auto_creates_gate():
    """Setting topology=gated without gate config should auto-create one."""
    raw = {
        "topic": {"name": "Test", "summary": "Test"},
        "topology": "gated",
        "providers": {"openai": {"model": "gpt-5.4-mini"}},
        "agents": {
            "Pro": {"provider": "openai", "side": "Proponent", "system_prompt": "x"},
        },
        "judge": {
            "rubric": [{"id": "R1", "name": "q", "description": "q"}],
            "panel": [{"provider": "openai"}],
        },
    }
    cfg = ArbiterConfig.model_validate(raw)
    assert cfg.gate is not None
    assert cfg.gate.enabled

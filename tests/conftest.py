"""Shared fixtures for Arbiter tests."""

from pathlib import Path

import pytest

FIXTURES_DIR = Path(__file__).parent / "fixtures"
REPO_ROOT = Path(__file__).parent.parent


@pytest.fixture
def quickstart_config():
    return REPO_ROOT / "configs" / "quickstart.yaml"


@pytest.fixture
def bit_config():
    return REPO_ROOT / "experiments" / "bit_creation_theory" / "config.yaml"

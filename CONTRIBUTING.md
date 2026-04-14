# Contributing to Arbiter

## Setup

```bash
git clone https://github.com/vishk23/arbiter.git
cd arbiter
pip install -e ".[all]"
cp .env.example .env
# Fill in at least OPENAI_API_KEY
```

## Running Tests

```bash
# Unit tests (no API keys needed)
pytest tests/ -v --ignore=tests/test_integration.py

# Full suite including integration tests (needs API keys)
pytest tests/ -v

# Lint
ruff check src/ tests/
```

## Code Style

- Format with `ruff` (configured in `pyproject.toml`)
- Use type hints for function signatures
- Docstrings on public functions (Google style)
- No `print()` in library code — use `logging.getLogger(__name__)`
- Console output via `rich.console.Console` in CLI only

## Architecture

See [ARCHITECTURE.md](ARCHITECTURE.md) for the full module map and data flow.

Key directories:
- `src/arbiter/` — core library
- `src/arbiter/init/` — agentic init pipeline (PDF → config)
- `src/arbiter/gate/` — LLM validity gate
- `src/arbiter/judge/` — multi-lab judge panel
- `src/arbiter/web/` — live dashboard (FastAPI + SSE)
- `tests/` — pytest suite
- `experiments/` — case studies and configs

## Pull Requests

1. Fork the repo
2. Create a feature branch (`git checkout -b feature/my-change`)
3. Make your changes with tests
4. Run `pytest tests/` and `ruff check src/`
5. Open a PR with a clear description

## Adding a Provider

1. Create `src/arbiter/providers/my_provider.py` extending `BaseProvider`
2. Implement `_init_client`, `_call_impl`, `_call_structured_impl`
3. Register in `PROVIDER_REGISTRY` in `src/arbiter/providers/__init__.py`
4. Add tests

## Adding an Experiment

1. Create `experiments/my_topic/` with the source PDF
2. Run `arbiter init --from-pdf experiments/my_topic/source.pdf --output-dir experiments/my_topic/`
3. Run `arbiter run experiments/my_topic/config.yaml`
4. Commit the config + gate_tests.yaml (not outputs or checkpoints)

"""Background thread wrappers for Arbiter runners.

Each function spawns a daemon thread, catches all exceptions, and emits
completion or error events via the shared event bus.
"""

from __future__ import annotations

import threading
import traceback
from typing import Any

from arbiter.web.event_bus import get_bus


# ---------------------------------------------------------------------------
# Init runner
# ---------------------------------------------------------------------------


def run_init_background(
    kwargs: dict[str, Any],
    stop_event: threading.Event | None = None,
) -> threading.Thread:
    """Run the init pipeline in a daemon thread.

    Emits ``init.done`` on success or ``error`` on failure.
    """

    def _target() -> None:
        bus = get_bus()
        try:
            from arbiter.init.pipeline import run_init  # lazy import

            # Map CLI param names to run_init param names
            init_args = {
                "from_pdf": kwargs.get("from_pdf"),
                "topic": kwargs.get("topic"),
                "output_dir": kwargs.get("output_dir", "web-init/"),
                "provider_name": kwargs.get("provider", "_auto_"),
                "provider_model": kwargs.get("model", ""),
                "providers_spec": kwargs.get("providers"),
                "interactive": kwargs.get("interactive", False),
                "effort": kwargs.get("effort", "medium"),
                "skip_calibration": kwargs.get("skip_calibration", False),
            }
            # Remove None values so defaults apply
            init_args = {k: v for k, v in init_args.items() if v is not None}
            run_init(**init_args)
            bus.emit("init.done", "init", {"status": "complete"})
        except Exception as exc:
            bus.emit(
                "error",
                "init",
                {
                    "error": str(exc),
                    "traceback": traceback.format_exc(),
                },
            )

    t = threading.Thread(target=_target, daemon=True, name="arbiter-init")
    t.start()
    return t


# ---------------------------------------------------------------------------
# Debate runner
# ---------------------------------------------------------------------------


def run_debate_background(
    config_path: str,
    stop_event: threading.Event | None = None,
) -> threading.Thread:
    """Run the debate engine in a daemon thread.

    Emits ``debate.done`` on success or ``error`` on failure.
    """

    def _target() -> None:
        bus = get_bus()
        try:
            from arbiter.config import load_config  # lazy imports
            from arbiter.graph import DebateEngine

            from pathlib import Path

            cfg = load_config(Path(config_path))
            engine = DebateEngine(cfg)
            engine.run()
            bus.emit(
                "debate.done",
                "debate",
                {"status": "complete"},
            )
        except Exception as exc:
            bus.emit(
                "error",
                "debate",
                {
                    "error": str(exc),
                    "traceback": traceback.format_exc(),
                },
            )

    t = threading.Thread(target=_target, daemon=True, name="arbiter-debate")
    t.start()
    return t


# ---------------------------------------------------------------------------
# Judge runner
# ---------------------------------------------------------------------------


def run_judge_background(
    output_path: str,
    config_path: str | None = None,
    stop_event: threading.Event | None = None,
) -> threading.Thread:
    """Run the judge panel in a daemon thread.

    Emits ``judge.verdict`` on success or ``error`` on failure.
    """

    def _target() -> None:
        bus = get_bus()
        try:
            from arbiter.judge import panel  # lazy import

            verdict = panel.run(
                output_path,
                config_path=config_path,
                stop_event=stop_event,
            )
            bus.emit(
                "judge.verdict",
                "judge",
                {"status": "complete", "verdict": verdict},
            )
        except Exception as exc:
            bus.emit(
                "error",
                "judge",
                {
                    "error": str(exc),
                    "traceback": traceback.format_exc(),
                },
            )

    t = threading.Thread(target=_target, daemon=True, name="arbiter-judge")
    t.start()
    return t

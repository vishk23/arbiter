"""FastAPI web dashboard for Arbiter.

Serves the static UI and provides SSE streaming of debate events,
plus REST endpoints for controlling runs.
"""

from __future__ import annotations

import asyncio
import json
import queue
import threading
from pathlib import Path
from typing import Any, AsyncIterable

from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, JSONResponse
from fastapi.sse import EventSourceResponse, ServerSentEvent

from arbiter.web.event_bus import get_bus

# ---------------------------------------------------------------------------
# App setup
# ---------------------------------------------------------------------------

app = FastAPI(title="Arbiter Dashboard")

STATIC_DIR = Path(__file__).parent / "static"

# ---------------------------------------------------------------------------
# Run state
# ---------------------------------------------------------------------------

_run_config: dict[str, Any] = {}
_stop_event = threading.Event()
_current_thread: threading.Thread | None = None
_auto_started = False


def set_run_config(config: dict[str, Any]) -> None:
    """Called before uvicorn starts to inject the desired run configuration."""
    global _run_config, _auto_started
    _run_config = config
    _auto_started = False


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------


@app.get("/")
async def index() -> FileResponse:
    """Serve the static dashboard page."""
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/events", response_class=EventSourceResponse)
async def events() -> AsyncIterable[ServerSentEvent]:
    """SSE endpoint — sends history for catch-up, then live events."""
    global _auto_started
    bus = get_bus()
    sub = bus.subscribe()

    # Auto-start runner on first SSE connection if configured
    if _run_config.get("auto_start") and not _auto_started:
        _auto_started = True
        _kick_runner(_run_config)

    # 1) Replay history for catch-up
    for evt in bus.history():
        yield ServerSentEvent(data=evt)

    # 2) Stream live events with keepalive
    try:
        while True:
            try:
                evt = await asyncio.wait_for(
                    asyncio.get_event_loop().run_in_executor(None, sub.get, True, 15),
                    timeout=16,
                )
                yield ServerSentEvent(data=evt)
            except (asyncio.TimeoutError, queue.Empty):
                yield ServerSentEvent(comment="keepalive")
    finally:
        bus.unsubscribe(sub)


@app.get("/api/status")
async def status() -> JSONResponse:
    """Return current bus stats and run state."""
    bus = get_bus()
    return JSONResponse(
        {
            "history_length": len(bus.history()),
            "subscriber_count": len(bus._subscribers),
            "running": _current_thread is not None and _current_thread.is_alive(),
        }
    )


@app.post("/api/run")
async def run(request: Request) -> JSONResponse:
    """Start a runner in the background."""
    global _current_thread, _stop_event

    body = await request.json()
    mode: str = body.get("mode", "debate")
    config: dict = body.get("config", {})

    if _current_thread is not None and _current_thread.is_alive():
        return JSONResponse(
            {"error": "A run is already in progress. POST /api/stop first."},
            status_code=409,
        )

    _stop_event = threading.Event()
    _current_thread = _kick_runner({"mode": mode, **config})

    return JSONResponse({"status": "started", "mode": mode})


@app.post("/api/stop")
async def stop() -> JSONResponse:
    """Signal the running task to stop."""
    _stop_event.set()
    return JSONResponse({"status": "stop_requested"})


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _kick_runner(cfg: dict) -> threading.Thread | None:
    """Dispatch to the correct runner based on mode. Returns the thread."""
    global _current_thread, _stop_event
    # Lazy import to avoid circular deps
    from arbiter.web.runner import (
        run_debate_background,
        run_init_background,
        run_judge_background,
    )

    mode = cfg.get("mode", "debate")
    _stop_event = threading.Event()

    if mode == "init":
        init_kwargs = cfg.get("init_kwargs", {k: v for k, v in cfg.items() if k not in ("mode", "auto_start")})
        t = run_init_background(init_kwargs, stop_event=_stop_event)
    elif mode == "judge":
        output_path = cfg.get("output_path", "")
        config_path = cfg.get("config_path")
        t = run_judge_background(
            output_path, config_path=config_path, stop_event=_stop_event
        )
    else:
        config_path = cfg.get("config_path", "")
        t = run_debate_background(
            config_path, stop_event=_stop_event,
        )

    _current_thread = t
    return t

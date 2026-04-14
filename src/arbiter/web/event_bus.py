"""Thread-safe event bus for streaming debate events to web clients.

Singleton pattern. Producers (graph.py, pipeline.py) call emit() from
sync threads. Consumers (FastAPI SSE) subscribe to get a per-client
queue. Zero cost when no subscribers — emit() is a no-op.
"""

from __future__ import annotations

import queue
import threading
import time
from typing import Any


class EventBus:
    """Fan-out event bus with per-subscriber queues and history buffer."""

    def __init__(self, history_size: int = 500) -> None:
        self._lock = threading.Lock()
        self._subscribers: list[queue.Queue] = []
        self._history: list[dict] = []
        self._history_size = history_size

    def has_subscribers(self) -> bool:
        """Fast check — avoids serialization cost when nobody is listening."""
        return bool(self._subscribers)

    def emit(self, event_type: str, phase: str, data: dict[str, Any]) -> None:
        """Emit an event to all subscribers. No-op if nobody is listening."""
        if not self._subscribers:
            return

        event = {
            "type": event_type,
            "ts": time.time(),
            "phase": phase,
            "data": data,
        }

        with self._lock:
            # Append to history ring buffer
            self._history.append(event)
            if len(self._history) > self._history_size:
                self._history = self._history[-self._history_size:]

            # Fan out to all subscriber queues
            dead: list[queue.Queue] = []
            for q in self._subscribers:
                try:
                    q.put_nowait(event)
                except queue.Full:
                    dead.append(q)
            for q in dead:
                self._subscribers.remove(q)

    def subscribe(self) -> queue.Queue:
        """Create a new subscriber queue. Returns it for polling."""
        q: queue.Queue = queue.Queue(maxsize=1000)
        with self._lock:
            self._subscribers.append(q)
        return q

    def unsubscribe(self, q: queue.Queue) -> None:
        """Remove a subscriber queue."""
        with self._lock:
            try:
                self._subscribers.remove(q)
            except ValueError:
                pass

    def history(self) -> list[dict]:
        """Return a copy of the history buffer for catch-up."""
        with self._lock:
            return list(self._history)

    def clear(self) -> None:
        """Clear history and all subscribers."""
        with self._lock:
            self._history.clear()
            self._subscribers.clear()


# Module-level singleton
_bus = EventBus()


def get_bus() -> EventBus:
    """Return the global event bus singleton."""
    return _bus

"""Per-turn live logger with Rich console output."""

from __future__ import annotations

import time
from pathlib import Path

from rich.console import Console

_console = Console()


class LiveLogger:
    """Append-only Markdown logger that flushes after every write.

    Each debate turn is immediately persisted so a crashed run still
    leaves a usable record.
    """

    def __init__(self, output_dir: str, label: str) -> None:
        self._dir = Path(output_dir)
        self._dir.mkdir(parents=True, exist_ok=True)
        ts = int(time.time())
        self._path = self._dir / f"live_{label}_{ts}.md"
        with self._path.open("w") as f:
            f.write(f"# {label} debate \u2014 live log (started {time.ctime()})\n\n")
            f.flush()

    # ------------------------------------------------------------------
    def log_turn(self, agent: str, round_idx: int, text: str) -> None:
        """Append a turn entry and print a Rich status line."""
        with self._path.open("a") as f:
            f.write(f"\n\n## ROUND {round_idx} \u2014 {agent}\n\n{text}\n")
            f.flush()
        _console.print(
            f"[bold cyan]Round {round_idx}[/] \u2014 [green]{agent}[/]  "
            f"({len(text)} chars)"
        )

    # ------------------------------------------------------------------
    def note(self, message: str) -> None:
        """Append an italicised note line."""
        with self._path.open("a") as f:
            f.write(f"\n_{message}_\n")
            f.flush()
        _console.print(f"[dim]{message}[/]")

    # ------------------------------------------------------------------
    @property
    def path(self) -> Path:
        """Absolute path to the live-log Markdown file."""
        return self._path

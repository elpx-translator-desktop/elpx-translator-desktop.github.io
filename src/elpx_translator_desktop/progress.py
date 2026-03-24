from __future__ import annotations

from dataclasses import dataclass


class TranslationCancelledError(Exception):
    pass


@dataclass(slots=True)
class ProgressEvent:
    message: str
    state: str = 'Trabajando'
    progress_percent: float | None = None
    completed_units: int | None = None
    total_units: int | None = None
    transient: bool = False
    silent: bool = False

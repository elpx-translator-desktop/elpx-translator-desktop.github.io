from __future__ import annotations

import json
import re
import urllib.request

from PySide6.QtCore import QObject, Signal, Slot

from . import PROJECT_REPOSITORY_URL, PROJECT_RELEASES_URL, __version__

LATEST_RELEASE_API_URL = f'{PROJECT_REPOSITORY_URL}/releases/latest'
LATEST_RELEASE_JSON_URL = 'https://api.github.com/repos/elpx-translator-desktop/elpx-translator-desktop.github.io/releases/latest'


class UpdateCheckWorker(QObject):
    update_found = Signal(str, str)
    finished = Signal()

    @Slot()
    def run(self) -> None:
        try:
            request = urllib.request.Request(
                LATEST_RELEASE_JSON_URL,
                headers={'User-Agent': 'elpx-translator-desktop'},
            )
            with urllib.request.urlopen(request, timeout=8) as response:
                payload = json.loads(response.read().decode('utf-8'))

            latest_version = str(payload.get('tag_name', '')).strip()
            latest_url = str(payload.get('html_url') or PROJECT_RELEASES_URL).strip()
            if latest_version and is_newer_version(latest_version, __version__):
                self.update_found.emit(latest_version, latest_url)
        except Exception:
            pass
        finally:
            self.finished.emit()


def is_newer_version(candidate: str, current: str) -> bool:
    return normalize_version(candidate) > normalize_version(current)


def normalize_version(value: str) -> tuple[int, ...]:
    cleaned = value.strip().lower().removeprefix('v')
    parts = [int(part) for part in re.findall(r'\d+', cleaned)]
    return tuple(parts or [0])

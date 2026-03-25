from __future__ import annotations

import json
import re
import urllib.request

from PySide6.QtCore import QObject, Signal, Slot

from . import PROJECT_RELEASES_URL, __version__

RELEASES_JSON_URL = 'https://api.github.com/repos/elpx-translator-desktop/elpx-translator-desktop.github.io/releases?per_page=20'
PRERELEASE_STAGE_RANK = {
    'alpha': 0,
    'beta': 1,
    'rc': 2,
    'stable': 3,
}


class UpdateCheckWorker(QObject):
    update_found = Signal(str, str)
    finished = Signal()

    @Slot()
    def run(self) -> None:
        try:
            request = urllib.request.Request(
                RELEASES_JSON_URL,
                headers={'User-Agent': 'elpx-translator-desktop'},
            )
            with urllib.request.urlopen(request, timeout=8) as response:
                payload = json.loads(response.read().decode('utf-8'))

            release = select_update_release(payload, __version__)
            if release:
                self.update_found.emit(release['version'], release['url'])
        except Exception:
            pass
        finally:
            self.finished.emit()


def select_update_release(releases_payload: object, current_version: str) -> dict[str, str] | None:
    if not isinstance(releases_payload, list):
        return None

    allow_prereleases = is_prerelease_version(current_version)
    candidates: list[dict[str, str]] = []
    for release in releases_payload:
        if not isinstance(release, dict):
            continue
        if release.get('draft'):
            continue
        if release.get('prerelease') and not allow_prereleases:
            continue

        version = str(release.get('tag_name', '')).strip()
        if not version or not is_newer_version(version, current_version):
            continue

        candidates.append(
            {
                'version': version,
                'url': str(release.get('html_url') or PROJECT_RELEASES_URL).strip(),
            },
        )

    if not candidates:
        return None

    return max(candidates, key=lambda release: normalize_version(release['version']))


def is_newer_version(candidate: str, current: str) -> bool:
    return normalize_version(candidate) > normalize_version(current)


def is_prerelease_version(value: str) -> bool:
    return prerelease_stage(value) != 'stable'


def prerelease_stage(value: str) -> str:
    cleaned = value.strip().lower().removeprefix('v')
    if re.search(r'(?:alpha|a)\d*', cleaned):
        return 'alpha'
    if re.search(r'(?:beta|b)\d*', cleaned):
        return 'beta'
    if re.search(r'rc\d*', cleaned):
        return 'rc'
    return 'stable'


def normalize_version(value: str) -> tuple[int, int, int, int, int]:
    cleaned = value.strip().lower().removeprefix('v')
    number_match = re.match(r'(\d+)(?:\.(\d+))?(?:\.(\d+))?', cleaned)
    if number_match:
        major = int(number_match.group(1) or 0)
        minor = int(number_match.group(2) or 0)
        patch = int(number_match.group(3) or 0)
    else:
        major = minor = patch = 0

    stage = prerelease_stage(cleaned)
    stage_rank = PRERELEASE_STAGE_RANK[stage]

    stage_number = 0
    if stage != 'stable':
        numeric_match = re.search(r'(?:alpha|a|beta|b|rc)\D*(\d+)', cleaned)
        if numeric_match:
            stage_number = int(numeric_match.group(1))

    return major, minor, patch, stage_rank, stage_number

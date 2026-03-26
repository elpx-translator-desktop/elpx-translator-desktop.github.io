#!/usr/bin/env bash

set -euo pipefail

APP_NAME="${APP_NAME:-ELPXTranslatorDesktop}"
PACKAGE_NAME="${PACKAGE_NAME:-elpx-translator-desktop}"
GLIBC_BASELINE="${GLIBC_BASELINE:-2.35}"
DIST_DIR="${DIST_DIR:-dist}"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"

app_version() {
    (
        cd "${PROJECT_ROOT}"
        python3 - <<'PY'
import sys
sys.path.insert(0, 'src')
from elpx_translator_desktop import __version__
print(__version__)
PY
    )
}

deb_app_version() {
    local version
    version="$(app_version)"
    if [[ "${version}" =~ ^([0-9]+\.[0-9]+\.[0-9]+)b([0-9]+)$ ]]; then
        printf '%s~beta%s\n' "${BASH_REMATCH[1]}" "${BASH_REMATCH[2]}"
        return
    fi
    printf '%s\n' "${version}"
}

app_arch() {
    dpkg --print-architecture
}

build_dist() {
    (
        cd "${PROJECT_ROOT}"
        pyinstaller \
            --name "${APP_NAME}" \
            --windowed \
            --noconfirm \
            --clean \
            --add-data "src/elpx_translator_desktop/assets:elpx_translator_desktop/assets" \
            src/elpx_translator_desktop/app.py
    )

    verify_glibc_compatibility
}

verify_glibc_compatibility() {
    local libpython_path required_glibc

    libpython_path="$(
        find "${PROJECT_ROOT}/${DIST_DIR}/${APP_NAME}/_internal" -maxdepth 1 -type f -name 'libpython*.so*' | head -n1
    )"

    if [[ -z "${libpython_path}" ]]; then
        echo "No bundled libpython was found under ${DIST_DIR}/${APP_NAME}/_internal" >&2
        exit 1
    fi

    required_glibc="$(
        objdump -T "${libpython_path}" \
            | grep -o 'GLIBC_[0-9.]*' \
            | sort -Vu \
            | tail -n1 \
            | sed 's/GLIBC_//'
    )"

    echo "Bundled libpython: ${libpython_path}"
    echo "Required glibc: ${required_glibc}"
    echo "Maximum allowed glibc: ${GLIBC_BASELINE}"

    if ! dpkg --compare-versions "${required_glibc}" le "${GLIBC_BASELINE}"; then
        echo "The bundled Python runtime requires glibc ${required_glibc}, above the supported baseline ${GLIBC_BASELINE}." >&2
        echo "Rebuild the Linux package on an older distro or container image." >&2
        exit 1
    fi
}

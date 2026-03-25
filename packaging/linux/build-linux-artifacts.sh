#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=packaging/linux/common.sh
source "${SCRIPT_DIR}/common.sh"

build_dist
SKIP_DIST_BUILD=1 "${SCRIPT_DIR}/build-deb.sh"
SKIP_DIST_BUILD=1 "${SCRIPT_DIR}/build-appimage.sh"

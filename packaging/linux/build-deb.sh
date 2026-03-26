#!/usr/bin/env bash

set -euo pipefail

PKG_ROOT="${PKG_ROOT:-package-root}"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=packaging/linux/common.sh
source "${SCRIPT_DIR}/common.sh"

APP_VERSION="$(deb_app_version)"
ARCH="$(app_arch)"

if [[ "${SKIP_DIST_BUILD:-0}" != "1" ]]; then
    build_dist
fi

APP_DIR="${PKG_ROOT}/usr/lib/${PACKAGE_NAME}"
rm -rf "${PROJECT_ROOT:?}/${PKG_ROOT}"
mkdir -p \
    "${PROJECT_ROOT}/${APP_DIR}" \
    "${PROJECT_ROOT}/${PKG_ROOT}/usr/bin" \
    "${PROJECT_ROOT}/${PKG_ROOT}/DEBIAN" \
    "${PROJECT_ROOT}/${PKG_ROOT}/usr/share/applications" \
    "${PROJECT_ROOT}/${PKG_ROOT}/usr/share/doc/${PACKAGE_NAME}" \
    "${PROJECT_ROOT}/${PKG_ROOT}/usr/share/icons/hicolor/scalable/apps"

cp -a "${PROJECT_ROOT}/${DIST_DIR}/${APP_NAME}/." "${PROJECT_ROOT}/${APP_DIR}/"
cp "${PROJECT_ROOT}/packaging/linux/elpx-translator-desktop.desktop" "${PROJECT_ROOT}/${PKG_ROOT}/usr/share/applications/"
cp "${PROJECT_ROOT}/src/elpx_translator_desktop/assets/elpx-translator-desktop.svg" "${PROJECT_ROOT}/${PKG_ROOT}/usr/share/icons/hicolor/scalable/apps/"
cp "${PROJECT_ROOT}/LICENSE" "${PROJECT_ROOT}/${PKG_ROOT}/usr/share/doc/${PACKAGE_NAME}/LICENSE"

cat > "${PROJECT_ROOT}/${PKG_ROOT}/usr/bin/${PACKAGE_NAME}" <<'SH'
#!/bin/sh
exec /usr/lib/elpx-translator-desktop/ELPXTranslatorDesktop "$@"
SH
chmod 755 "${PROJECT_ROOT}/${PKG_ROOT}/usr/bin/${PACKAGE_NAME}"

cat > "${PROJECT_ROOT}/${PKG_ROOT}/DEBIAN/control" <<EOF
Package: ${PACKAGE_NAME}
Version: ${APP_VERSION}
Section: education
Priority: optional
Architecture: ${ARCH}
Maintainer: Juan José de Haro
Depends: libegl1, libxkbcommon-x11-0, libdbus-1-3
Description: Desktop app to translate .elpx projects locally
 Translate .elpx projects locally on Linux, Windows, and macOS.
EOF

(
    cd "${PROJECT_ROOT}"
    dpkg-deb --build --root-owner-group "${PKG_ROOT}" "${PACKAGE_NAME}_${APP_VERSION}_${ARCH}.deb"
)

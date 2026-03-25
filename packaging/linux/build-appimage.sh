#!/usr/bin/env bash

set -euo pipefail

APPDIR="${APPDIR:-AppDir}"
APPIMAGE_TOOL="${APPIMAGE_TOOL:-appimagetool}"
ARCH_ALIAS="${ARCH_ALIAS:-x86_64}"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=packaging/linux/common.sh
source "${SCRIPT_DIR}/common.sh"

APP_VERSION="$(app_version)"
ARCH="$(app_arch)"
APPIMAGE_ARCH="${ARCH_ALIAS}"

case "${ARCH}" in
amd64)
    APPIMAGE_ARCH="${ARCH_ALIAS:-x86_64}"
    ;;
arm64)
    APPIMAGE_ARCH="${ARCH_ALIAS:-aarch64}"
    ;;
esac

if [[ "${SKIP_DIST_BUILD:-0}" != "1" ]]; then
    build_dist
fi

rm -rf "${PROJECT_ROOT:?}/${APPDIR}"
mkdir -p \
    "${PROJECT_ROOT}/${APPDIR}/usr/bin" \
    "${PROJECT_ROOT}/${APPDIR}/usr/lib/${PACKAGE_NAME}" \
    "${PROJECT_ROOT}/${APPDIR}/usr/share/applications" \
    "${PROJECT_ROOT}/${APPDIR}/usr/share/icons/hicolor/scalable/apps"

cp -a "${PROJECT_ROOT}/${DIST_DIR}/${APP_NAME}/." "${PROJECT_ROOT}/${APPDIR}/usr/lib/${PACKAGE_NAME}/"
cp "${PROJECT_ROOT}/packaging/linux/elpx-translator-desktop.desktop" "${PROJECT_ROOT}/${APPDIR}/usr/share/applications/"
cp "${PROJECT_ROOT}/src/elpx_translator_desktop/assets/elpx-translator-desktop.svg" "${PROJECT_ROOT}/${APPDIR}/usr/share/icons/hicolor/scalable/apps/"
cp "${PROJECT_ROOT}/src/elpx_translator_desktop/assets/elpx-translator-desktop.svg" "${PROJECT_ROOT}/${APPDIR}/elpx-translator-desktop.svg"
cp "${PROJECT_ROOT}/packaging/linux/elpx-translator-desktop.desktop" "${PROJECT_ROOT}/${APPDIR}/elpx-translator-desktop.desktop"

cat > "${PROJECT_ROOT}/${APPDIR}/AppRun" <<'SH'
#!/bin/sh
HERE="$(dirname "$(readlink -f "$0")")"
exec "${HERE}/usr/lib/elpx-translator-desktop/ELPXTranslatorDesktop" "$@"
SH
chmod 755 "${PROJECT_ROOT}/${APPDIR}/AppRun"

cat > "${PROJECT_ROOT}/${APPDIR}/usr/bin/${PACKAGE_NAME}" <<'SH'
#!/bin/sh
HERE="$(dirname "$(readlink -f "$0")")"
APPDIR="$(dirname "$(dirname "${HERE}")")"
exec "${APPDIR}/usr/lib/elpx-translator-desktop/ELPXTranslatorDesktop" "$@"
SH
chmod 755 "${PROJECT_ROOT}/${APPDIR}/usr/bin/${PACKAGE_NAME}"

sed -i 's/^Exec=.*/Exec=elpx-translator-desktop/' "${PROJECT_ROOT}/${APPDIR}/elpx-translator-desktop.desktop"

(
    cd "${PROJECT_ROOT}"
    ARCH="${APPIMAGE_ARCH}" ${APPIMAGE_TOOL} "${APPDIR}" "${PACKAGE_NAME}-${APP_VERSION}-${APPIMAGE_ARCH}.AppImage"
)

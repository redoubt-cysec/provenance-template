#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT_DIR"

YML="packaging/appimage/AppImageBuilder.yml"
OUT="provenance-demo-$(date +%Y.%m.%d)-x86_64.AppImage"

# Prefer linuxdeploy to avoid appimage-builder version parser bugs
if command -v linuxdeploy >/dev/null 2>&1; then
  echo "Using linuxdeploy for AppImage build"
  mkdir -p AppDir/usr/bin
  # expect your pyz or binary exists:
  if [[ -f "dist/provenance-demo.pyz" ]]; then
    install -m 0755 dist/provenance-demo.pyz AppDir/usr/bin/provenance-demo
  else
    echo "dist/provenance-demo.pyz missing. Build your binary first."; exit 3
  fi

  # Use desktop file and icon
  DESKTOP_FILE="packaging/appimage/provenance-demo.desktop"
  ICON_FILE="packaging/appimage/icons/provenance-demo.png"

  linuxdeploy --appdir AppDir \
    --desktop-file "$DESKTOP_FILE" \
    --icon-file "$ICON_FILE" \
    --output appimage

  find . -maxdepth 1 -name "*.AppImage" -print -quit | while read -r f; do
    mv -f "$f" "$OUT"
  done
elif command -v appimage-builder >/dev/null 2>&1; then
  echo "linuxdeploy not found; trying appimage-builder (may have version parser issues)"
  appimage-builder --recipe "$YML" --skip-test
  # appimage-builder typically yields something like Redoubt-<ver>.AppImage; rename for consistency if needed
  find . -maxdepth 1 -name "*.AppImage" -print -quit | while read -r f; do
    mv -f "$f" "$OUT"
  done
else
  echo "Neither linuxdeploy nor appimage-builder found; please install one of them"; exit 2
fi

echo "✓ Built AppImage: $OUT"

#!/usr/bin/env bash
# Creates a standalone .deb package for Ubuntu / Debian
set -euo pipefail
cd "$(dirname "$0")/.."

VERSION="1.0.0"
ARCH="all"
PKG_NAME="clipbar_${VERSION}_${ARCH}"
BUILD_DIR="dist/$PKG_NAME"

echo "==> Packaging Debian / Ubuntu .deb package ($PKG_NAME)..."
rm -rf "$BUILD_DIR"
mkdir -p "$BUILD_DIR/DEBIAN"
mkdir -p "$BUILD_DIR/usr/bin"
mkdir -p "$BUILD_DIR/usr/lib/clipbar"
mkdir -p "$BUILD_DIR/usr/share/applications"
mkdir -p "$BUILD_DIR/usr/share/icons/hicolor/scalable/apps"

# 1. DEBIAN/control
cat << 'EOF' > "$BUILD_DIR/DEBIAN/control"
Package: clipbar
Version: 1.0.0
Section: utils
Priority: optional
Architecture: all
Depends: python3, python3-pyqt6, python3-pyqt6.qtsvg, python3-cryptography, xdotool
Recommends: tesseract-ocr, python3-pynput, python3-gi, gir1.2-atspi-2.0, at-spi2-core
Maintainer: Sajjad Mohabati <https://github.com/SajjadMohabati>
Description: Clipboard manager for Linux that never loses what you type
 A modern, elegant clipboard history with Liquid Glass design for Ubuntu,
 Debian, Fedora and other Linux distributions.
 Features include:
  - Drafts autosave: never lose what you type in other apps
  - Locked items encrypted with your ClipBar password (AES-256-GCM)
  - On-device OCR text recognition inside images
  - Instant direct paste into previous applications
  - 13 text transformations and complete inspector
EOF

# 2. Copy source code
cp -r clipbar resources "$BUILD_DIR/usr/lib/clipbar/"
find "$BUILD_DIR" -name "__pycache__" -prune -exec rm -rf {} +

# 3. Create /usr/bin/clipbar launcher
cat << 'EOF' > "$BUILD_DIR/usr/bin/clipbar"
#!/usr/bin/env python3
import sys
sys.path.insert(0, "/usr/lib/clipbar")
from clipbar.main import main
if __name__ == "__main__":
    sys.exit(main())
EOF
chmod +x "$BUILD_DIR/usr/bin/clipbar"

# 4. Copy desktop file and icons
cp clipbar.desktop "$BUILD_DIR/usr/share/applications/clipbar.desktop"
cp resources/clipbar.svg "$BUILD_DIR/usr/share/icons/hicolor/scalable/apps/clipbar.svg"

# 5. Build package
mkdir -p dist
dpkg-deb --build "$BUILD_DIR" "dist/${PKG_NAME}.deb" 2>/dev/null || (
    echo "dpkg-deb not found on this system. Output directory prepared at: $BUILD_DIR"
    echo "To package on Ubuntu/Debian run: dpkg-deb --build $BUILD_DIR dist/${PKG_NAME}.deb"
)

if [[ -f "dist/${PKG_NAME}.deb" ]]; then
    echo "==> Successfully created dist/${PKG_NAME}.deb"
fi

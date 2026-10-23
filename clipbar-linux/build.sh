#!/usr/bin/env bash
# Usage: ./build.sh            Build package
#        ./build.sh install    Install locally to ~/.local with desktop entry & icons
#        ./build.sh deb        Build Debian / Ubuntu .deb package
set -euo pipefail
cd "$(dirname "$0")"

ACTION="${1:-build}"

if [[ "$ACTION" == "build" ]]; then
    echo "==> Verifying Python syntax..."
    python3 -m py_compile clipbar/*.py
    echo "==> Building distribution wheel..."
    python3 setup.py sdist bdist_wheel
    echo "==> Built successfully in dist/"

elif [[ "$ACTION" == "install" ]]; then
    echo "==> Installing ClipBar locally for current user..."
    python3 -m pip install --upgrade --user .

    # Install icon
    ICON_DIR="$HOME/.local/share/icons/hicolor/scalable/apps"
    mkdir -p "$ICON_DIR"
    cp resources/clipbar.svg "$ICON_DIR/clipbar.svg"

    # Install desktop entry
    DESKTOP_DIR="$HOME/.local/share/applications"
    mkdir -p "$DESKTOP_DIR"
    cp clipbar.desktop "$DESKTOP_DIR/clipbar.desktop"
    sed -i "s|Exec=clipbar|Exec=$HOME/.local/bin/clipbar|g" "$DESKTOP_DIR/clipbar.desktop" 2>/dev/null || true

    # Update desktop database
    update-desktop-database "$DESKTOP_DIR" 2>/dev/null || true

    echo "==> Installed ClipBar successfully!"
    echo "    Executable: ~/.local/bin/clipbar"
    echo "    Desktop entry: ~/.local/share/applications/clipbar.desktop"
    echo "    Launch with: clipbar"

elif [[ "$ACTION" == "deb" ]]; then
    ./scripts/build-deb.sh

else
    echo "Unknown action: $ACTION"
    echo "Usage: ./build.sh [build | install | deb]"
    exit 1
fi

#!/usr/bin/env bash
# Usage: ./build.sh            Build package
#        ./build.sh install    Install locally to ~/.local with desktop entry & icons
#        ./build.sh uninstall  Remove the local install
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
    # No pip: Ubuntu 24.04 and newer refuse `pip install --user`, and the system packages
    # (PyQt6, cryptography, gi) are what ClipBar runs on, exactly like the .deb.
    LIB_DIR="$HOME/.local/lib/clipbar"
    rm -rf "$LIB_DIR"
    mkdir -p "$LIB_DIR" "$HOME/.local/bin"
    cp -r clipbar resources "$LIB_DIR/"
    find "$LIB_DIR" -name "__pycache__" -prune -exec rm -rf {} +
    printf '#!/usr/bin/env python3\nimport sys\nsys.path.insert(0, "%s")\nfrom clipbar.main import main\nsys.exit(main())\n' "$LIB_DIR" > "$HOME/.local/bin/clipbar"
    chmod +x "$HOME/.local/bin/clipbar"

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

elif [[ "$ACTION" == "uninstall" ]]; then
    rm -rf "$HOME/.local/lib/clipbar" "$HOME/.local/bin/clipbar" \
        "$HOME/.local/share/applications/clipbar.desktop" \
        "$HOME/.local/share/icons/hicolor/scalable/apps/clipbar.svg"
    echo "==> Removed ClipBar. Your history is still in ~/.local/share/clipbar"

elif [[ "$ACTION" == "deb" ]]; then
    ./scripts/build-deb.sh

else
    echo "Unknown action: $ACTION"
    echo "Usage: ./build.sh [build | install | uninstall | deb]"
    exit 1
fi

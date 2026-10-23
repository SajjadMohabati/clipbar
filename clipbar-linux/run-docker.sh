#!/usr/bin/env bash
set -e

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$DIR"

# Ensure Docker binaries and credential helpers are in PATH
export PATH="/Applications/Docker.app/Contents/Resources/bin:/usr/local/bin:/opt/homebrew/bin:$PATH"

echo "=========================================================="
echo " Building & Launching ClipBar Linux in Docker..."
echo "=========================================================="

# Check if docker is available
DOCKER_BIN="$(which docker 2>/dev/null || true)"
if [ -z "$DOCKER_BIN" ]; then
    if [ -x "/usr/local/bin/docker" ]; then
        DOCKER_BIN="/usr/local/bin/docker"
    elif [ -x "/opt/homebrew/bin/docker" ]; then
        DOCKER_BIN="/opt/homebrew/bin/docker"
    elif [ -x "/Applications/Docker.app/Contents/Resources/bin/docker" ]; then
        DOCKER_BIN="/Applications/Docker.app/Contents/Resources/bin/docker"
    else
        echo "Error: Docker not found. Please make sure Docker Desktop is installed."
        exit 1
    fi
fi

# Ensure Docker daemon is running
if ! $DOCKER_BIN ps >/dev/null 2>&1; then
    echo "Docker daemon is not running. Starting Docker Desktop..."
    open -a Docker || true
    echo "Waiting for Docker daemon to become ready..."
    READY=false
    for i in $(seq 1 30); do
        if $DOCKER_BIN ps >/dev/null 2>&1; then
            READY=true
            echo "Docker is ready!"
            break
        fi
        sleep 2
    done
    if [ "$READY" = false ]; then
        echo "Error: Could not connect to Docker. Please ensure Docker Desktop is open."
        exit 1
    fi
fi

$DOCKER_BIN compose up --build -d

echo ""
echo "=========================================================="
echo " ClipBar Linux is now live!"
echo " Opening web viewer at: http://localhost:6080/vnc.html?autoconnect=true&resize=scale&quality=9&compression=2"
echo "=========================================================="
echo ""

# Open automatically in macOS default browser
if which open >/dev/null 2>&1; then
    sleep 2
    open "http://localhost:6080/vnc.html?autoconnect=true&resize=scale&quality=9&compression=2" || true
fi

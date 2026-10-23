#!/bin/bash

echo "Cleaning up any stale X locks..."
rm -rf /tmp/.X*-lock /tmp/.X11-unix
mkdir -p /tmp/.X11-unix && chmod 1777 /tmp/.X11-unix

echo "Starting D-Bus..."
eval $(dbus-launch --sh-syntax)
export DBUS_SESSION_BUS_ADDRESS

# Seed sample clips on first run so the UI shows its full capabilities immediately
DATA_DIR="${XDG_DATA_HOME:-$HOME/.local/share}/clipbar"
mkdir -p "$DATA_DIR"
if [ ! -f "$DATA_DIR/history.json" ]; then
    cat << 'EOF' > "$DATA_DIR/history.json"
[
  {
    "id": "sample-1",
    "text": "Welcome to ClipBar on Linux! 🚀\nUltra-lightweight clipboard manager with Liquid Glass design.",
    "pinned": true,
    "uses": 5,
    "date": "2026-10-23T01:00:00"
  },
  {
    "id": "sample-2",
    "text": "https://github.com/SajjadMohabati/clipbar-mac",
    "pinned": false,
    "uses": 2,
    "date": "2026-10-23T01:10:00"
  },
  {
    "id": "sample-3",
    "text": "#6366f1",
    "pinned": false,
    "uses": 1,
    "date": "2026-10-23T01:15:00"
  },
  {
    "id": "sample-4",
    "text": "def calculate_savings(ram_old, ram_new):\n    return f\"{(1 - ram_new / ram_old) * 100:.1f}% reduction\"",
    "pinned": false,
    "uses": 3,
    "date": "2026-10-23T01:20:00"
  }
]
EOF
fi

RES="${RESOLUTION:-1280x800}"
export DISPLAY=:0

echo "Starting Xvfb on display :0 ($RES)..."
Xvfb :0 -screen 0 ${RES}x24 -ac -noreset &
XVFB_PID=$!

echo "Waiting for X display socket..."
for i in $(seq 1 30); do
    if [ -S /tmp/.X11-unix/X0 ]; then
        echo "Xvfb is ready!"
        break
    fi
    sleep 0.2
done
sleep 0.5

echo "Starting Openbox window manager..."
# Openbox draws its title bars at 1x; scale their text with the 2x desktop.
mkdir -p ~/.config/openbox
sed "s#<size>[0-9]*</size>#<size>$((8 * ${UI_SCALE:-1}))</size>#g" /etc/xdg/openbox/rc.xml > ~/.config/openbox/rc.xml
openbox &

echo "Starting tint2 panel with system tray..."
if [ -f /app/docker/tint2rc ]; then
    tint2 -c /app/docker/tint2rc &
else
    tint2 &
fi

echo "Starting x11vnc..."
x11vnc -display :0 -forever -shared -rfbport 5900 -nopw -bg -wait 5 -xkb

echo "Starting noVNC web interface on port 6080..."
websockify --web /usr/share/novnc 6080 localhost:5900 &

sleep 1

echo "=========================================================="
echo " [OK] ClipBar Linux is live and running!"
echo " Open your web browser at:"
echo "   -> http://localhost:6080/vnc.html?autoconnect=true"
echo "=========================================================="

# Launch ClipBar
QT_SCALE_FACTOR="${UI_SCALE:-1}" python3 -m clipbar.main &
CLIPBAR_PID=$!

# Pop up the floating panel after 2 seconds so it's immediately visible
# Open the panel once ClipBar is listening, so the first thing you see is the app.
(for i in $(seq 1 50); do [ -S "/tmp/clipbar-$(id -u).sock" ] && break; sleep 0.2; done; sleep 1; python3 -m clipbar.main --toggle) &

# Keep container alive
wait $XVFB_PID

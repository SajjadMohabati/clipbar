FROM ubuntu:24.04

ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=UTC
ENV DISPLAY=:0
ENV RESOLUTION=2560x1600
ENV UI_SCALE=2

# Install system dependencies & native Qt6/Python packages from Ubuntu 24.04 LTS (supports arm64 & amd64)
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 \
    python3-pip \
    python3-pyqt6 \
    python3-pyqt6.qtsvg \
    libqt6svg6 \
    python3-cryptography \
    python3-gi \
    gir1.2-atspi-2.0 \
    at-spi2-core \
    python3-pynput \
    python3-pil \
    xvfb \
    x11vnc \
    novnc \
    websockify \
    openbox \
    tint2 \
    xdotool \
    tesseract-ocr \
    libsecret-1-0 \
    dbus-x11 \
    fonts-dejavu-core \
    fonts-inter \
    fonts-noto-core \
    fonts-noto-color-emoji \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Set up noVNC index redirect
RUN if [ -f /usr/share/novnc/vnc.html ]; then ln -sf /usr/share/novnc/vnc.html /usr/share/novnc/index.html; fi

WORKDIR /app
COPY . /app

# Set PYTHONPATH and create clipbar CLI shortcut
ENV PYTHONPATH="/app:$PYTHONPATH"
RUN printf '#!/bin/sh\nexec python3 -m clipbar.main "$@"\n' > /usr/local/bin/clipbar && chmod +x /usr/local/bin/clipbar

EXPOSE 6080

RUN chmod +x /app/docker/entrypoint.sh

CMD ["/app/docker/entrypoint.sh"]

"""Liquid Glass stylesheet, colors, and embedded SVG icons for ClipBar."""

from __future__ import annotations

import os

# Line icons drawn on a 24-point grid in the spirit of SF Symbols: 1.7-point strokes,
# round caps and joins, filled variants for selected states.
_STROKE = 'fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"'
_FILL = 'fill="currentColor" stroke="currentColor" stroke-width="1.2" stroke-linejoin="round"'


def _svg(body: str) -> str:
    return f'<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24">{body}</svg>'


ICONS_SVG = {
    # Clipboard: app and tray icon
    "clipboard": _svg(f'<g {_STROKE}><rect x="5" y="4.5" width="14" height="17" rx="3"/>'
                      '<rect x="9" y="2.75" width="6" height="3.5" rx="1.4"/>'
                      '<path d="M9 11h6M9 14.5h6M9 18h3.5"/></g>'),
    # clock
    "history": _svg(f'<g {_STROKE}><circle cx="12" cy="12" r="8.75"/><path d="M12 7.25V12l3.25 2"/></g>'),
    # square.and.pencil
    "drafts": _svg(f'<g {_STROKE}><path d="M11 4.5H7a2.5 2.5 0 0 0-2.5 2.5v10A2.5 2.5 0 0 0 7 19.5h10a2.5 2.5 0 0 0 2.5-2.5v-4"/>'
                   '<path d="M17.6 3.9a1.9 1.9 0 0 1 2.7 2.7L12.5 14.4l-3.4.7.7-3.4z"/></g>'),
    "edit": _svg(f'<g {_STROKE}><path d="M11 4.5H7a2.5 2.5 0 0 0-2.5 2.5v10A2.5 2.5 0 0 0 7 19.5h10a2.5 2.5 0 0 0 2.5-2.5v-4"/>'
                 '<path d="M17.6 3.9a1.9 1.9 0 0 1 2.7 2.7L12.5 14.4l-3.4.7.7-3.4z"/></g>'),
    # bookmark.fill / bookmark
    "saved": _svg(f'<path {_FILL} d="M7.5 3.5h9A1.5 1.5 0 0 1 18 5v15.2a.6.6 0 0 1-.95.5L12 17.2l-5.05 3.5a.6.6 0 0 1-.95-.5V5a1.5 1.5 0 0 1 1.5-1.5z"/>'),
    "bookmark": _svg(f'<path {_STROKE} d="M7.5 3.5h9A1.5 1.5 0 0 1 18 5v15.2a.6.6 0 0 1-.95.5L12 17.2l-5.05 3.5a.6.6 0 0 1-.95-.5V5a1.5 1.5 0 0 1 1.5-1.5z"/>'),
    # trash
    "trash": _svg(f'<g {_STROKE}><path d="M4 6.5h16M9.5 6.5V4.75A1.25 1.25 0 0 1 10.75 3.5h2.5a1.25 1.25 0 0 1 1.25 1.25V6.5"/>'
                  '<path d="M6 6.5l.9 12.6A1.5 1.5 0 0 0 8.4 20.5h7.2a1.5 1.5 0 0 0 1.5-1.4L18 6.5M10 10.5v6M14 10.5v6"/></g>'),
    # gearshape
    "gear": _svg(f'<g {_STROKE}><circle cx="12" cy="12" r="3"/>'
                 '<path d="M10.3 3.5h3.4l.5 2.3 1.6.9 2.2-.8 1.7 2.9-1.8 1.6v1.8l1.8 1.6-1.7 2.9-2.2-.8-1.6.9-.5 2.3h-3.4l-.5-2.3-1.6-.9-2.2.8-1.7-2.9 1.8-1.6v-1.8L4.3 8.8 6 5.9l2.2.8 1.6-.9z"/></g>'),
    "plus": _svg(f'<path {_STROKE} d="M12 5v14M5 12h14"/>'),
    # magnifyingglass
    "search": _svg(f'<g {_STROKE}><circle cx="10.5" cy="10.5" r="6.25"/><path d="M15.2 15.2 20 20"/></g>'),
    # xmark
    "close": _svg(f'<path {_STROKE} d="M6.5 6.5l11 11M17.5 6.5l-11 11"/>'),
    # pin / pin.fill
    "pin": _svg(f'<g {_STROKE}><path d="M8.5 3.5h7l-1 6 3 3.5h-11l3-3.5z"/><path d="M12 13v7.5"/></g>'),
    "pin_fill": _svg(f'<g {_FILL}><path d="M8.5 3.5h7l-1 6 3 3.5h-11l3-3.5z"/></g><path {_STROKE} d="M12 13v7.5"/>'),
    # character.cursor.ibeam
    "rename": _svg(f'<g {_STROKE}><path d="M3.5 18l4-11 4 11M5 14h5"/><path d="M17.5 4.5v15M15.5 4.5h4M15.5 19.5h4"/></g>'),
    "link": _svg(f'<g {_STROKE}><path d="M10 14a4 4 0 0 0 5.66 0l3-3a4 4 0 0 0-5.66-5.66l-1.2 1.2"/>'
                 '<path d="M14 10a4 4 0 0 0-5.66 0l-3 3a4 4 0 0 0 5.66 5.66l1.2-1.2"/></g>'),
    # text.alignleft
    "text": _svg(f'<path {_STROKE} d="M5 6.5h14M5 10.5h10M5 14.5h14M5 18.5h8"/>'),
    "photo": _svg(f'<g {_STROKE}><rect x="3.5" y="5" width="17" height="14" rx="3"/><circle cx="9" cy="10" r="1.6"/>'
                  '<path d="M20.5 15.5l-4.5-4.5-8 8"/></g>'),
    "document": _svg(f'<g {_STROKE}><path d="M13.5 3.5H8A2.5 2.5 0 0 0 5.5 6v12A2.5 2.5 0 0 0 8 20.5h8a2.5 2.5 0 0 0 2.5-2.5V8.5z"/>'
                     '<path d="M13.5 3.5v5h5"/></g>'),
    # lock.fill
    "lock": _svg(f'<rect {_FILL} x="5" y="10.5" width="14" height="10" rx="2.5"/><path {_STROKE} d="M8.25 10.5V8a3.75 3.75 0 0 1 7.5 0v2.5"/>'),
    "keyboard": _svg(f'<g {_STROKE}><rect x="2.75" y="6" width="18.5" height="12" rx="2.5"/>'
                     '<path d="M6.5 9.75h.01M9.5 9.75h.01M12.5 9.75h.01M15.5 9.75h.01M18 9.75h.01M7.5 14.25h9"/></g>'),
    # doc.on.doc
    "copy": _svg(f'<g {_STROKE}><rect x="8.5" y="8.5" width="11.5" height="12" rx="2.5"/>'
                 '<path d="M15.5 8.5V6A2.5 2.5 0 0 0 13 3.5H6.5A2.5 2.5 0 0 0 4 6v8a2.5 2.5 0 0 0 2.5 2.5h2"/></g>'),
    # doc.on.clipboard
    "paste": _svg(f'<g {_STROKE}><rect x="5" y="4.5" width="14" height="17" rx="3"/>'
                  '<rect x="9" y="2.75" width="6" height="3.5" rx="1.4"/><path d="M12 10v7M9 14l3 3 3-3"/></g>'),
    # camera.viewfinder
    "camera": _svg(f'<g {_STROKE}><path d="M4 8V6a2 2 0 0 1 2-2h2M16 4h2a2 2 0 0 1 2 2v2M20 16v2a2 2 0 0 1-2 2h-2M8 20H6a2 2 0 0 1-2-2v-2"/>'
                   '<circle cx="12" cy="12" r="3.25"/></g>'),
    # hand.raised
    "hand": _svg(f'<g {_STROKE}><path d="M8 12V5.5a1.5 1.5 0 0 1 3 0V11M11 10V4a1.5 1.5 0 0 1 3 0v6M14 10V5.5a1.5 1.5 0 0 1 3 0V13"/>'
                 '<path d="M17 9.5a1.5 1.5 0 0 1 3 0V14a7 7 0 0 1-7 7h-1a7 7 0 0 1-5.6-2.8L4 15.5a1.6 1.6 0 0 1 2.5-2L8 15"/></g>'),
    # clock.arrow.circlepath
    "clock_arrow": _svg(f'<g {_STROKE}><path d="M4 12a8 8 0 1 0 2.4-5.7L4 8.5"/><path d="M4 4.5v4h4"/><path d="M12 8v4l2.75 1.75"/></g>'),
    # info.circle
    "info": _svg(f'<g {_STROKE}><circle cx="12" cy="12" r="8.75"/><path d="M12 11v5.5M12 7.75h.01"/></g>'),
    "checkmark": _svg(f'<path {_STROKE} d="M5 12.5l4.5 4.5L19 7.5"/>'),
    "wand": _svg(f'<g {_STROKE}><path d="M4 20l11-11M14 4v2.5M18.5 5.5l-1.8 1.8M20 10h-2.5M10 5.5l1.8 1.8"/></g>'),
    # return
    "enter": _svg(f'<g {_STROKE}><path d="M19 5v6a3 3 0 0 1-3 3H5"/><path d="M9 10l-4 4 4 4"/></g>'),
}


def _color(value: str) -> tuple[str, str]:
    """Splits a CSS color into an SVG color and opacity; Qt's SVG renderer ignores rgba()."""
    value = value.strip()
    if value.startswith("rgba"):
        r, g, b, a = (part.strip() for part in value[value.index("(") + 1:value.index(")")].split(","))
        return f"#{int(r):02x}{int(g):02x}{int(b):02x}", a
    return value, "1"


_icon_cache: dict = {}


def get_icon(name: str, color: str = "#ffffff"):
    """A vector icon in the given color that stays sharp at any size and screen scale."""
    try:
        from clipbar.qt import QIcon
        import hashlib
        import tempfile
        from pathlib import Path

        key = (name, color)
        if key in _icon_cache:
            return _icon_cache[key]
        svg = ICONS_SVG.get(name)
        if not svg:
            return QIcon()
        fill, opacity = _color(color)
        svg = svg.replace("currentColor", fill).replace("<svg ", f'<svg opacity="{opacity}" ', 1)
        # Loading from a file lets Qt's SVG icon engine render at the exact pixel size needed.
        folder = Path(tempfile.gettempdir()) / f"clipbar-icons-{os.getuid()}"
        folder.mkdir(mode=0o700, exist_ok=True)
        path = folder / (hashlib.sha1(svg.encode()).hexdigest()[:16] + ".svg")
        if not path.exists():
            path.write_text(svg, encoding="utf-8")
        icon = QIcon(str(path))
        _icon_cache[key] = icon
        return icon
    except Exception:
        try:
            from clipbar.qt import QIcon
            return QIcon()
        except Exception:
            return None


# Liquid Glass QSS stylesheet
LIQUID_GLASS_QSS = """
/* Liquid Glass Panel Container */
QFrame#PanelContainer {
    background: rgba(22, 28, 36, 0.92);
    border-radius: 26px;
    border: 1px solid rgba(255, 255, 255, 0.12);
    border-top: 1px solid rgba(255, 255, 255, 0.32);
}

/* Header Mode Switch */
QFrame#ModeSwitchFrame {
    background: rgba(255, 255, 255, 0.08);
    border-radius: 14px;
    padding: 2px;
}

QPushButton.ModeButton {
    background: transparent;
    color: rgba(255, 255, 255, 0.65);
    border: none;
    border-radius: 12px;
    font-size: 12px;
    font-weight: 600;
    padding: 4px 11px;
}

QPushButton.ModeButton:hover {
    color: #ffffff;
}

QPushButton.ModeButton[active="true"] {
    color: #ffffff;
    background: rgba(255, 255, 255, 0.10);
    border: 1px solid rgba(255, 255, 255, 0.16);
    border-top: 1px solid rgba(255, 255, 255, 0.34);
    border-bottom: 1px solid rgba(255, 255, 255, 0.07);
}

/* Action & Header Buttons */
QPushButton.GlassIconButton {
    background: transparent;
    border: none;
    border-radius: 14px;
    padding: 6px;
    color: rgba(255, 255, 255, 0.7);
}

QPushButton.GlassIconButton:hover {
    color: #ffffff;
    background: rgba(255, 255, 255, 0.10);
    border: 1px solid rgba(255, 255, 255, 0.16);
    border-top: 1px solid rgba(255, 255, 255, 0.34);
    border-bottom: 1px solid rgba(255, 255, 255, 0.07);
}

QPushButton#ClearConfirmButton {
    background: #e03131;
    color: #ffffff;
    border: none;
    border-radius: 12px;
    font-size: 11px;
    font-weight: 600;
    padding: 4px 10px;
}

QPushButton#ClearConfirmButton:hover {
    background: #c92a2a;
}

QPushButton#PausedButton {
    background: rgba(245, 159, 0, 0.2);
    color: #f59f00;
    border: 1px solid rgba(245, 159, 0, 0.4);
    border-radius: 12px;
    font-size: 10px;
    font-weight: 600;
    padding: 3px 8px;
}

/* Search Input */
QFrame#SearchFrame {
    background: rgba(255, 255, 255, 0.08);
    border: 1px solid rgba(255, 255, 255, 0.12);
    border-top: 1px solid rgba(255, 255, 255, 0.26);
    border-radius: 12px;
    padding: 4px 8px;
}

QFrame#SearchFrame[focused="true"] {
    background: rgba(255, 255, 255, 0.12);
    border: 1px solid rgba(255, 255, 255, 0.3);
}

QLineEdit#SearchInput {
    background: transparent;
    border: none;
    color: #ffffff;
    font-size: 13px;
    selection-background-color: rgba(64, 150, 255, 0.6);
}

QLineEdit#SearchInput::placeholder {
    color: rgba(255, 255, 255, 0.45);
}

/* Filter Chips */
QPushButton.FilterChip {
    background: transparent;
    color: rgba(255, 255, 255, 0.65);
    border: none;
    border-radius: 11px;
    font-size: 11px;
    font-weight: 500;
    padding: 4px 9px;
}

QPushButton.FilterChip:hover {
    color: #ffffff;
    background: rgba(255, 255, 255, 0.06);
}

QPushButton.FilterChip[active="true"] {
    color: #ffffff;
    font-weight: 600;
    background: rgba(255, 255, 255, 0.10);
    border: 1px solid rgba(255, 255, 255, 0.16);
    border-top: 1px solid rgba(255, 255, 255, 0.34);
    border-bottom: 1px solid rgba(255, 255, 255, 0.07);
}

/* Section Header */
QLabel.SectionHeader {
    font-size: 10px;
    font-weight: 700;
    color: rgba(255, 255, 255, 0.38);
    text-transform: uppercase;
    letter-spacing: 0.8px;
    padding-left: 6px;
    padding-top: 4px;
}

/* ClipRow */
QFrame.ClipRowFrame {
    background: transparent;
    border-radius: 12px;
    border: 1px solid transparent;
}

QFrame.ClipRowFrame:hover {
    background: rgba(255, 255, 255, 0.07);
}

QFrame.ClipRowFrame[selected="true"] {
    background: rgba(255, 255, 255, 0.10);
    border: 1px solid rgba(255, 255, 255, 0.16);
    border-top: 1px solid rgba(255, 255, 255, 0.34);
    border-bottom: 1px solid rgba(255, 255, 255, 0.07);
}

/* Row Action Buttons */
QPushButton.RowActionButton {
    background: transparent;
    border: none;
    border-radius: 11px;
    color: rgba(255, 255, 255, 0.65);
    padding: 3px;
}

QPushButton.RowActionButton:hover {
    background: rgba(255, 255, 255, 0.14);
    color: #ffffff;
}

QPushButton.RowActionButton[destructive="true"]:hover {
    background: rgba(224, 49, 49, 0.25);
    color: #ff6b6b;
}

/* Shortcut badge (Ctrl+1) */
QLabel.ShortcutBadge {
    font-size: 11px;
    font-weight: 600;
    color: rgba(255, 255, 255, 0.38);
    padding-right: 4px;
}

/* Footer */
QLabel#FooterCount {
    font-size: 11px;
    color: rgba(255, 255, 255, 0.45);
    font-weight: 500;
}

QLabel#FooterToast {
    font-size: 11px;
    color: #51cf66;
    font-weight: 600;
}

QPushButton#PasteFooterButton {
    background: transparent;
    border: 1px solid transparent;
    border-radius: 14px;
}

QPushButton#PasteFooterButton:hover {
    background: rgba(255, 255, 255, 0.10);
    border: 1px solid rgba(255, 255, 255, 0.16);
    border-top: 1px solid rgba(255, 255, 255, 0.34);
    border-bottom: 1px solid rgba(255, 255, 255, 0.07);
}

QLabel#PasteFooterLabel {
    color: #ffffff;
    font-size: 12px;
    font-weight: 600;
    background: transparent;
}

/* Keycap icon container */
QLabel.KeyCap {
    background: rgba(255, 255, 255, 0.12);
    border: 1px solid rgba(255, 255, 255, 0.2);
    border-radius: 5px;
    padding: 1px 4px;
    font-size: 10px;
    font-weight: 600;
    color: rgba(255, 255, 255, 0.7);
}

/* Scroll Area */
QScrollArea {
    background: transparent;
    border: none;
}

QScrollBar:vertical {
    border: none;
    background: transparent;
    width: 6px;
    margin: 0px;
}

QScrollBar::handle:vertical {
    background: rgba(255, 255, 255, 0.2);
    border-radius: 3px;
    min-height: 20px;
}

QScrollBar::handle:vertical:hover {
    background: rgba(255, 255, 255, 0.35);
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}

/* Context Menu */
QMenu {
    background-color: rgba(30, 36, 46, 0.96);
    border: 1px solid rgba(255, 255, 255, 0.15);
    border-radius: 10px;
    padding: 5px;
    color: #ffffff;
}

QMenu::item {
    padding: 6px 18px 6px 12px;
    border-radius: 6px;
    font-size: 12px;
}

QMenu::item:selected {
    background-color: rgba(255, 255, 255, 0.14);
}

QMenu::separator {
    height: 1px;
    background: rgba(255, 255, 255, 0.12);
    margin: 4px 6px;
}
"""


def tile_icon(name: str, tint: str, size: int = 22):
    """A white symbol on a rounded colored square, like the Mac settings sidebar."""
    from clipbar.qt import QIcon, QPixmap, QPainter, QColor, QPainterPath, Qt
    scale = 3  # draw large so it stays sharp when scaled to the screen
    side = size * scale
    pix = QPixmap(side, side)
    pix.fill(Qt.GlobalColor.transparent)
    p = QPainter(pix)
    p.setRenderHint(QPainter.RenderHint.Antialiasing)
    path = QPainterPath()
    path.addRoundedRect(0, 0, side, side, side * 0.26, side * 0.26)
    p.fillPath(path, QColor(tint))
    inset = int(side * 0.2)
    get_icon(name, "#ffffff").paint(p, inset, inset, side - 2 * inset, side - 2 * inset)
    p.end()
    pix.setDevicePixelRatio(scale)
    return QIcon(pix)


def switch_qss() -> str:
    """Check boxes drawn as macOS-style switches (Qt style sheets can't draw the knob)."""
    import tempfile
    from pathlib import Path
    folder = Path(tempfile.gettempdir()) / f"clipbar-icons-{os.getuid()}"
    folder.mkdir(mode=0o700, exist_ok=True)
    shapes = {
        "off": '<rect x="1" y="1" width="36" height="22" rx="11" fill="#ffffff" fill-opacity="0.18"/>'
               '<circle cx="12" cy="12" r="9" fill="#ffffff"/>',
        "on": '<rect x="1" y="1" width="36" height="22" rx="11" fill="#0a84ff"/>'
              '<circle cx="26" cy="12" r="9" fill="#ffffff"/>',
    }
    paths = {}
    for state, body in shapes.items():
        path = folder / f"switch-{state}.svg"
        path.write_text(f'<svg xmlns="http://www.w3.org/2000/svg" width="38" height="24" viewBox="0 0 38 24">{body}</svg>')
        paths[state] = path.as_posix()
    return f"""
QCheckBox {{ spacing: 10px; color: #ffffff; }}
QCheckBox::indicator {{ width: 38px; height: 24px; }}
QCheckBox::indicator:unchecked {{ image: url({paths["off"]}); }}
QCheckBox::indicator:checked {{ image: url({paths["on"]}); }}
QCheckBox:disabled {{ color: rgba(255, 255, 255, 0.35); }}
"""

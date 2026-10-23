<p align="center">
  <img src="resources/clipbar.svg" width="160" alt="ClipBar, a clipboard manager for Linux">
</p>

<h1 align="center">ClipBar: Clipboard Manager for Linux That Never Loses What You Type</h1>

<p align="center">
  <b>A free, open-source clipboard history for the Linux desktop, built with Liquid Glass design.</b><br>
  <b>Drafts: recover text you typed and lost</b> · password-encrypted locked items · automatic screenshots · OCR search · instant paste
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Ubuntu-22.04%20%7C%2024.04-E95420?logo=ubuntu&logoColor=white" alt="Ubuntu">
  <img src="https://img.shields.io/badge/Debian-11%20%7C%2012-A81D33?logo=debian&logoColor=white" alt="Debian">
  <img src="https://img.shields.io/badge/Fedora%20%2F%20RHEL-supported-294172?logo=fedora&logoColor=white" alt="Fedora / RHEL">
  <img src="https://img.shields.io/badge/Arch%20Linux-supported-1793D1?logo=archlinux&logoColor=white" alt="Arch Linux">
  <img src="https://img.shields.io/badge/Python-3.8+-3776AB?logo=python&logoColor=white" alt="Python 3.8+">
  <img src="https://img.shields.io/badge/License-MIT-2ea44f" alt="MIT License">
</p>

<p align="center">
  <a href="#install"><b>⬇️ Install ClipBar</b></a>
  &nbsp;·&nbsp; <a href="#drafts-never-lose-what-you-typed-again">Drafts</a>
  &nbsp;·&nbsp; <a href="#features">Features</a>
  &nbsp;·&nbsp; <a href="#keyboard-shortcuts">Shortcuts</a>
  &nbsp;·&nbsp; <a href="#faq">FAQ</a>
</p>

<p align="center"><a href="README.fa.md">🇮🇷 فارسی</a></p>

<p align="center"><sub>Created by <a href="https://github.com/SajjadMohabati"><b>Sajjad Mohabati</b></a></sub></p>

---

## Drafts: never lose what you typed again

You write a long message, press Send, and it's gone. The form reloaded, the session expired, the app crashed, the upload failed, or you closed the tab by mistake. Nobody wants to type it all again.

**ClipBar Drafts saves what you type while you type it**, in any app, even if you never copied it. When the text disappears, open ClipBar, go to the **Drafts** tab and paste it back.

| What went wrong | What ClipBar does |
| --- | --- |
| A web form reset or the page reloaded | Your text is in Drafts |
| "Message failed to send" and the box is empty | Your text is in Drafts |
| You closed the tab or the app quit | Your text is in Drafts |
| A site rejected your post and cleared the field | Your text is in Drafts |
| You selected everything and overwrote it by accident | The earlier version is in Drafts |

**How it works**

1. Turn it on once in **Settings → Drafts**.
2. Type anywhere: chat apps, email, browsers, forms, notes.
3. ClipBar keeps **one draft per message**. It updates as you type, and when the field is emptied (sent, cleared or wiped) the full text stays in Drafts.
4. Lost something? Press `Ctrl+Shift+V`, open **Drafts**, press `Enter`. It's pasted back where you were typing.

**Private and safe**

- It is **not a keylogger**. ClipBar never listens to raw keystrokes. Once a second it checks the Linux Accessibility (AT-SPI2) API for the text of the field you're typing in.
- **Password fields are never read.** Terminals, password managers and search fields are skipped, and card numbers and API keys are filtered out.
- **Off by default**, and everything stays on your PC. Nothing is uploaded anywhere.
- Full Right-to-Left (RTL) support (Persian, Arabic, Hebrew).

---

## Why ClipBar?

Most clipboard managers stop at "remember what I copied". ClipBar also keeps your **sensitive data locked**, **catches every screenshot**, **reads the text inside images with on-device OCR**, and **pastes straight into the app you were using**, while looking stunning with its frosted Liquid Glass design.

- 📝 **Never lose a typed message again.** [Drafts](#drafts-never-lose-what-you-typed-again) keeps a copy of what you type in other apps.
- 🔐 **Encrypted locked items.** Card numbers, IDs and secrets are encrypted with AES-256-GCM using a key derived from your ClipBar password (scrypt). The password is never stored; a wrong one simply can't decrypt.
- 📸 **Screenshots go straight into your history.** Screenshots taken with your system shortcut land directly in ClipBar, ready to paste.
- 🔎 **Search inside images.** Text in copied images and screenshots is recognized on-device with Tesseract OCR, so you can find a screenshot by what's written in it.
- ⚡️ **Direct paste.** Pick an item with `Enter` and ClipBar pastes it directly into the focused field of the previous app. `Ctrl+1`–`Ctrl+9` paste the first nine items instantly.
- 🫧 **Real Liquid Glass UI.** Translucent dark glass panel, glowing specular highlights, smooth motion, high-DPI scaling.
- 🛡 **Private by design.** No account, no cloud, no analytics and zero network requests. Everything stays on your computer.

---

## Features

### Clipboard history
- Remembers **text, links, colors, images and files** copied from your file manager, with the app it came from and when.
- **Filters**: All · Pinned · Text · Links · Images · Files (`Tab` to switch).
- **Instant search** across text, titles and the text recognized in images.
- **Pin** important snippets to the top.
- Auto cleanup by age (1–365 days) and size (50–2,000 items); pinned items can be kept forever.

### Saved items and locking
- A separate **Saved** list for things you paste again and again: card number, student ID, address, email signature.
- Add them with **+** or move any history item in with `Ctrl+S`. Saved items are never cleaned up automatically.
- **Give any saved item a title**: label a card number with the bank's name, or a screenshot with what it shows.
- **Lock an item**: the first time, ClipBar asks you to choose a password. The value moves into the encrypted vault, is shown as `••••••••`, and needs the password before paste, copy, view, edit or delete (it's remembered for 30 seconds). If you forget the password, locked items can't be recovered.

### Screenshots and images
- New screenshots from `~/Pictures/Screenshots` are **added to the history and copied to clipboard** automatically.
- **On-device text recognition (OCR)** with Tesseract makes text in images searchable and copyable.

### Editor and transforms
- View and edit any item in a full editor with inspector: character, word and line counts, color values (HEX, RGB, HSL) and image text.
- **One-click transforms**: UPPERCASE, lowercase, Capitalize Words, trim whitespace, remove empty lines, sort, deduplicate or join lines, format or minify JSON, Base64 encode/decode, URL encode/decode.

---

## Install

### Ubuntu & Debian

#### Method 1: APT Dependencies & Local Install (Recommended)
```bash
# 1. Install system dependencies
sudo apt update
sudo apt install -y python3 python3-pyqt6 python3-pyqt6.qtsvg python3-cryptography xdotool tesseract-ocr \
  python3-gi gir1.2-atspi-2.0 at-spi2-core

# 2. Clone and install
git clone https://github.com/SajjadMohabati/clipbar-mac.git
cd clipbar-mac/clipbar-linux
./build.sh install
```

#### Method 2: Debian Package (.deb)
```bash
cd clipbar-linux
./build.sh deb
sudo dpkg -i dist/clipbar_*.deb || sudo apt install -f
```

---

### Fedora, RHEL & CentOS

```bash
# Install dependencies
sudo dnf install -y python3 python3-pyqt6 xdotool tesseract

# Install ClipBar
cd clipbar-linux
./build.sh install
```

---

### Arch Linux & Manjaro

```bash
# Install dependencies
sudo pacman -S python python-pyqt6 xdotool tesseract

# Install ClipBar
cd clipbar-linux
./build.sh install
```

---

## Keyboard shortcuts

| Key | Action |
| --- | --- |
| `Ctrl+Shift+V` | Open ClipBar (change it in Settings) |
| `↑` `↓` | Move selection |
| `Enter` | Paste selected item |
| `Alt+Enter` | Copy without pasting |
| `Ctrl+1`–`Ctrl+9` | Paste item 1–9 |
| `Tab` / `Shift+Tab` | Next / previous filter |
| `Ctrl+[` / `Ctrl+]` | Previous / next tab (History, Drafts, Saved) |
| `Ctrl+S` | Move to Saved |
| `Ctrl+P` | Pin or unpin |
| `Ctrl+E` | View and edit |
| `Ctrl+Backspace` | Delete |
| `Ctrl+,` | Settings |
| `Esc` | Clear search, then close |

---

## Your data

Everything lives in standard XDG directories:

- `~/.local/share/clipbar/history.json`: clipboard history
- `~/.local/share/clipbar/saved.json`: saved items (locked values live encrypted in `vault.enc`, never in this file)
- `~/.local/share/clipbar/drafts.json`: drafts of text you typed
- `~/.local/share/clipbar/images/`: copied images, stored once as PNG files even if copied multiple times
- `~/.config/clipbar/settings.json`: user preferences

---

## Project layout

```
clipbar-linux/
  clipbar/
    app.py                system tray, panel controller, focus handling
    clip_view.py          the main floating panel
    editor_view.py        item viewer and editor window
    settings_view.py      settings window
    store.py              history model, capture, cleanup, persistence
    clipboard.py          clipboard I/O, secret detection, image storage, OCR
    vault.py              encrypted storage and password unlock for locked items
    screenshot_watcher.py watches screenshot folder
    draft_watcher.py      keeps drafts of text typed in other apps
    transforms.py         text transforms
    hotkey.py             global shortcut
    settings.py           preferences
    styles.py             Liquid Glass theme, QSS, embedded SVG icons
    main.py               entrypoint and single-instance IPC
  resources/
    clipbar.svg           app icon
    clipbar-tray.svg      tray icon
  build.sh                build and install script
  setup.py                Python package configuration
```

## Author

Created by **Sajjad Mohabati** · [github.com/SajjadMohabati](https://github.com/SajjadMohabati)

## License

[MIT](LICENSE) © Sajjad Mohabati

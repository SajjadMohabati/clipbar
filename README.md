<p align="center">
  <img src="docs/icon.png" width="160" alt="ClipBar, a clipboard manager for macOS and Linux">
</p>

<h1 align="center">ClipBar: Clipboard Manager for Mac and Linux That Never Loses What You Type</h1>

<p align="center">
  <b>A free, open-source clipboard history for the Mac menu bar and the Linux desktop, with a Liquid Glass design.</b><br>
  <b>Drafts: recover text you typed and lost</b> · locked items · automatic screenshots · OCR search · instant paste
</p>

<p align="center">
  <a href="https://github.com/SajjadMohabati/clipbar-mac/releases/latest"><img src="https://img.shields.io/github/v/release/SajjadMohabati/clipbar-mac?label=download&color=7c5cff" alt="Download the latest release"></a>
  <img src="https://img.shields.io/badge/macOS-26%20Tahoe-black?logo=apple" alt="macOS 26 Tahoe">
  <a href="https://github.com/SajjadMohabati/clipbar-mac/releases/tag/linux-v1.0"><img src="https://img.shields.io/badge/Linux-1.0-FCC624?logo=linux&logoColor=black" alt="ClipBar for Linux 1.0"></a>
  <img src="https://img.shields.io/badge/Apple%20silicon%20%2B%20Intel-universal-555" alt="Universal binary">
  <img src="https://img.shields.io/badge/Swift-6-F05138?logo=swift&logoColor=white" alt="Swift 6">
  <a href="LICENSE"><img src="https://img.shields.io/github/license/SajjadMohabati/clipbar-mac?color=2ea44f" alt="MIT license"></a>
  <a href="https://github.com/SajjadMohabati/clipbar-mac/stargazers"><img src="https://img.shields.io/github/stars/SajjadMohabati/clipbar-mac?style=social" alt="GitHub stars"></a>
</p>

<p align="center">
  <a href="https://github.com/SajjadMohabati/clipbar-mac/releases/latest"><b>⬇️ Download for Mac</b></a>
  &nbsp;·&nbsp; <a href="#clipbar-for-linux"><b>🐧 Linux</b></a>
  &nbsp;·&nbsp; <a href="#drafts-never-lose-what-you-typed-again">Drafts</a>
  &nbsp;·&nbsp; <a href="#features">Features</a>
  &nbsp;·&nbsp; <a href="#keyboard-shortcuts">Shortcuts</a>
  &nbsp;·&nbsp; <a href="#faq">FAQ</a>
</p>

<p align="center">
  <img src="docs/panel.png" width="440" alt="ClipBar clipboard history panel with Liquid Glass design on macOS Tahoe">
</p>

<p align="center"><a href="README.fa.md">🇮🇷 فارسی</a> &nbsp;·&nbsp; <a href="README.ar.md">🇸🇦 العربية</a></p>

<p align="center"><sub>Created by <a href="https://github.com/SajjadMohabati"><b>Sajjad Mohabati</b></a></sub></p>

---

## Drafts: never lose what you typed again

You write a long message, press Send, and it's gone. The form reloaded, the session expired, the
app crashed, the upload failed, or you closed the tab by mistake. Nobody wants to type it all again.

**ClipBar Drafts saves what you type while you type it**, in any app, even if you never copied it.
When the text disappears, open ClipBar, go to the **Drafts** tab and paste it back.

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
4. Lost something? Press `⇧⌘V`, open **Drafts**, press `↩`. It's pasted back where you were typing.

**You stay in control**

- **Minimum length** (default 30 characters), so searches and short replies aren't kept.
- **How long** drafts are kept (default 12 hours, from 1 hour to 7 days).
- **How many** drafts are kept (default 10, up to 50).
- Move a draft to **Saved** with `⌘S` to keep it for good.

**Private and safe**

- It is **not a keylogger**. ClipBar never listens to your keyboard. Once a second it asks macOS (Accessibility) for the text of the field you're typing in.
- **Password fields are never read.** Terminals, password managers and search fields are skipped, and card numbers and API keys are filtered out.
- **Off by default**, and everything stays on your Mac. Nothing is uploaded.
- Works with left-to-right and right-to-left text (Persian, Arabic, Hebrew).

<sub>Works in most Mac apps and browsers. A few apps don't share their text fields with macOS, so their text can't be saved.</sub>

## Why ClipBar?

Most clipboard managers stop at "remember what I copied". ClipBar also keeps your **sensitive data
locked**, **catches every screenshot**, **reads the text inside images** and **pastes straight into the
app you were using**, while looking like it shipped with macOS Tahoe.

- 📝 **Never lose a typed message again.** [Drafts](#drafts-never-lose-what-you-typed-again) keeps a copy of what you type in other apps, so a failed send, a reset form or a closed tab doesn't cost you your text.
- 🔐 **Touch ID–locked items.** Card numbers, IDs and passwords are kept in the macOS Keychain, not in a plain file, and every paste, copy, edit or delete asks for Touch ID or your Mac password.
- 📸 **Screenshots go straight into your history.** Press ⇧⌘3 or ⇧⌘4 and the screenshot is on the clipboard and in ClipBar, ready to paste. No extra step.
- 🔎 **Search inside images.** Text in copied images and screenshots is recognized on-device, so you can find a screenshot by what's written in it.
- ⚡️ **Paste where you were typing.** Pick an item with `↩` and ClipBar pastes it into the focused text field of the previous app. `⌘1`–`⌘9` paste the first nine items instantly.
- 🫧 **Real Liquid Glass.** A native SwiftUI interface made for macOS 26: glass panel, glass controls, smooth motion, light and dark mode.
- 🛡 **Private by design.** No account, no cloud, no analytics and not a single network request. Everything stays on your Mac.
- 🪶 **Tiny and dependency-free.** About 3,000 lines of Swift, zero third-party packages, a universal binary for Apple silicon and Intel. Version 2.4 frees memory as soon as each check finishes and caps its image caches, so it stays light all day.
- 🐧 **On Linux too.** [ClipBar for Linux](#clipbar-for-linux) brings the same history, Drafts, Saved items and glass design to Ubuntu, Debian and other distributions.

## What's new

- **2.4 (Mac):** lower memory use, and image thumbnails keep their real proportions instead of being squashed into a square.
- **Linux 1.0:** the [first release of ClipBar for Linux](https://github.com/SajjadMohabati/clipbar-mac/releases/tag/linux-v1.0), with a `.deb` package for Ubuntu and Debian.
- **2.3 (Mac):** [Drafts](#drafts-never-lose-what-you-typed-again), so you never lose what you typed.

## Features

### Clipboard history
- Remembers **text, links, colors, images and files** copied from Finder, with the app it came from and when.
- **Filters**: All · Pinned · Text · Links · Images · Files (`⇥` to switch).
- **Instant search** across text, titles and the text recognized in images.
- **Pin** important snippets to the top and **drag to reorder**. Drag any row into another app to drop its content there.
- Copying the same thing again moves it to the top instead of making a duplicate, and counts how often you use it.
- **Auto cleanup** by age (1–365 days) and size (50–2,000 items); pinned items can be kept forever.

### Saved items and locking
- A separate **Saved** list for things you paste again and again: card number, student ID, address, email signature.
- Add them with **+** or move any history item in with `⌘S`. Saved items are never cleaned up automatically.
- **Give any saved item a title**, text or image: label a card number with the bank's name, or a screenshot with what it shows. Titles are searchable.
- **Lock an item** and its value moves into the **macOS Keychain**. It is shown as `••••••••` and needs **Touch ID or your password** to paste, copy, view, edit or delete.
- After unlocking, you have 30 seconds to do a few things without being asked again.
- Locked values you paste are marked as *concealed*, so other clipboard tools don't record them.

### Drafts: never lose what you typed
- Turn on **Drafts** in Settings and ClipBar keeps a copy of longer text **while you type it in other apps**, even if you never copy it.
- If a web form resets, a message fails to send or a tab closes, the text is waiting in the **Drafts** tab, ready to paste back.
- One draft per text field: it updates as you type, and when the field is emptied (sent or cleared) the full text is kept and the next message becomes a new draft.
- You choose the **minimum length** (30 characters by default), **how long** drafts are kept (12 hours) and **how many** (10). Limits are capped so it stays light.
- Off by default. ClipBar reads the focused field through Accessibility once a second; it **never records keystrokes**, never reads password fields, and skips terminals and password managers.
- Works in most apps and browsers; a few apps don't share their text fields with macOS.

### Screenshots and images
- New screenshots (⇧⌘3, ⇧⌘4, ⇧⌘5) are **added to the history and copied to the clipboard** automatically.
- ClipBar follows the screenshot location you choose in ⇧⌘5 → Options, even if you change it later.
- **On-device text recognition (OCR)** with Apple's Vision framework makes text in images searchable and copyable.

### Pasting
- **Direct paste**: `↩` pastes into the app you were using, `⌥↩` only copies.
- **`⌘1`–`⌘9`** paste the first nine items without moving the selection.
- The panel never steals focus, so the text field you were typing in stays focused.

### Editor and transforms
- View and edit any item in a full editor with an inspector: character, word and line counts, link details, color values (HEX, RGB, HSL) and image text.
- **One-click transforms**: UPPERCASE, lowercase, Capitalize Words, trim whitespace, remove empty lines, sort, deduplicate or join lines, format or minify JSON, Base64 encode/decode, URL encode/decode.

### Privacy and security
- Skips anything password managers mark as **confidential or transient** (1Password, Bitwarden, KeePassXC and others that follow [nspasteboard.org](http://nspasteboard.org)).
- Automatically ignores **private keys, API tokens** (GitHub, OpenAI, Stripe, AWS, Slack, Google and more) and **credit card numbers** (validated with the Luhn check).
- **Pause capturing** any time from the menu bar icon's right-click menu.
- No network access at all. Your history is stored only in `~/Library/Application Support/ClipBar/`.

### Native and lightweight
- Menu bar app with a **custom global shortcut** (default `⇧⌘V`) and launch at login.
- Liquid Glass design, full keyboard control, light and dark mode.
- Universal binary for **Apple silicon and Intel**, written in Swift 6 with SwiftUI and AppKit.

## ClipBar for Linux

<p align="center">
  <img src="docs/linux-panel.png" width="400" alt="ClipBar clipboard manager for Linux with Liquid Glass design on Ubuntu">
</p>

The same clipboard manager, built for the Linux desktop with Python and Qt 6. It has the same look,
the same tabs and the same keyboard-first workflow as the Mac app.

| | Mac | Linux |
| --- | --- | --- |
| Clipboard history, pins, filters, search | ✅ | ✅ |
| Drafts (recover text you typed) | ✅ Accessibility | ✅ AT-SPI, X11 and Wayland |
| Saved items with titles | ✅ | ✅ |
| Locked items | Keychain + Touch ID | AES-256-GCM, unlocked with your ClipBar password |
| Screenshots in the history | ✅ | ✅ |
| Text in images (OCR) | Apple Vision | Tesseract |
| Direct paste | ✅ | ✅ xdotool, or wtype / ydotool on Wayland |
| Open with | `⇧⌘V` | `Ctrl+Shift+V` |

**Install on Ubuntu or Debian:** download `clipbar_1.0.0_all.deb` from the
[Linux 1.0 release](https://github.com/SajjadMohabati/clipbar-mac/releases/tag/linux-v1.0), then:

```bash
sudo apt install ./clipbar_1.0.0_all.deb
```

For Fedora, Arch, installing from source, Wayland setup and a Docker preview, see the
[Linux README](clipbar-linux/README.md).

## Install on Mac

**Requirements:** macOS 26 Tahoe or later, on Apple silicon or Intel.

### Download (recommended)

1. Download **`ClipBar-<version>.dmg`** from the [latest release](https://github.com/SajjadMohabati/clipbar-mac/releases/latest).
2. Open it and drag **ClipBar** onto **Applications**.

<p align="center">
  <img src="docs/installer.png" width="520" alt="ClipBar installer window">
</p>

3. Open ClipBar. Because it's an independent open-source app that isn't notarized by Apple, macOS
   shows a warning the first time. Click **Done**, open **System Settings → Privacy & Security**,
   scroll down and click **Open Anyway**. You only do this once.

   Prefer Terminal? This does the same thing:

   ```bash
   xattr -dr com.apple.quarantine /Applications/ClipBar.app
   ```

4. Press **`⇧⌘V`** or click the clipboard icon in the menu bar.

### Allow pasting

To paste directly into other apps, ClipBar needs **Accessibility** access. Click **Allow…** in the
panel, or turn on ClipBar in **System Settings → Privacy & Security → Accessibility**. Without it,
ClipBar still copies the item and you press `⌘V` yourself.

### Build from source

Requires the Swift 6 toolchain (Xcode 26 or the Command Line Tools).

```bash
git clone https://github.com/SajjadMohabati/clipbar-mac.git
cd clipbar-mac
./build.sh install
```

| Command | Result |
| --- | --- |
| `./build.sh` | Builds `ClipBar.app` in the project folder |
| `./build.sh install` | Builds, copies to `/Applications` and launches |
| `./build.sh dmg` | Builds a universal binary and the installer at `dist/ClipBar-<version>.dmg` |

<details>
<summary>Keep Accessibility access between your own builds</summary>

Builds are ad-hoc signed, so macOS treats every rebuild as a new app and the old Accessibility
entry stops working (it stays switched on but does nothing). Remove it with **−** and add ClipBar
again, or sign with a stable certificate: in Keychain Access choose
*Certificate Assistant → Create a Certificate…*, name it `ClipBar Local` and set the type to
**Code Signing**. Then build with:

```bash
CLIPBAR_SIGN_IDENTITY="ClipBar Local" ./build.sh install
```
</details>

## Keyboard shortcuts

| Key | Action |
| --- | --- |
| `⇧⌘V` | Open ClipBar (change it in Settings) |
| `↑` `↓` | Move the selection |
| `↩` | Paste the selected item |
| `⌥↩` | Copy without pasting |
| `⌘1`–`⌘9` | Paste item 1–9 |
| `⇥` / `⇧⇥` | Next / previous filter |
| `⌘[` / `⌘]` | Previous / next tab (History, Drafts, Saved) |
| `⌘S` | Move to Saved |
| `⌘P` | Pin or unpin |
| `⌘E` | View and edit |
| `⌘⌫` | Delete |
| `⌘,` | Settings |
| `Esc` | Clear the search, then close |

## FAQ

<details>
<summary><b>How do I recover text I typed that disappeared on my Mac?</b></summary>

Turn on **Drafts** in ClipBar's settings. From then on ClipBar keeps a copy of longer text while you
type it in other apps. If a form resets, a message fails to send or a tab closes, open ClipBar,
switch to the **Drafts** tab and paste the text back. Text typed before you turned Drafts on can't
be recovered.
</details>

<details>
<summary><b>Is Drafts a keylogger? Is it safe?</b></summary>

No. ClipBar never records keystrokes. It reads the text of the focused text field through the macOS
Accessibility API once a second, never reads password fields, skips terminals and password managers,
and stores drafts only on your Mac for a limited time. It's off until you turn it on.
</details>

<details>
<summary><b>Which apps does Drafts work in?</b></summary>

Most native Mac apps, browsers such as Safari and Chrome, and most chat and email apps. A few apps
don't expose their text fields to macOS, and in those ClipBar can't see what you type.
</details>

<details>
<summary><b>Is ClipBar free?</b></summary>

Yes. ClipBar is free and open source under the MIT license, with no subscription, account or in-app purchase.
</details>

<details>
<summary><b>Does ClipBar send my clipboard anywhere?</b></summary>

No. ClipBar makes no network requests. Your history is stored only on your Mac in
`~/Library/Application Support/ClipBar/`, and locked values are stored in your macOS Keychain.
</details>

<details>
<summary><b>How do I keep a credit card number or password safe in ClipBar?</b></summary>

Add it to **Saved** with **+** and turn on **Lock with Touch ID**. The value moves into the Keychain,
is hidden in the list and needs Touch ID or your Mac password every time you use it.
</details>

<details>
<summary><b>Why isn't my screenshot showing up right away?</b></summary>

macOS saves a screenshot only after its floating thumbnail disappears, about five seconds later.
Open ⇧⌘5 → Options and turn off **Show Floating Thumbnail** to get it instantly. Screenshots taken
with **Control** held (⌃⇧⌘3 / ⌃⇧⌘4) go straight to the clipboard and appear in ClipBar immediately.
</details>

<details>
<summary><b>Why does macOS ask for Desktop or Pictures access?</b></summary>

That's where macOS saves screenshots. ClipBar reads that one folder to add new screenshots to your
history. You can turn screenshot capture off in Settings → Screenshots.
</details>

<details>
<summary><b>Is there a Linux version of ClipBar?</b></summary>

Yes. [ClipBar for Linux](#clipbar-for-linux) has the clipboard history, Drafts, Saved and locked
items, screenshots and OCR. Install the `.deb` from the
[Linux release](https://github.com/SajjadMohabati/clipbar-mac/releases/tag/linux-v1.0) on Ubuntu
or Debian, or run it from source on other distributions.
</details>

<details>
<summary><b>Does it work on Intel Macs and older macOS versions?</b></summary>

It runs on both Apple silicon and Intel Macs. It needs macOS 26 Tahoe, because the interface is
built on the Liquid Glass APIs introduced there.
</details>

## Your data

Everything lives in `~/Library/Application Support/ClipBar/`:

- `history.json`: your clipboard history
- `saved.json`: saved items (locked values are in the Keychain, never in this file)
- `drafts.json`: drafts of text you typed, if you turned Drafts on
- `Images/`: copied images, stored once as PNG files even if you copy them many times

To start over, quit ClipBar and delete that folder.

## Project layout

```
Sources/ClipBar/
  App.swift                menu bar item, panel, windows, keyboard handling
  ClipView.swift           the menu bar panel
  EditorView.swift         item viewer and editor window
  SettingsView.swift       settings window
  Store.swift              history model, capture, cleanup, persistence
  Clipboard.swift          pasteboard I/O, secret detection, image storage, OCR
  Vault.swift              Keychain storage and Touch ID for locked items
  ScreenshotWatcher.swift  picks up new screenshots from the screenshot folder
  DraftWatcher.swift       keeps drafts of text typed in other apps
  Transforms.swift         text transforms
  HotKey.swift             global shortcut
  Settings.swift           preferences
scripts/
  make-icon.swift          renders the app icon
  make-dmg-background.swift renders the installer background
clipbar-linux/             ClipBar for Linux (Python and Qt 6)
```

## Contributing

Bug reports, ideas and pull requests are welcome. Open an
[issue](https://github.com/SajjadMohabati/clipbar-mac/issues) to start a conversation.
If ClipBar saves you time, a ⭐️ on GitHub helps other people find it.

## Author

Created by **Sajjad Mohabati** · [github.com/SajjadMohabati](https://github.com/SajjadMohabati)

## License

[MIT](LICENSE) © Sajjad Mohabati

<sub>Keywords: recover lost typed text on Mac, restore unsent message, form text recovery, autosave what you type, typing history Mac, draft autosave, lost text recovery macOS, clipboard manager for Mac, clipboard history macOS, menu bar clipboard app, macOS Tahoe clipboard, Liquid Glass app, free clipboard manager, open source clipboard manager, copy paste history Mac, Touch ID clipboard, screenshot to clipboard, OCR clipboard, SwiftUI menu bar app, clipboard manager for Linux, Ubuntu clipboard history, Linux clipboard manager with history, Wayland clipboard manager, recover lost typed text on Linux.</sub>

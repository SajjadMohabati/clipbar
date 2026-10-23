import AppKit
import ApplicationServices

/// Keeps a copy of what you're typing in other apps, so a message isn't lost when a form resets,
/// a send fails or a tab closes. It asks Accessibility for the text of the focused field once a
/// second; it never listens to the keyboard, and it never reads password fields.
@MainActor
final class DraftWatcher {
    /// Longer than this is a document or a terminal buffer, not a message.
    private static let maxLength = 20_000
    private static let textRoles: Set<String> = [
        kAXTextFieldRole as String, kAXTextAreaRole as String, kAXComboBoxRole as String,
    ]
    /// Terminals expose their whole scrollback as one text area; password managers are private.
    private static let skippedApps: Set<String> = [
        "com.apple.Terminal", "com.googlecode.iterm2", "dev.warp.Warp-Stable", "com.mitchellh.ghostty",
        "net.kovidgoyal.kitty", "org.alacritty", "com.github.wez.wezterm",
        "com.apple.keychainaccess", "com.apple.Passwords", "com.1password.1password",
        "com.agilebits.onepassword7", "com.bitwarden.desktop", "org.keepassxc.keepassxc",
    ]
    /// Chromium only builds its accessibility tree for web pages once an assistive app asks for it.
    private static let chromiumApps: Set<String> = [
        "com.google.Chrome", "com.google.Chrome.canary", "com.microsoft.edgemac", "com.brave.Browser",
        "company.thebrowser.Browser", "com.vivaldi.Vivaldi", "com.operasoftware.Opera", "org.chromium.Chromium",
    ]

    private let store: ClipStore
    private var timer: Timer?
    private var prepared: Set<pid_t> = []

    // The field being typed in, and the draft that belongs to it.
    private var field: AXUIElement?
    private var draft: UUID?
    private var last = ""
    private var peak = 0

    init(store: ClipStore) {
        self.store = store
    }

    func start() {
        guard timer == nil else { return }
        let timer = Timer.scheduledTimer(withTimeInterval: 1, repeats: true) { [weak self] _ in
            MainActor.assumeIsolated { self?.check() }
        }
        timer.tolerance = 0.3
        self.timer = timer
    }

    func stop() {
        timer?.invalidate()
        timer = nil
        forget()
    }

    private func forget() {
        field = nil
        draft = nil
        last = ""
        peak = 0
    }

    private func check() {
        autoreleasepool {
            guard AXIsProcessTrusted(), !store.paused,
                  let app = NSWorkspace.shared.frontmostApplication,
                  app.processIdentifier != ProcessInfo.processInfo.processIdentifier,
                  let bundleID = app.bundleIdentifier,
                  !Self.skippedApps.contains(bundleID) else { return forget() }
            let application = AXUIElementCreateApplication(app.processIdentifier)
            prepare(application, pid: app.processIdentifier, bundleID: bundleID)

            // No focused element usually means a menu or dialog is in the way; keep the session.
            guard let element = focusedElement(of: application) else { return }

            guard let role = string(kAXRoleAttribute, of: element), Self.textRoles.contains(role),
                  string(kAXSubroleAttribute, of: element) != kAXSecureTextFieldSubrole as String,
                  string(kAXSubroleAttribute, of: element) != kAXSearchFieldSubrole as String,
                  let text = text(of: element) else { return forget() }

            guard let field, CFEqual(field, element) else {
                // Web and Electron apps hand out a new element for the same field now and then;
                // if the text carries on from what was there, it's still the same message.
                if !last.isEmpty, text.continues(last) {
                    field = element
                    return
                }
                // A different field: whatever is already in it isn't something being typed now.
                forget()
                field = element
                last = text
                peak = text.count
                return
            }
            guard text != last else { return }
            last = text

            // Sent, cleared or wiped: the draft keeps the full text, and what follows is a new one.
            if text.count * 2 < peak {
                draft = nil
                peak = text.count
            }
            peak = max(peak, text.count)

            let settings = Settings.shared
            let typed = text.trimmingCharacters(in: .whitespacesAndNewlines)
            guard typed.count >= settings.draftMinLength,
                  !(settings.skipSensitive && Clipboard.looksSensitive(typed)) else { return }
            draft = store.recordDraft(draft, text: typed, source: bundleID)
        }
    }

    private func focusedElement(of application: AXUIElement) -> AXUIElement? {
        var value: CFTypeRef?
        guard AXUIElementCopyAttributeValue(application, kAXFocusedUIElementAttribute as CFString, &value) == .success,
              let value, CFGetTypeID(value) == AXUIElementGetTypeID() else { return nil }
        return (value as! AXUIElement)
    }

    /// The field's text in typing order. Chromium's `AXValue` returns right-to-left lines with
    /// their runs in visual order, so the range API, which doesn't, is asked first.
    private func text(of element: AXUIElement) -> String? {
        var count: CFTypeRef?
        if AXUIElementCopyAttributeValue(element, kAXNumberOfCharactersAttribute as CFString, &count) == .success,
           let length = count as? Int {
            guard length <= Self.maxLength else { return nil }
            var range = CFRange(location: 0, length: length)
            var value: CFTypeRef?
            if length > 0, let range = AXValueCreate(.cfRange, &range),
               AXUIElementCopyParameterizedAttributeValue(
                   element, kAXStringForRangeParameterizedAttribute as CFString, range, &value
               ) == .success, let text = value as? String {
                return text
            }
        }
        guard let text = string(kAXValueAttribute, of: element), text.utf16.count <= Self.maxLength else { return nil }
        return text
    }

    private func string(_ attribute: String, of element: AXUIElement) -> String? {
        var value: CFTypeRef?
        guard AXUIElementCopyAttributeValue(element, attribute as CFString, &value) == .success else { return nil }
        return value as? String
    }

    /// Electron and Chromium apps hide their text fields from Accessibility until asked.
    private func prepare(_ element: AXUIElement, pid: pid_t, bundleID: String) {
        // A slow or hung app must not stall ClipBar.
        AXUIElementSetMessagingTimeout(element, 0.25)
        guard !prepared.contains(pid) else { return }
        if prepared.count > 200 { prepared.removeAll() }
        prepared.insert(pid)
        AXUIElementSetAttributeValue(element, "AXManualAccessibility" as CFString, kCFBooleanTrue)
        if Self.chromiumApps.contains(bundleID) {
            AXUIElementSetAttributeValue(element, "AXEnhancedUserInterface" as CFString, kCFBooleanTrue)
        }
    }
}

extension String {
    /// Whether this text is `earlier` with more typed or edited: they share most of their beginning.
    func continues(_ earlier: String) -> Bool {
        let shorter = Swift.min(count, earlier.count)
        guard shorter > 0 else { return false }
        return commonPrefix(with: earlier).count * 10 >= shorter * 7
    }
}

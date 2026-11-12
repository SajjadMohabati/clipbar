import Foundation

/// Reports new screenshots (⇧⌘3 / ⇧⌘4 / ⇧⌘5) by watching the folder macOS saves them to.
/// Opening the folder is also what makes macOS ask for Desktop access the first time.
@MainActor
final class ScreenshotWatcher {
    private let onScreenshot: (URL) -> Void
    private var source: DispatchSourceFileSystemObject?
    private var locationCheck: Timer?
    private var retryTimer: Timer?
    private var folder: URL?
    private var seen: Set<String> = []
    private var pendingRetries: [String: Int] = [:]
    private var startDate = Date.now.addingTimeInterval(-5)

    init(onScreenshot: @escaping (URL) -> Void) {
        self.onScreenshot = onScreenshot
    }

    /// The location chosen in the ⇧⌘5 Options menu, or the Desktop.
    private static var screenshotFolder: URL {
        let custom = (CFPreferencesCopyAppValue("location" as CFString, "com.apple.screencapture" as CFString) as? String)
            ?? UserDefaults(suiteName: "com.apple.screencapture")?.string(forKey: "location")
        let path = (custom.map { NSString(string: $0).expandingTildeInPath }) ?? ""
        var isDirectory: ObjCBool = false
        if FileManager.default.fileExists(atPath: path, isDirectory: &isDirectory), isDirectory.boolValue {
            return URL(fileURLWithPath: path, isDirectory: true)
        }
        return URL.desktopDirectory
    }

    func start() {
        guard locationCheck == nil else { return }
        watch(Self.screenshotFolder)
        // Follow changes to the save location (⇧⌘5 → Options) and run a catch-up scan
        locationCheck = Timer.scheduledTimer(withTimeInterval: 2, repeats: true) { [weak self] _ in
            MainActor.assumeIsolated {
                guard let self else { return }
                if Self.screenshotFolder != self.folder {
                    self.watch(Self.screenshotFolder)
                } else {
                    self.scan()
                }
            }
        }
    }

    func stop() {
        locationCheck?.invalidate()
        locationCheck = nil
        retryTimer?.invalidate()
        retryTimer = nil
        pendingRetries.removeAll()
        source?.cancel()
        source = nil
        folder = nil
    }

    private func watch(_ folder: URL) {
        source?.cancel()
        source = nil
        retryTimer?.invalidate()
        retryTimer = nil
        pendingRetries.removeAll()
        self.folder = folder

        let descriptor = open(folder.path, O_EVTONLY)
        // Not readable (yet): forget it so the next location check tries again.
        guard descriptor >= 0 else { return self.folder = nil }
        startDate = Date.now.addingTimeInterval(-5)
        seen = Set(files(in: folder).map(\.path))

        let source = DispatchSource.makeFileSystemObjectSource(fileDescriptor: descriptor, eventMask: .write, queue: .main)
        source.setEventHandler { [weak self] in
            MainActor.assumeIsolated { self?.scan() }
        }
        source.setCancelHandler { close(descriptor) }
        source.resume()
        self.source = source
    }

    private func scan() {
        autoreleasepool {
            guard let folder else { return }
            for url in files(in: folder) {
                let path = url.path
                guard !seen.contains(path) else { continue }

                if Self.isReadyScreenshot(url, since: startDate) {
                    seen.insert(path)
                    pendingRetries.removeValue(forKey: path)
                    onScreenshot(url)
                } else if Self.isCandidate(url, since: startDate) {
                    if pendingRetries[path] == nil {
                        pendingRetries[path] = 0
                        startRetryTimerIfNeeded()
                    }
                }
            }
        }
    }

    private func startRetryTimerIfNeeded() {
        guard retryTimer == nil, !pendingRetries.isEmpty else { return }
        retryTimer = Timer.scheduledTimer(withTimeInterval: 0.1, repeats: true) { [weak self] _ in
            MainActor.assumeIsolated {
                guard let self else { return }
                self.checkPendingRetries()
            }
        }
    }

    private func checkPendingRetries() {
        autoreleasepool {
            guard folder != nil else {
                retryTimer?.invalidate()
                retryTimer = nil
                pendingRetries.removeAll()
                return
            }

            for (path, attempts) in pendingRetries {
                let url = URL(fileURLWithPath: path)
                if Self.isReadyScreenshot(url, since: startDate) {
                    seen.insert(path)
                    pendingRetries.removeValue(forKey: path)
                    onScreenshot(url)
                } else if attempts >= 35 {
                    // Timeout after 3.5 seconds; mark as seen so we don't retry forever
                    seen.insert(path)
                    pendingRetries.removeValue(forKey: path)
                } else {
                    pendingRetries[path] = attempts + 1
                }
            }

            if pendingRetries.isEmpty {
                retryTimer?.invalidate()
                retryTimer = nil
            }
        }
    }

    private func files(in folder: URL) -> [URL] {
        (try? FileManager.default.contentsOfDirectory(
            at: folder, includingPropertiesForKeys: [.creationDateKey, .fileSizeKey], options: .skipsHiddenFiles
        )) ?? []
    }

    /// Checks if a file is candidate to become a screenshot (created recently with image extension or in progress)
    private static func isCandidate(_ url: URL, since date: Date) -> Bool {
        guard let created = try? url.resourceValues(forKeys: [.creationDateKey]).creationDate,
              created >= date else { return false }
        let ext = url.pathExtension.lowercased()
        return ext.isEmpty || ["png", "jpg", "jpeg", "heic", "tiff", "pdf"].contains(ext)
    }

    /// Checks if the file is fully ready, has positive size, and is recognized as a screenshot.
    private static func isReadyScreenshot(_ url: URL, since date: Date) -> Bool {
        guard let values = try? url.resourceValues(forKeys: [.creationDateKey, .fileSizeKey]),
              let created = values.creationDate,
              created >= date,
              let size = values.fileSize, size > 0 else { return false }
        return isScreenshotFile(url)
    }

    /// macOS tags screenshots with extended attributes; also match standard localized prefixes.
    private static func isScreenshotFile(_ url: URL) -> Bool {
        let path = url.path
        if getxattr(path, "com.apple.metadata:kMDItemIsScreenCapture", nil, 0, 0, 0) >= 0 {
            return true
        }
        if getxattr(path, "com.apple.metadata:kMDItemScreenCaptureType", nil, 0, 0, 0) >= 0 {
            return true
        }
        let name = url.lastPathComponent
        let knownPrefixes = [
            "Screenshot", "Screen Shot", "ScreenCapture", "Capture d’écran", "Capture d'écran",
            "Bildschirmfoto", "Captura de pantalla", "Schermopname", "عکس صفحه", "تصویر صفحه",
            "لقطة الشاشة", "Снимок экрана", "스크린샷", "スクリーンショット", "屏幕快照", "螢幕快照"
        ]
        return knownPrefixes.contains(where: { name.hasPrefix($0) })
    }
}

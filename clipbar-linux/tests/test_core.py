#!/usr/bin/env python3
"""Comprehensive test suite for ClipBar Linux core logic."""

import sys
import unittest
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).parent.parent))

from clipbar.transforms import TextTransform
from clipbar.settings import Settings
from clipbar.clipboard import Clipboard
from clipbar.store import ClipItem, ClipStore, Filter
from clipbar.vault import Vault


class TestClipBarCore(unittest.TestCase):

    def test_transforms(self):
        # Uppercase
        self.assertEqual(TextTransform.UPPERCASE.apply("hello world"), "HELLO WORLD")
        # Lowercase
        self.assertEqual(TextTransform.LOWERCASE.apply("HELLO WORLD"), "hello world")
        # Capitalize
        self.assertEqual(TextTransform.CAPITALIZED.apply("hello world"), "Hello World")
        # Trim
        self.assertEqual(TextTransform.TRIMMED.apply("   hello   \n   world   "), "hello\nworld")
        # Remove empty lines
        self.assertEqual(TextTransform.REMOVE_EMPTY_LINES.apply("line1\n\nline2\n   \nline3"), "line1\nline2\nline3")
        # Sort lines
        self.assertEqual(TextTransform.SORT_LINES.apply("banana\napple\ncherry"), "apple\nbanana\ncherry")
        # Unique lines
        self.assertEqual(TextTransform.UNIQUE_LINES.apply("apple\nbanana\napple\ncherry"), "apple\nbanana\ncherry")
        # Join lines
        self.assertEqual(TextTransform.JOIN_LINES.apply("hello\nworld"), "hello world")
        # JSON pretty and minify
        raw_json = '{"b":2,"a":1}'
        pretty = TextTransform.PRETTY_JSON.apply(raw_json)
        self.assertIn('"a": 1', pretty)
        minified = TextTransform.MINIFY_JSON.apply(raw_json)
        self.assertEqual(minified, '{"b":2,"a":1}')
        # Base64
        b64 = TextTransform.BASE64_ENCODE.apply("ClipBar")
        self.assertEqual(b64, "Q2xpcEJhcg==")
        self.assertEqual(TextTransform.BASE64_DECODE.apply(b64), "ClipBar")
        # URL
        url_enc = TextTransform.URL_ENCODE.apply("hello world & test")
        self.assertEqual(url_enc, "hello%20world%20%26%20test")
        self.assertEqual(TextTransform.URL_DECODE.apply(url_enc), "hello world & test")

    def test_sensitive_detection(self):
        # Private key
        self.assertTrue(Clipboard.looks_sensitive("-----BEGIN RSA PRIVATE KEY-----\nMIIE..."))
        # API token
        self.assertTrue(Clipboard.looks_sensitive("sk-1234567890abcdef1234567890abcdef"))
        self.assertTrue(Clipboard.looks_sensitive("ghp_1234567890abcdef1234567890abcdef"))
        # Credit Card Luhn check
        # Valid test Visa number (check digit 1)
        self.assertTrue(Clipboard.looks_sensitive("4532 0150 1234 5671"))
        # Invalid credit card number
        self.assertFalse(Clipboard.looks_sensitive("4532 0150 1234 5679"))
        # Regular text
        self.assertFalse(Clipboard.looks_sensitive("Just a regular message to send"))

    def test_clip_item_model(self):
        # Text item
        item = ClipItem(text="Hello world")
        self.assertEqual(item.kind, "text")
        self.assertEqual(item.preview, "Hello world")

        # Color item
        color_item = ClipItem(text="#7c5cff")
        self.assertEqual(color_item.kind, "color")
        self.assertEqual(color_item.color, "#7C5CFF")

        # Link item
        link_item = ClipItem(text="https://github.com/SajjadMohabati")
        self.assertEqual(link_item.kind, "link")
        self.assertEqual(link_item.url, "https://github.com/SajjadMohabati")

        # Image item
        img_item = ClipItem(image="test1234.png", text="Recognized text inside image")
        self.assertEqual(img_item.kind, "image")
        self.assertEqual(img_item.preview, "Image — Recognized text inside image")

        # Files item
        file_item = ClipItem(files=["/home/user/document.pdf", "/home/user/photo.png"])
        self.assertEqual(file_item.kind, "files")
        self.assertIn("document.pdf", file_item.preview)

        # Secret / Locked item
        secret_item = ClipItem(title="Bank card", secret=True)
        self.assertTrue(secret_item.is_locked)
        self.assertEqual(secret_item.preview, "••••••••")

    def test_store_operations(self):
        store = ClipStore()
        # Clean state
        store.clear(including_pinned=True)

        # Insert items
        item1 = ClipItem(text="First item")
        item2 = ClipItem(text="Second item")
        store.insert(item1)
        store.insert(item2)

        self.assertEqual(len(store.items), 2)
        # item2 was inserted last, should be first
        self.assertEqual(store.items[0].text, "Second item")

        # Pin item1
        store.toggle_pin(item1)
        self.assertTrue(item1.pinned)
        # item1 (pinned) should now be at index 0
        self.assertEqual(store.items[0].id, item1.id)

        # Move item2 to saved
        store.save_item(item2)
        self.assertEqual(len(store.items), 1)
        self.assertEqual(len(store.saved), 1)
        self.assertEqual(store.saved[0].id, item2.id)

        # Drafts record
        draft_id = store.record_draft(None, "Draft typing test in progress...", "test-app")
        self.assertEqual(len(store.drafts), 1)
        self.assertEqual(store.drafts[0].id, draft_id)
        self.assertEqual(store.drafts[0].text, "Draft typing test in progress...")

    def test_vault_local(self):
        import tempfile
        from unittest import mock
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "vault.enc"
            with mock.patch.object(Vault, "_path", classmethod(lambda cls: path)):
                Vault.lock()
                # Without a password nothing can be stored, and nothing asks on a non-GUI path.
                self.assertFalse(Vault.is_set_up())
                self.assertFalse(Vault.create("short"))
                self.assertTrue(Vault.create("correct horse"))
                self.assertTrue(Vault.write("my-super-secret-password-123", "id-1"))
                self.assertEqual(Vault.read("id-1"), "my-super-secret-password-123")

                # The file holds no plain text and is private.
                raw = path.read_bytes()
                self.assertNotIn(b"my-super-secret", raw)
                self.assertEqual(path.stat().st_mode & 0o777, 0o600)

                # Locked: no reads, no writes, and wrong or empty passwords don't open it.
                Vault.lock()
                self.assertIsNone(Vault.read("id-1"))
                self.assertFalse(Vault.write("x", "id-2"))
                self.assertFalse(Vault.unlock(""))
                self.assertFalse(Vault.unlock("wrong password"))
                self.assertIsNone(Vault.read("id-1"))

                self.assertTrue(Vault.unlock("correct horse"))
                self.assertEqual(Vault.read("id-1"), "my-super-secret-password-123")
                self.assertTrue(Vault.delete("id-1"))
                self.assertIsNone(Vault.read("id-1"))

                # The grace period ends and the key is forgotten.
                Vault._unlocked_until = 0
                self.assertFalse(Vault.is_unlocked())
                self.assertIsNone(Vault._key)

                # A tampered file is rejected, not half-read.
                Vault.lock()
                import json
                env = json.loads(path.read_text())
                data = bytearray(__import__("base64").b64decode(env["data"]))
                data[0] ^= 1
                env["data"] = __import__("base64").b64encode(bytes(data)).decode()
                path.write_text(json.dumps(env))
                self.assertFalse(Vault.unlock("correct horse"))

                # An old-format file is set aside rather than trusted.
                path.write_bytes(b"\x01\x02xor-data")
                self.assertFalse(Vault.is_set_up())
                self.assertTrue((Path(tmp) / "vault.enc.unreadable").exists())
                Vault.lock()

    def test_locked_save_needs_password(self):
        from unittest import mock
        store = ClipStore()
        store.save = lambda: None
        with mock.patch.object(Vault, "authenticate", return_value=False):
            Vault.lock()
            # The prompt was cancelled: nothing is added, and nothing leaks unencrypted.
            self.assertFalse(store.add_saved("Card", "4111 1111 1111 1111", locked=True))
            self.assertEqual(store.saved, [])

    def test_draft_continues(self):
        from clipbar.draft_watcher import continues
        self.assertTrue(continues("Hello there, how are you", "Hello there, how"))
        self.assertTrue(continues("سلام خوبی", "سلام خو"))
        self.assertFalse(continues("Something else entirely", "Hello there"))
        self.assertFalse(continues("", "Hello"))

    def test_bounded_cache(self):
        from clipbar.clipboard import BoundedCache
        cache = BoundedCache(maxsize=3)
        cache["a"] = 1
        cache["b"] = 2
        cache["c"] = 3
        self.assertEqual(len(cache), 3)

        # Adding 4th item should evict oldest ("a")
        cache["d"] = 4
        self.assertEqual(len(cache), 3)
        self.assertNotIn("a", cache)
        self.assertIn("b", cache)
        self.assertIn("c", cache)
        self.assertIn("d", cache)

        # Accessing "b" makes it most recent
        _ = cache.get("b")
        # Adding 5th item should now evict "c", keeping "b" and "d"
        cache["e"] = 5
        self.assertNotIn("c", cache)
        self.assertIn("b", cache)
        self.assertIn("e", cache)

    def test_poll_clipboard_deduplication(self):
        store = ClipStore()
        store.clear(including_pinned=True)

        # Poll same text twice - only one item should be inserted
        store.poll_clipboard(text="Identical clipboard text")
        store.poll_clipboard(text="Identical clipboard text")
        self.assertEqual(len(store.items), 1)
        self.assertEqual(store.items[0].text, "Identical clipboard text")

        # Poll new text
        store.poll_clipboard(text="New text")
        self.assertEqual(len(store.items), 2)
        self.assertEqual(store.items[0].text, "New text")


if __name__ == "__main__":
    unittest.main()

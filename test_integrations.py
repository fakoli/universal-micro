"""Patch workflow uses a real disposable Git checkout, never a deployed client."""
import hashlib
import subprocess
import tempfile
import unittest
from pathlib import Path


class PatchCheck(unittest.TestCase):
    def test_apply_reverse_refuses_repeat_drift_and_tampering(self):
        import prepare_integrations as integration
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "client"
            source.mkdir()
            def git(*args):
                return subprocess.check_output(["git", "-C", str(source), *args], text=True).strip()
            git("init", "-q")
            git("config", "user.name", "Example")
            git("config", "user.email", "example@example.invalid")
            git("config", "core.autocrlf", "false")
            (source / "file.txt").write_bytes(b"before\n")
            git("add", "file.txt")
            git("commit", "-qm", "fixture")
            patch = root / "change.patch"
            patch.write_bytes(b"--- a/file.txt\n+++ b/file.txt\n@@ -1 +1 @@\n-before\n+after\n")
            digest = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
            adapter = {"base_commit": git("rev-parse", "HEAD"), "files": {"file.txt": digest(source / "file.txt")},
                       "patches": [{"path": "change.patch", "sha256": digest(patch)}],
                       "patched_files": {"file.txt": hashlib.sha256(b"after\n").hexdigest()}}
            integration.prepare(adapter, source, "check", root)
            self.assertEqual((source / "file.txt").read_bytes(), b"before\n")
            integration.prepare(adapter, source, "apply", root)
            self.assertEqual((source / "file.txt").read_bytes(), b"after\n")
            with self.assertRaises(ValueError):
                integration.prepare(adapter, source, "apply", root)
            integration.prepare(adapter, source, "reverse", root)
            self.assertEqual((source / "file.txt").read_bytes(), b"before\n")
            (source / "file.txt").write_bytes(b"drift\n")
            with self.assertRaises(ValueError):
                integration.prepare(adapter, source, "apply", root)
            (source / "file.txt").write_bytes(b"before\n")
            patch.write_bytes(patch.read_bytes() + b"tampered\n")
            with self.assertRaises(ValueError):
                integration.prepare(adapter, source, "apply", root)


if __name__ == "__main__":
    unittest.main()

"""The archive must contain exactly the reviewed allowlist and reject local state."""
import subprocess
import tempfile
import unittest
import zipfile
from pathlib import Path


class ReleaseCheck(unittest.TestCase):
    def test_refuses_extra_files_private_paths_and_credentials(self):
        from check_release import validate
        allowed = {"README.md"}
        validate({"README.md": b"example"}, allowed)
        validate({"README.md": rb"Example pattern: /home/[^\s/]+/"}, allowed)
        for files in ({"README.md": b"ok", ".local/state.json": b"private"},
                      {"README.md": b"ghp_" + b"x" * 36},
                      {"README.md": b"C:\\Users\\some-person\\private"}):
            with self.assertRaises(ValueError):
                validate(files, allowed)

    def test_archives_only_clean_reviewed_commit(self):
        from check_release import archive
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            def git(*args):
                subprocess.run(["git", "-C", str(root), *args], check=True, capture_output=True)
            git("init", "-q")
            git("config", "user.name", "Example")
            git("config", "user.email", "example@example.invalid")
            git("config", "core.autocrlf", "false")
            (root / "release-files.txt").write_text("README.md\nrelease-files.txt\n")
            (root / "README.md").write_text("Synthetic example\n")
            git("add", "README.md", "release-files.txt")
            git("commit", "-qm", "fixture")
            (root / "private.txt").write_text("never package this")
            output = root / "review.zip"
            archive(root, output)
            with zipfile.ZipFile(output) as zipped:
                self.assertEqual({x for x in zipped.namelist() if not x.endswith('/')},
                                 {"universal-micro/README.md", "universal-micro/release-files.txt"})
            (root / "README.md").write_text("unreviewed edit\n")
            with self.assertRaises(ValueError):
                archive(root, root / "dirty.zip")


if __name__ == "__main__":
    unittest.main()

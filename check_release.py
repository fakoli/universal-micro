"""Check the explicit public file allowlist; optionally archive the clean Git commit."""
import argparse
import hashlib
from pathlib import Path, PurePosixPath
import re
import subprocess
import zipfile

ROOT = Path(__file__).resolve().parent
SENSITIVE = re.compile(r"gh[pousr]_[A-Za-z0-9]{20,}|sk-[A-Za-z0-9_-]{20,}|-----BEGIN [A-Z ]*PRIVATE KEY-----|[A-Za-z]:[\\/]Users[\\/][^\s\\/]+|/home/[A-Za-z0-9_.-]+/|\b(?:10\.\d+|192\.168|172\.(?:1[6-9]|2\d|3[01]))\.\d+\.\d+\b")


def validate(files, allowed):
    if set(files) != set(allowed):
        raise ValueError("Public file allowlist differs: " + ", ".join(sorted(set(files) ^ set(allowed))))
    for name, data in files.items():
        path = PurePosixPath(name)
        if path.is_absolute() or ".." in path.parts or "\\" in name or ".local" in path.parts:
            raise ValueError("Unsafe public path: " + name)
        try:
            text = data.decode("utf-8")
        except UnicodeDecodeError:
            raise ValueError("Only reviewed UTF-8 source files are allowed: " + name) from None
        if "\x00" in text or SENSITIVE.search(text):
            raise ValueError("Possible private material in " + name + "; inspect locally")


def approved_files(root):
    allowed = set((root / "release-files.txt").read_text(encoding="utf-8").splitlines())
    result = subprocess.run(["git", "-C", str(root), "ls-files", "-z"], capture_output=True, check=True)
    files = {name: (root / name).read_bytes() for name in result.stdout.decode("utf-8").split("\0") if name}
    validate(files, allowed)
    return allowed


def archive(root, destination):
    allowed = approved_files(root)
    clean = subprocess.run(["git", "-C", str(root), "diff", "--quiet", "HEAD", "--"])
    if clean.returncode:
        raise ValueError("Commit reviewed changes before creating an archive")
    data = subprocess.check_output(["git", "-C", str(root), "archive", "--format=zip", "--prefix=universal-micro/", "HEAD"])
    import io
    with zipfile.ZipFile(io.BytesIO(data)) as zipped:
        files = {name.removeprefix("universal-micro/"): zipped.read(name)
                 for name in zipped.namelist() if not name.endswith("/")}
        validate(files, allowed)
    destination = Path(destination)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_bytes(data)
    digest = hashlib.sha256(data).hexdigest()
    destination.with_suffix(destination.suffix + ".sha256").write_text(f"{digest}  {destination.name}\n", encoding="utf-8")
    print(f"Checked {len(files)} files; SHA-256 {digest}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--archive", type=Path)
    args = parser.parse_args()
    try:
        if args.archive:
            archive(ROOT, args.archive)
        else:
            count = len(approved_files(ROOT))
            print(f"Public source check passed ({count} allowlisted files). Manual privacy review is still required.")
    except (OSError, ValueError, subprocess.CalledProcessError) as error:
        parser.exit(1, f"{error}\n")


if __name__ == "__main__":
    main()

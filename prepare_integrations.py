"""Apply reviewed adapters only to explicit, pinned client checkouts. No deployment."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parent


def prepare(adapter, source, mode, root=ROOT):
    source = Path(source).resolve()
    def git(*args, input=None):
        result = subprocess.run(["git", "-c", "core.autocrlf=false", "-c", "core.eol=lf", "-C", str(source), *args], input=input, capture_output=True)
        if result.returncode:
            raise ValueError("Git refused the operation: " + result.stderr.decode("utf-8", "replace").strip())
        return result.stdout
    if git("rev-parse", "HEAD").decode().strip() != adapter["base_commit"]:
        raise ValueError("Wrong client revision; use the manifest's immutable base commit")
    patches = []
    for item in adapter["patches"]:
        data = (root / item["path"]).read_bytes()
        if hashlib.sha256(data).hexdigest() != item["sha256"]:
            raise ValueError("Patch checksum mismatch")
        patches.append(data)
    combined = b"".join(patches)
    if mode == "reverse":
        for name, expected in adapter["patched_files"].items():
            if hashlib.sha256((source / name).read_bytes()).hexdigest() != expected:
                raise ValueError("Patched source changed; refusing rollback: " + name)
        # Refuse rollback across unrelated tracked changes, not just overlapping hunks.
        expected = git("apply", "--numstat", "-", input=combined).decode().splitlines()
        allowed = {line.split("\t", 2)[2] for line in expected}
        changed = set(git("diff", "--name-only").decode().splitlines())
        if changed - allowed or git("diff", "--cached", "--name-only").strip():
            raise ValueError("Unrelated changes exist; use a dedicated integration checkout")
        git("apply", "--reverse", "--check", "-", input=combined)
        git("apply", "--reverse", "-", input=combined)
        return
    if git("status", "--porcelain", "--untracked-files=normal").strip():
        raise ValueError("Client checkout must be clean; repeat application and local changes are refused")
    for name, expected in adapter["files"].items():
        if hashlib.sha256((source / name).read_bytes()).hexdigest() != expected:
            raise ValueError("Client source checksum mismatch (use LF checkouts): " + name)
    git("apply", "--check", "-", input=combined)
    if mode == "apply":
        git("apply", "-", input=combined)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("adapter", choices=("hermes", "pi"))
    parser.add_argument("source", type=Path, help="Dedicated clean Git checkout; never a live installation")
    parser.add_argument("--mode", choices=("check", "apply", "reverse"), default="check")
    args = parser.parse_args()
    try:
        manifest = json.loads((ROOT / "adapters.json").read_text(encoding="utf-8"))
        prepare(manifest["adapters"][args.adapter], args.source, args.mode)
    except (OSError, ValueError) as error:
        parser.exit(1, f"{error}\n")
    print(f"{args.adapter}: {args.mode} succeeded; no services were restarted")


if __name__ == "__main__":
    main()

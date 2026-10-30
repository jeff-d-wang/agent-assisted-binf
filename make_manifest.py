"""Write or check submission_manifest.json: SHA-256 of every file Git would ship.

The file list is `git ls-files --cached --others --exclude-standard`, so ignored run
folders, caches, .h5ad files and secrets are left out. Paths are repository-relative.

    python make_manifest.py          # write submission_manifest.json
    python make_manifest.py --check  # verify the files still match it
"""
import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "submission_manifest.json"


def shipped_files():
    names = subprocess.run(
        ["git", "ls-files", "--cached", "--others", "--exclude-standard", "-z"],
        cwd=ROOT, capture_output=True, check=True,
    ).stdout.decode().split("\0")
    return sorted(n for n in names if n and n != OUT.name and (ROOT / n).is_file())


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def main():
    current = {n: sha256(ROOT / n) for n in shipped_files()}
    if "--check" not in sys.argv:
        OUT.write_text(json.dumps({"algorithm": "sha256", "files": current}, indent=1) + "\n")
        print(f"wrote {OUT.name}: {len(current)} files")
        return
    saved = json.loads(OUT.read_text())["files"]
    changed = sorted(n for n in saved.keys() & current.keys() if saved[n] != current[n])
    missing, added = sorted(saved.keys() - current.keys()), sorted(current.keys() - saved.keys())
    for label, names in (("changed", changed), ("missing", missing), ("not in manifest", added)):
        for n in names:
            print(f"{label}: {n}")
    print(f"{len(saved)} in manifest; {len(changed)} changed, {len(missing)} missing, {len(added)} new")
    sys.exit(1 if changed or missing or added else 0)


if __name__ == "__main__":
    main()

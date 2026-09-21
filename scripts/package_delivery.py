"""Package reviewed, tracked CAD files and a hash-locked APK for delivery.

Usage: python scripts/package_delivery.py manifest.json --output .delivery
The manifest is a local build input. Signing keys and untracked files are excluded.
"""
import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import subprocess
import zipfile


def git(*args):
    return subprocess.check_output(["git", *args], cwd=ROOT)


def digest(data):
    return hashlib.sha256(data).hexdigest()


ROOT = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("manifest", type=Path)
parser.add_argument("--output", type=Path, default=ROOT / ".delivery")
args = parser.parse_args()
manifest = json.loads(args.manifest.read_text(encoding="utf-8-sig"))
revision = git("rev-parse", manifest["source_commit"] + "^{commit}").decode().strip()
output = args.output.resolve()
output.mkdir(parents=True, exist_ok=True)
artifacts = []

for package in manifest["packages"]:
    name = package["name"]
    if Path(name).name != name or not name.endswith(".zip"):
        raise ValueError("Package name must be a plain .zip filename")
    root = PurePosixPath(package["root"])
    if root.is_absolute() or ".." in root.parts:
        raise ValueError("Package root must be a repository-relative directory")
    files = git("ls-tree", "-r", "--name-only", "-z", revision, "--", str(root)).decode().split("\0")
    files = sorted(name for name in files if name)
    if not files:
        raise ValueError(f"No tracked files under {root}")
    contents = []
    destination = output / name
    with zipfile.ZipFile(destination, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for source in files:
            relative = PurePosixPath(source).relative_to(root)
            data = git("show", f"{revision}:{source}")
            archive.writestr(str(relative), data)
            contents.append({"path": str(relative), "sha256": digest(data), "bytes": len(data)})
        archive.writestr("PACKAGE_MANIFEST.json", json.dumps({
            "source_commit": revision, "source_directory": str(root),
            "files": contents,
            "note": "Digital trial package. Follow README calibration, materials, quantities and assembly instructions. Not physically printed by the agent.",
        }, ensure_ascii=False, indent=2))
    with zipfile.ZipFile(destination) as archive:
        if archive.testzip() is not None:
            raise RuntimeError(f"ZIP integrity failure: {name}")
    artifacts.append({"file": name, "sha256": digest(destination.read_bytes()), "bytes": destination.stat().st_size})

apk = manifest.get("apk")
if apk:
    name = apk["name"]
    if Path(name).name != name or not name.endswith(".apk"):
        raise ValueError("APK name must be a plain .apk filename")
    data = Path(apk["path"]).read_bytes()
    if digest(data).lower() != apk["sha256"].lower():
        raise RuntimeError("APK differs from the tested hash; refusing to package")
    (output / name).write_bytes(data)
    artifacts.append({"file": name, "sha256": digest(data), "bytes": len(data)})

for asset in manifest.get("additional_artifacts", []):
    name = asset["name"]
    if Path(name).name != name or name in {item["file"] for item in artifacts}:
        raise ValueError("Additional artifact needs a unique plain filename")
    data = Path(asset["path"]).read_bytes()
    if digest(data).lower() != asset["sha256"].lower():
        raise RuntimeError(f"Artifact differs from the reviewed hash: {name}")
    (output / name).write_bytes(data)
    artifacts.append({"file": name, "sha256": digest(data), "bytes": len(data)})

(output / "SHA256SUMS.txt").write_text("".join(f"{item['sha256']}  {item['file']}\n" for item in artifacts), encoding="utf-8")
(output / "delivery-manifest.json").write_text(json.dumps({"source_commit": revision, "artifacts": artifacts}, indent=2), encoding="utf-8")
print(json.dumps({"output": str(output), "source_commit": revision, "artifacts": artifacts}, indent=2))

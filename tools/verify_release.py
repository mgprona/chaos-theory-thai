"""Verify a distributed ZIP with the real pristine inputs in an isolated fixture.

Reads the actual installation's executable/settings only. Never installs to it.
Keeps the fixture under out for inspection and records machine-readable evidence.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import zipfile

ROOT = Path(__file__).resolve().parents[1]


def sha256(path: Path) -> str:
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def snapshot(root: Path) -> dict[str, str]:
    return {path.relative_to(root).as_posix(): sha256(path)
            for path in sorted(root.rglob("*")) if path.is_file()
            and ".chaos-theory-thai" not in path.parts}


def verify(archive: Path, report_path: Path) -> dict:
    config = json.loads((ROOT / "config.json").read_text(encoding="utf-8"))
    actual_game = Path(config["game_dir"])
    # Account for every mod target in the real installation to prove no writes.
    live_before = snapshot(actual_game / "System")
    input_hash = sha256(ROOT / "backups/dynamic-pc.umd")
    run_dir = Path(tempfile.mkdtemp(prefix="release-test-", dir=ROOT / "out"))
    with zipfile.ZipFile(archive) as zipped:
        if zipped.testzip() is not None:
            raise ValueError("ZIP CRC check failed")
        for member in zipped.infolist():
            target = (run_dir / member.filename).resolve()
            if not target.is_relative_to(run_dir.resolve()):
                raise ValueError("ZIP path traversal")
        zipped.extractall(run_dir)
    package = next(run_dir.glob("ChaosTheory-Thai-*"))
    manifest = json.loads((package / "manifest.json").read_text(encoding="utf-8"))
    real_payload_before = {record["path"]: sha256(actual_game / record["path"])
                           if (actual_game / record["path"]).is_file() else None
                           for record in manifest["files"]}
    game = run_dir / "เกมจำลอง with spaces"
    (game / "System").mkdir(parents=True)
    shutil.copy2(ROOT / "backups/dynamic-pc.umd", game / "System/dynamic-pc.umd")
    for name in ("splintercell3.exe", "SplinterCell3.ini", "Settings.ini"):
        shutil.copy2(actual_game / "System" / name, game / "System" / name)
    for source, relative in ((ROOT / "backups/Fonts", "Data/Textures/Font"),
                             (ROOT / "data/raw_official/fonts/magma", "Data/Magma/DataPC/Fonts"),
                             (ROOT / "data/raw_official/int", "Data/System/Localization"),
                             (ROOT / "backups/System", "System")):
        destination = game / relative
        destination.mkdir(parents=True, exist_ok=True)
        for path in source.iterdir():
            if path.is_file():
                shutil.copy2(path, destination / path.name)
    (game / "Save").mkdir()
    (game / "Save/sentinel.sav").write_bytes(b"release test: preserve save bytes\n")
    before = snapshot(game)
    steps = []

    def run(action: str, *switches: str) -> None:
        command = ["powershell.exe", "-NoProfile", "-ExecutionPolicy", "Bypass",
                   "-File", str(package / "Install.ps1"), "-GameDir", str(game), *switches]
        result = subprocess.run(command, capture_output=True, timeout=180)
        output = (result.stdout + result.stderr).decode("utf-8", errors="replace")
        if result.returncode:
            raise RuntimeError(f"{action} failed ({result.returncode}): {output}")
        steps.append({"action": action, "result": "PASS", "output": output.strip()})
        print(f"PASS: {action}", flush=True)

    run("check-only", "-CheckOnly")
    if snapshot(game) != before or (game / ".chaos-theory-thai").exists():
        raise ValueError("Check-only changed fixture files")
    run("install")
    for record in manifest["files"]:
        if sha256(game / record["path"]) != record["sha256"]:
            raise ValueError(f"Installed file differs: {record['path']}")
    if sha256(game / "System/dynamic-pc.umd") != sha256(ROOT / "dist/System/dynamic-pc.umd"):
        raise ValueError("Delta output is not byte-identical to source build")
    state_path = game / ".chaos-theory-thai/state.json"
    installed_state = state_path.read_bytes()
    installed = snapshot(game)
    run("verify", "-Verify")
    run("repeat-install")
    if state_path.read_bytes() != installed_state or snapshot(game) != installed:
        raise ValueError("Repeat install changed the backup or installed files")
    for path in ("System/splintercell3.exe", "System/SplinterCell3.ini", "System/Settings.ini", "Save/sentinel.sav"):
        if installed[path] != before[path]:
            raise ValueError(f"Protected fixture file changed: {path}")
    run("uninstall", "-Uninstall")
    if snapshot(game) != before:
        raise ValueError("Uninstall did not restore original file set and exact bytes")
    run("repeat-uninstall", "-Uninstall")
    if snapshot(game) != before:
        raise ValueError("Repeat uninstall changed originals")
    if snapshot(actual_game / "System") != live_before:
        raise ValueError("Live game System files changed during verification")
    for record in manifest["files"]:
        path = actual_game / record["path"]
        digest = sha256(path) if path.is_file() else None
        if digest != real_payload_before[record["path"]]:
            raise ValueError("Live game payload changed during verification")
    if sha256(ROOT / "backups/dynamic-pc.umd") != input_hash:
        raise ValueError("Original backup changed")
    report = {"result": "PASS", "zip": archive.name, "zip_sha256": sha256(archive),
              "installed_files_verified": len(manifest["files"]),
              "preinstall_fixture_files_restored": len(before),
              "umd_matches_dist_exactly": True, "real_game_files_unchanged": True,
              "original_backup_unchanged": True, "protected_exe_ini_save_unchanged": True,
              "uninstall_restores_originals_and_removes_added_files": True,
              "fixture": str(run_dir), "steps": steps,
              "runtime_rendering_verified": False}
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: v for k, v in report.items() if k != "steps"}, ensure_ascii=False, indent=2))
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("zip", type=Path)
    parser.add_argument("--report", type=Path, default=ROOT / "out/releases/installer-verification.json")
    arguments = parser.parse_args()
    verify(arguments.zip.resolve(), arguments.report.resolve())

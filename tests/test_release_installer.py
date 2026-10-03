"""Exercise the shipped PowerShell 5.1 installer against isolated game fixtures."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import shutil
import struct
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
POWERSHELL = shutil.which("powershell.exe")


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


@unittest.skipUnless(POWERSHELL, "Windows PowerShell required")
class TestReleaseInstaller(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="chaos-thai-release-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.game = self.root / "เกมจำลอง with spaces"
        self.package = self.root / "package"
        shutil.copytree(ROOT / "release", self.package)
        self.original = bytes(range(256)) * 16
        self.modified = self.original[:100] + b"Thai patch" + self.original[110:] + b"\0" * 5
        self.write_game("System/splintercell3.exe", b"fixture exe")
        self.write_game("System/dynamic-pc.umd", self.original)
        self.write_game("Data/Textures/Font/test.pcx", b"original font")
        self.write_game("System/SplinterCell3.ini", b"[Init]\nUseDynamicDataFile=true\n[Engine.Engine]\nLanguage=int\n")
        self.write_game("System/Settings.ini", b"[Localization]\nLanguage=int\n")
        self.write_game("Save/profile.sav", b"untouched save")
        patch = (b"CTPATCH1\x01" + struct.pack("<qI", 0, 100)
                 + b"\x02" + struct.pack("<I", 10) + b"Thai patch"
                 + b"\x01" + struct.pack("<qI", 110, len(self.original) - 110)
                 + b"\x03" + struct.pack("<I", 5) + b"\x00")
        self.write_package("patches/game.ctpatch", patch)
        self.write_package("payload/font.pcx", b"Thai font")
        self.write_package("payload/new.int", b"Thai text")
        self.manifest = {"format": 1, "version": "1.0.0-rc1",
                         "executable_sha256": digest(b"fixture exe"),
                         "base_umd_sha256": digest(self.original),
                         "files": [
                             {"path": "System/dynamic-pc.umd", "size": len(self.modified),
                              "sha256": digest(self.modified), "patch": "patches/game.ctpatch"},
                             {"path": "Data/Textures/Font/test.pcx", "size": 9,
                              "sha256": digest(b"Thai font"), "payload": "payload/font.pcx"},
                             {"path": "Data/System/Localization/new.int", "size": 9,
                              "sha256": digest(b"Thai text"), "payload": "payload/new.int"}]}
        self.refresh_manifest()
        self.before = self.snapshot()

    def write_game(self, relative, data):
        path = self.game / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)

    def write_package(self, relative, data):
        path = self.package / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)

    def refresh_manifest(self):
        self.manifest["package_files"] = [
            {"path": path.relative_to(self.package).as_posix(), "size": path.stat().st_size,
             "sha256": digest(path.read_bytes())} for path in sorted(self.package.rglob("*"))
            if path.is_file() and path.name != "manifest.json"]
        (self.package / "manifest.json").write_text(json.dumps(self.manifest), encoding="utf-8")

    def run_installer(self, *args, success=True):
        result = subprocess.run([POWERSHELL, "-NoProfile", "-ExecutionPolicy", "Bypass",
                                 "-File", str(self.package / "Install.ps1"),
                                 "-GameDir", str(self.game), *args],
                                capture_output=True, timeout=60)
        output = (result.stdout + result.stderr).decode("utf-8", errors="replace")
        self.assertEqual(result.returncode, 0 if success else 1, output)
        return output

    def snapshot(self):
        return {path.relative_to(self.game).as_posix(): digest(path.read_bytes())
                for path in self.game.rglob("*") if path.is_file()
                and ".chaos-theory-thai" not in path.parts}

    def test_check_install_verify_repeat_uninstall_reinstall(self):
        self.run_installer("-CheckOnly")
        self.assertEqual(self.snapshot(), self.before)
        self.assertFalse((self.game / ".chaos-theory-thai").exists())
        self.run_installer()
        self.assertEqual((self.game / "System/dynamic-pc.umd").read_bytes(), self.modified)
        self.run_installer("-Verify")
        state = self.game / ".chaos-theory-thai/state.json"
        first = state.read_bytes()
        self.run_installer()
        self.assertEqual(state.read_bytes(), first)
        self.run_installer("-Uninstall")
        self.assertEqual(self.snapshot(), self.before)
        self.run_installer("-Uninstall")
        self.run_installer()
        self.assertNotEqual(json.loads(state.read_text(encoding="utf-8-sig"))["backup_id"],
                            json.loads(first.decode("utf-8-sig"))["backup_id"])
        self.run_installer("-Uninstall")
        self.assertEqual(self.snapshot(), self.before)

    def test_corrupt_package_rejected_without_game_changes(self):
        self.write_package("payload/font.pcx", b"corruption")
        self.run_installer(success=False)
        self.assertEqual(self.snapshot(), self.before)
        self.assertFalse((self.game / ".chaos-theory-thai").exists())

    def test_wrong_game_archive_rejected_without_changes(self):
        self.write_game("System/dynamic-pc.umd", b"different game build")
        before = self.snapshot()
        self.run_installer(success=False)
        self.assertEqual(self.snapshot(), before)
        self.assertFalse((self.game / ".chaos-theory-thai").exists())

    def test_corrupt_patch_rejected_before_game_writes(self):
        # Valid package hash, but illegal source copy range inside the patch.
        self.write_package("patches/game.ctpatch", b"CTPATCH1\x01" + struct.pack("<qI", 99999, 10) + b"\x00")
        self.refresh_manifest()
        self.run_installer(success=False)
        self.assertEqual(self.snapshot(), self.before)
        self.assertFalse((self.game / ".chaos-theory-thai/state.json").exists())

    def test_installed_edits_and_damaged_backup_are_preserved(self):
        self.run_installer()
        self.write_game("Data/System/Localization/new.int", b"user edit")
        changed = self.snapshot()
        self.run_installer("-Verify", success=False)
        self.run_installer("-Uninstall", success=False)
        self.assertEqual(self.snapshot(), changed)
        self.write_game("Data/System/Localization/new.int", b"Thai text")
        state = json.loads((self.game / ".chaos-theory-thai/state.json").read_text(encoding="utf-8-sig"))
        self.write_game(f'.chaos-theory-thai/{state["backup_id"]}/original/Data/Textures/Font/test.pcx', b"bad backup")
        installed = self.snapshot()
        self.run_installer("-Uninstall", success=False)
        self.assertEqual(self.snapshot(), installed)

    def test_manifest_path_traversal_rejected(self):
        self.manifest["files"][1]["path"] = "../outside.pcx"
        self.refresh_manifest()
        self.run_installer(success=False)
        self.assertEqual(self.snapshot(), self.before)
        self.assertFalse((self.root / "outside.pcx").exists())

    def test_language_in_wrong_section_is_rejected(self):
        self.write_game("System/SplinterCell3.ini", b"[Init]\nUseDynamicDataFile=true\nLanguage=int\n[Engine.Engine]\nLanguage=fra\n")
        before = self.snapshot()
        self.run_installer("-CheckOnly", success=False)
        self.assertEqual(self.snapshot(), before)

    def test_interrupted_install_restores_all_originals(self):
        self.run_installer()
        state_path = self.game / ".chaos-theory-thai/state.json"
        state = json.loads(state_path.read_text(encoding="utf-8-sig"))
        state["status"] = "prepared"
        state_path.write_text(json.dumps(state), encoding="utf-8")
        self.write_game("System/dynamic-pc.umd", b"interrupted partial write")
        self.run_installer(success=False)
        self.run_installer("-Uninstall")
        self.assertEqual(self.snapshot(), self.before)


if __name__ == "__main__":
    unittest.main()

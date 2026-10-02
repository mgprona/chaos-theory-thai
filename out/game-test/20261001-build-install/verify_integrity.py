"""Verify this build against the preserved source archive and installed files."""
from pathlib import Path
import argparse
import hashlib
import json
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from src.core.umd_parser import UMDArchive
from src.cli import STARTUP_IMAGE_NAMES


def sha256(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def main(output_name="integrity.json"):
    report = Path(__file__).resolve().parent
    config = json.loads((ROOT / "config.json").read_text(encoding="utf-8"))
    game = Path(config["game_dir"])
    dist = ROOT / "dist"
    source = UMDArchive(ROOT / "backups/dynamic-pc.umd")
    built = UMDArchive(dist / "System/dynamic-pc.umd")
    assert len(source.entries) == len(built.entries) == 20252
    assert built.archive_size == built.filepath.stat().st_size
    expected = {str(p.relative_to(dist / "loose")).lower(): p
                for p in (dist / "loose").rglob("*.int")}
    for p in (dist / "Data/Magma/DataPC/Fonts").glob("*"):
        if p.is_file():
            expected[str(p.relative_to(dist)).lower()] = p
    replacements = []
    preserved = 0
    with source.filepath.open("rb") as original, built.filepath.open("rb") as packed:
        for old, new in zip(source.entries, built.entries):
            assert (old.name, old.flags, old.is_unicode) == (new.name, new.flags, new.is_unicode)
            assert new.offset + new.size <= built.toc_offset
            original.seek(old.offset)
            packed.seek(new.offset)
            before, after = original.read(old.size), packed.read(new.size)
            if new.name.lower() in expected:
                assert after == expected[new.name.lower()].read_bytes(), new.name
                replacements.append({"path": new.name, "size": new.size,
                                     "sha256": hashlib.sha256(after).hexdigest(),
                                     "changed_from_original": before != after})
            else:
                assert before == after, new.name
                preserved += 1
    assert len(replacements) == len(expected) == 65
    files = [(built.filepath, game / "System/dynamic-pc.umd")]
    files.extend((p, game / p.relative_to(dist / "loose"))
                 for p in (dist / "loose").rglob("*.int"))
    files.extend((p, game / p.relative_to(dist))
                 for p in (dist / "Data/Textures/Font").glob("*.pcx"))
    files.extend((p, game / p.relative_to(dist))
                 for p in (dist / "Data/Magma/DataPC/Fonts").glob("*") if p.is_file())
    files.extend((dist / "System" / name, game / "System" / name)
                 for name in STARTUP_IMAGE_NAMES if (dist / "System" / name).is_file())
    installed = []
    for output, target in files:
        digest = sha256(output)
        assert digest == sha256(target), str(target)
        installed.append({"path": str(target.relative_to(game)),
                          "size": target.stat().st_size, "sha256": digest})
    pre = json.loads((report / "preinstall.json").read_text(encoding="utf-8"))
    assert sha256(game / "System/splintercell3.exe") == pre["executable_sha256"]
    assert sha256(source.filepath) == pre["umd_sha256"]
    result = {"result": "PASS", "umd_entries": len(built.entries),
              "replacement_assets_verified": len(replacements),
              "unchanged_payloads_verified": preserved,
              "installed_files_verified": len(installed),
              "built_umd_bytes": built.filepath.stat().st_size,
              "built_umd_sha256": sha256(built.filepath),
              "backup_umd_sha256": pre["umd_sha256"], "executable_unchanged": True,
              "replacements": replacements, "installed": installed}
    (report / output_name).write_text(json.dumps(result, indent=2), encoding="utf-8")
    print({key: value for key, value in result.items()
           if key not in ("replacements", "installed")})


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", default="integrity.json", help="Report JSON filename")
    main(parser.parse_args().output)

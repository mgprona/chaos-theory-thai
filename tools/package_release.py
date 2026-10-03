"""Build a validated end-user ZIP; never install or publish it.

The UMD delta references unchanged bytes in the player's original archive.
It reconstructs exactly the tested dist archive, including its footer.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import shutil
import struct
import subprocess
import sys
import zipfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.core.umd_parser import UMDArchive
from src.pipeline.validation import validate_localization_assets

BASE_SHA256 = "f42c884dcef45fea70489c213e31fd1176c3d84ce27265da6cd718a8414005af"
EXE_SHA256 = "54df25b238356024248085ca7fa6af9005b0be4ec40beef3c32faa8c06b6d4e5"
VERSION = "1.0.0-rc1"


def sha256(path: Path) -> str:
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def file_record(path: Path, root: Path) -> dict:
    return {"path": path.relative_to(root).as_posix(), "size": path.stat().st_size,
            "sha256": sha256(path)}


def translation_coverage() -> dict:
    total = nonblank = templates = 0
    for path in sorted((ROOT / "data/translations").glob("*/*.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        for section in data["sections"].values():
            for key, value in section.items():
                if key.startswith("_"):
                    continue
                if not isinstance(value, dict) or not isinstance(value.get("th"), str):
                    raise ValueError(f"Invalid translation: {path.name}/{key}")
                total += 1
                en, th = value.get("en", ""), value["th"]
                if str(en).strip():
                    if not th.strip():
                        raise ValueError(f"Missing translation: {path.name}/{key}")
                    nonblank += 1
                else:
                    if th != en:
                        raise ValueError(f"Changed blank template: {path.name}/{key}")
                    templates += 1
    return {"total": total, "translated_nonblank": nonblank, "blank_templates": templates}


def make_umd_delta(base: Path, target: Path, patch: Path, expected: dict[str, bytes]) -> dict:
    original, built = UMDArchive(base), UMDArchive(target)
    if len(original.entries) != len(built.entries):
        raise ValueError("UMD entry count changed")
    if built.archive_size != target.stat().st_size:
        raise ValueError("Invalid UMD footer size")
    expected = {name.lower().replace("/", "\\"): data for name, data in expected.items()}
    preserved = replacements = changed = 0
    seen = set()
    cursor = 0
    patch.parent.mkdir(parents=True, exist_ok=True)
    with base.open("rb") as source, target.open("rb") as output, patch.open("wb") as delta:
        delta.write(b"CTPATCH1")
        for old, new in zip(original.entries, built.entries):
            if (old.name, old.flags, old.is_unicode) != (new.name, new.flags, new.is_unicode):
                raise ValueError(f"UMD metadata changed: {new.name}")
            if new.offset < cursor or new.offset + new.size > built.toc_offset:
                raise ValueError(f"Invalid UMD bounds: {new.name}")
            output.seek(cursor)
            padding = output.read(new.offset - cursor)
            if padding:
                if any(padding):
                    raise ValueError("Nonzero UMD alignment padding")
                delta.write(b"\x03" + struct.pack("<I", len(padding)))
            source.seek(old.offset)
            output.seek(new.offset)
            before, after = source.read(old.size), output.read(new.size)
            name = new.name.lower().replace("/", "\\")
            if name in expected:
                if after != expected[name]:
                    raise ValueError(f"Stale built UMD payload: {new.name}")
                replacements += 1
                seen.add(name)
            elif before != after:
                raise ValueError(f"Unrelated UMD payload changed: {new.name}")
            else:
                preserved += 1
            if before == after:
                delta.write(b"\x01" + struct.pack("<qI", old.offset, old.size))
            else:
                delta.write(b"\x02" + struct.pack("<I", len(after)) + after)
                changed += 1
            cursor = new.offset + new.size
        if seen != set(expected):
            raise ValueError(f"Replacements missing from UMD: {set(expected) - seen}")
        output.seek(cursor)
        tail = output.read()
        delta.write(b"\x02" + struct.pack("<I", len(tail)) + tail + b"\x00")
    return {"entries": len(built.entries), "replacements_verified": replacements,
            "unchanged_nonreplacement_payloads": preserved, "changed_payloads": changed}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / "out/releases")
    args = parser.parse_args()
    dist = ROOT / "dist"
    base = ROOT / "backups/dynamic-pc.umd"
    if sha256(base) != BASE_SHA256:
        raise ValueError("Pristine Steam UMD hash mismatch")
    coverage = translation_coverage()
    compiled = {p.relative_to(dist / "loose").as_posix().replace("/", "\\"): p.read_bytes()
                for p in (dist / "loose").rglob("*.int")}
    font_dir = dist / "Data/Magma/DataPC/Fonts"
    fonts = {p.relative_to(dist).as_posix().replace("/", "\\"): p.read_bytes()
             for p in font_dir.iterdir() if p.is_file()}
    validation = validate_localization_assets(compiled, fonts, ROOT / "config.json")
    args.output.mkdir(parents=True, exist_ok=True)
    # Unique staging directory: previous releases and ZIPs are preserved.
    import tempfile
    stage = Path(tempfile.mkdtemp(prefix="package-", dir=args.output))
    name = f"ChaosTheory-Thai-{VERSION}"
    package = stage / name
    package.mkdir()
    for path in (ROOT / "release").rglob("*"):
        if path.is_file():
            destination = package / path.relative_to(ROOT / "release")
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, destination)
    output_files = [(p, p.relative_to(dist / "loose")) for p in (dist / "loose").rglob("*.int")]
    output_files.extend((p, p.relative_to(dist)) for p in font_dir.iterdir() if p.is_file())
    output_files.extend((p, p.relative_to(dist)) for p in (dist / "Data/Textures/Font").glob("*.pcx"))
    output_files.extend((dist / "System" / n, Path("System") / n)
                        for n in ("splintercell3logo.bmp", "SplinterCell3Logo.tga"))
    installed = []
    for path, relative in sorted(output_files, key=lambda pair: pair[1].as_posix()):
        destination = package / "payload" / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, destination)
        record = {"path": relative.as_posix(), "size": path.stat().st_size, "sha256": sha256(path)}
        record["payload"] = "payload/" + relative.as_posix()
        installed.append(record)
    umd = dist / "System/dynamic-pc.umd"
    integrity = make_umd_delta(base, umd, package / "patches/dynamic-pc.ctpatch", {**compiled, **fonts})
    installed.append({"path": "System/dynamic-pc.umd", "size": umd.stat().st_size,
                      "sha256": sha256(umd), "patch": "patches/dynamic-pc.ctpatch"})
    manifest = {"format": 1, "version": VERSION, "game": "Splinter Cell Chaos Theory PC Steam 1.05",
                "steam_build_id": "252084", "base_umd_sha256": BASE_SHA256,
                "executable_sha256": EXE_SHA256, "coverage": coverage,
                "validation": validation, "archive_integrity": integrity,
                "source_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
                "source_translation_sha256": {p.relative_to(ROOT).as_posix(): sha256(p)
                                              for p in sorted((ROOT / "data/translations").glob("*/*.json"))},
                "files": installed, "package_files": [file_record(p, package)
                    for p in sorted(package.rglob("*")) if p.is_file()]}
    (package / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    archive = args.output / (name + ".zip")
    if archive.exists():
        raise FileExistsError(f"Preserving existing release: {archive}. Choose another --output directory.")
    with zipfile.ZipFile(archive, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as zipped:
        for path in sorted(package.rglob("*")):
            if path.is_file():
                zipped.write(path, path.relative_to(stage).as_posix())
    with zipfile.ZipFile(archive) as zipped:
        if zipped.testzip() is not None:
            raise ValueError("ZIP CRC check failed")
    checksum = f"{sha256(archive)}  {archive.name}\n"
    archive.with_suffix(".zip.sha256").write_text(checksum, encoding="ascii")
    print(json.dumps({"zip": str(archive), "bytes": archive.stat().st_size,
                      "package": str(package), "coverage": coverage, "validation": validation,
                      "integrity": integrity, "installed_files": len(installed)}, indent=2))


if __name__ == "__main__":
    main()

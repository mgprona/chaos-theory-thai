"""Validation script for every translated story mission.

For each ``data/translations/story/*.json`` the script checks that

* every key has a Thai value (whitespace-only templates stay verbatim),
* values carry no curly quotes or ellipsis and are CP874 encodable,
* leading/trailing spaces mirror the English source,
* the key count matches ``_meta.total_strings``,

and then round-trips every compiled ``.int`` file in ``dist/loose`` back to the
Thai source, decoding PUA where the renderer uses UTF-16.
"""

from __future__ import annotations

import json
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
from src.core.ini_codec import IniDocument
from src.core.thai_shaper import create_ui_shaper, uses_unicode_pua

FORBIDDEN = {"\u201c", "\u201d", "\u2018", "\u2019", "\u2026"}


def validate_sources(story_dir: Path) -> dict[str, Path]:
    """Validate every story JSON and return the required compiled stems."""
    stems: dict[str, Path] = {}
    files = sorted(story_dir.glob("*.json"))
    assert files, f"No story translations found in {story_dir}"

    total = 0
    for filepath in files:
        data = json.loads(filepath.read_text(encoding="utf-8"))
        expected = data.get("_meta", {}).get("total_strings")
        count = 0
        for sec_name, sec_data in data["sections"].items():
            stems[sec_data["_source"].lower()] = filepath
            for key, val in sec_data.items():
                if key.startswith("_"):
                    continue
                count += 1
                assert isinstance(val, dict), f"Entry [{sec_name}][{key}] is not dict"
                th = val.get("th")
                en = val.get("en", "")
                location = f"{filepath.name} [{sec_name}][{key}]"
                assert th is not None, f"Missing th in {location}"
                if en.strip():
                    assert str(th).strip() != "", f"Empty th in {location}"
                else:
                    assert th == en, f"Template changed in {location}: {en!r} != {th!r}"

                for char in FORBIDDEN:
                    assert char not in th, f"Forbidden character {char} in {location}: {th}"

                for byte in th.encode("cp874"):
                    assert byte < 128 or 161 <= byte <= 251, (
                        f"Byte {byte} outside CP874 in {location}: {th}"
                    )

                assert (len(en) - len(en.lstrip(" "))) == (len(th) - len(th.lstrip(" "))), (
                    f"Leading space mismatch in {location}"
                )
                assert (len(en) - len(en.rstrip(" "))) == (len(th) - len(th.rstrip(" "))), (
                    f"Trailing space mismatch in {location}"
                )

        if expected is not None:
            assert count == expected, f"{filepath.name}: expected {expected}, got {count}"
        total += count
        print(f"[VALIDATE] {filepath.name}: {count} strings valid & CP874 clean.")

    print(f"[VALIDATE] story sources: {len(files)} files, {total} strings")
    return stems


def compiled_files(int_dir: Path) -> dict[str, Path]:
    """Map lower-case stems to their on-disk ``.int`` files."""
    return {path.stem.lower(): path for path in sorted(int_dir.glob("*.int"))}


def validate_compiled(stems: dict[str, Path], config: dict, shaper, int_dir: Path) -> dict:
    available = compiled_files(int_dir)
    documents = {}

    missing = sorted(stem for stem in stems if stem not in available)
    assert not missing, f"Compiled localization missing for: {missing}"

    for stem in sorted(stems):
        path = available[stem]
        raw = path.read_bytes()
        if uses_unicode_pua(config, path.stem):
            assert raw.startswith(b"\xff\xfe"), f"UTF-16 BOM missing: {path.name}"
            decoded = shaper.decode(raw.decode("utf-16"))
            mode = "UTF-16/PUA"
        else:
            decoded = raw.decode("cp874")
            mode = "CP874"
        assert decoded, f"Empty compiled file: {path.name}"
        documents[stem] = IniDocument.from_bytes(raw, default_encoding="cp874")
        print(f"[VALIDATE] Compiled {path.name}: {len(raw)} bytes, decoded {mode} successfully.")
    return documents


def validate_round_trip(story_dir: Path, documents: dict, config: dict, shaper) -> None:
    for filepath in sorted(story_dir.glob("*.json")):
        data = json.loads(filepath.read_text(encoding="utf-8"))
        for section_name, section in data["sections"].items():
            stem = section["_source"].lower()
            compiled_section = documents[stem].get_section(section_name)
            assert compiled_section is not None, (stem, section_name)
            for key, value in section.items():
                if not isinstance(value, dict):
                    continue
                actual = compiled_section.get(key)
                assert actual is not None, (stem, section_name, key)
                if uses_unicode_pua(config, stem):
                    actual = shaper.decode(actual)
                assert actual == value["th"], (stem, section_name, key)
        print(f"[VALIDATE] {filepath.name}: every compiled value round-trips to its Thai source.")


def validate_all() -> None:
    config = json.loads((PROJECT_ROOT / "config.json").read_text(encoding="utf-8"))
    story_dir = PROJECT_ROOT / "data" / "translations" / "story"
    int_dir = PROJECT_ROOT / "dist" / "loose" / "Data" / "System" / "Localization"

    stems = validate_sources(story_dir)
    shaper = create_ui_shaper()
    documents = validate_compiled(stems, config, shaper, int_dir)
    validate_round_trip(story_dir, documents, config, shaper)


if __name__ == "__main__":
    validate_all()
    print("[VALIDATE] ALL CHECKS PASSED PERFECTLY!")

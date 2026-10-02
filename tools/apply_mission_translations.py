"""Shared applier and validator for story mission translations.

Each mission ships a data module ``tools/translations_<name>.py`` holding a
``TRANSLATIONS[section][key] = "Thai"`` mapping and calls
``apply_translations("<mission>.json", TRANSLATIONS)``.

The applier refuses to write unless the data matches the JSON one-to-one and
every value passes the project rules: non-empty, CP874 encodable, no curly
quotes or ellipsis, and leading/trailing whitespace identical to the English
source (whitespace-only templates must be kept verbatim).
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
STORY_DIR = PROJECT_ROOT / "data" / "translations" / "story"

FORBIDDEN = ("\u201c", "\u201d", "\u2018", "\u2019", "\u2026")


def story_files() -> list[Path]:
    return sorted(STORY_DIR.glob("*.json"))


def pending_report() -> tuple[int, int, list[tuple[str, int, int]]]:
    """Return (translated, total, per-file rows with remaining strings)."""
    translated = total = 0
    rows = []
    for path in story_files():
        data = json.loads(path.read_text(encoding="utf-8"))
        file_total = file_done = 0
        for section in data.get("sections", {}).values():
            for key, value in section.items():
                if key.startswith("_"):
                    continue
                file_total += 1
                en_text = str(value.get("en") or "")
                th_text = str(value.get("th") or "")
                # Whitespace-only templates need no translation: count as satisfied.
                if th_text.strip() or not en_text.strip():
                    file_done += 1
        translated += file_done
        total += file_total
        if file_done < file_total:
            rows.append((path.stem, file_done, file_total))
    return translated, total, rows


def apply_translations(
    mission_filename: str, translations: dict[str, dict[str, str]], write: bool = True
) -> bool:
    target = STORY_DIR / mission_filename
    if not target.is_file():
        print(f"Mission file not found: {target}")
        return False

    data = json.loads(target.read_text(encoding="utf-8"))
    sections = data["sections"]
    errors: list[str] = []
    total_keys = 0
    applied = 0

    for section_name, section in sections.items():
        if section_name not in translations:
            errors.append(f"Missing section in TRANSLATIONS: {section_name}")
            continue
        planned = translations[section_name]
        for key, value in section.items():
            if key.startswith("_"):
                continue
            total_keys += 1
            if key not in planned:
                errors.append(f"Missing key in TRANSLATIONS: [{section_name}][{key}]")
                continue

            th = planned[key]
            en = value.get("en", "")
            location = f"[{section_name}][{key}]"

            if not en.strip():
                # Whitespace-only template: keep it byte-for-byte.
                if th != en:
                    errors.append(f"Template must stay verbatim: {location} {en!r} != {th!r}")
            elif not th.strip():
                errors.append(f"Empty translation: {location}")

            for char in FORBIDDEN:
                if char in th:
                    errors.append(f"Forbidden character in {location}: {th}")

            try:
                for byte in th.encode("cp874"):
                    if not (byte < 128 or 161 <= byte <= 251):
                        errors.append(f"Byte {byte} outside CP874 in {location}: {th}")
            except UnicodeEncodeError as error:
                errors.append(f"CP874 encode error in {location}: {error}")

            if (len(en) - len(en.lstrip(" "))) != (len(th) - len(th.lstrip(" "))):
                errors.append(f"Leading space mismatch in {location}")
            if (len(en) - len(en.rstrip(" "))) != (len(th) - len(th.rstrip(" "))):
                errors.append(f"Trailing space mismatch in {location}")

            value["th"] = th
            applied += 1

    for section_name, planned in translations.items():
        if section_name not in sections:
            errors.append(f"Extra section in TRANSLATIONS: {section_name}")
            continue
        for key in planned:
            if key not in sections[section_name]:
                errors.append(f"Extra key in TRANSLATIONS: [{section_name}][{key}]")

    expected = data.get("_meta", {}).get("total_strings")
    if expected is not None and total_keys != expected:
        errors.append(f"String count {total_keys} != _meta.total_strings {expected}")

    if errors:
        print(f"FAILED {mission_filename} with {len(errors)} error(s):")
        for error in errors[:40]:
            print(f"  - {error}")
        if len(errors) > 40:
            print(f"  ... +{len(errors) - 40} more")
        return False

    if write:
        with open(target, "w", encoding="utf-8") as handle:
            json.dump(data, handle, ensure_ascii=False, indent=2)
            handle.write("\n")

    translated, total, rows = pending_report()
    print(
        f"OK {mission_filename}: {applied}/{total_keys} strings"
        f"{' written' if write else ' (dry run)'}"
    )
    print(f"   story progress: {translated}/{total} ({100.0 * translated / total:.2f}%)")
    if rows:
        print("   remaining: " + ", ".join(f"{n} ({d}/{t})" for n, d, t in rows))
    else:
        print("   remaining: none — every story mission is translated")
    return True


def main() -> int:
    if len(sys.argv) < 2:
        translated, total, rows = pending_report()
        print(f"story progress: {translated}/{total} ({100.0 * translated / total:.2f}%)")
        for name, done, file_total in rows:
            print(f"  {name:28} {done:4}/{file_total:<4} missing {file_total - done}")
        return 0
    print("Use a mission data module instead, e.g. tools/translations_chembunker.py")
    return 1


if __name__ == "__main__":
    sys.exit(main())

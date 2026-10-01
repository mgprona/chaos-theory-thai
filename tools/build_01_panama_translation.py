"""Master builder to compile and apply 01_Panama.json translations (168 strings).

Mirrors tools/build_01_lighthouse_translation.py: the translation dictionaries in
tools/translations_panama_part{1,2,3}.py are the single source of truth, and this
script validates them before writing data/translations/story/01_Panama.json.

Validation gates (same bar as 00_Training / 01_Lighthouse / 02_CargoShip):
- every JSON key has exactly one translation, and no extra keys are defined
- no forbidden characters (“ ” ‘ ’ …)
- every value is CP874-encodable and every byte is < 128 or 161..251
- leading/trailing spaces of each value match its English source exactly
"""

from __future__ import annotations
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from tools.translations_panama_part1 import (
    GENERAL,
    COMPUTER,
    EMAIL,
    OBJECTIVES,
    COMMUNICATIONS,
)
from tools.translations_panama_part2 import (
    ALARM_SYSTEM,
    LOCKER_ROOM,
    MEETING_ROOM,
    OUTSIDE,
    SECURITY_ROOM_01,
)
from tools.translations_panama_part3 import (
    SOCCER_GAME,
    TALKING_TO_SECURITY_CHIEF,
    THE_VP,
    THIRD_FLOOR_SECURITY,
    VP_OFFICE,
)

TARGET_PATH = PROJECT_ROOT / "data" / "translations" / "story" / "01_Panama.json"

SECTION_MAP = {
    "GENERAL": GENERAL,
    "Computer": COMPUTER,
    "Email": EMAIL,
    "P_01_Panama_AlarmSystem": ALARM_SYSTEM,
    "P_01_Panama_Communications": COMMUNICATIONS,
    "P_01_Panama_LockerRoom": LOCKER_ROOM,
    "P_01_Panama_MeetingRoom": MEETING_ROOM,
    "P_01_Panama_Objectives": OBJECTIVES,
    "P_01_Panama_Outside": OUTSIDE,
    "P_01_Panama_SecurityRoom01": SECURITY_ROOM_01,
    "P_01_Panama_SoccerGame": SOCCER_GAME,
    # Official in-game typo: the section really is spelled "PAnama". Do not "fix" it.
    "P_01_PAnama_TalkingToSecurityChief": TALKING_TO_SECURITY_CHIEF,
    "P_01_Panama_TheVP": THE_VP,
    "P_01_Panama_ThirdFloorSecurity": THIRD_FLOOR_SECURITY,
    "P_01_Panama_VPOffice": VP_OFFICE,
}

FORBIDDEN_CHARS = {"“", "”", "‘", "’", "…"}


def _edge_spaces(text: str) -> tuple[int, int]:
    return len(text) - len(text.lstrip(" ")), len(text) - len(text.rstrip(" "))


def apply_panama_translations() -> None:
    with open(TARGET_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    sections = data["sections"]
    errors: list[str] = []
    missing: list[str] = []
    extra: list[str] = []
    translated = 0
    padded = 0

    unknown = set(sections) - set(SECTION_MAP)
    for sec_name in unknown:
        errors.append(f"Section {sec_name} exists in JSON but has no translation dict")

    for sec_name, trans_dict in SECTION_MAP.items():
        if sec_name not in sections:
            errors.append(f"Section {sec_name} not found in JSON!")
            continue
        sec = sections[sec_name]
        json_keys = [k for k in sec if k != "_source"]

        for key in json_keys:
            if key not in trans_dict:
                missing.append(f"[{sec_name}] {key}: {sec.get(key, {}).get('en', '')}")
        for key in trans_dict:
            if key not in json_keys:
                extra.append(f"[{sec_name}] {key}")

        for key in json_keys:
            if key not in trans_dict:
                continue
            en_val = sec[key].get("en", "")
            th_val = str(trans_dict[key])

            for fc in FORBIDDEN_CHARS:
                if fc in th_val:
                    errors.append(f"Forbidden character {fc!r} in [{sec_name}][{key}]")

            try:
                raw = th_val.encode("cp874")
            except UnicodeEncodeError as exc:
                errors.append(f"CP874 encode error in [{sec_name}][{key}]: {exc}")
                continue
            for b in raw:
                if not (b < 128 or (161 <= b <= 251)):
                    errors.append(
                        f"CP874 byte out of range: {b} in [{sec_name}][{key}]: {th_val}"
                    )

            en_lead, en_trail = _edge_spaces(en_val)
            th_lead, th_trail = _edge_spaces(th_val)
            if (en_lead, en_trail) != (th_lead, th_trail):
                th_val = (" " * en_lead) + th_val.strip(" ") + (" " * en_trail)
                padded += 1

            sec[key]["th"] = th_val
            translated += 1

    print(f"Total translated: {translated} / {data['_meta']['total_strings']}")
    print(f"Whitespace padded to match en: {padded}")

    if missing:
        print(f"ERROR: {len(missing)} missing keys:")
        for line in missing:
            print(f"  {line}")
    if extra:
        print(f"ERROR: {len(extra)} unknown keys defined:")
        for line in extra:
            print(f"  {line}")
    if errors:
        print(f"ERROR: {len(errors)} validation errors:")
        for line in errors[:20]:
            print(f"  {line}")
    if missing or extra or errors:
        raise SystemExit(1)

    if translated != data["_meta"]["total_strings"]:
        raise SystemExit(
            f"Count mismatch: translated {translated}, meta says {data['_meta']['total_strings']}"
        )

    with open(TARGET_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"Saved {TARGET_PATH} successfully!")


if __name__ == "__main__":
    apply_panama_translations()

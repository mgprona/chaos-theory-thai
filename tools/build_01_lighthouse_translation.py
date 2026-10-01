"""Master builder to compile and apply 01_Lighthouse.json translations (381 strings)."""

from __future__ import annotations
import json
import re
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from tools.translations_01_part1 import (
    GENERAL,
    INTERACTION,
    COMPUTER,
    EMAIL,
    CAVE_GUARDS,
    MARIA_NARCISSA,
    MORGENHOLT,
    NO_LACERDA,
    RAIN_PATROL,
    WEATHER,
    WELDER_TECH,
    MASTER,
    OBJECTIVES,
    SRC_ABOUT_GIRL,
    SRC_ASTRONAUTS,
    SRC_SOCCER_PLAYER,
)
from tools.translations_01_part2 import (
    COMMUNICATIONS,
)
from tools.translations_01_part3 import (
    INT_CAPTAIN,
    INT_CAVE_GUARD,
    INT_HIGH_TECH_GUN,
    INT_RADIO_ROOM,
    INT_THUNDER,
    INT_TORTURE,
    INT_TORTURE_GUARD,
    INT_WELDER_TECH,
)

SECTION_MAP = {
    "GENERAL": GENERAL,
    "Interaction": INTERACTION,
    "Computer": COMPUTER,
    "Email": EMAIL,
    "P_01_Lighthouse_CnvCaveGuards": CAVE_GUARDS,
    "P_01_Lighthouse_CnvMariaNarcissa": MARIA_NARCISSA,
    "P_01_Lighthouse_CnvMorgenholt": MORGENHOLT,
    "P_01_Lighthouse_CnvNoLacerda": NO_LACERDA,
    "P_01_Lighthouse_CnvRainPatrol": RAIN_PATROL,
    "P_01_Lighthouse_CnvWeather": WEATHER,
    "P_01_Lighthouse_CnvWelderTech": WELDER_TECH,
    "P_01_Lighthouse_Master": MASTER,
    "P_01_Lighthouse_Objectives": OBJECTIVES,
    "P_01_Lighthouse_SRCAboutGirl": SRC_ABOUT_GIRL,
    "P_01_Lighthouse_SRCAstronauts": SRC_ASTRONAUTS,
    "P_01_Lighthouse_SRCSoccerPlayer": SRC_SOCCER_PLAYER,
    "P_01_Lighthouse_Communications": COMMUNICATIONS,
    "P_01_Lighthouse_IntCaptain": INT_CAPTAIN,
    "P_01_Lighthouse_IntCaveGuard": INT_CAVE_GUARD,
    "P_01_Lighthouse_IntHighTechGun": INT_HIGH_TECH_GUN,
    "P_01_Lighthouse_IntRadioRoom": INT_RADIO_ROOM,
    "P_01_Lighthouse_IntThunder": INT_THUNDER,
    "P_01_Lighthouse_IntTorture": INT_TORTURE,
    "P_01_Lighthouse_IntTortureGuard": INT_TORTURE_GUARD,
    "P_01_Lighthouse_IntWelderTech": INT_WELDER_TECH,
}

FORBIDDEN_CHARS = {"“", "”", "‘", "’", "…"}

def apply_lighthouse_translations():
    target_path = PROJECT_ROOT / "data" / "translations" / "story" / "01_Lighthouse.json"
    with open(target_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    sections = data["sections"]
    translated_count = 0
    missing_keys = []
    errors = []

    for sec_name, trans_dict in SECTION_MAP.items():
        if sec_name not in sections:
            errors.append(f"Section {sec_name} not found in JSON!")
            continue
        sec = sections[sec_name]
        for k, v in sec.items():
            if k == "_source":
                continue
            if k not in trans_dict:
                missing_keys.append((sec_name, k, v.get("en", "")))
                continue

            th_val = trans_dict[k]
            # Verify no forbidden characters
            for fc in FORBIDDEN_CHARS:
                if fc in th_val:
                    errors.append(f"Forbidden character {fc} in [{sec_name}][{k}]: {th_val}")

            # Verify CP874 encodable
            try:
                raw = th_val.encode("cp874")
                for b in raw:
                    if not (b < 128 or (161 <= b <= 251)):
                        errors.append(f"CP874 byte out of range: {b} in [{sec_name}][{k}]: {th_val}")
            except UnicodeEncodeError as e:
                errors.append(f"CP874 encode error in [{sec_name}][{k}]: {e}")

            # Verify whitespace preservation
            en_val = v.get("en", "")
            # Leading spaces
            en_leading = len(en_val) - len(en_val.lstrip(' '))
            th_leading = len(th_val) - len(th_val.lstrip(' '))
            if en_leading != th_leading:
                # adjust leading spaces
                th_val = (' ' * en_leading) + th_val.lstrip(' ')

            # Trailing spaces
            en_trailing = len(en_val) - len(en_val.rstrip(' '))
            th_trailing = len(th_val) - len(th_val.rstrip(' '))
            if en_trailing != th_trailing:
                # adjust trailing spaces
                th_val = th_val.rstrip(' ') + (' ' * en_trailing)

            v["th"] = th_val
            translated_count += 1

    print(f"Total translated: {translated_count} / {data['_meta']['total_strings']}")
    if missing_keys:
        print(f"ERROR: {len(missing_keys)} missing keys:")
        for sec_name, k, en in missing_keys:
            print(f"  [{sec_name}] {k}: {en}")
        raise ValueError(f"Missing {len(missing_keys)} keys in 01_Lighthouse.json")

    if errors:
        print(f"ERROR: {len(errors)} validation errors:")
        for err in errors[:10]:
            print(f"  {err}")
        raise ValueError(f"{len(errors)} errors found in 01_Lighthouse.json")

    # Save file
    with open(target_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"Saved {target_path} successfully!")

if __name__ == "__main__":
    apply_lighthouse_translations()

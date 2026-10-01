"""Master builder to compile and apply 00_Training.json translations."""

from __future__ import annotations
import json
import re
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from tools.translations_00_part1 import (
    VIDEO_NAMES,
    VIDEO_DESCRIPTIONS,
    BROADCAST,
    OBJECTIVES,
    COMMUNICATIONS,
    PAUL,
    JASON,
    HANTZ,
    FALKO,
    MATHIEU,
)
from tools.translations_00_part2 import (
    PHIL,
    SEBASTIEN,
    PARTRIDGE,
    REDDING,
)
from tools.translations_00_part3 import (
    POPUPS,
)

PROJECT_ROOT = Path(__file__).resolve().parent.parent

SECTION_MAP = {
    "P_00_Training_Broadcast": BROADCAST,
    "P_00_Training_Objectives": OBJECTIVES,
    "P_00_Training_Communications": COMMUNICATIONS,
    "P_00_Training_CnvUSSol_Paul": PAUL,
    "P_00_Training_CnvUSSol_Jason": JASON,
    "P_00_Training_CnvOff_Hantz": HANTZ,
    "P_00_Training_CnvOff_Falko": FALKO,
    "P_00_Training_CnvTech_Mathieu": MATHIEU,
    "P_00_Training_CnvUSSol_Phil": PHIL,
    "P_00_Training_CnvCook_Sebastien": SEBASTIEN,
    "P_00_Training_CnvPartridge": PARTRIDGE,
    "P_00_Training_CnvRedding": REDDING,
    "P_00_Training_Popup": POPUPS,
}

FORBIDDEN_CHARS = {"“", "”", "‘", "’", "…"}

def apply_training_translations():
    target_path = PROJECT_ROOT / "data" / "translations" / "story" / "00_Training.json"
    with open(target_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    sections = data["sections"]
    translated_count = 0
    missing_keys = []
    errors = []

    # 1. Apply video sections
    for sec_name, name_th in VIDEO_NAMES.items():
        if sec_name in sections:
            sec = sections[sec_name]
            # Name
            if "Name" in sec:
                sec["Name"]["th"] = name_th
                translated_count += 1
            # Descriptions
            for desc_k, desc_th in VIDEO_DESCRIPTIONS.items():
                if desc_k in sec:
                    sec[desc_k]["th"] = desc_th
                    translated_count += 1

    # 2. Apply dialogue and popup sections
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
        raise ValueError(f"Missing {len(missing_keys)} keys in 00_Training.json")

    if errors:
        print(f"ERROR: {len(errors)} validation errors:")
        for err in errors[:10]:
            print(f"  {err}")
        raise ValueError(f"{len(errors)} errors found in 00_Training.json")

    # Save file
    with open(target_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"Saved {target_path} successfully!")

if __name__ == "__main__":
    apply_training_translations()

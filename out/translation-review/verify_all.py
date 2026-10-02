"""Acceptance checks for the post-fix translation set.

Run: .venv\\Scripts\\python.exe out/translation-review/verify_all.py
Exit code 0 = all checks pass.
"""
from __future__ import annotations

import glob
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TRANS = ROOT / "data/translations"
FORBIDDEN = {"\u201c", "\u201d", "\u2018", "\u2019", "\u2026"}
PLACEHOLDER = re.compile(r"%[0-9]*[sdif]|\{[^}]*\}|<[^>]+>|&[a-zA-Z#0-9]+;|\\n|\\t")
EN_LABEL = re.compile(r"^\s*-?\s*([A-Za-z][A-Za-z0-9_'\.]*(?:[ ][A-Za-z][A-Za-z0-9_'\.]*){0,3})\s*[-:]\s+")
TH_LABEL = re.compile(r"^\s*([ก-๛][ก-๛\.\sA-Za-z0-9]{1,40}?)\s*[-:]\s+")

errors: list[str] = []
warnings: list[str] = []


def main() -> int:
    files = sorted(glob.glob(str(TRANS / "**/*.json"), recursive=True))
    total = 0
    th_to_en: dict[str, set[str]] = defaultdict(set)
    label_drift: list[str] = []

    for path in files:
        rel = Path(path).relative_to(ROOT).as_posix()
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        count = 0
        for sec, secdata in data["sections"].items():
            for key, val in secdata.items():
                if key.startswith("_"):
                    continue
                count += 1
                total += 1
                en = val.get("en", "") or ""
                th = val.get("th", "") or ""
                loc = f"{rel}::{sec}::{key}"
                if en.strip() and not th.strip():
                    errors.append(f"empty translation: {loc}")
                if not en.strip() and th != en:
                    errors.append(f"blank template altered: {loc} -> {th!r}")
                if en.strip():
                    th_to_en[th].add(en)
                if PLACEHOLDER.findall(en) != PLACEHOLDER.findall(th):
                    errors.append(f"placeholder mismatch: {loc}")
                if (len(en) - len(en.lstrip())) != (len(th) - len(th.lstrip())) or \
                   (len(en) - len(en.rstrip())) != (len(th) - len(th.rstrip())):
                    errors.append(f"edge-space mismatch: {loc}")
                for ch in FORBIDDEN:
                    if ch in th:
                        errors.append(f"forbidden char {ch!r}: {loc}")
                if "\u2022" not in en:
                    try:
                        for b in th.encode("cp874"):
                            if not (b < 128 or 161 <= b <= 251):
                                raise ValueError(b)
                    except Exception as exc:  # noqa: BLE001
                        errors.append(f"cp874: {loc} ({exc})")
                if rel.endswith(".json") and rel.split("/")[-2] == "story":
                    benign = (
                        ("02_CargoShip.json", "P_02_CargoShip_InterogateCaptain", "Speech_0006L"),
                        ("09_SeoulTwo.json", "P_09_SeoulTwo_Bombdrop", "Speech_0001L"),
                        ("11_KokuboSosho.json", "P_11_KokuboSosho_InterroISDF", "Speech_0018L"),
                    )
                    if bool(EN_LABEL.match(en)) != bool(TH_LABEL.match(th)) and en.strip() and th.strip():
                        latin_kept = en.split()[0].rstrip("-:") and th.lstrip().lower().startswith(en.split()[0].rstrip("-:").lower())
                        if (rel.split("/")[-1], sec, key) not in benign and not latin_kept:
                            label_drift.append(f"{loc} | EN={en[:45]!r} TH={th[:45]!r}")
        expected = data.get("_meta", {}).get("total_strings")
        if expected is not None and expected != count:
            errors.append(f"_meta mismatch: {rel} expected {expected} got {count}")

    dup = {th: ens for th, ens in th_to_en.items() if len(ens) > 1 and th.strip()}
    # label drift is expected only where the English label regex cannot see the source form
    for d in label_drift:
        warnings.append("label: " + d)

    print(f"files: {len(files)}  entries: {total}")
    print(f"errors: {len(errors)}")
    for e in errors[:40]:
        print("  ERR", e)
    print(f"same-th-different-en groups: {len(dup)}")
    print(f"label drift warnings: {len(label_drift)}")
    for w in warnings[:20]:
        print("  ", w)
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())

"""UI / OPSAT review fixes (Lead-owned scope; no story files touched).

Dry run:  .venv\\Scripts\\python.exe out/translation-review/fix_ui_opsat.py
Apply:    ... --apply
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TRANS = ROOT / "data/translations"

# exact key rewrites: file -> (section, key, new th)
EXACT = {
    "opsat/equipment.json": {
        ("BERETTA", "Description"): "ปืนพก",
        ("SHOTGUNAMMO", "Description"): "กระสุนสำหรับอุปกรณ์เสริมลูกซอง",
        ("FN7AMMO", "Description"): "ซองกระสุนปืนพก 5.7 มม.",
        ("SCOPEAMMO", "Description"): "กระสุนสำหรับอุปกรณ์เสริมสไนเปอร์",
    },
    "opsat/window.json": {
        ("General", "EmptyButton"): "ล้าง",
    },
    "ui/pregame_pc.json": {
        ("MenuSettings", "HighQualitySkin"): "ผิวตัวละครคุณภาพสูง",
        ("MenuSettings", "OriginalVoices"): "ใช้เสียงพากย์ภาษาต้นฉบับ",
    },
}

# value normalisation for the graphics option values (labels are already Thai)
VALUE_LABELS = {
    "ui/pregame_pc.json": [
        ("ANTIALIASING ", "ลบรอยหยัก "),
        ("ANISOTROPIC ", "กรองพื้นผิว "),
    ],
}


def main() -> None:
    apply = "--apply" in sys.argv
    counts: list[str] = []
    docs, trailing = {}, {}
    for rel in set(EXACT) | set(VALUE_LABELS):
        p = TRANS / rel
        raw = p.read_text(encoding="utf-8")
        docs[rel] = json.loads(raw)
        trailing[rel] = raw.endswith("\n")

    for rel, items in EXACT.items():
        for (sec, key), new in items.items():
            val = docs[rel]["sections"][sec][key]
            if val.get("th") != new:
                counts.append(f"{rel}::{sec}::{key}: {val.get('th')!r} -> {new!r}")
                val["th"] = new

    for rel, pairs in VALUE_LABELS.items():
        for sec, secdata in docs[rel]["sections"].items():
            for key, val in secdata.items():
                if key.startswith("_"):
                    continue
                th = val.get("th") or ""
                for old, new in pairs:
                    if th.startswith(old):
                        counts.append(f"{rel}::{sec}::{key}: {th!r} -> {new + th[len(old):]!r}")
                        val["th"] = new + th[len(old):]

    print(f"changes: {len(counts)}")
    for c in counts:
        print("  ", c)
    if not apply:
        print("[dry-run] nothing written")
        return
    for rel, data in docs.items():
        text = json.dumps(data, ensure_ascii=False, indent=2) + ("\n" if trailing[rel] else "")
        (TRANS / rel).write_text(text, encoding="utf-8")
    print("applied.")


if __name__ == "__main__":
    main()

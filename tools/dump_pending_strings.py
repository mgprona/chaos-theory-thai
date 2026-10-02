"""Dump the untranslated strings of one story mission for translation work.

Usage: python tools/dump_pending_strings.py 03_ChemBunker
Writes out/_dump_<mission>.txt and prints the path.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
STORY_DIR = PROJECT_ROOT / "data" / "translations" / "story"
OUT_DIR = PROJECT_ROOT / "out"


def main() -> int:
    if len(sys.argv) != 2:
        print(__doc__)
        return 1
    stem = sys.argv[1]
    path = STORY_DIR / f"{stem}.json"
    data = json.loads(path.read_text(encoding="utf-8"))

    lines = [f"# {stem} — pending strings", ""]
    count = 0
    for section_name, section in data["sections"].items():
        pending = [
            (key, value)
            for key, value in section.items()
            if not key.startswith("_") and not str(value.get("th") or "").strip()
        ]
        if not pending:
            continue
        lines.append("=" * 78)
        lines.append(f"### {section_name}  ({len(pending)} strings)")
        lines.append("=" * 78)
        for key, value in pending:
            count += 1
            en = value.get("en", "")
            lead = len(en) - len(en.lstrip(" "))
            trail = len(en) - len(en.rstrip(" "))
            notes = []
            if lead:
                notes.append(f"lead={lead}")
            if trail:
                notes.append(f"trail={trail}")
            if not en.strip():
                notes.append("WHITESPACE-ONLY TEMPLATE")
            suffix = f"  <<{', '.join(notes)}>>" if notes else ""
            lines.append(f"[{key}]{suffix}")
            lines.append(en)
            lines.append("")

    OUT_DIR.mkdir(exist_ok=True)
    out_path = OUT_DIR / f"_dump_{stem}.txt"
    out_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"{count} pending strings -> {out_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

"""Final diff audit: compare every translation file against the pristine backup.

Proves that only `th` values changed, counts them per file, and flags any
structural drift (keys, other languages, ordering, formatting).
Run: .venv\\Scripts\\python.exe out/translation-review/diff_audit.py
"""
from __future__ import annotations

import glob
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CUR = ROOT / "data/translations"
BAK = ROOT / "out/translation-review/backup-translations"

total_th = 0
rows = []
struct = []

for path in sorted(glob.glob(str(CUR / "**/*.json"), recursive=True)):
    rel = Path(path).relative_to(CUR)
    bpath = BAK / rel
    cur = json.loads(Path(path).read_text(encoding="utf-8"))
    old = json.loads(bpath.read_text(encoding="utf-8"))

    if list(cur.get("sections", {})) != list(old.get("sections", {})):
        struct.append(f"{rel.as_posix()}: section list/order changed")
    cmeta = {k: v for k, v in cur.get("_meta", {}).items() if k != "total_strings"}
    ometa = {k: v for k, v in old.get("_meta", {}).items() if k != "total_strings"}
    if cmeta != ometa:
        struct.append(f"{rel.as_posix()}: _meta changed")

    changed = 0
    for sec, secdata in cur["sections"].items():
        osec = old["sections"].get(sec, {})
        if list(secdata) != list(osec):
            struct.append(f"{rel.as_posix()}::{sec}: key list/order changed")
        for key, val in secdata.items():
            if key.startswith("_") or not isinstance(val, dict):
                continue
            o = osec.get(key)
            if o is None or not isinstance(o, dict):
                struct.append(f"{rel.as_posix()}::{sec}::{key}: added/changed key")
                continue
            for lang in ("en", "fr", "de", "es", "it"):
                if val.get(lang) != o.get(lang):
                    struct.append(f"{rel.as_posix()}::{sec}::{key}: {lang} changed")
            if val.get("th") != o.get("th"):
                changed += 1
    total_th += changed
    rows.append((rel.as_posix(), changed))

print(f"files: {len(rows)}   changed th values: {total_th}")
for rel, n in sorted(rows, key=lambda r: -r[1]):
    if n:
        print(f"  {rel:<45} {n}")
print(f"structural problems: {len(struct)}")
for s in struct[:20]:
    print("  !!", s)
sys.exit(1 if struct else 0)

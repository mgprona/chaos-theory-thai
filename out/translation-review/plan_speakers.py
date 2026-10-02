"""Plan (dry-run) for speaker-label normalisation: mirror the English source label.

Policy: the Thai value must carry exactly the same label presence/identity as `en`.
  * en has label  -> th must have the mapped Thai label
  * en has none   -> th must have none
Run:  .venv\\Scripts\\python.exe out/translation-review/plan_speakers.py
"""
from __future__ import annotations

import collections
import glob
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

DASH = re.compile(r"^\s*-\s*([A-Za-z0-9_]{3,28})\s*-\s*")
CAPS = re.compile(r"^\s*-?([A-Z][A-Z0-9_'\.]*(?: [A-Z][A-Z0-9_'\.]*){0,3})\s*[-:]\s*")
UNDER = re.compile(r"^\s*-?([A-Za-z]+_[A-Za-z0-9_]+)\s*[-:]\s*")
MIXED = re.compile(r"^\s*([A-Z][a-z]{2,15})\s*[-:]\s*")
KNOWN_MIXED = {"Lambert", "Fisher", "Redding", "Grimsdottir", "Otomo", "Shetland", "Coen",
               "Nedich", "Mason", "Partridge", "Sam", "Frances", "Hutton", "Milan", "Zherkezhi"}
TH_LABEL = re.compile(r"^\s*([ก-๛][ก-๛\.\s]{1,26}?)\s*[-:]\s+")


def en_label(en: str) -> str | None:
    for rx in (DASH, UNDER):
        m = rx.match(en)
        if m:
            return m.group(1)
    m = CAPS.match(en)
    if m:
        return m.group(1)
    m = MIXED.match(en)
    if m and m.group(1) in KNOWN_MIXED:
        return m.group(1)
    return None


def main() -> None:
    rows = []
    for path in sorted(glob.glob(str(ROOT / "data/translations/**/*.json"), recursive=True)):
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        rel = str(Path(path).relative_to(ROOT)).replace("\\", "/")
        for sec, secdata in data["sections"].items():
            for key, val in secdata.items():
                if key.startswith("_"):
                    continue
                rows.append((rel, sec, key, val.get("en", "") or "", val.get("th", "") or ""))

    mapping: dict[str, collections.Counter] = collections.defaultdict(collections.Counter)
    for _, _, _, en, th in rows:
        le = en_label(en)
        mt = TH_LABEL.match(th)
        if le and mt:
            mapping[le.lower()][mt.group(1).strip()] += 1

    canon = {k: v.most_common(1)[0][0] for k, v in mapping.items()}
    add, strip, relabel, ambiguous = [], [], [], []
    for rel, sec, key, en, th in rows:
        if not th.strip():
            continue
        le = en_label(en)
        mt = TH_LABEL.match(th)
        if le and mt:
            want = canon.get(le.lower())
            if want and mt.group(1).strip() != want:
                relabel.append((rel, sec, key, le, mt.group(1).strip(), want, th[:70]))
        elif le and not mt:
            want = canon.get(le.lower())
            if want:
                add.append((rel, sec, key, le, want, en[:60], th[:60]))
            else:
                ambiguous.append((rel, sec, key, le, en[:60], th[:60]))
        elif not le and mt:
            strip.append((rel, sec, key, mt.group(1).strip(), en[:65], th[:65]))

    print("== canonical en-label -> th-label ==")
    for k, v in sorted(mapping.items(), key=lambda kv: -sum(kv[1].values())):
        print(f"  {k:22} -> {dict(v)}")
    for title, items in (("ADD (en has label, th lost it)", add),
                         ("STRIP (en has none, th added one)", strip),
                         ("RELABEL (name differs)", relabel),
                         ("NO MAPPING (needs manual)", ambiguous)):
        perfile = collections.Counter(i[0] for i in items)
        print(f"\n== {title}: {len(items)} ==")
        for f, n in perfile.most_common():
            print(f"   {f}: {n}")
        for i in items[:100]:
            print("   ", " | ".join(str(x) for x in i[3:]))


if __name__ == "__main__":
    main()

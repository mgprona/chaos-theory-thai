"""Normalise speaker labels in story JSON so each `th` mirrors its `en` label.

Policy (decided in out/translation-review/REVIEW.md 4.2): the compiled Thai string
carries exactly the same speaker label as the English source - no more, no less.

Dry run:  .venv\\Scripts\\python.exe out/translation-review/fix_speakers.py
Apply:    .venv\\Scripts\\python.exe out/translation-review/fix_speakers.py --apply
"""
from __future__ import annotations

import collections
import glob
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent

# Any "Word[ Word]*" or "Word_Word" token followed by a separator and whitespace.
EN_LABEL = re.compile(r"^\s*-?\s*([A-Za-z][A-Za-z0-9_'\.]*(?:[ ][A-Za-z][A-Za-z0-9_'\.]*){0,3})\s*[-:]\s+")
TH_LABEL = re.compile(r"^\s*([ก-๛][ก-๛\.\sA-Za-z0-9]{1,26}?)\s*[-:]\s+")
# manual mapping for labels whose Thai form is not reachable from the corpus
MANUAL = {
    "capt_diego": "กัปตันดิเอโก",
    "dis sol walter": None,
}
# English labels the detector cannot see (missing space after the separator);
# their Thai labels are already correct - never strip these.
SKIP_STRIP = {
    ("02_CargoShip.json", "P_02_CargoShip_InterogateCaptain", "Speech_0006L"),
    ("09_SeoulTwo.json", "P_09_SeoulTwo_Bombdrop", "Speech_0001L"),
    ("11_KokuboSosho.json", "P_11_KokuboSosho_InterroISDF", "Speech_0018L"),
}
# story files; Latin in-source tags are only localised when they use the Name_Name style
UNDERSCORE_LABEL = re.compile(r"^[A-Za-z]+_[A-Za-z0-9_]+$")


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: dict, trailing_newline: bool) -> None:
    text = json.dumps(data, ensure_ascii=False, indent=2)
    path.write_text(text + ("\n" if trailing_newline else ""), encoding="utf-8")


def main() -> None:
    apply = "--apply" in sys.argv
    files = sorted(glob.glob(str(ROOT / "data/translations/story/*.json")))
    docs = {}
    for p in files:
        raw = Path(p).read_text(encoding="utf-8")
        docs[p] = (read_json(Path(p)), raw.endswith("\n"), raw)

    rows = []
    for p, (data, _, _) in docs.items():
        name = Path(p).name
        for sec, secdata in data["sections"].items():
            for key, val in secdata.items():
                if key.startswith("_"):
                    continue
                rows.append((p, name, sec, key, val))

    # 1. canonical Thai label per English label, learned from the corpus
    mapping: dict[str, collections.Counter] = collections.defaultdict(collections.Counter)
    for p, name, sec, key, val in rows:
        le = EN_LABEL.match(val.get("en", "") or "")
        mt = TH_LABEL.match(val.get("th", "") or "")
        if le and mt:
            mapping[le.group(1).strip().lower()][mt.group(1).strip()] += 1
    canon = {k: v.most_common(1)[0][0] for k, v in mapping.items()}
    thai_names = set(canon.values())

    add, strip, relabel, replace_latin, skipped = [], [], [], [], []
    for p, name, sec, key, val in rows:
        en = val.get("en", "") or ""
        th = val.get("th", "") or ""
        if not th.strip() or not en.strip():
            continue
        le = EN_LABEL.match(en)
        mt = TH_LABEL.match(th)
        latin_th = EN_LABEL.match(th)
        if le and not mt:
            want = canon.get(le.group(1).strip().lower())
            if latin_th:
                # Thai still carries a Latin label; only localise the Name_Name style
                if want and UNDERSCORE_LABEL.match(latin_th.group(1).strip()):
                    replace_latin.append((p, name, sec, key, le.group(1).strip(),
                                          latin_th.group(1).strip(), want, th))
            elif want:
                add.append((p, name, sec, key, le.group(1).strip(), want, th))
            else:
                skipped.append(("no-mapping", name, sec, key, le.group(1), en[:60], th[:60]))
        elif not le and mt and mt.group(1).strip() in thai_names:
            if (name, sec, key) in SKIP_STRIP:
                continue
            strip.append((p, name, sec, key, mt.group(1).strip(), th))
        elif le and mt:
            want = canon.get(le.group(1).strip().lower())
            if want and mt.group(1).strip() != want:
                relabel.append((p, name, sec, key, le.group(1).strip(), mt.group(1).strip(), want, th))

    print(f"canonical labels: {len(canon)}")
    print(f"ADD {len(add)} | STRIP {len(strip)} | RELABEL {len(relabel)} | "
          f"REPLACE-LATIN {len(replace_latin)} | skipped {len(skipped)}")
    for tag, items in (("ADD", add), ("STRIP", strip), ("RELABEL", relabel), ("REPLACE-LATIN", replace_latin)):
        per = collections.Counter(i[1] for i in items)
        print(f"  {tag} per file: {dict(per)}")
    print("\n-- STRIP list --")
    for s in strip:
        print(f"   {s[1]}::{s[2]}::{s[3]} | label={s[4]} | {s[5][:70]}")
    print("\n-- RELABEL list --")
    for s in relabel:
        print(f"   {s[1]}::{s[2]}::{s[3]} | en={s[4]} th={s[5]} -> {s[6]} | {s[7][:70]}")
    print("\n-- REPLACE-LATIN list --")
    for s in replace_latin:
        print(f"   {s[1]}::{s[2]}::{s[3]} | en={s[4]} latinTh={s[5]} -> {s[6]}")
    print("\n-- ADD list (first 60) --")
    for s in add[:60]:
        print(f"   {s[1]}::{s[2]}::{s[3]} | en={s[4]} -> {s[5]} | {s[6][:60]}")

    if not apply:
        print("\n[dry-run] nothing written")
        return

    changed = collections.Counter()
    for kind, items in (("add", add), ("strip", strip), ("relabel", relabel), ("replace", replace_latin)):
        for p, name, sec, key, *rest in items:
            data = docs[p][0]
            th = data["sections"][sec][key]["th"]
            if kind == "add":
                want = rest[1]
                data["sections"][sec][key]["th"] = f"{want} - {th}"
            elif kind == "strip":
                data["sections"][sec][key]["th"] = TH_LABEL.sub("", th, count=1)
            elif kind == "relabel":
                want = rest[2]
                data["sections"][sec][key]["th"] = TH_LABEL.sub(f"{want} - ", th, count=1)
            else:  # replace Latin in-source tag with the Thai label
                want = rest[2]
                data["sections"][sec][key]["th"] = EN_LABEL.sub(f"{want} - ", th, count=1)
            changed[name] += 1

    for p, (data, trailing, _) in docs.items():
        if changed[Path(p).name]:
            write_json(Path(p), data, trailing)
    print("\napplied:", dict(changed))
    print("total edits:", sum(changed.values()))


if __name__ == "__main__":
    main()

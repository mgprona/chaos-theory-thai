"""Objective QA sweep over data/translations/**/*.json.

Produces machine-checkable findings (never edits the source JSON).
Run:  .venv\\Scripts\\python.exe out/translation-review/qa_review.py
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

FORBIDDEN = {"\u201c", "\u201d", "\u2018", "\u2019", "\u2026"}
PLACEHOLDER = re.compile(r"%[0-9]*[sdif]|\{[^}]*\}|<[^>]+>|&[a-zA-Z#0-9]+;|\\n|\\t")
DIGITS = re.compile(r"\d")
LATIN_WORD = re.compile(r"[A-Za-z][A-Za-z'\-\.]*")
THAI = re.compile(r"[\u0e00-\u0e7f]")
SPEAKER = re.compile(r"^([^\-:\n]{1,28}?)\s*([-:])\s+")

ALLOWED_LATIN = {
    # product / acronym tokens that are deliberately kept in Latin script
    "opsat", "sc", "20k", "sc-20k", "nka", "i-sdf", "iso", "pda", "hud", "splinter",
    "cell", "cd", "dvd", "pc", "usb", "tv", "fps", "ai", "id", "vip", "fbi", "cia",
    "nsa", "un", "ok", "tv", "gps", "echelon", "sam", "kbs", "nm", "kg", "km", "cm",
    "mm", "m", "sec", "xx", "asap", "po", "wc", "beta", "alpha", "jpg", "url", "www",
    "com", "http", "www.displace", "zherkezhi", "dvorak", "sha", "a", "b", "o", "ab",
    "kgb", "hr", "sigint", "sig", "int", "mhz", "ghz", "kb", "mb", "gb",
}

entries = []  # (file, section, key, en, th)


def load():
    for path in sorted(glob.glob(str(ROOT / "data/translations/**/*.json"), recursive=True)):
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        rel = str(Path(path).relative_to(ROOT)).replace("\\", "/")
        for sec_name, sec in data["sections"].items():
            for key, val in sec.items():
                if key.startswith("_"):
                    continue
                entries.append((rel, sec_name, key, val.get("en", "") or "", val.get("th", "") or ""))


def main():
    load()
    report: dict[str, object] = {"total": len(entries)}

    identical, latin_heavy, digits_mismatch, space_mismatch = [], [], [], []
    forbidden_hits, cp874_fail, short_ratio, placeholder_mismatch = [], [], [], []
    latin_tokens = collections.Counter()
    en_to_th = collections.defaultdict(set)
    th_to_en = collections.defaultdict(set)
    speaker_en, speaker_th = collections.Counter(), collections.Counter()
    speaker_pairs = collections.defaultdict(collections.Counter)
    per_file = collections.Counter()

    for rel, sec, key, en, th in entries:
        loc = f"{rel}::{sec}::{key}"
        if en.strip() and th.strip():
            per_file[rel] += 1
            en_to_th[en].add(th)
            th_to_en[th].add(en)
            if en == th:
                identical.append((loc, en))
            en_lat = sum(c.isascii() and c.isalpha() for c in en)
            th_chars = [c for c in th if not c.isspace()]
            latin_ratio = (sum(1 for c in th_chars if c.isascii() and c.isalpha()) / max(1, len(th_chars)))
            if latin_ratio > 0.45 and en_lat > 12:
                latin_heavy.append((loc, round(latin_ratio, 2), en[:90], th[:90]))
            if sorted(DIGITS.findall(en)) != sorted(DIGITS.findall(th)):
                digits_mismatch.append((loc, en[:100], th[:100]))
            if PLACEHOLDER.findall(en) != PLACEHOLDER.findall(th):
                placeholder_mismatch.append((loc, PLACEHOLDER.findall(en), PLACEHOLDER.findall(th), en[:80], th[:80]))
            if (len(en) - len(en.lstrip())) != (len(th) - len(th.lstrip())) or \
               (len(en) - len(en.rstrip())) != (len(th) - len(th.rstrip())):
                space_mismatch.append((loc, repr(en[:40]), repr(th[:40])))
            if en.strip() and len(th) < 0.28 * len(en) and len(en) > 40:
                short_ratio.append((loc, len(en), len(th), en[:90], th[:90]))
            for ch in FORBIDDEN:
                if ch in th:
                    forbidden_hits.append((loc, ch, th[:80]))
            try:
                for b in th.encode("cp874"):
                    if not (b < 128 or 161 <= b <= 251):
                        raise ValueError(b)
            except Exception as exc:  # noqa: BLE001
                cp874_fail.append((loc, str(exc), th[:80]))
        for tok in LATIN_WORD.findall(th):
            t = tok.lower().strip(".-'")
            if t and t not in ALLOWED_LATIN and not t.isdigit():
                latin_tokens[t] += 1
        m_en, m_th = SPEAKER.match(en), SPEAKER.match(th)
        if m_en and m_th:
            speaker_en[m_en.group(1).strip()] += 1
            speaker_th[m_th.group(1).strip()] += 1
            speaker_pairs[m_en.group(1).strip()][m_th.group(1).strip()] += 1

    # en -> multiple Thai renderings
    multi_th = {en: sorted(v) for en, v in en_to_th.items() if len(v) > 1}
    multi_en = {th: sorted(v) for th, v in th_to_en.items() if len(v) > 1}
    speaker_inconsistent = {
        en: dict(cnt) for en, cnt in speaker_pairs.items() if len(cnt) > 1
    }

    out = {
        "total_entries": len(entries),
        "translated_nonempty": sum(per_file.values()),
        "identical_en_th": [list(x) for x in identical],
        "latin_heavy": [list(x) for x in latin_heavy],
        "digits_mismatch": [list(x) for x in digits_mismatch],
        "placeholder_mismatch": [list(x) for x in placeholder_mismatch],
        "space_mismatch": [list(x) for x in space_mismatch],
        "short_ratio_lt_0.28": [list(x) for x in short_ratio],
        "forbidden_chars": [list(x) for x in forbidden_hits],
        "cp874_fail": [list(x) for x in cp874_fail],
        "multi_thai_for_same_en": {k: v for k, v in list(multi_th.items())[:400]},
        "multi_en_for_same_th": {k: v for k, v in list(multi_en.items())[:400]},
        "speaker_variants": {k: dict(v) for k, v in speaker_inconsistent.items()},
        "latin_tokens_in_th": latin_tokens.most_common(200),
        "counts": {
            "identical_en_th": len(identical),
            "latin_heavy": len(latin_heavy),
            "digits_mismatch": len(digits_mismatch),
            "placeholder_mismatch": len(placeholder_mismatch),
            "space_mismatch": len(space_mismatch),
            "short_ratio": len(short_ratio),
            "forbidden_chars": len(forbidden_hits),
            "cp874_fail": len(cp874_fail),
            "multi_thai_for_same_en": len(multi_th),
            "multi_en_for_same_th": len(multi_en),
            "speaker_variants": len(speaker_inconsistent),
            "distinct_en": len(en_to_th),
            "distinct_th": len(th_to_en),
        },
    }
    (OUT / "qa_findings.json").write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")

    c = out["counts"]
    print("== counts ==")
    for k, v in c.items():
        print(f"  {k}: {v}")
    print("\n== top latin tokens inside Thai ==")
    print(", ".join(f"{t}:{n}" for t, n in latin_tokens.most_common(40)))
    print("\n== top inconsistent en->th ==")
    for en, vals in sorted(multi_th.items(), key=lambda kv: -len(kv[1]))[:15]:
        print(f"  [{len(vals)}] {en[:70]}")
        for v in vals[:4]:
            print(f"        - {v[:70]}")
    print("\n== speaker variants ==")
    for en, cnt in sorted(speaker_inconsistent.items(), key=lambda kv: -sum(kv[1].values()))[:25]:
        print(f"  {en}: {cnt}")
    print("\nwrote", OUT / "qa_findings.json")


if __name__ == "__main__":
    sys.exit(main())

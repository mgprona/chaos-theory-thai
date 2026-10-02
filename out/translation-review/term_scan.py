"""Cross-file term/name variant scan over data/translations/**/*.json.

For each locked term, report every Thai rendering variant found, with counts and
example locations, so inconsistencies are provable rather than impressionistic.
Run:  .venv\\Scripts\\python.exe out/translation-review/term_scan.py
"""
from __future__ import annotations

import collections
import glob
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

# canonical, [variant regexes]  (regex searched inside the th value)
TERMS: dict[str, tuple[str, list[str]]] = {
    "Fisher": ("ฟิชเชอร์", [r"ฟิชเชอร์", r"ฟิสเชอร์", r"ฟิชเช่อ", r"ฟิชเชอ(?!ร์)", r"ฟีชเชอร์"]),
    "Lambert": ("แลมเบิร์ต", [r"แลมเบิร์ต", r"แลมเบิร์(?!ต)", r"ลัมเบิร์", r"แลมเบิร์ด"]),
    "Grimsdottir": ("กริมส์ดอตเตียร์", [r"กริมส์ดอตเตียร์", r"กริมดอต", r"กริมส(?!์ดอต)"]),
    "Shetland": ("เชตแลนด์", [r"เชตแลนด์", r"เช็ตแลนด์", r"ชีตแลนด์", r"เชทแลนด์"]),
    "Morgenholt": ("มอร์เกนโฮลต์", [r"มอร์เกนโฮลต์", r"มอร์แกนโฮลต์", r"มอร์เกนฮอลต์"]),
    "Lacerda": ("ลาแซร์ดา", [r"ลาแซร์ดา", r"ลาเซอร์ดา", r"ลาแซร์ด้า", r"ลาเซด้า"]),
    "Otomo": ("โอโตโม", [r"โอโตโมะ", r"โอโตโม(?!ะ)"]),
    "Toshiro": ("โทชิโร", [r"โทชิโร(?!ะ)", r"โทชิโระ"]),
    "Zherkezhi": ("เซอร์เคซี", [r"เซอร์เคซี", r"เซอร์เคซี่", r"เซอร์เคชี่", r"เซอร์เกซี"]),
    "Nedich": ("เนดิช", [r"เนดิช์", r"เนดิช(?!์)", r"เนดิซ", r"เนดิทช์"]),
    "Narcissa": ("นาร์ซิสซา", [r"นาร์ซิสซา", r"นาซิสซา", r"นาร์ซิสสา"]),
    "Redding": ("เรดดิง", [r"เรดดิง", r"เรดดิ้ง", r"เรดิง"]),
    "Partridge": ("พาร์ทริดจ์", [r"พาร์ทริดจ์", r"พาร์ทริдж", r"พาทริดจ์"]),
    "Displace": ("ดิสเพลส", [r"ดิสเพลส", r"ดิสเพลซ"]),
    "Echelon": ("เอเชลอน", [r"เอเชลอน", r"เอ็ชเชลอน", r"เอชาลอน", r"เอเชล่อน", r"อีเชลอน"]),
    "Masse": ("มาสส์", [r"มาสส์", r"แมสส์", r"มาส์ส"]),
    "MasseKernels": ("มาสส์เคอร์เนล", [r"มาสส์เคอร์เนล", r"มาส์สเคอร์เนล", r"แมสส์เคอร์เนล", r"Masse Kernels"]),
    "ShetlandGlossary": ("ดักลาส เชตแลนด์", [r"ดักลาส เชตแลนด์", r"ดั๊ก เชตแลนด์", r"ดัก เชตแลนด์"]),
    "RedNishin": ("เรดนิชิน", [r"เรดนิชิน", r"เรด นิชิน", r"เรดนิชิ่น", r"เรดนิชินน์"]),
    "StickyCamera": ("กล้องสติ๊กกี้", [r"สติ๊กกี้", r"สติ๊กกี(?!้)", r"สติกกี้", r"สติกกี"]),
    "NKA": ("NKA", [r"NKA", r"เอ็นเคเอ", r"เอ็น\.เค\.เอ"]),
    "ISDF": ("I-SDF", [r"I-SDF", r"ไอ-เอสดีเอฟ", r"ไอเอสดีเอฟ"]),
    "OPSAT": ("OPSAT", [r"OPSAT", r"ออปแซต", r"ออปแซท", r"โอปแซต"]),
    "FifthFreedom": ("สิทธิเสรีภาพขั้นที่ 5",
                     [r"สิทธิเสรีภาพขั้นที่ ?5", r"ฟิฟธ์ฟรีดอม", r"(?<!ิ)เสรีภาพขั้นที่ ?5",
                      r"สิทธิที่ ?5"]),
    "JongPomChu": ("จอง ปอมชู", [r"จอง ปอมชู", r"จง พอมจู", r"จง ปอมชู"]),
    "ThirdEchelon": ("เธิร์ดเอเชลอน", [r"เธิร์ดเอเชลอน", r"เธิร์ด เอเชลอน", r"เธิร์ดเอ็ชเชลอน", r"เทิร์ดเอเชลอน"]),
}


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

    lines = ["# Term / name variant scan", ""]
    for name, (canon, variants) in TERMS.items():
        counts = collections.Counter()
        examples: dict[str, list[str]] = collections.defaultdict(list)
        for rel, sec, key, en, th in rows:
            if not th:
                continue
            for pat in variants:
                import re
                if re.search(pat, th):
                    counts[pat] += 1
                    if len(examples[pat]) < 3:
                        examples[pat].append(f"{rel.split('/')[-1]}::{sec}::{key} = {th[:70]}")
        total = sum(counts.values())
        lines.append(f"## {name} (canonical: {canon}) — {total} hits")
        for pat, n in counts.most_common():
            flag = "" if pat == variants[0] else "  <-- VARIANT"
            lines.append(f"- `{pat}` x{n}{flag}")
            if flag:
                for ex in examples[pat]:
                    lines.append(f"    - {ex}")
        lines.append("")

    out = ROOT / "out/translation-review/term_variants.md"
    out.write_text("\n".join(lines), encoding="utf-8")
    print("\n".join(lines))
    print("wrote", out)


if __name__ == "__main__":
    main()

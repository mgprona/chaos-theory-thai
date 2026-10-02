"""Speaker-prefix attribution audit.

Compares the English speaker label ("LAMBERT - ...", "FISHER: ...") with the Thai
label in front of the same value, and flags lost, added, or changed attribution.
Run:  .venv\\Scripts\\python.exe out/translation-review/speaker_audit.py
"""
from __future__ import annotations

import collections
import glob
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent

SEP = re.compile(r"^([^\-:\n]{1,30}?)\s*([-:])\s+")
GLOSS = {
    "fisher": "ฟิชเชอร์", "sam": "แซม", "lambert": "แลมเบิร์ต", "grimsdottir": "กริมส์ดอตเตียร์",
    "redding": "เรดดิง", "partridge": "พาร์ทริดจ์", "shetland": "เชตแลนด์", "morgenholt": "มอร์เกนโฮลต์",
    "otomo": "โอโตโม", "coen": "โคเอน", "zherkezhi": "เซอร์เคซี", "nedich": "มิลาน เนดิช",
}
THAI_NAMES = set(GLOSS.values()) | {
    "ฟิชเชอร์", "แลมเบิร์ต", "กริมส์ดอตเตียร์", "เรดดิง", "พาร์ทริดจ์", "เชตแลนด์", "โอโตโม",
    "โคเอน", "เซอร์เคซี", "ฮาร์เปอร์", "คาเนดะ", "จิน", "จอง", "คิม", "โคโน", "คาเนดะ",
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

    en_to_th = collections.defaultdict(collections.Counter)
    added, lost, changed = [], [], []
    for rel, sec, key, en, th in rows:
        m_en, m_th = SEP.match(en), SEP.match(th)
        if m_en and m_th:
            en_to_th[m_en.group(1).strip().lower()][m_th.group(1).strip()] += 1
        elif m_en and not m_th:
            lost.append((rel, sec, key, m_en.group(1).strip(), en[:70], th[:70]))
        elif m_th and not m_en:
            added.append((rel, sec, key, m_th.group(1).strip(), en[:70], th[:70]))

    # explicit name-on-name mismatches
    for rel, sec, key, en, th in rows:
        m_en, m_th = SEP.match(en), SEP.match(th)
        if not (m_en and m_th):
            continue
        name = m_en.group(1).strip().lower()
        expected = GLOSS.get(name)
        if expected and m_th.group(1).strip() != expected:
            changed.append((rel, sec, key, name, m_th.group(1).strip(), en[:60], th[:60]))

    lines = ["# Speaker-prefix attribution audit", "",
             f"- entries: {len(rows)}",
             f"- en has label, th lost it: **{len(lost)}**",
             f"- en has no label, th added one: **{len(added)}**",
             f"- glossary name mismatch: **{len(changed)}**", ""]
    lines.append("## en label -> Thai label mapping (labels where Thai differs by speaker)")
    for en_name, cnt in sorted(en_to_th.items(), key=lambda kv: -sum(kv[1].values())):
        if len(cnt) > 1:
            lines.append(f"- **{en_name}** -> {dict(cnt)}")
    lines.append("")
    lines.append("## Glossary mismatches (wrong speaker name)")
    for r in changed[:60]:
        lines.append(f"- {r[0]}::{r[1]}::{r[2]} | en={r[3]!r} -> th={r[4]!r}\n    EN: {r[5]}\n    TH: {r[6]}")
    lines.append("")
    lines.append("## en label dropped in Thai")
    by_file = collections.Counter(r[0] for r in lost)
    lines.append(f"- per file: {dict(by_file)}")
    for r in lost[:25]:
        lines.append(f"- {r[0]}::{r[1]}::{r[2]} [{r[3]}]\n    EN: {r[4]}\n    TH: {r[5]}")
    lines.append("")
    lines.append("## Thai added a label English does not have")
    by_file2 = collections.Counter(r[0] for r in added)
    lines.append(f"- per file: {dict(by_file2)}")
    for r in added[:25]:
        lines.append(f"- {r[0]}::{r[1]}::{r[2]} [th={r[3]}]\n    EN: {r[4]}\n    TH: {r[5]}")

    (OUT / "speaker_audit.md").write_text("\n".join(lines), encoding="utf-8")
    print("\n".join(lines[:80]))
    print("\n... wrote", OUT / "speaker_audit.md")


if __name__ == "__main__":
    main()

"""Global translation fixes: terminology normalisation + verified HIGH defects +
empty-template policy + UI wording.  Dry run by default.

  .venv\\Scripts\\python.exe out/translation-review/fix_global.py
  .venv\\Scripts\\python.exe out/translation-review/fix_global.py --apply
"""
from __future__ import annotations

import collections
import glob
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
TRANS = ROOT / "data/translations"

# ---------------------------------------------------------------- term fixes
# (old, new, optional filename filter)  applied to every `th`
TERM = [
    ("ดิสเพลซ", "ดิสเพลส", None),
    ("แมสส์", "มาสส์", None),
    ("มาส์ส", "มาสส์", None),
    ("โอโตโมะ", "โอโตโม", None),
    ("โทชิโระ", "โทชิโร", None),
    ("กริมสดอตตีร์", "กริมส์ดอตเตียร์", None),
    ("ดั๊ก เชตแลนด์", "ดักลาส เชตแลนด์", None),
    ("ดัก เชตแลนด์", "ดักลาส เชตแลนด์", None),
    ("เฮกเตอร์", "เฮกตอร์", None),
    ("อีเชลอน", "เอเชลอน", None),
    ("ซินญอร์", "เซญอร์", None),
    ("Dvorak", "ดโวรัก", None),
    ("Masse Kernels", "มาสส์เคอร์เนล", None),
    ("จง พอมจู", "จอง ปอมชู", None),
    ("นักวิ่งภาคสนาม", "เจ้าหน้าที่ภาคสนาม", None),
    ("ศัตรูยืนลดอาวุธ", "ศัตรูหยุดปฏิบัติการ", None),          # H1
    ("สายลับทหารหนึ่ง", "ทหารสารวัตร", None),                 # H8
    ("เพชฌฆาตแห่งบอสเนีย", "ช่างตัดผมแห่งบอสเนีย", None),      # H11
    ("ด้วยมองกลางคืน", "ด้วยโหมดมองกลางคืน", "04_Penthouse.json"),
    ("ห้องทำงานประธานาธิบดี", "ห้องทำงานประธานธนาคาร", "03_Bank.json"),
    ("เสียนก", "เสียงนก", "03_Bank.json"),
    ("ลองเอบันทึก", "ลองเอาบันทึก", "07_Battery.json"),
    ("ฉันย้ำไม่พอ", "ฉันย้ำเท่าไรก็ไม่พอ", "11_KokuboSosho.json"),
]

# ------------------------------------------------------- exact key rewrites
KEY = {
    ("01_Lighthouse.json", "P_01_Lighthouse_CnvNoLacerda", "Speech_0002L"):
        "อิอาโก: ใช่ พวกนั้นออกไปได้สักพักใหญ่แล้ว",                                   # H2
    ("05_Displace01.json", "P_05_Displace01_SecurityEvents", "Speech_0022L"):
        "พลทหารดิสเพลสอเล็กซ์ - ฉันจะจัดการแกเองถ้าแกไม่เปิดประตูบ้าๆ นี่",             # H3
    ("02_Seoulthree.json", "P_02_Seoulthree_goals_activ", "Objective_0010"):
        "ทำให้เรือหลบหนีของจงใช้การไม่ได้",                                             # H4
    ("02_Seoulthree.json", "P_02_Seoulthree_goals_activ", "Objective_0022"):
        "ทำให้เครื่องยนต์บนเรือของจงใช้การไม่ได้",
    ("09_SeoulTwo.json", "P_09_SeoulTwo_Fin", "Objective_0002"):
        "ปิดการทำงานรถถังรบแบบ 86 ทั้งหมดเพื่อช่วยทอนกำลังเกาหลีเหนือ",                  # H5
    ("07_Battery.json", "P_07_Battery_Communications", "Speech_0185L"):
        "ทหาร - ประกาศ ห้ามติดประกาศใดๆ บนกระดานประกาศของฐาน หากไม่ได้รับอนุมัติจากพันจ่าพก",  # H7
    ("05_Displace01.json", "P_05_Displace01_InterroRDLounge", "Speech_0010L"):
        "ช่างเทคนิคดิสเพลสวาซลาฟ - เร... เรากำลังพัฒนาชุดเครื่องกระจายเสียง...สำหรับควบคุมฝูงชน... "
        "แต่ต้นแบบเป็นแบบพกพา... ยิงได้ 40 มม....",                                      # H10
    ("00_Training.json", "P_00_Training_CnvOff_Falko", "Speech_0002L"):
        "ฟัลโก - เอ่อ... อนุญาตเฉพาะผู้ที่ได้รับอนุญาตให้ขึ้นสะพานเดินเรือเท่านั้นครับ... ท่าน",  # H15
    ("00_Training.json", "P_00_Training_CnvOff_Hantz", "Speech_0022L"):
        "ฮานต์ซ - ยุ่งตลอดเลยครับท่าน พยายามตรวจวัดสภาพอากาศและกระแสลมร้อนให้แม่นยำเพื่อให้ฝ่ายการบินใช้ "
        "แต่พายุที่เราเจอเมื่อคืนก่อนทิ้งรูปแบบอุณหภูมิขนาดใหญ่ไว้ในเส้นทาง ค่าความกดอากาศปั่นป่วนไปหมดเลยครับ",  # H16
    ("10_BathHouse.json", "P_10_Bathhouse_Communications", "Speech_0062L"):
        "กริมส์ดอตเตียร์ - คิดได้ดี ฟิชเชอร์ ดูเหมือนเชตแลนด์ใช้โค้ดเรียกซ้ำไม่รู้จบของเซอร์เคซี "
        "รันอัลกอริทึมพันธุกรรม เพื่อสั่งการคนของเขาจากระยะไกล",                          # H17
    ("10_BathHouse.json", "P_10_Bathhouse_Communications", "Speech_0122L"):
        "แลมเบิร์ต - I-SDF อาจกำลังวางแผนจับกุม เข้าถึงคอมพิวเตอร์ของเจ้าของในห้องทำงานถัดไป",  # H18
    ("10_BathHouse.json", "P_10_Bathhouse_Communications", "Speech_0011L"):
        "ฟิชเชอร์...",                                                                   # H19
    ("10_BathHouse.json", "P_10_Bathhouse_InterroPrivateBath02", "Speech_0007L"):
        "ผิวของฉันเหล็กแทงไม่เข้า ฉันไม่กลัว ฉันคือเรดนิชิน",                              # H20
    ("11_KokuboSosho.json", "P_11_KokuboSosho_Communications", "Speech_0154L"):
        "ฟิชเชอร์ - ข้อมูลอะไรก็ตามเกี่ยวกับที่นี่มีแต่ช่วยได้ทั้งนั้น",                    # H22
    ("11_KokuboSosho.json", "P_11_KokuboSosho_Communications", "Speech_0117L"):
        "ฟิชเชอร์ - นั่นเป็นแผนที่ครึ่งๆ กลางๆ ที่สุดเท่าที่ฉันเคยได้ยินมา...",           # H23
    # shipped source placeholder "TODO" -> Thai (matches opsat/training.json treatment)
    ("03_Bank.json", "GENERAL", "Briefing"): "รอดำเนินการ",
    ("05_Displace01.json", "GENERAL", "Briefing"): "รอดำเนินการ",
    ("07_Battery.json", "GENERAL", "Briefing"): "รอดำเนินการ",
    ("09_SeoulTwo.json", "GENERAL", "Briefing"): "รอดำเนินการ",
    ("11_KokuboSosho.json", "GENERAL", "Briefing"): "รอดำเนินการ",
}

# safe whole-string substring rewrites across every `th`
SUB = [
    ("ขีปนาวุธขีปนาวุธ", "ขีปนาวุธ", None),                                            # H21
    ("ไอ้ตัวตลกนี่", "ไอ้หมอนี่", None),
    ("คนไม่มีหัวนอนปลายเท้า", "ไม่มีใครรู้จัก", None),
    ("ในเพนตากอน", "", None),
    ("กลัวที่สูง", "กลัวความสูง", None),
]

# exact substrings, story files only
SUB_STORY = [
    ("แต่ช่างเถอะ เรามีปืนที่ยิงกระสุนแบบนั้นไหมล่ะ?",
     "แต่ช่างเถอะ เราไม่มีอาวุธที่ยิงกระสุนแบบนั้นได้เลย"),                                   # H6
    ("เพื่อช่วยทุพพลภาพเกาหลีเหนือ", "เพื่อช่วยทอนกำลังเกาหลีเหนือ"),
    ("ดีที่คุณทำลายมันไว้แล้ว", "ดีที่คุณทำให้มันใช้การไม่ได้"),
    ("ทำลายเรือหลบหนีของจง", "ทำให้เรือหลบหนีของจงใช้การไม่ได้"),
    ("ทำลายเครื่องยนต์บนเรือของจง", "ทำให้เครื่องยนต์บนเรือของจงใช้การไม่ได้"),
    ("เข้าออกตัวเมืองไปแล้ว", "เขาออกจากเมืองไปแล้ว"),                                       # H9
    ("บริการช่วยเหลือ roadside", "บริการช่วยเหลือรถเสียข้างทาง"),                            # H13
    ("บริการ roadside", "บริการช่วยเหลือรถเสียข้างทาง"),
    ("หลักฐาน overwhelming", "หลักฐานท่วมท้น"),                                             # H12
    ("ถ้าคุณทุ่มคู่หูของคุณใส่มือศัตรู ศัตรูจะหมดสติ",
     "ถ้าคุณทุ่มคู่หูของคุณพุ่งชนศัตรู ศัตรูจะสลบไป"),                                       # H14
    ("ยิงได้ไกล 40 เมตร", "ยิงได้ 40 มม."),                                                # H10 backup
    ("ฉันจะจัดเรียงแกเอง", "ฉันจะจัดการแกเอง"),                                             # H3 backup
    ("อนุญาตเฉพาะเจ้าหน้าที่ที่มีอำนาจ", "อนุญาตเฉพาะผู้ที่ได้รับอนุญาต"),
]

# UI wording (file, section, key, new th)
UI = [
    ("pregame_menus.json", "COMMON", "QuitDemo", "ออกไปเมนูเดโม"),
    ("hud.json", "Interaction", "NpcZone5", "ดำเนินบทสนทนาต่อ"),
    ("ingame_menus.json", "OPSATMENU", "MapAlarmTriggered", "สัญญาณเตือนภัยที่ดังขึ้น"),
]


def main() -> None:
    apply = "--apply" in sys.argv
    docs, trailing = {}, {}
    for p in sorted(glob.glob(str(TRANS / "**/*.json"), recursive=True)):
        raw = Path(p).read_text(encoding="utf-8")
        docs[p] = json.loads(raw)
        trailing[p] = raw.endswith("\n")

    removed: list[tuple[str, str, str, str, str]] = []
    counts = collections.Counter()

    def each(scope=None):
        for p, data in docs.items():
            name = Path(p).name
            if scope and name != scope:
                continue
            for sec, secdata in data["sections"].items():
                for key, val in secdata.items():
                    if key.startswith("_"):
                        continue
                    yield p, name, sec, key, val

    # 1. terminology (all files)
    for old, new, only in TERM:
        for p, name, sec, key, val in each(only):
            th = val.get("th") or ""
            if old in th:
                n = th.count(old)
                val["th"] = th.replace(old, new)
                counts[f"TERM {old}->{new}"] += n

    # 2. substrings (all files then story only)
    for old, new, only in SUB:
        if old == new:
            continue
        for p, name, sec, key, val in each(only):
            th = val.get("th") or ""
            if old in th:
                counts[f"SUB {old[:14]}"] += th.count(old)
                val["th"] = th.replace(old, new)
    for old, new in SUB_STORY:
        for p, name, sec, key, val in each():
            if not p.endswith(".json") or f"{Path(p).parent.name}" != "story":
                continue
            th = val.get("th") or ""
            if old in th:
                counts[f"SUB {old[:14]}"] += th.count(old)
                val["th"] = th.replace(old, new)

    # 3. exact key rewrites
    for (fname, sec, key), new in KEY.items():
        if new is None:
            continue
        for p, name, s, k, val in each(fname):
            if s == sec and k == key:
                if val.get("th") != new:
                    counts[f"KEY {fname}:{key}"] += 1
                    val["th"] = new

    # 4. UI wording
    for fname, sec, key, new in UI:
        for p, name, s, k, val in each(fname):
            if s == sec and k == key and val.get("th") != new:
                counts[f"UI {fname}:{key}"] += 1
                val["th"] = new

    # 5. empty template policy: en is blank -> th must stay blank (same as en)
    for p, name, sec, key, val in each():
        en = val.get("en") or ""
        th = val.get("th") or ""
        if not en.strip() and th.strip():
            removed.append((name, sec, key, en, th))
            val["th"] = en
            counts[f"EMPTY {name}"] += 1

    print("== change summary ==")
    for k, v in sorted(counts.items()):
        print(f"  {k}: {v}")
    print("  empty-template values cleared:", len(removed))

    if not apply:
        print("\n[dry-run] nothing written")
        return

    for p, data in docs.items():
        text = json.dumps(data, ensure_ascii=False, indent=2) + ("\n" if trailing[p] else "")
        Path(p).write_text(text, encoding="utf-8")
    (OUT / "cleared-empty-templates.json").write_text(
        json.dumps([{"file": r[0], "section": r[1], "key": r[2], "en": r[3], "th_removed": r[4]}
                    for r in removed], ensure_ascii=False, indent=2), encoding="utf-8")
    print("applied.")


if __name__ == "__main__":
    main()

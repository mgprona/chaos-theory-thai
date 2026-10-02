# ปิดงานแปล — Splinter Cell: Chaos Theory Thai Mod (2026-10-01)

**ผลลัพธ์: แปลครบ 100% — 8,537 / 8,537 สตริง** (Story 6,318 · UI 1,706 · OPSAT 513)

| รายการ | ค่า |
| --- | --- |
| ไฟล์คำแปล Story | 19 ไฟล์ (ครบทุกภารกิจ รวม co-op) |
| ไฟล์ที่คอมไพล์ | 52 ไฟล์ `.int` |
| PUA catalog | **574 clusters** (ก่อนงานชุดนี้ 529) |
| ฟอนต์ Magma | 6 ขนาด + alias 1 ไฟล์ (13 assets) |
| PCX fonts | 5 ไฟล์ |
| UMD | 618,139,447 ไบต์ |
| UMD SHA-256 | `90560dca4c93266180b2609bb1aaf2a12626c98fb9ac79cf8a2682be2813eeb5` |
| เทสต์ | **36 ผ่าน** (`python -m unittest discover -s tests`) |
| Validator | ผ่าน — 19 ไฟล์ต้นทาง + round-trip ทุกค่าจาก `.int` ทั้ง 52 ไฟล์ |
| ติดตั้งลงเกม | 67 ไฟล์ SHA-256 ตรงกับ `dist` ทุกไฟล์ |

## งานที่ทำในชุดนี้

1. **แปลภารกิจ Story ที่เหลือ 14 ไฟล์ 4,725 สตริง** — `03_ChemBunker`, `04_GCS`, `00_Training_COOP`, `07_UNhq`, `05_NuclearPlant`, `03_Bank`, `04_Penthouse`, `05_Displace01`, `06_Hokkaido`, `07_Battery`, `08_SeoulOne`, `09_SeoulTwo`, `10_BathHouse`, `11_KokuboSosho`
2. **เครื่องมือกลาง** — `tools/apply_mission_translations.py` (เติม + ตรวจกฎข้อความ) และ `tools/dump_pending_strings.py` (ดึงสตริงที่ยังไม่แปล) พร้อมโมดูลข้อมูล `tools/translations_<mission>.py` ต่อภารกิจ
3. **ตัวตรวจครอบทุกภารกิจ** — `tools/validate_translations.py` เลิกฮาร์ดโค้ดรายชื่อภารกิจ ตรวจทุกไฟล์ใน `data/translations/story` และ round-trip `.int` ทุกไฟล์
4. **เทสต์รวม** — `test_all_story_missions_complete_and_cp874` ตรวจทั้ง 19 ไฟล์ (จำนวนสตริงตาม `_meta`, CP874, อักขระต้องห้าม, whitespace mirror, newline)
5. **แก้ปัญหาการนับ** — template ว่างล้วน (`P_03_Chemical_Objectives.Objective_0034`) ไม่ถูกนับเป็น "ยังไม่แปล" อีก ทำให้ยอดรวมคงที่ 8,537 และไปถึง 100% ได้
6. **แก้บิลด์ล้ม intermittently** — การเขียนไฟล์ `.mft`/`.tga` ในโฟลเดอร์ Magma ล้มด้วย `OSError [Errno 22]` แบบสุ่ม (ตัวสแกนไฟล์ของ Windows ล็อกไฟล์ชั่วครู่) เพิ่ม `write_bytes_with_retry()` ใน `src/pipeline/magma_builder.py`; เทสต์ผ่าน 36/36 สามรอบติดกันหลังแก้

## กติกาที่บังคับใช้กับทุกสตริง

- CP874 เขียนได้ (ไบต์ `<128` หรือ `161–251`)
- ห้าม `“ ” ‘ ’ …` และห้าม newline จริง
- ช่องว่างหัว–ท้ายตรงกับต้นฉบับอังกฤษทุกตัวอักษร (59 สตริงที่ลงท้ายด้วยช่องว่างในภารกิจใหม่)
- ชื่อเฉพาะล็อกตามภารกิจที่แปลก่อนหน้า (`จง พอมจู`, `แลมเบิร์ต`, `กริมส์ดอตเตียร์`, `มอร์เกนโฮลต์`, `ลาแซร์ดา`, `สปลินเตอร์เซล`, `เรดนิชิน`, `เนดิช`, `ดโวรัก`, `เซอร์เคซี` ฯลฯ)

## ยังไม่ได้พิสูจน์ (ข้อจำกัด)

- **ยังไม่ตรวจด้วยภาพในเกมสำหรับภารกิจใหม่ 14 ไฟล์** — การตรวจอัตโนมัติยืนยันได้แค่ encoding/ความครบ/glyph coverage ไม่ได้ยืนยันการแสดงผลจริง แนะนำสุ่มตรวจตัวแทนชนิดหน้าจอ: บทบรรยายสรุป, วัตถุประสงค์ OPSAT, บทสนทนา/ซับไทเทิล, co-op
- ชื่อ SC-20K ใน HUD ยังยาวเกินช่อง (ปัญหาค้างเดิม ไม่ใช่ปัญหาการแปล)
- ฟอนต์/atlas: 574 clusters ยังพอดีกับ atlas 1024×1024 แต่ถ้าเพิ่มคำแปลอีกควรเฝ้าดู overflow

## ไฟล์หลักที่เปลี่ยน

- `data/translations/story/*.json` — 14 ไฟล์แปลใหม่ (+140 ของ Seoul 3 ในรอบก่อนหน้า)
- `tools/apply_mission_translations.py`, `tools/dump_pending_strings.py`, `tools/translations_*.py` (ใหม่)
- `tools/validate_translations.py`, `tests/test_toolchain.py`, `src/cli.py`, `src/pipeline/magma_builder.py`
- `dist/` — ข้อความ, ฟอนต์ Magma/PCX และ UMD ที่บิลด์ใหม่

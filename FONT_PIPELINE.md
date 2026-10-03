# ระบบฟอนต์ไทยและ PUA

สถานะ **1.0.0-rc1 — 3 ตุลาคม 2026**: Magma 6 ขนาดใช้ Chakra Petch,
HarfBuzz/FreeType แบบ offline และ catalog **571 กลุ่มอักษร**
ข้อความกับฟอนต์ถูกบิลด์ร่วมกันและติดตั้งครบแล้ว
ผู้เล่นใช้ [แพ็กใน Releases](https://github.com/mgprona/chaos-theory-thai/releases/tag/v1.0.0-rc1)
ไม่ต้องติดตั้งฟอนต์หรือไลบรารีลงระบบ

## เกมใช้ฟอนต์สองเส้นทาง

| เส้นทาง | Encoding ของบิลด์ | ไฟล์ |
| --- | --- | --- |
| Magma | UTF-16LE พร้อม BOM และ PUA สำหรับข้อความไทย | `.mft` lookup/metrics และ `.tga` atlas |
| Legacy PCX | CP874 | PCX 5 ไฟล์ใน `Data/Textures/Font` |

Magma ครอบคลุมเมนู HUD/OPSAT ที่ใช้เส้นทางนี้ และไฟล์ภารกิจทั้ง 38 ไฟล์รวม `P_`/co-op
`config.json` กำหนด `unicode_ui_stems`; ไม่ต้องเพิ่มชื่อด่านทีละรายการ
รายชื่อข้อความอื่นที่เข้าระบบคือ PreGame_PC, PreGameMenus, HUD, InGameMenus,
LoadingScreens, System, Equipments และ Training

PUA หมายถึงรหัสใน Unicode Private Use Area ที่เราใช้เรียก bitmap ของกลุ่มอักษรไทย
ไม่ได้เปลี่ยน JSON ต้นทางเป็นรหัสอ่านไม่ออก: JSON ยังเป็นภาษาไทยปกติ
ไฟล์ legacy ที่ใช้ PCX จึงไม่จำเป็นต้องแปลงเป็น PUA

## กระบวนการบิลด์

1. อ่านคำแปลของไฟล์ที่ตรง `unicode_ui_stems`
2. ให้ HarfBuzz จัด glyph IDs/positions ตาม GSUB/GPOS ของ Chakra Petch
3. แยกกลุ่มอักษรและให้ FreeType วาดภาพพร้อมตำแหน่งสระ/วรรณยุกต์
4. จัดแต่ละกลุ่มลงรหัส PUA เริ่มที่ U+E000 โดยใช้ catalog เดียวกันทุกขนาด
5. เพิ่ม bitmap, glyph records และ sparse Unicode lookup ใน MFT/atlas
6. แปลงช่วงภาษาไทยในข้อความเป็นรหัส PUA และเขียน UTF-16LE พร้อม BOM
7. ตรวจค่าคอมไพล์เทียบคำแปล/แม่แบบและตรวจ glyph lookup ครบทุกขนาดก่อน repack UMD

ฟอนต์ที่สร้าง: **Bios Three Regular 20 / 32 / 48** และ **Prototype Regular 13 / 26 / 36**
PCX ที่สร้าง: txt_hud, txt_mission, txt_integration, titre_regular_integration และ titre_bold_integration

เมื่อเปลี่ยนคำแปลหรือฟอนต์ ต้องบิลด์ข้อความและฟอนต์ใหม่พร้อมกันเสมอ
ห้ามผสม `.int` และ `.mft/.tga` จากคนละบิลด์ เพราะ PUA mapping อาจต่างกัน
แผนผังพร้อม hash ฟอนต์ต้นทางอยู่ที่ `dist/thai_pua_map.json`

## การรักษาฟอนต์เดิม

ตัวสร้าง Magma เก็บ pixels/metrics ของ glyph ละตินเดิม ปรับ UV ให้ตรง atlas 1024×1024
แล้วใช้พื้นที่ว่างข้าง/ใต้ภาพเดิมสำหรับ glyph ไทย โดยจัด glyph สูงก่อน
หาก catalog ใช้พื้นที่มากเกินความจุ ตัวสร้างจะรายงาน overflow ให้แก้ก่อนติดตั้ง
การเก็บ lookup อย่างเดียวไม่พอ: tests ยังเทียบ pixels กับ glyph IDs/positions จาก HarfBuzz

PCX ใช้ภาพ indexed palette และ delimiter index 255 กำหนดเซลล์ตัวอักษร
ตัวสร้างวาดอักษรไทยในช่อง CP874 โดยตรวจความกว้างเซลล์และสีที่มองเห็น

## ตรวจสอบแบบออฟไลน์

RC1 ผ่านการตรวจ **52 ไฟล์ / 8,537 ค่า / 571 PUA clusters / 6 Magma fonts**
รวม round-trip, BOM, lookup coverage, atlas pixels และ original Latin metrics
ตรวจฟอนต์ที่ติดตั้งครบ 18 ไฟล์ตรง dist และฟอนต์ Magma ภายใน UMD ตรงกันทั้ง 13 assets

```powershell
$env:PYTHONIOENCODING = 'utf-8'
.\.venv\Scripts\python.exe build.py
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
.\.venv\Scripts\python.exe tools/validate_translations.py
.\.venv\Scripts\python.exe tools/preview_magma.py
```

preview อ่าน MFT/atlas ที่สร้างจริง แต่ไม่ใช่ screenshot จากเกม
เครื่องมือและคำสั่งสร้าง ZIP อยู่ใน [คู่มือพัฒนา](docs/DEVELOPMENT.md)

## ขอบเขตการยืนยัน

ผลออฟไลน์ยืนยัน mapping, glyph และข้อความคอมไพล์ครบตามคลัง
ยังต้องตรวจในเกมว่าแต่ละหน้าจอเลือก renderer/ฟอนต์ตามคาดและจัดวางข้อความพอดี
ข้อความที่ผู้เล่นพิมพ์เองไม่ผ่าน offline shaping ของแพ็ก

ภาพเมนู/การตั้งค่า/briefing/HUD ที่มีใน `out/game-test/` เป็นหลักฐานของบิลด์ก่อนหน้า
ยังไม่มีภาพ RC1 ที่ผูกกับ hash นี้ และยังไม่ยืนยันทุกด่าน co-op หรือ save/load ของ RC1
ดู [สถานะการตรวจสอบล่าสุด](docs/RELEASE_READINESS.md)

## อ้างอิง

- [HarfBuzz: OpenType features](https://harfbuzz.github.io/shaping-opentype-features.html)
- [HarfBuzz: clusters](https://harfbuzz.github.io/working-with-harfbuzz-clusters.html)
- [FC2MFTConverter: sparse Unicode lookup](https://github.com/eprilx/FC2MFTConverter/blob/master/FC2MFTConverter/MFT/MFTFormat.cs)
  ใช้อ้างอิง lookup; glyph record ของ Chaos Theory ต่างจาก Far Cry 2
- [คู่มือม็อดฟอนต์ไทยสำหรับเกมเก่า](docs/THAI_FONT_MODDING.md)

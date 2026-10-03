# พัฒนา บิลด์ และจัดแพ็ก

ผู้เล่นทั่วไปใช้ [ZIP ใน Releases](https://github.com/mgprona/chaos-theory-thai/releases)
คู่มือนี้สำหรับผู้ที่ต้องการแก้คำแปล ฟอนต์ หรือเครื่องมือ

## เริ่มต้น

ใช้ Python **3.11** ที่ตรงกับ dependencies ของโปรเจกต์
รันคำสั่งจาก repository root:

```powershell
git clone https://github.com/mgprona/chaos-theory-thai.git
cd chaos-theory-thai
py -3.11 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
$env:PYTHONIOENCODING = 'utf-8'
```

แก้ `game_dir` ใน `config.json` ให้ตรงเกมของคุณ
การ full build และสร้าง ZIP ต้องมี pristine UMD ที่ `backups/dynamic-pc.umd`
สำรองจากเกมต้นฉบับที่ยังไม่ลงม็อดด้วย `.\.venv\Scripts\python.exe src/cli.py backup`
อย่าใช้ UMD ที่ติดตั้งม็อดแล้วเป็นต้นฉบับสำรอง

## โครงสร้าง

| พาธ | หน้าที่ |
| --- | --- |
| `data/translations/story,ui,opsat` | คำแปล JSON 33 ไฟล์ |
| `data/raw_official` | ต้นแบบภาษา/ฟอนต์เกมสำหรับ build; รักษาต้นฉบับ |
| `data/fonts` | ฟอนต์ OpenType ภาษาไทยและ working PCX |
| `src/core` | UMD/INI/PCX parsers และ offline shaping |
| `src/pipeline` | extraction, merging, compilation และ font builders |
| `dist` | localization และฟอนต์ที่สร้างแล้ว; UMD ขนาดใหญ่ไม่เก็บใน Git |
| `release` | ตัวติดตั้ง คู่มือแบบ text เครดิตและ license ที่ใส่ ZIP |
| `tools/package_release.py` | ตรวจ build แล้วสร้างแพ็กและ checksum |
| `tools/verify_release.py` | ทดสอบ ZIP ในโฟลเดอร์จำลอง |
| `tests` | unittest ของ toolchain และตัวติดตั้ง Windows |
| `out/game-test` | หลักฐานเกมจริงของบิลด์ตามวันที่ในแต่ละรายงาน |

## แก้คำแปล

แก้เฉพาะค่า `th` โดยรักษาคีย์ `_source`, placeholder, escape และช่องว่างตามกฎ
ใช้ [glossary](GLOSSARY.md) ให้ชื่อเฉพาะและศัพท์ตรงกัน
แม่แบบที่ `en` ว่าง/มีแต่ช่องว่างต้องคง `th` ตามเดิม
ระบบทั่วไปใช้ภาษาอังกฤษ fallback เมื่อ `th` ว่าง แต่ตัวจัดแพ็ก RC จะปฏิเสธข้อความที่ยังแปลไม่ครบ

อย่ารัน extract/merge กับเกมที่ติดตั้งม็อดแล้วเพื่อสร้างต้นฉบับใหม่
แก้คำแปลแล้วบิลด์ localization และฟอนต์ทั้งหกขนาดพร้อมกันเสมอ
PUA mapping อาจเปลี่ยน ห้ามผสมข้อความเก่ากับฟอนต์ใหม่

## บิลด์และตรวจ

```powershell
.\.venv\Scripts\python.exe build.py --stats
.\.venv\Scripts\python.exe build.py
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
.\.venv\Scripts\python.exe tools/validate_translations.py
git diff --check
```

`build.py` คอมไพล์ สร้าง PCX/Magma และ repack UMD โดยปริยาย
ใช้ `--no-umd` เมื่อต้องการเฉพาะ localization/PCX; เส้นทางนี้ไม่สร้างชุด Magma/UMD สำหรับแจก
`src/cli.py compile` และ `build-fonts` เป็นงานเฉพาะส่วน ไม่ใช่ full release build
รายละเอียด mapping, lookup, atlas และการตรวจ glyph อยู่ใน [FONT_PIPELINE.md](../FONT_PIPELINE.md)

การติดตั้งฉบับพัฒนาต้องปิดเกมและตรวจ backup ก่อน:

```powershell
.\.venv\Scripts\python.exe src/cli.py install
```

CLI นี้ใช้ backup ใน repository และไม่มีสถานะ uninstall แบบตัวติดตั้ง RC
ทดสอบภาพในเกมและบันทึก hash บิลด์ เวอร์ชัน ความละเอียด หน้าจอที่ตรวจ และส่วนที่ยังไม่ได้ตรวจ

## สร้าง ZIP สำหรับแจก

```powershell
.\.venv\Scripts\python.exe tools/package_release.py --output out/releases/new-build
.\.venv\Scripts\python.exe tools/verify_release.py out/releases/new-build/ChaosTheory-Thai-1.0.0-rc1.zip --report out/releases/new-build/installer-verification.json
```

กำหนดรุ่นใน `tools/package_release.py` และอัปเดต README/คู่มือ/release notes ให้ตรงกันก่อนรุ่นใหม่
ตัวแพ็กไม่ทับ ZIP ชื่อเดิม ให้ระบุ output ใหม่เพื่อรักษาฉบับที่ตรวจแล้ว
UMD delta สร้างจาก pristine archive และต้องคืน UMD ตรงกับ dist ทุกไบต์
ตัวตรวจ ZIP อ่าน EXE/INI จากเกมจริงเพื่อทำ fixture แต่ติดตั้งเฉพาะใน `out/release-test-*`
ไม่เปิดเกมและไม่ติดตั้งลง game directory จริง

ก่อนอัปโหลด ให้ตรวจ tests, checksum, round-trip, archive integrity และ installation/uninstallation
เผยแพร่ ZIP และ `.zip.sha256` ใน GitHub Release ที่ tag ตรง source commit
ถ้ายังไม่มีหลักฐาน renderer ครบตามขอบเขต ให้คงสถานะ prerelease และระบุข้อจำกัด
ดู [ข้อมูลตรวจ RC1](RELEASE_READINESS.md) และ [ประวัติรุ่น](../CHANGELOG.md)

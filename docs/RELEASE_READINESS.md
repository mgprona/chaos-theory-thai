# Chaos Theory Thai 1.0.0-rc1 — สถานะพร้อมแจก

จัดแพ็กวันที่ **3 ตุลาคม 2026** สำหรับ PC/Steam **1.05 / build 252084**
พร้อมแจกเป็น **release candidate** เพื่อรับผลทดสอบจากผู้เล่น
ดาวน์โหลดจาก [GitHub Release v1.0.0-rc1](https://github.com/mgprona/chaos-theory-thai/releases/tag/v1.0.0-rc1)
และใช้ [คู่มือติดตั้ง](INSTALLATION.md) สำหรับผู้เล่น
ติดตั้งบิลด์เดียวกับ RC ลงเกมในเครื่องพัฒนาแล้ววันที่ 3 ตุลาคม 2026
ตรวจไฟล์ที่ติดตั้งครบ 73 ไฟล์ตรงกับ manifest ใน ZIP และคำแปลต้นทาง 33 ไฟล์ตรงฉบับที่จัดแพ็ก
EXE/INI 25 ไฟล์และ pristine UMD backup คง hash เดิม
สำรองสถานะก่อนติดตั้งที่ `backups/preinstall-latest-20261003-100551/`
หลักฐานอยู่ใน `out/releases/live-install-verification.json`
ยังไม่มีหลักฐานเปิดเกมตรวจ renderer ของฉบับนี้
ผลตรวจสำหรับอ่านบน GitHub อยู่ใน [สรุป JSON ของ RC1](verification/rc1.json)

## ผลตรวจฉบับล่าสุด

| รายการ | ผล |
| --- | --- |
| คลังคำแปล | 8,537 รายการครบ: 8,470 ข้อความที่มีต้นฉบับ + 67 แม่แบบว่างที่คงเดิม |
| ไฟล์ต้นทาง | JSON 33 ไฟล์; ไม่แก้คำแปลหรือ raw official ในการจัดแพ็ก |
| เทียบ pristine UMD | .int ทั้ง 52 ไฟล์ / 8,537 คีย์ตรงคลังแปล; missing/extra keys = 0; ไม่นับ dummy `(null)` |
| Full build | ผ่าน; ข้อความและฟอนต์บิลด์จากคลังเดียวกัน |
| Localization/font validation | 52 ไฟล์ / 8,537 ค่า / 571 PUA clusters / 6 Magma fonts |
| Story round-trip | ผ่านทั้ง 19 JSON เทียบค่าคอมไพล์กลับไปยังคำแปล |
| Regression tests | 46 ผ่าน: toolchain เดิม 38 + ตัวติดตั้ง Windows PowerShell 5.1 อีก 8 |
| UMD integrity | 20,252 entries; ลำดับ/flags/ชนิดชื่อคงเดิม |
| Replacement assets | 65 รายการตรงผลคอมไพล์และฟอนต์; 64 รายการต่างจากต้นฉบับ |
| Other UMD payloads | 20,187 รายการเหมือนต้นฉบับทุกไบต์ |
| ZIP | CRC และ SHA-256; ไม่มี full UMD, executable, เซฟ, ข้อมูลบัญชีหรือสำเนาเกมเดิม |
| ติดตั้งจาก ZIP ในโฟลเดอร์จำลอง | 73 ไฟล์ผ่าน SHA-256; UMD ตรง dist ทุกไบต์รวม footer |
| ถอนม็อด | คืนไฟล์ที่มีอยู่ก่อนติดตั้งครบ 102 ไฟล์และลบไฟล์ที่ม็อดเพิ่มใหม่ |
| Install/uninstall ซ้ำ | ผ่าน; install ซ้ำไม่สำรองทับต้นฉบับ |
| Protection | EXE, INI และเซฟจำลองเหมือนเดิม; ตรวจ hash เกมจริงและ pristine backup ว่าไม่เปลี่ยน |
| ฟอนต์ในเครื่องพัฒนา | PCX 5 + Magma 13 ไฟล์ตรงบิลด์; Magma ใน UMD ตรงทั้ง 13 assets |

ทดสอบตัวติดตั้งเพิ่มเติมด้วยแพ็ก/แพตช์เสีย, UMD คนละฉบับ, พาธหลุดโฟลเดอร์,
ตั้งภาษาใน section ผิด, ผู้เล่นแก้ไฟล์หลังติดตั้ง, สำเนาสำรองเสีย และสถานะติดตั้งถูกขัดจังหวะ
ตัวตรวจปฏิเสธกรณีที่ไม่ควรแก้ไฟล์และกู้คืนจาก backup ในกรณี interrupted install

## ไฟล์สำหรับผู้เล่น

`ChaosTheory-Thai-1.0.0-rc1.zip` และไฟล์ `.zip.sha256` ใน Assets ของ GitHub Release
ไฟล์ Source code (zip/tar.gz) เป็นซอร์สสำหรับนักพัฒนา ไม่ใช่แพ็กติดตั้ง
ภายในมี `Install.cmd`, `Check.cmd`, `Verify.cmd`, `Uninstall.cmd`, ตัวติดตั้ง PowerShell,
แพตช์ UMD, localization/font/startup payloads, manifest, คู่มือไทย, release notes และเครดิต
พร้อม license ของ Chakra Petch จาก [Google Fonts](https://github.com/google/fonts/blob/main/ofl/chakrapetch/OFL.txt)

ผู้เล่นแตก ZIP แล้วเปิด `Check.cmd` และ `Install.cmd` ตามคู่มือ
ใช้ Windows PowerShell 5.1 และ .NET ที่มีในเครื่อง; ไม่ใช้ Python/Pillow/HarfBuzz ตอนติดตั้ง
ใช้ไฟล์ UMD ของผู้เล่นเป็นฐานและตรวจผลลัพธ์ก่อนแทนที่
ไฟล์สำรองอยู่ใน `.chaos-theory-thai/<session>/original/` ภายในเกม
การถอนเก็บ backup ต่อและอาจเหลือโฟลเดอร์ว่าง; ไม่ลบเซฟหรือแก้ INI/WidescreenFix

ความเข้ากันได้จำกัดด้วย SHA-256 ของ UMD ต้นฉบับและ EXE ใน manifest
ไม่มีการรับรอง retail/GOG/ฉบับ executable ที่ถูกแก้ไข หรือม็อดที่แก้ UMD ร่วมกัน

## ขอบเขตเกมจริงที่ยังต้องยืนยัน

รายงาน/ภาพเดิมใน `out/game-test/` ยืนยันเมนู การตั้งค่า หน้าโหลด briefing
equipment และ Lighthouse HUD/OPSAT ของ **บิลด์เก่า** เท่านั้น
แพ็ก RC นี้สร้างหลังเกลาคำแปลและยังไม่มีภาพใหม่ที่ผูกกับ SHA-256 นี้

ต้องตรวจคำบรรยายบทพูด renderer ของข้อความ legacy/PCX ข้อความล้นช่อง
หน้าจอที่มีข้อความยาว เช่น Terms of Use รวมถึง SC-20K HUD ที่เคยล้นในภาพเก่า
ยังไม่ได้เล่นครบภารกิจหรือพิสูจน์ co-op/network, save/load และความละเอียดอื่นของ RC นี้
การแปลครบและการตรวจไฟล์ผ่านไม่เท่ากับการรับรองการแสดงผลทุกหน้าจอ

## คำสั่งตรวจซ้ำ

รันจาก repository root; ใช้ Python ใน `.venv` ที่มี dependencies:

```powershell
$env:PYTHONIOENCODING = 'utf-8'
.\.venv\Scripts\python.exe build.py
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
.\.venv\Scripts\python.exe tools/validate_translations.py
.\.venv\Scripts\python.exe tools/package_release.py
.\.venv\Scripts\python.exe tools/verify_release.py out/releases/ChaosTheory-Thai-1.0.0-rc1.zip
git diff --check
```

ตัวแพ็กตรวจความครบของคำแปล ค่าคอมไพล์ ฟอนต์ UMD และ pristine hash ก่อนสร้าง ZIP
หาก ZIP ชื่อเดิมมีอยู่แล้วจะไม่ทับ ให้ใช้ `--output out/releases/<new-build>`
ตัวตรวจ ZIP แตกแพ็กและทดสอบใน `out/release-test-*` พร้อมอ่าน executable/settings ของเกมจริง
เพื่อสร้าง fixture; ไม่เรียกติดตั้งกับ game directory จริง
หลักฐานแบบย่ออยู่ใน `docs/verification/rc1.json`; รายงานเต็มในเครื่องที่รันทดสอบอยู่ใน
`out/releases/installer-verification.json` พร้อม SHA-256 ของ ZIP
และ logs ใน `out/release-build.log`, `out/release-tests.log`, `out/release-translations.log`
ซึ่งเป็น diagnostic outputs ที่ไม่เก็บใน Git

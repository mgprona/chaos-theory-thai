# ติดตั้งและถอนม็อดภาษาไทย

คู่มือสำหรับ **1.0.0-rc1** บน **Splinter Cell Chaos Theory PC/Steam 1.05 / build 252084**
ดาวน์โหลดจาก [GitHub Releases](https://github.com/mgprona/chaos-theory-thai/releases/tag/v1.0.0-rc1)
เลือก `ChaosTheory-Thai-1.0.0-rc1.zip` ใน Assets

## ก่อนติดตั้ง

- ตั้งภาษาเกมใน Steam เป็น **English** และปิดเกม
- ใช้ไฟล์เกมต้นฉบับตรงรุ่น ตัวติดตั้งตรวจ SHA-256 ของ EXE และ UMD
- มี Windows PowerShell 5.1 และพื้นที่ว่างอย่างน้อย 2 GB ในไดรฟ์เกม
- ถ้ามีม็อดภาษาอื่นหรือเคยลงฉบับพัฒนาด้วย CLI ให้คืนไฟล์ต้นฉบับก่อน
  ตัวติดตั้ง RC จะไม่รับ UMD ที่ถูกแก้ไขแล้ว

แพ็กนี้ไม่ต้องติดตั้ง Python, HarfBuzz หรือฟอนต์ลง Windows
ไฟล์ Source code บน GitHub เป็นซอร์สสำหรับนักพัฒนา ใช้ติดตั้งแทน ZIP ม็อดไม่ได้

## ติดตั้ง

1. แตก ZIP ทั้งหมดลงโฟลเดอร์ใหม่ก่อน เปิดตัวติดตั้งจากใน ZIP ไม่ได้
2. เปิด `Check.cmd` เพื่อตรวจความเข้ากันได้ หากไม่ผ่านให้ดูข้อความ ERROR ก่อน
3. เปิด `Install.cmd` ตัวติดตั้งค้นหาเกมจาก Steam libraries อัตโนมัติ
4. ถ้าถามพาธ ให้ใส่โฟลเดอร์เกมที่มี **System และ Data** อยู่ข้างใน เช่น
   `D:\SteamLibrary\steamapps\common\Splintercell Chaos Theory`
5. รอข้อความ **Installed** และจำนวนไฟล์ที่ตรวจผ่าน **73 ไฟล์**
6. เปิดเกมจาก Steam เปิดคำบรรยายในตัวเลือกเกม แล้วเริ่มทดสอบ

หากขึ้น Access denied ใน Program Files ให้คลิกขวา `Install.cmd` > **Run as administrator**
การระบุพาธจาก PowerShell ทำได้ดังนี้ โดยรันจากโฟลเดอร์ที่แตกแพ็ก:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\Install.ps1 -GameDir "D:\SteamLibrary\steamapps\common\Splintercell Chaos Theory"
```

ตัวติดตั้งสร้าง UMD จากไฟล์เดิมของผู้เล่น ตรวจผลลัพธ์ แล้วลง localization/font/startup files
สำรองไฟล์ที่มีอยู่ก่อนติดตั้ง และเก็บข้อมูลว่าไฟล์ใดม็อดเพิ่มใหม่
ไม่แก้ EXE, INI, เซฟ, โปรไฟล์ หรือ WidescreenFix

## ตรวจหลังติดตั้ง

เปิด `Verify.cmd` จากแพ็กเดิม ระบบตรวจ SHA-256 ของไฟล์เกมทั้ง 73 ไฟล์
การตรวจผ่านยืนยันว่าไฟล์ติดตั้งครบและตรงกับ RC นี้
การแสดงสระ/วรรณยุกต์ การตัดบรรทัด และข้อความล้นช่องยังต้องดูในเกม

เปิด `Install.cmd` ซ้ำได้ ระบบจะตรวจไฟล์ที่ลงไว้และแจ้งว่าติดตั้งแล้ว
จะไม่สร้าง backup ทับต้นฉบับด้วยไฟล์ม็อด

## ถอนม็อด

1. ปิดเกมแล้วเปิด `Uninstall.cmd` จากแพ็กเดียวกับที่ติดตั้ง
2. รอข้อความ **Uninstall complete**
3. ไฟล์ที่มีอยู่ก่อนติดตั้งจะถูกคืน ส่วนไฟล์ที่ม็อดเพิ่มใหม่จะถูกลบ
4. เก็บ `.chaos-theory-thai` ในโฟลเดอร์เกมไว้จนกว่าจะถอนสำเร็จ
   หลังถอนสำเร็จ ตัวถอนยังเก็บ backup ต่อและอาจเหลือโฟลเดอร์ว่าง

ตัวถอนนี้ใช้กับการติดตั้งผ่านแพ็ก RC เท่านั้น
การลงด้วย `src/cli.py install` ใช้ backup ของโปรเจกต์และไม่ได้สร้างสถานะของตัวติดตั้ง RC
ถ้าแก้ไฟล์ม็อดหลังติดตั้ง ตัวถอนจะหยุดเพื่อไม่ทับงานนั้น ให้สำรองงานแล้วคืนไฟล์ RC ก่อนถอน
หากติดตั้งถูกขัดจังหวะ ให้ใช้ `Uninstall.cmd` คืนจาก backup ก่อนลองติดตั้งอีกครั้ง

## แก้ปัญหา

| อาการ | วิธีตรวจ/แก้ |
| --- | --- |
| UMD หรือ EXE มี SHA-256 mismatch | ใช้เกมคนละฉบับหรือมีม็อดเดิม คืนต้นฉบับก่อนและตั้งภาษาเป็น English |
| แพ็กมี SHA-256 mismatch | ดาวน์โหลด/แตก ZIP ใหม่ และเทียบ checksum ที่ให้มาพร้อม Release |
| Access denied | ปิดเกมและเปิด CMD launcher แบบ Run as administrator |
| หาโฟลเดอร์เกมไม่พบ | ระบุ game root ที่มี System/Data หรือใช้ `-GameDir` |
| ฟอนต์หรือข้อความเพี้ยน | ใช้ Verify.cmd ตรวจไฟล์ และอย่าผสมข้อความ/ฟอนต์คนละบิลด์ |
| Windows แจ้งไฟล์มาจากอินเทอร์เน็ต | เมื่อตรวจแหล่งที่มาและ checksum แล้ว ใช้ Properties > Unblock ที่ ZIP แล้วแตกใหม่ |
| ข้อความภาษาไทยล้นช่อง | ส่งภาพพร้อมด่าน ความละเอียด และรุ่นม็อดใน Issues |

หากจำเป็นต้องคืนเกมผ่าน Steam Verify integrity ให้สำรองม็อดอื่นก่อนเพราะ Steam อาจแทนที่ไฟล์เหล่านั้น
Steam อาจเก็บ loose files ที่ม็อดเพิ่มไว้ จึงควรใช้ตัวถอนของม็อดก่อนเมื่อมี backup ที่สมบูรณ์

ค่าภาษาที่ตัวติดตั้งตรวจคือ `Language=int` ในส่วน `[Localization]` ของ `System/Settings.ini`,
`Language=int` ในส่วน `[Engine.Engine]` และ `UseDynamicDataFile=true` ในส่วน `[Init]`
ของ `System/SplinterCell3.ini` ตัวติดตั้งจะไม่แก้ค่าเหล่านี้เอง

## ตรวจ checksum ของ ZIP

ดาวน์โหลด `.zip.sha256` จาก Assets เดียวกันแล้วเทียบกับ:

```powershell
Get-FileHash .\ChaosTheory-Thai-1.0.0-rc1.zip -Algorithm SHA256
```

## แจ้งปัญหา

ใช้ [GitHub Issues](https://github.com/mgprona/chaos-theory-thai/issues/new/choose)
แนบรุ่นม็อด รุ่นเกม ความละเอียด ด่าน/หน้าจอ ขั้นตอนทำซ้ำ ภาพ และข้อความจาก Verify.cmd
RC1 ยังไม่มีหลักฐานเล่นครบเกมด้วยบิลด์นี้ ดู [ขอบเขตการตรวจ](RELEASE_READINESS.md)

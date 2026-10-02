# Thai Glossary & Translation Contract

แหล่งอ้างอิงเดียวสำหรับศัพท์ ชื่อเฉพาะ และกติกาการแปลของมอดนี้
ใช้คู่กับ `docs/TRANSLATION_PLAN.md` (แผนงาน) และ `out/translation-review/REVIEW.md` (ผลรีวิวคุณภาพ)

---

## 1. กติกาบังคับ (ตรวจด้วยเทสต์)

| กฎ | รายละเอียด |
| --- | --- |
| Encoding | ค่า `th` ต้องเข้ารหัส CP874 ได้ (ไบต์ `<128` หรือ `161–251`) ยกเว้นสตริงที่ต้นฉบับมีอักขระ `•` (U+2022) อยู่แล้ว |
| อักขระต้องห้าม | `“ ” ‘ ’ …` — ใช้ `"` และ `...` |
| ช่องว่างหัว–ท้าย | ต้องตรงกับ `en` ทุกตัวอักษร |
| Placeholder | `%s` `%i` `%1` `{0}` ต้องตรงกับ `en` ทั้งจำนวนและลำดับ |
| Template ว่าง | ถ้า `en` เป็นค่าว่าง/ช่องว่างล้วน **ห้ามเติมข้อความ** — `th` ต้องเป็นค่าเดียวกัน (`""`) |
| ประโยคซ้ำ | `en` ที่เหมือนกันทุกตัวอักษรต้องได้ `th` ที่เหมือนกันทุกตัวอักษร (ห้ามแปลต่างกัน) |
| ป้ายผู้พูด | `th` ต้องมีป้ายผู้พูด (`ชื่อ - ข้อความ`) **ก็ต่อเมื่อ** `en` มี — ห้ามเพิ่มหรือตัดเอง |
| ตัวเลข | คงตัวเลขเดิม เว้นแต่ต้นฉบับเขียนเป็นคำ (เช่น `3` → "สาม" ทำได้) |

## 2. ชื่อบุคคล (ล็อกแล้ว)

| EN | ไทย |
| --- | --- |
| Sam Fisher | แซม ฟิชเชอร์ (สาย: ฟิชเชอร์) |
| Lambert | แลมเบิร์ต |
| Anna Grimsdottir | แอนนา กริมส์ดอตเตียร์ |
| Redding | เรดดิง |
| Partridge | พาร์ทริดจ์ |
| Douglas Shetland | ดักลาส เชตแลนด์ (ชื่อย่อในบทพูด: ดั๊ก) |
| Bruce Morgenholt | บรูซ มอร์เกนโฮลต์ |
| Hugo Lacerda | ฮูโก ลาแซร์ดา |
| Milan Nedich / Milos Nowak | มิลาน เนดิช / มิโลส โนวัก |
| Zherkezhi | เซอร์เคซี |
| Dvorak | ดโวรัก |
| Admiral Toshiro Otomo | พลเรือเอก โทชิโร โอโตโม |
| Jong Pom-chu | จง พอมจู |
| Hector | เฮกตอร์ |
| Frances Coen | ฟรานเซส โคเอน |
| Maria Narcissa | มาเรีย นาร์ซิสซา |

## 3. องค์กร / หน่วยงาน

| EN | ไทย |
| --- | --- |
| Third Echelon (หน่วย) | เธิร์ดเอเชลอน (เรียกสั้น: เอเชลอน) |
| Displace International | ดิสเพลส อินเทอร์เนชันแนล |
| Red Nishin | เรดนิชิน |
| NKA | NKA (คงอักษรละติน) |
| I-SDF | I-SDF (คงอักษรละติน) |
| OPSAT / EEV / OCP / SHADOWNET | คงอักษรละติน |
| Fifth Freedom | สิทธิเสรีภาพขั้นที่ 5 (ไม่ต้องวงเล็บอังกฤษ) |

## 4. คำเทคนิค / อาวุธ

| EN | ไทย |
| --- | --- |
| Masse Kernels | มาสส์เคอร์เนล |
| Sticky Camera | กล้องสติ๊กกี้ |
| Optic Cable | กล้องสายเคเบิล |
| SC-20K / SC Pistol | คงอักษรละติน |
| Medkit | ชุดปฐมพยาบาล |
| Wall Mine | กับระเบิดติดผนัง |
| extraction / exfiltrate | จุดถอนกำลัง / ถอนกำลัง |
| interrogation | การเค้นข้อมูล |
| alarm stage | ระดับสัญญาณเตือนภัยขั้นที่ … |
| Enemies Standing Down | ศัตรูหยุดปฏิบัติการ |
| gear/body/bearing (มุมยิง) | มุมทิศ (bearing) — ห้ามใช้ "แบริ่ง" |

## 5. เมนูและ UI

- ค่าตัวเลือกกราฟิกเป็นไทยตามป้าย: `ลบรอยหยัก 4X`, `กรองพื้นผิว 8X`, `SHADER MODEL 2.0` (คงอักษรละตินเฉพาะ SHADER MODEL)
- ทิศเข็มทิศคง `N NE E SE S SW W NW`
- `ALARMS TRIGGERED` = `สัญญาณเตือนภัยที่ดังขึ้น` (ใช้เหมือนกันทุกเมนู)
- `QUIT TO DEMOS MENU` = `ออกไปเมนูเดโม`
- `Sergeant` = สิบเอก · `Corporal` = สิบโท · `Warrant Officer` = พันจ่า

## 6. วิธีตรวจก่อนคอมมิต

```powershell
$env:PYTHONIOENCODING = 'utf-8'
.\.venv\Scripts\python.exe out/translation-review/verify_all.py   # กติกาข้อ 1
.\.venv\Scripts\python.exe -m unittest discover -s tests          # เทสต์รวม (36)
.\.venv\Scripts\python.exe tools/validate_translations.py         # round-trip story + PUA
.\.venv\Scripts\python.exe build.py                               # คอมไพล์ + ฟอนต์ + UMD
```

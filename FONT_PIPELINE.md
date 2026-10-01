# Chakra Petch: HarfBuzz offline และ PUA สำหรับเมนู

ระบบนี้แก้ฟอนต์ **Magma** ที่หน้าเมนูหลัก การตั้งค่า HUD และ OPSAT ใช้
ไม่ต้องติดตั้ง HarfBuzz ลงในตัวเกม และไม่แก้ executable

## กระบวนการบิลด์

1. อ่านข้อความไทยจาก JSON ของไฟล์ที่ระบุใน `unicode_ui_stems` ใน config.json
2. ให้ HarfBuzz shape ข้อความไทยทั้งช่วงด้วย Chakra Petch รวม GSUB และ GPOS
3. แยกผลตาม HarfBuzz cluster เพื่อเก็บพยัญชนะ สระ และวรรณยุกต์ที่ต้องอยู่ด้วยกัน
4. ใช้ FreeType วาด glyph ID ที่ HarfBuzz เลือก ณ พิกัดที่คำนวณไว้ แล้วรวมเป็น bitmap ของกลุ่มอักษร
5. จัดกลุ่มอักษรลงช่อง PUA เริ่ม U+E000 ใช้แผนผังเดียวกันสำหรับฟอนต์ทั้งสองขนาด
6. เพิ่ม glyph record และ sparse Unicode lookup ของ PUA ลงใน MFT
7. แปลงข้อความในไฟล์ .int เป็น PUA แล้วบันทึก UTF-16LE พร้อม BOM

JSON คำแปลยังเป็นไทยปกติ การแปลงเกิดเฉพาะไฟล์ผลลัพธ์
เมื่อแก้คำแปลหรือเปลี่ยนฟอนต์ ต้องบิลด์ทั้งข้อความและฟอนต์ใหม่พร้อมกัน
ห้ามจับคู่ไฟล์ .int เก่ากับ MFT ใหม่ เพราะการจัดรหัส PUA อาจเปลี่ยนตามคลังข้อความ
แผนผังพร้อม hash ของฟอนต์อยู่ที่ `dist/thai_pua_map.json`

## ปัญหาที่แก้

- ฟอนต์เดิมมี lookup เฉพาะ Unicode U+0000–U+00FF จึงไม่มี glyph lookup ภาษาไทย
- การใช้ CP874 โดยไม่มี BOM ขึ้นอยู่กับการอ่าน ANSI ของเกมและ Windows
- ตัวสร้างฟอนต์เดิมเขียนทับ atlas หน้าสุดท้าย ทั้งที่ยังมีอักษรอังกฤษ เช่น i และ j อยู่ในหน้านั้น
- การวาดตัวอักษรทีละตัวพร้อมระยะเดินเท่ากันทำให้สระและวรรณยุกต์ไม่เกาะพยัญชนะ

ตัวสร้างใหม่เก็บภาพอักษรเดิมไว้ ขยาย atlas เป็น 512×512 ปรับ UV ของอักษรเดิม
และเพิ่มภาพไทยในพื้นที่ว่าง ไม่ทับภาพอังกฤษและไม่เพิ่มชื่อไฟล์ใหม่ใน UMD

## คำสั่ง

```bash
python -m pip install -r requirements.txt
python build.py
python -m unittest discover -s tests -v
python tools/preview_magma.py
python src/cli.py install
```

ภาพ `dist/magma_thai_pua_preview.png` จำลองการอ่าน MFT/atlas ที่สร้างจริง
ใช้ตรวจรูปอักษรและ offsets แต่ไม่ใช่ภาพที่จับจากเกม
การตรวจอัตโนมัติครอบคลุมข้อความไทยที่คอมไพล์ทุกบรรทัด lookup PUA ภาพอักษรเดิม
และภาพ PUA เทียบกับ glyph IDs/positions จาก HarfBuzz
ยังต้องตรวจการโหลด UTF-16/PUA และการตัดบรรทัดในเกมจริง

## ขอบเขต

ใช้กับข้อความที่บิลด์ไว้ล่วงหน้าและฟอนต์ Magma สองตัว: Bios Three Regular 20 และ Prototype Regular 13
ข้อความไทยที่ผู้เล่นพิมพ์ขึ้นใหม่ไม่ได้ผ่าน offline shaping
ฟอนต์ PCX ในเกมยังใช้ระบบเดิม และเนื้อเรื่องที่ช่อง th ว่างยังแสดงอังกฤษ
ไม่ได้อ้างว่าฟอนต์ทั้งเกมรองรับไทยสมบูรณ์แล้ว

## แหล่งอ้างอิง

- [HarfBuzz: OpenType features / GSUB / GPOS](https://harfbuzz.github.io/shaping-opentype-features.html)
- [HarfBuzz: clusters และการรวม glyph](https://harfbuzz.github.io/working-with-harfbuzz-clusters.html)
- [FC2MFTConverter: sparse Unicode lookup](https://github.com/eprilx/FC2MFTConverter/blob/master/FC2MFTConverter/MFT/MFTFormat.cs)
  ใช้อ้างอิงโครงสร้าง lookup เท่านั้น layout ของ glyph record ใน Chaos Theory ต่างจาก Far Cry 2

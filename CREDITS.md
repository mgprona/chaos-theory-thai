# เครดิต

คำแปลและการทำม็อดภาษาไทย: **MennzKTR**

เกม ตัวละคร ภาพ ศัพท์เฉพาะ และสินทรัพย์ฟอนต์เดิมเป็นของเจ้าของสิทธิ์เดิม
โปรเจกต์นี้เป็นม็อดชุมชนสำหรับใช้ร่วมกับเกมที่ผู้เล่นมีอยู่เอง
Release ไม่รวม executable, full UMD, เซฟหรือข้อมูลบัญชีผู้เล่น

## ฟอนต์ภาษาไทย

- **Chakra Petch Bold / SemiBold** ใช้สร้าง glyph ไทยในบิลด์ปัจจุบัน
  Copyright 2018 The Chakra Petch Project Authors
  [ต้นทาง](https://github.com/m4rc1e/Chakra-Petch.git) · [SIL OFL 1.1](release/licenses/ChakraPetch-OFL.txt)
- **Kanit** เป็นฟอนต์ที่เก็บไว้ใน source repository; ไม่ได้ใช้ใน RC1 ปัจจุบัน
  Copyright 2020 The Kanit Project Authors
  [ต้นทาง](https://github.com/cadsondemak/kanit) · [SIL OFL 1.1](data/fonts/licenses/Kanit-OFL.txt)

glyph ไทยที่สร้างจาก Chakra Petch คงเงื่อนไข OFL ของฟอนต์
license นี้ไม่ได้ใช้แทนสิทธิ์ของเกมหรือกำหนด license ใหม่ให้คำแปล/โค้ดทั้งโปรเจกต์

## เครื่องมือบิลด์

Python, Pillow, NumPy, HarfBuzz (`uharfbuzz`) และ FreeType (`freetype-py`)
ใช้ตอนสร้างม็อด; ผู้เล่นไม่ต้องติดตั้งเครื่องมือเหล่านี้
รายละเอียดรุ่น dependencies อยู่ใน `requirements.txt`

## เอกสารอ้างอิงเทคนิค

[HarfBuzz](https://harfbuzz.github.io/) และ
[FC2MFTConverter](https://github.com/eprilx/FC2MFTConverter)
ใช้ประกอบการศึกษา shaping และ sparse Unicode lookup
glyph record ของ Chaos Theory ใช้ layout ที่ตรวจจากเกมนี้เอง

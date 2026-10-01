# Tom Clancy's Splinter Cell: Chaos Theory - Thai Translation Mod

ชุดเครื่องมือและโครงสร้างโปรเจกต์ม็อดแปลภาษาไทยสำหรับเกม **Tom Clancy's Splinter Cell Chaos Theory** (PC / Steam)
รองรับระบบการแกะ/แพ็กไฟล์ `dynamic-pc.umd`, การแยกไฟล์ภาษา Official ทั้ง 5 ภาษา (English, French, German, Spanish, Italian), การจัดการไฟล์แปลในรูปแบบ JSON ที่ใช้งานง่าย, และระบบสร้างฟอนต์ภาษาไทยลงบน PCX Bitmap Fonts ของ Unreal Engine 2

---

## 📁 โครงสร้างโปรเจกต์ (Project Architecture)

```
Chaos Theory Thai/
├── config.json                     # การตั้งค่าพาธตัวเกม, ภาษา, และ Encoding
├── build.py                        # สคริปต์หลักสำหรับคอมไพล์และบิลด์ม็อด
├── README.md                       # เอกสารแนะนำการใช้งาน
├── src/
│   ├── cli.py                      # Command-Line Interface รวมคำสั่งทั้งหมด
│   ├── core/                       # แกนหลักระบบ Engine Parsers
│   │   ├── umd_parser.py           # ตัวอ่าน/แยก/แพ็ก UMD Archive (FCompactIndex & TOC)
│   │   ├── ini_codec.py            # ตัวอ่าน/เขียน Unreal Engine INI (CP1252, CP874, UTF-16LE)
│   │   └── pcx_font.py             # ตัวจัดการ 8-bit Indexed PCX Font และ Cell Delimiters
│   └── pipeline/                   # Pipeline การประมวลผล
│       ├── extractor.py            # ดึงไฟล์ภาษา 236 ไฟล์และฟอนต์จากเกม
│       ├── merger.py               # รวม 5 ภาษาเป็น JSON Translation (en, fr, de, es, it, th)
│       ├── compiler.py             # แปลง JSON กลับเป็นไฟล์ .int ภาษาไทย
│       └── font_builder.py         # วาดฟอนต์ไทยลงบน PCX Font Bitmaps
├── data/
│   ├── raw_official/               # ไฟล์ต้นฉบับ Official ทั้งหมดที่ดึงออกมาจากเกม
│   │   ├── int/                    # ภาษาอังกฤษ (52 ไฟล์)
│   │   ├── fra/                    # ภาษาฝรั่งเศส (46 ไฟล์)
│   │   ├── deu/                    # ภาษาเยอรมัน (46 ไฟล์)
│   │   ├── esp/                    # ภาษาสเปน (46 ไฟล์)
│   │   ├── ita/                    # ภาษาอิตาลี (46 ไฟล์)
│   │   └── fonts/                  # ฟอนต์ต้นฉบับ (Magma UI และ PCX In-game Fonts)
│   ├── translations/               # ไฟล์ JSON สำหรับแปลภาษาไทย (แบ่งหมวดหมู่ชัดเจน)
│   │   ├── story/                  # 19 ภารกิจเนื้อเรื่อง (รวมไฟล์เนื้อเรื่องและบทพูด P_ เข้าด้วยกัน)
│   │   ├── ui/                     # เมนูหลัก, HUD, หน้าโหลด, และเครดิต
│   │   └── opsat/                  # อุปกรณ์, ฐานข้อมูล OPSAT, และข้อความระบบ
│   └── fonts/                      # ฟอนต์สำหรับใช้สร้างตัวอักษรไทย (TTF/OTF)
├── dist/                           # ผลลัพธ์จากการ Build พร้อมนำไปลงเกม
│   ├── loose/                      # ไฟล์ .int ที่คอมไพล์แล้วแบบ Loose Files
│   ├── System/                     # dynamic-pc.umd ที่แพ็กไฟล์แปลไทยแล้ว
│   └── Data/Textures/Font/         # PCX Font Bitmaps ภาษาไทยที่สร้างเสร็จแล้ว
├── backups/                        # โฟลเดอร์สำรองไฟล์เกมต้นฉบับ
└── tests/                          # Automated Unit Tests
```

---

## 🚀 วิธีการใช้งาน (Quick Start)

ติดตั้งไลบรารีก่อนบิลด์:
```bash
python -m pip install -r requirements.txt
```

เมนู Magma ใช้ **Chakra Petch + HarfBuzz แบบ offline + PUA** แล้ว:
คำนวณ GSUB/GPOS ตอนบิลด์ วาดกลุ่มอักษรไทยลง bitmap และแปลงเฉพาะไฟล์เกมเป็น UTF-16LE พร้อม BOM
ไฟล์ JSON ต้นฉบับยังอ่านและแก้ไขเป็นภาษาไทยตามปกติ ดูรายละเอียดที่ [FONT_PIPELINE.md](FONT_PIPELINE.md)

องค์ความรู้สำหรับนำเทคนิคไปใช้กับเกมอื่น: [คู่มือม็อดฟอนต์ไทยสำหรับเกมเก่า](docs/THAI_FONT_MODDING.md)
ครอบคลุมการตรวจ encoding/ฟอนต์ที่โหลดจริง, offline shaping, PUA, atlas, metrics และการทดสอบ

### 1. ดูความคืบหน้าการแปล (Translation Progress)
เรียกดูสถิติจำนวนคำและเปอร์เซ็นต์ที่แปลไปแล้ว:
```bash
python build.py --stats
```

### 2. บิลด์ม็อด (Compile & Build Fonts)
คอมไพล์ข้อความแปลและสร้างฟอนต์ภาษาไทย:
```bash
python build.py
```
ไฟล์ผลลัพธ์จะอยู่ที่โฟลเดอร์ `dist/`

### 3. แพ็กไฟล์ `dynamic-pc.umd` (Repack UMD)
สร้างไฟล์ UMD ใหม่ที่ใส่คำแปลภาษาไทยเข้าไป:
```bash
python build.py --umd
```

### 4. ติดตั้งม็อดลงตัวเกม (Install Mod)
ติดตั้งไฟล์ที่คอมไพล์แล้วลงในโฟลเดอร์เกม Splinter Cell Chaos Theory โดยอัตโนมัติ (จะทำการสำรองไฟล์เดิมไว้ใน `backups/` ก่อนเสมอ):
```bash
python build.py --install
# หรือติดตั้งพร้อมแพ็ก UMD
python build.py --umd --install
```

---

## ✍️ แนวทางการแปล (Translation Workflow)

ไฟล์ข้อความทั้งหมดถูกรวมไว้ใน `data/translations/` ในรูปแบบ **JSON (UTF-8)** โดยแบ่งออกเป็น 3 หมวดหมู่หลัก:

1. **`data/translations/story/`**: รวมภารกิจเนื้อเรื่อง 19 ภารกิจ เช่น `01_Lighthouse.json`
   - รวบรวมทั้ง Objectives, อีเมล, คำสั่งภารกิจ และบทพูดวิทยุ/การสอบปากคำ (`P_01_Lighthouse`) ไว้อย่างครบถ้วนในไฟล์เดียว
2. **`data/translations/ui/`**: เมนูเกม, HUD, Loading Screens
3. **`data/translations/opsat/`**: รายละเอียดอาวุธและอุปกรณ์

### รูปแบบของ Key ใน JSON
แต่ละข้อความจะมีข้อความต้นฉบับ Official ครบทั้ง 5 ภาษาเพื่อใช้เทียบเคียงบริบท พร้อมช่อง `"th"` สำหรับใส่คำแปลภาษาไทย:

```json
"Speech_0001L": {
  "en": "QUINTON: Hey!  Stefano... look here!",
  "fr": "Hé, Stefano ! Regarde-moi ça !",
  "de": "Hey! Stefano ... schau dir das an!",
  "es": "¡Eh, Stefano! ¡Mira aquí!",
  "it": "Ehi! Stefano... guarda qui!",
  "th": "ควินตัน: เฮ้ย! สเตฟาโน... มาดูนี่สิ!"
}
```

> **หมายเหตุสำคัญ:** หากช่อง `"th"` เว้นว่างไว้เป็น `""` ระบบบิลด์จะดึงข้อความภาษาอังกฤษ (`"en"`) มาแสดงเป็นค่าเริ่มต้นให้อัตโนมัติ ทำให้เกมไม่แครชและสามารถทยอยแปลทีละส่วนได้อย่างราบรื่น

---

## 🔤 ระบบฟอนต์ภาษาไทย (Font System)

เกม Splinter Cell Chaos Theory ใช้ฟอนต์ 2 ระบบ:
1. **In-game 3D Subtitles & HUD Fonts** (ไฟล์ `.pcx` ใน `Data\Textures\Font\`):
   - `txt_hud.pcx`
   - `txt_mission.pcx`
   - `txt_integration.pcx`
   - `titre_regular_integration.pcx`
   - `titre_bold_integration.pcx`
   - เป็นภาพ 8-bit Indexed Palette โดยมีเส้นขอบสีม่วง (Index 255) กำกับความกว้าง/ความสูงของแต่ละตัวอักษร
   - ระบบ `src/pipeline/font_builder.py` จะวาดตัวอักษรภาษาไทย (รหัส Windows-874 / CP874: 161–251) ลงในช่องตัวอักษรอย่างแม่นยำ พร้อมทั้งสร้างไฟล์พรีวิว `.png` ให้ตรวจเช็กได้ง่าย
2. **2D Magma UI Fonts** (ไฟล์ `.tga`, `.mft`, `.ttf` ใน `Data\Magma\DataPC\Fonts\`):
   - ดึงไฟล์ต้นฉบับทั้งหมด 38 ไฟล์เก็บไว้ใน `data/raw_official/fonts/magma/`

---

## 🛠️ รายการคำสั่ง CLI เพิ่มเติม (`src/cli.py`)

- `python src/cli.py extract`: ดึงไฟล์ภาษา 236 ไฟล์และฟอนต์จากตัวเกม
- `python src/cli.py merge`: อัปเดต/รวมไฟล์แปล JSON โดยคงคำแปลไทยเดิมที่เคยแปลไว้
- `python src/cli.py compile`: คอมไพล์ไฟล์ JSON ออกมาเป็นไฟล์ `.int`
- `python src/cli.py build-fonts [--font PATH]`: สร้างฟอนต์ไทย (สามารถระบุไฟล์ `.ttf` เองได้)
- `python src/cli.py build-umd`: แพ็ก `dynamic-pc.umd`
- `python src/cli.py stats`: ตรวจสอบสถานะและเปอร์เซ็นต์การแปล
- `python src/cli.py backup`: สำรองไฟล์เกมเดิม
- `python src/cli.py install`: นำไฟล์ม็อดไปติดตั้งในเกม

---

## 🧪 การทดสอบระบบ (Automated Tests)

สามารถรันชุดการทดสอบทั้งหมดของระบบเพื่อตรวจสอบความถูกต้อง:
```bash
python -m unittest discover -s tests -v
```
ครอบคลุมการตรวจสอบ CompactIndex roundtrip, INI parser/serializer, PCX delimiter cell detection, JSON translation schema, และ Compiler.

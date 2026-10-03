# แผนการขัดเกลางานแปลระดับ Professional Localization

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** ขัดเกลาและยกระดับงานแปลภาษาไทยของ Splinter Cell: Chaos Theory ให้เป็นมาตรฐาน Professional Localization ครบทุกมิติ ทั้งความสม่ำเสมอของสรรพนาม, การเก็บตก Glossary, สำนวนภาษาที่เป็นธรรมชาติ และความกระชับของ UI

**Architecture:** ปรับแก้ค่า `th` ในไฟล์ JSON ใน `data/translations/{story,ui}/` โดยคงโครงสร้าง คีย์ ป้ายผู้พูด และ placeholders ทุกตัวตามกติกา `docs/GLOSSARY.md` จากนั้นรันการตรวจสอบผ่านชุดเทสต์ `tests/`, `verify_all.py`, `validate_translations.py` และรีบิลด์ฟอนต์/UMD ผ่าน `build.py`

**Tech Stack:** Python 3.11+, JSON (UTF-8), CP874 codec, HarfBuzz/FreeType font toolchain, UMD repacker

**Spec:** [`docs/GLOSSARY.md`](file:///c:/Users/MennzKTR/chaos-theory-thai/docs/GLOSSARY.md) and [`out/translation-review/REVIEW.md`](file:///c:/Users/MennzKTR/chaos-theory-thai/out/translation-review/REVIEW.md)

## Global Constraints
- ห้ามแตะต้องโครงสร้าง คีย์ หรือค่าภาษาอื่น (`en`, `fr`, `de`, `es`, `it`)
- ค่า `th` ต้องเข้ารหัส CP874 ได้ 100%
- ป้ายผู้พูด (`ชื่อ - ข้อความ`) ต้องตรงกับต้นฉบับภาษาอังกฤษเป๊ะ
- ช่องว่างหัว-ท้าย และ placeholder (`%s`, `%i`, ฯลฯ) ต้องตรงกับ `en` ทุกประการ

---

### Task 1: Pronoun and Tone Alignment in Mission 2 (`02_CargoShip.json`) & Mission 7 (`07_Battery.json`)

**Files:**
- Modify: `data/translations/story/02_CargoShip.json`
- Modify: `data/translations/story/07_Battery.json`

- [ ] **Step 1: แก้ไขสรรพนามของ Sam Fisher ใน `02_CargoShip.json` ให้ใช้ `ฉัน` และสอดคล้องกับบุคลิกแซม**
  - `P_02_CargoShip_LambertComms::Speech_0007L` -> เปลี่ยน "ผมได้กลิ่นแล้ว" เป็น "ฉันได้กลิ่นแล้ว"
  - `P_02_CargoShip_LambertComms::Speech_0020L` -> เปลี่ยน "ผมเข้าใจแล้ว... ผมจะระมัดระวังเป็นพิเศษ" เป็น "เข้าใจแล้ว... ฉันจะระวังเป็นพิเศษ"
  - `P_02_CargoShip_LambertComms::Speech_0023L` -> เปลี่ยน "สงสัยผมคงต้องกวาดค้น..." เป็น "สงสัยฉันคงต้องกวาดค้น..."
  - `P_02_CargoShip_LambertComms::Speech_0029L` -> เปลี่ยน "เดี๋ยวผมหาดู" เป็น "เดี๋ยวฉันหาดู"
  - `P_02_CargoShip_LambertComms::Speech_0034L` -> เปลี่ยน "คุณอยากให้ผมสแกนลังอาวุธเพิ่มอีกไหม" เป็น "นายอยากให้ฉันสแกนลังอาวุธเพิ่มอีกไหม"
  - `P_02_CargoShip_LambertComms::Speech_0057L` -> เปลี่ยน "เดี๋ยวผมจะลองสำรวจดู" เป็น "เดี๋ยวฉันจะลองสำรวจดู"
  - `P_02_CargoShip_LambertComms::Speech_0063L` -> เปลี่ยน "ผมล่ะชอบพวกคนนั่งโต๊ะจริงๆ" เป็น "ฉันล่ะชอบพวกคนนั่งโต๊ะจริงๆ"
  - `P_02_CargoShip_LambertComms::Speech_0064L` -> เปลี่ยน "ผมจำชื่อนั้นได้" เป็น "ฉันจำชื่อนั้นได้"
  - `P_02_CargoShip_LambertComms::Speech_0073L` & `Speech_0084L` -> เปลี่ยน "ผมลืมเอาช่อดอกไม้ติดอกมาด้วยสิ" เป็น "ฉันลืมเอาช่อดอกไม้ติดอกมาด้วยสิ"
  - `P_02_CargoShip_LambertComms::Speech_0086L` -> เปลี่ยน "ผมจะพบบัญชีรายการขนส่งที่นั่นใช่ไหม?" เป็น "ฉันจะพบบัญชีรายการขนส่งที่นั่นใช่ไหม?"
  - `P_02_CargoShip_LambertComms::Speech_0100L` -> เปลี่ยน "รับทราบ ผมจะย้อนกลับไป" เป็น "รับทราบ ฉันจะย้อนกลับไป"

- [ ] **Step 2: แก้ไขสรรพนามของ Sam Fisher ใน `07_Battery.json`**
  - `P_07_Battery_Communications::Speech_0004L` -> เปลี่ยน "คืนนี้มีอะไรให้ผมช่วยอีกไหม?" เป็น "คืนนี้มีอะไรให้ฉันช่วยอีกไหม?"

- [ ] **Step 3: ตรวจสอบความถูกต้องของ CP874 และรันเทสต์**
  - Run: `.\.venv\Scripts\python.exe -m unittest tests/test_toolchain.py`

---

### Task 2: Terminology and Glossary Normalization

**Files:**
- Modify: `data/translations/story/00_Training.json`
- Modify: `data/translations/story/01_Lighthouse.json`
- Modify: `data/translations/story/01_Panama.json`
- Modify: `data/translations/story/02_CargoShip.json`
- Modify: `data/translations/story/03_ChemBunker.json`
- Modify: `data/translations/story/11_KokuboSosho.json`
- Modify: `data/translations/ui/loading_screens.json`

- [ ] **Step 1: ปรับแก้ `ดิสเพลส อินเตอร์เนชันแนล` เป็น `ดิสเพลส อินเทอร์เนชันแนล`**
  - `00_Training.json::P_00_Training_Broadcast::Speech_0009L`
  - `00_Training.json::P_00_Training_CnvRedding::Speech_0037L`
  - `01_Lighthouse.json::GENERAL::Briefing_SHETLAND`
  - `01_Lighthouse.json::P_01_Lighthouse_Briefings::Speech_0005L`
  - `loading_screens.json::05_displace01::Location`
  - `loading_screens.json::05_displace01::Overview`

- [ ] **Step 2: แก้ไขคำอังกฤษตกหล่น `Masse` ใน `loading_screens.json`**
  - `loading_screens.json::07_battery::Overview` -> เปลี่ยน "ด้วยรหัส Masse" เป็น "ด้วยอัลกอริทึมมาสส์"

- [ ] **Step 3: ปรับแก้ `สติ๊กกี้ช็อกเกอร์` ให้เป็น `กระสุนช็อตไฟฟ้า`**
  - `11_KokuboSosho.json::P_11_KokuboSosho_InterroBasement::Note_0016L` -> "หากระสุนช็อตไฟฟ้าได้ในห้องเก็บของ"

- [ ] **Step 4: ปรับ `จุดรับตัวหลัก` ให้เป็น `จุดถอนกำลังหลัก`**
  - `01_Lighthouse.json::P_01_Lighthouse_GoalsActiv::Objective_0033`
  - `01_Panama.json::P_01_Panama_Popups::POPUPMESSAGE_0015`

- [ ] **Step 5: ปรับศัพท์ War Room ใน `11_KokuboSosho.json` ให้สมจริง**
  - `P_11_KokuboSosho_InterroHostagers::Speech_0016L` -> "ฟิชเชอร์ - ห้องวอร์รูมอยู่ที่ไหน?"
  - `P_11_KokuboSosho_InterroWarRoom::Speech_0003L` -> "ฟิชเชอร์ - จะเข้าไปในห้องวอร์รูมได้ยังไง?"

- [ ] **Step 6: ปรับชื่อโพรโทคอลต้านไวรัสใน `03_ChemBunker.json` ให้ตรงกับ `hud.json`**
  - `03_ChemBunker.json::P_03_Chemical_Objectives::Note_0009L` -> "โพรโทคอลต้านไวรัส ส่วนประกอบที่หนึ่ง = เซรั่มเลือดกลุ่ม O"

- [ ] **Step 7: ปรับคำสั่งหาผู้ติดต่อปานามาใน `02_CargoShip.json` ให้ตรงกับ `03_Bank.json`**
  - `02_CargoShip.json::P_02_CargoShip_GoalsActiv::Objective_0008` -> "หาชื่อผู้ติดต่อชาวปานามาของลาแซร์ดา"

---

### Task 3: Polish Unnatural / Literal Phrasing in Story Dialogue

**Files:**
- Modify: `data/translations/story/00_Training.json`
- Modify: `data/translations/story/09_SeoulTwo.json`
- Modify: `data/translations/story/11_KokuboSosho.json`

- [ ] **Step 1: ปรับแก้สำนวน "ไม่มีที่ให้กับอุบัติเหตุ" ใน `09_SeoulTwo.json`**
  - `P_09_SeoulTwo_LambertComms::Speech_0177L` -> "แลมเบิร์ต - เราจะปล่อยให้เกิดความผิดพลาดไม่ได้เด็ดขาด ระวังการยิงของตัวเอง"

- [ ] **Step 2: ปรับแก้สำนวน "มีความสามารถในการ" ใน `00_Training.json`**
  - `P_00_Training_CnvPartridge::Speech_0021L` -> "พาร์ทริดจ์ - มาสส์เคอร์เนลทำให้เราสามารถเข้าควบคุมและเปลี่ยนทิศทางระบบอาวุธปล่อยกลางอากาศได้..."

- [ ] **Step 3: ปรับแก้สำนวนเค้นคอใน `11_KokuboSosho.json`**
  - `P_11_KokuboSosho_InterroWarRoom::Speech_0005L` -> "ฟิชเชอร์ - เพื่อประโยชน์ของตัวคุณเอง หวังว่าคุณจะมีความคิดที่ดีกว่านี้นะ..."
  - `P_11_KokuboSosho_InterroHostagers::Speech_0001L` -> "ฟิชเชอร์ - กักตัวคนพวกนี้ไว้ทำไม?"
  - `P_11_KokuboSosho_InterroHostagers::Speech_0018L` -> "ฟิชเชอร์ - จะเปิดประตูปิดผนึกยังไง?"

---

### Task 4: UI & Key Binding Polish in `pregame_pc.json` & `pregame_menus.json`

**Files:**
- Modify: `data/translations/ui/pregame_pc.json`
- Modify: `data/translations/ui/pregame_menus.json`

- [ ] **Step 1: ปรับปุ่มควบคุมทิศทางใน `pregame_pc.json::Keys` ให้สมมาตรและกระชับ**
  - `Keys::K_StrafeLeft` -> "เดินซ้าย" (เดิม "เคลื่อนที่ไปทางซ้าย")
  - `Keys::K_StrafeRight` -> "เดินขวา" (เดิม "เคลื่อนที่ไปทางขวา")

- [ ] **Step 2: ปรับปุ่มเติมกระสุนใน `pregame_pc.json::Keys` ให้ใช้คำเดียวกัน**
  - `Keys::K_InteractionReload` -> "ปฏิสัมพันธ์ / รีโหลดกระสุน" (เดิม "ปฏิสัมพันธ์ / เติมกระสุน")

- [ ] **Step 3: ปรับความยาวของโหมด EMF ใน `pregame_pc.json::Keys`**
  - `Keys::K_EEVVision` -> "วิสัยทัศน์ EMF" (เดิม "กล้องตรวจจับคลื่นแม่เหล็กไฟฟ้า")

- [ ] **Step 4: ปรับชื่อกล่องข้อความใน `pregame_menus.json`**
  - `MESSAGING::InboxTitle` -> "กล่องข้อความ" (เดิม "กล่องข้อความเข้า")

---

### Task 5: Full Regression Testing, Font Generation & UMD Rebuild

**Files:**
- Output check: `dist/`, `data/translations/`

- [ ] **Step 1: รัน `verify_all.py` ตรวจกฎโปรเจกต์**
  - Run: `.\.venv\Scripts\python.exe out/translation-review/verify_all.py`
  - Expected: 0 errors, 0 label drift warnings

- [ ] **Step 2: รัน regression unit tests ทั้งหมด**
  - Run: `.\.venv\Scripts\python.exe -m unittest discover -s tests -v`
  - Expected: 38/38 tests PASS

- [ ] **Step 3: รัน `validate_translations.py`**
  - Run: `.\.venv\Scripts\python.exe tools/validate_translations.py`
  - Expected: ALL CHECKS PASSED PERFECTLY

- [ ] **Step 4: รันบิลด์เต็มรูปแบบ (Localization + Fonts + UMD)**
  - Run: `.\.venv\Scripts\python.exe build.py`
  - Expected: Complete build without errors, UMD archive updated

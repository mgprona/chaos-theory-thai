"""Comprehensive automated test suite for the Chaos Theory Thai Mod toolchain."""

from __future__ import annotations
import io
import json
import os
import sys
import unittest
from pathlib import Path
import numpy as np

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.core.umd_parser import (
    UMDArchive,
    read_compact_index,
    write_compact_index,
)
from src.core.ini_codec import IniDocument, IniSection, IniEntry
from src.core.pcx_font import PCXFont


class TestCompactIndex(unittest.TestCase):
    """Test Unreal Engine CompactIndex encoding and decoding."""

    def test_roundtrip_values(self):
        test_values = [
            0, 1, -1, 15, -15, 63, -63, 64, -64,
            127, -127, 128, -128, 255, -255, 1024,
            20252, -20252, 1000000, -1000000
        ]
        for val in test_values:
            encoded = write_compact_index(val)
            stream = io.BytesIO(encoded)
            decoded = read_compact_index(stream)
            self.assertEqual(val, decoded, f"Failed roundtrip for {val} (bytes: {encoded.hex()})")


class TestIniCodec(unittest.TestCase):
    """Test INI parser, serializer, and translation application."""

    def test_basic_parse_and_serialize(self):
        sample_ini = (
            "; Sample comment\r\n"
            "[GENERAL]\r\n"
            "MapName=LIGHTHOUSE\r\n"
            "Briefing=Hello Fisher\r\n"
            "\r\n"
            "[Objectives]\r\n"
            "Obj_01=Rescue Morgenholt\r\n"
        ).encode("cp1252")

        doc = IniDocument.from_bytes(sample_ini)
        self.assertEqual(len(doc.sections), 2)
        self.assertIn("GENERAL", doc.sections)
        self.assertIn("Objectives", doc.sections)
        self.assertEqual(doc.sections["GENERAL"].get("MapName"), "LIGHTHOUSE")
        self.assertEqual(doc.sections["GENERAL"].get("Briefing"), "Hello Fisher")

        # Serialized output should match original
        serialized = doc.serialize()
        self.assertEqual(serialized, sample_ini)

    def test_apply_translation(self):
        sample_ini = (
            "[GENERAL]\r\n"
            "MapName=LIGHTHOUSE\r\n"
            "Briefing=Hello Fisher\r\n"
        ).encode("cp1252")

        doc = IniDocument.from_bytes(sample_ini)
        translations = {
            "GENERAL": {
                "MapName": "ประภาคาร",
                "Briefing": "",  # Empty should fallback to existing English
            }
        }
        updated = doc.apply_translations(translations, fallback_to_english=True)
        self.assertEqual(updated, 1)
        self.assertEqual(doc.sections["GENERAL"].get("MapName"), "ประภาคาร")
        self.assertEqual(doc.sections["GENERAL"].get("Briefing"), "Hello Fisher")

    def test_utf16_detection(self):
        text = "[GENERAL]\r\nMapName=NUCLEAR PLANT\r\n"
        data = b"\xff\xfe" + text.encode("utf-16le")
        doc = IniDocument.from_bytes(data)
        self.assertEqual(doc.encoding, "utf-16le")
        self.assertTrue(doc.has_bom)
        self.assertEqual(doc.sections["GENERAL"].get("MapName"), "NUCLEAR PLANT")
        serialized = doc.serialize()
        self.assertTrue(serialized.startswith(b"\xff\xfe"))


class TestPCXFont(unittest.TestCase):
    """Test PCX font parser and delimiter cell detection."""

    def test_pcx_cell_detection(self):
        template_path = PROJECT_ROOT / "data" / "raw_official" / "fonts" / "pcx" / "txt_hud.pcx"
        if not template_path.exists():
            self.skipTest("PCX font template not yet extracted")

        pcx = PCXFont(template_path)
        self.assertEqual(len(pcx.glyphs), 224)
        self.assertEqual(pcx.glyphs[0].char_code, 32)   # space
        self.assertEqual(pcx.glyphs[1].char_code, 33)   # '!'
        self.assertEqual(pcx.glyphs[33].char_code, 65)  # 'A'

    def test_thai_glyph_injection(self):
        template_path = PROJECT_ROOT / "data" / "raw_official" / "fonts" / "pcx" / "txt_hud.pcx"
        if not template_path.exists():
            self.skipTest("PCX font template not yet extracted")

        pcx = PCXFont(template_path)
        ttf_path = Path(r"C:\Windows\Fonts\tahoma.ttf")
        if not ttf_path.exists():
            self.skipTest("Tahoma font not found")

        injected = pcx.inject_thai_glyphs(ttf_path)
        self.assertGreaterEqual(injected, 80)
        self.assertEqual(len(pcx.glyphs), 224)

    def test_txt_mission_thai_visibility_and_color(self):
        """Verify txt_mission.pcx does not render black-on-black Thai text."""
        template_path = PROJECT_ROOT / "data" / "raw_official" / "fonts" / "pcx" / "txt_mission.pcx"
        if not template_path.exists():
            self.skipTest("PCX font template not yet extracted")

        pcx = PCXFont(template_path)
        ttf_path = Path(r"C:\Windows\Fonts\tahoma.ttf")
        if not ttf_path.exists():
            self.skipTest("Tahoma font not found")

        pcx.inject_thai_glyphs(ttf_path)
        g_thai = pcx.get_glyph(161)  # Thai 'ก'
        self.assertIsNotNone(g_thai)
        self.assertGreaterEqual(g_thai.bbox[2], 6, "Thai cell must not be a 1-2px sliver")

        # Check that pixels are drawn with bright white color (not index 0 or black index 169)
        arr = np.array(g_thai.image)
        non_zero = arr[arr > 0]
        self.assertGreater(len(non_zero), 0, "Thai glyph must have non-zero pixels")
        pal = pcx.palette
        # At least some pixels should be index 254 (bright white)
        self.assertIn(254, non_zero, "Thai glyph should contain white index 254 pixels")
        max_idx = int(np.max(non_zero))
        r, g, b = pal[max_idx * 3], pal[max_idx * 3 + 1], pal[max_idx * 3 + 2]
        self.assertGreater(r + g + b, 500, f"Expected bright text color, got RGB({r},{g},{b})")

    def test_all_fonts_no_narrow_thai_cells(self):
        """Ensure no Thai character cell is narrower than 6 pixels across any PCX font."""
        ttf_path = Path(r"C:\Windows\Fonts\tahoma.ttf")
        if not ttf_path.exists():
            self.skipTest("Tahoma font not found")

        for pcx_name in ["txt_hud.pcx", "txt_mission.pcx", "txt_integration.pcx"]:
            template_path = PROJECT_ROOT / "data" / "raw_official" / "fonts" / "pcx" / pcx_name
            if not template_path.exists():
                continue
            pcx = PCXFont(template_path)
            pcx.inject_thai_glyphs(ttf_path)
            for code in range(161, 252):
                g = pcx.get_glyph(code)
                if g:
                    self.assertGreaterEqual(g.bbox[2], 6, f"{pcx_name} code {code} cell width {g.bbox[2]} < 6")


class TestTranslationsJSON(unittest.TestCase):
    """Verify that all generated JSON translation files are valid and complete."""

    def test_all_json_files_valid(self):
        trans_root = PROJECT_ROOT / "data" / "translations"
        json_files = list(trans_root.glob("*/*.json"))
        self.assertEqual(len(json_files), 33, f"Expected 33 translation JSON files, found {len(json_files)}")

        total_strings = 0
        for jf in json_files:
            with open(jf, "r", encoding="utf-8") as f:
                data = json.load(f)
            self.assertIn("_meta", data)
            self.assertIn("sections", data)
            sections = data["sections"]
            for sec_name, sec_dict in sections.items():
                self.assertIn("_source", sec_dict)
                for k, v in sec_dict.items():
                    if k.startswith("_"):
                        continue
                    self.assertIsInstance(v, dict)
                    self.assertIn("en", v)
                    self.assertIn("fr", v)
                    self.assertIn("de", v)
                    self.assertIn("es", v)
                    self.assertIn("it", v)
                    self.assertIn("th", v)
                    total_strings += 1

        self.assertGreater(total_strings, 8000)

    def test_hud_translations_complete_and_cp874(self):
        hud_path = PROJECT_ROOT / "data" / "translations" / "ui" / "hud.json"
        with open(hud_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        count = 0
        forbidden_chars = {"“", "”", "‘", "’", "…"}  # standard ASCII or periods should be used
        for sec, sdict in data["sections"].items():
            for k, v in sdict.items():
                if k.startswith("_"):
                    continue
                th = v.get("th", "")
                self.assertTrue(th, f"Missing Thai translation for HUD {sec}/{k}")
                for fc in ["“", "”", "‘", "’"]:
                    self.assertNotIn(fc, th, f"Curly quote found in HUD {sec}/{k}: {th}")
                raw_bytes = th.encode("cp874")
                for b in raw_bytes:
                    self.assertTrue(b < 128 or (161 <= b <= 251), f"Byte {b} out of range in HUD {sec}/{k}: {th}")
                count += 1
        self.assertEqual(count, 135)
        # Canonical terminology checks
        self.assertEqual(data["sections"]["Interaction"]["DoorOpen"]["th"], "เปิดประตู")
        self.assertEqual(data["sections"]["Interaction"]["DoorPick"]["th"], "สะเดาะกลอน")
        self.assertEqual(data["sections"]["Interaction"]["NpcZone0"]["th"], "จับตัว")
        self.assertEqual(data["sections"]["Interaction"]["NpcZone2"]["th"], "เค้นข้อมูล")
        self.assertEqual(data["sections"]["Interaction"]["NpcZone5"]["th"], "ข้ามบทสนทนา")
        self.assertEqual(data["sections"]["Interaction"]["Bomb"]["th"], "กู้ระเบิด")
        self.assertEqual(data["sections"]["Interaction"]["C4"]["th"], "ติดตั้ง C4")
        self.assertEqual(data["sections"]["Transmission"]["DoorLock"]["th"], "ประตูล็อก")
        self.assertEqual(data["sections"]["Transmission"]["DoorJam"]["th"], "กลอนติดขัด")
        self.assertEqual(data["sections"]["Transmission"]["BodyFound"]["th"], "พบศพ... ระดับสัญญาณเตือนภัยเพิ่มขึ้น")

    def test_ingame_menus_translations_complete_and_cp874(self):
        menus_path = PROJECT_ROOT / "data" / "translations" / "ui" / "ingame_menus.json"
        with open(menus_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        count = 0
        for sec, sdict in data["sections"].items():
            for k, v in sdict.items():
                if k.startswith("_"):
                    continue
                th = v.get("th", "")
                self.assertTrue(th, f"Missing Thai translation for InGameMenus {sec}/{k}")
                for fc in ["“", "”", "‘", "’"]:
                    self.assertNotIn(fc, th, f"Curly quote found in InGameMenus {sec}/{k}: {th}")
                raw_bytes = th.encode("cp874")
                for b in raw_bytes:
                    self.assertTrue(b < 128 or (161 <= b <= 251), f"Byte {b} out of range in InGameMenus {sec}/{k}: {th}")
                count += 1
        self.assertEqual(count, 122)
        # Canonical terminology checks
        self.assertEqual(data["sections"]["OPSATMENU"]["GoalType[0]"]["th"], "เป้าหมายหลัก")
        self.assertEqual(data["sections"]["OPSATMENU"]["GoalType[1]"]["th"], "เป้าหมายรอง")
        self.assertEqual(data["sections"]["OPSATMENU"]["GoalType[2]"]["th"], "เป้าหมายเสริม")
        self.assertEqual(data["sections"]["OPSATMENU"]["Goals"]["th"], "เป้าหมาย")
        self.assertEqual(data["sections"]["OPSATMENU"]["Notes"]["th"], "บันทึก")
        self.assertEqual(data["sections"]["OPSATMENU"]["Datas"]["th"], "ข้อมูล")
        self.assertEqual(data["sections"]["OPSATMENU"]["Map"]["th"], "แผนที่")
        self.assertEqual(data["sections"]["OPSATMENU"]["Equipment"]["th"], "อุปกรณ์")
        self.assertEqual(data["sections"]["ENDMISSION"]["MissionSuccessMsg"]["th"], "ภารกิจสำเร็จ")
        self.assertEqual(data["sections"]["ENDMISSION"]["MissionFailedMsg"]["th"], "ภารกิจล้มเหลว")
        self.assertEqual(data["sections"]["PAUSEMENU"]["PauseNormal"]["th"], "หยุดชั่วคราว")
        self.assertEqual(data["sections"]["PAUSEMENU"]["ChoiceRetryGame"]["th"], "เริ่มใหม่")
        self.assertEqual(data["sections"]["PAUSEMENU"]["ChoiceContinueGame"]["th"], "เล่นต่อ")
        self.assertEqual(data["sections"]["COMPUTER"]["HackingDetail"]["th"], "กระบวนการแฮก")

    def test_opsat_translations_complete_and_cp874(self):
        """Test that all 7 OPSAT JSON files are 100% translated and CP874 encodable."""
        opsat_dir = PROJECT_ROOT / "data" / "translations" / "opsat"
        expected_files = {
            "d3ddrv.json": 5,
            "echelon.json": 1,
            "engine.json": 115,
            "equipment.json": 164,
            "system.json": 130,
            "training.json": 40,
            "window.json": 58,
        }
        total_strings = 0
        for fname, exp_count in expected_files.items():
            fpath = opsat_dir / fname
            self.assertTrue(fpath.exists(), f"Missing OPSAT file {fname}")
            with open(fpath, "r", encoding="utf-8") as f:
                data = json.load(f)
            file_count = 0
            for sec, sd in data.get("sections", {}).items():
                for k, v in sd.items():
                    if k.startswith("_"):
                        continue
                    file_count += 1
                    th = v.get("th", "")
                    self.assertTrue(th.strip(), f"Missing Thai translation in {fname} [{sec}] {k}")
                    for fc in ["“", "”", "‘", "’"]:
                        self.assertNotIn(fc, th, f"Curly quote found in {fname} [{sec}] {k}: {th}")
                    raw_bytes = th.encode("cp874")
                    for b in raw_bytes:
                        self.assertTrue(
                            b < 128 or (161 <= b <= 251),
                            f"Byte {b} out of range in {fname} [{sec}] {k}: {th}",
                        )
            self.assertEqual(file_count, exp_count, f"String count mismatch in {fname}")
            total_strings += file_count
        self.assertEqual(total_strings, 513)

        # Canonical equipment and system checks
        eq_path = opsat_dir / "equipment.json"
        with open(eq_path, "r", encoding="utf-8") as f:
            eq = json.load(f)["sections"]
        self.assertEqual(eq["FN2000"]["Name"]["th"], "SC-20K")
        self.assertEqual(eq["FN7"]["Name"]["th"], "ปืนพก SC")
        self.assertEqual(eq["SCOPE"]["NameShort"]["th"], "สไนเปอร์")
        self.assertEqual(eq["WALLMINE"]["Name"]["th"], "กับระเบิดติดผนัง")
        self.assertEqual(eq["STICKYSHOCKER"]["Name"]["th"], "กระสุนช็อตไฟฟ้า")
        self.assertEqual(eq["STICKYCAMERA"]["Name"]["th"], "กล้องสติ๊กกี้")
        self.assertEqual(eq["CATEGORIES"]["Category[2]"]["th"], "อาวุธหลัก")
        self.assertEqual(eq["BERETTA"]["Name"]["th"], "เบเร็ตต้า 92FS")
        self.assertEqual(eq["FRAGGRENADE"]["Name"]["th"], "ระเบิดสังหาร")
        self.assertEqual(eq["OPTICCABLE"]["Name"]["th"], "กล้องสายเคเบิล")
        self.assertEqual(eq["INFRAREDSTRESSGEN"]["NameShort"]["th"], "เครื่องกวนอินฟราเรด")

        sys_path = opsat_dir / "system.json"
        with open(sys_path, "r", encoding="utf-8") as f:
            sys_sec = json.load(f)["sections"]
        self.assertEqual(sys_sec["MESSAGEBOX"]["DefaultAccept"]["th"], "ตกลง")
        self.assertEqual(sys_sec["SAVELOAD"]["SaveMsg"]["th"], "กำลังบันทึกเกม...")
        self.assertEqual(sys_sec["NAVIGATION"]["StickyCamera_X"]["th"], "เสียงล่อ")
        self.assertEqual(sys_sec["NAVIGATION"]["StickyCamera_Y"]["th"], "แก๊ส")
        self.assertEqual(sys_sec["NAVIGATION"]["StickyCamera_DL"]["th"], "มองกลางคืน")
        self.assertEqual(sys_sec["NAVIGATION"]["StickyCamera_DR"]["th"], "มองความร้อน")

        win_path = opsat_dir / "window.json"
        with open(win_path, "r", encoding="utf-8") as f:
            win_sec = json.load(f)["sections"]
        self.assertEqual(win_sec["General"]["BackButton"]["th"], "< ย้อนกลับ (&B)")
        self.assertEqual(win_sec["General"]["NextButton"]["th"], "ถัดไป (&N) >")
        self.assertEqual(win_sec["General"]["FinishButton"]["th"], "เสร็จสิ้น (&F)")

    def test_story_00_and_01_translations_complete_and_cp874(self):
        """Test that story missions 00_Training and 01_Lighthouse are 100% translated and CP874 encodable."""
        story_dir = PROJECT_ROOT / "data" / "translations" / "story"
        expected_files = {
            "00_Training.json": 594,
            "01_Lighthouse.json": 381,
        }
        for fname, exp_count in expected_files.items():
            fpath = story_dir / fname
            self.assertTrue(fpath.exists(), f"Missing story file {fname}")
            with open(fpath, "r", encoding="utf-8") as f:
                data = json.load(f)
            file_count = 0
            for sec, sd in data.get("sections", {}).items():
                for k, v in sd.items():
                    if k.startswith("_"):
                        continue
                    file_count += 1
                    th = v.get("th", "")
                    self.assertTrue(th.strip(), f"Missing Thai translation in {fname} [{sec}] {k}")
                    for fc in ["“", "”", "‘", "’"]:
                        self.assertNotIn(fc, th, f"Curly quote found in {fname} [{sec}] {k}: {th}")
                    raw_bytes = th.encode("cp874")
                    for b in raw_bytes:
                        self.assertTrue(
                            b < 128 or (161 <= b <= 251),
                            f"Byte {b} out of range in {fname} [{sec}] {k}: {th}",
                        )
            self.assertEqual(file_count, exp_count, f"String count mismatch in {fname}")

        # Check canonical 00_Training translations
        with open(story_dir / "00_Training.json", "r", encoding="utf-8") as f:
            t00 = json.load(f)["sections"]
        self.assertEqual(t00["VIDEOSTEALTHBASICS"]["Name"]["th"], "พื้นฐานการลอบเร้น")
        self.assertEqual(t00["P_00_Training_Objectives"]["Objective_0004"]["th"], "รับฟังการบรรยายสรุปภารกิจจากแลมเบิร์ต")
        self.assertEqual(t00["P_00_Training_Popup"]["Note_0001L"]["th"], "หากต้องการคุยกับใคร ให้กดปุ่มปฏิสัมพันธ์ (A)")
        self.assertEqual(t00["P_00_Training_CnvUSSol_Phil"]["Speech_0047L"]["th"], "ฟิชเชอร์ - เปล่าหรอก... ฉันไม่ค่อยมีครอบครัวเหลืออยู่แล้วน่ะ พลทหาร")
        self.assertEqual(t00["P_00_Training_CnvPartridge"]["Speech_0054L"]["th"], "ฟิชเชอร์ - ได้ยินข่าวลือมาว่าผมอาจไม่ได้กลับขึ้นเรือลำนี้หลังจบภารกิจ คงอีกนานกว่าเราจะได้เจอกันอีกนะครับท่าน")
        self.assertEqual(t00["P_00_Training_CnvCook_Sebastien"]["Speech_0031L"]["th"], "เซบาสเตียน - คุณชอบอาหารทะเลไหมครับ?")

        # Check canonical 01_Lighthouse translations
        with open(story_dir / "01_Lighthouse.json", "r", encoding="utf-8") as f:
            t01 = json.load(f)["sections"]
        self.assertEqual(t01["GENERAL"]["MapName"]["th"], "ประภาคาร")
        self.assertEqual(t01["P_01_Lighthouse_Objectives"]["Objective_0024"]["th"], "ช่วยชีวิตมอร์เกนโฮลต์")
        self.assertEqual(t01["P_01_Lighthouse_Communications"]["Speech_0025L"]["th"], "ฟิชเชอร์ - ตายสนิทยิ่งกว่าเอลวิสอีก")
        self.assertEqual(t01["P_01_Lighthouse_IntThunder"]["Speech_0001L"]["th"], "ฟิชเชอร์: จ๊ะเอ๋")
        self.assertIn("ลิง", t01["P_01_Lighthouse_IntCaveGuard"]["Speech_0003L"]["th"])
        self.assertEqual(t01["P_01_Lighthouse_CnvMariaNarcissa"]["Speech_0016L"]["th"], "วิทยุ: รับทราบ มาเรีย นาร์ซิสซา จบการติดต่อ")
        self.assertIn("พวกบ้าเลือด", t01["P_01_Lighthouse_CnvWeather"]["Speech_0010L"]["th"])
        self.assertNotIn("คนชำแหละเนื้อสัตว์", t01["P_01_Lighthouse_CnvWeather"]["Speech_0010L"]["th"])

    def test_story_02_cargoship_translations_complete_and_cp874(self):
        """Test that story mission 02_CargoShip is 100% translated, CP874 encodable, and matches canonical terms."""
        story_dir = PROJECT_ROOT / "data" / "translations" / "story"
        fpath = story_dir / "02_CargoShip.json"
        self.assertTrue(fpath.exists(), "Missing 02_CargoShip.json")
        with open(fpath, "r", encoding="utf-8") as f:
            data = json.load(f)
        file_count = 0
        for sec, sd in data.get("sections", {}).items():
            for k, v in sd.items():
                if k.startswith("_"):
                    continue
                file_count += 1
                th = v.get("th", "")
                self.assertTrue(th.strip(), f"Missing Thai translation in 02_CargoShip [{sec}] {k}")
                for fc in ["“", "”", "‘", "’"]:
                    self.assertNotIn(fc, th, f"Curly quote found in 02_CargoShip [{sec}] {k}: {th}")
                raw_bytes = th.encode("cp874")
                for b in raw_bytes:
                    self.assertTrue(
                        b < 128 or (161 <= b <= 251),
                        f"Byte {b} out of range in 02_CargoShip [{sec}] {k}: {th}",
                    )
        self.assertEqual(file_count, 450, "String count mismatch in 02_CargoShip.json")

        # Canonical checks
        t02 = data["sections"]
        self.assertEqual(t02["GENERAL"]["MapName"]["th"], "เรือสินค้า")
        self.assertIn("ฮูโก ลาแซร์ดา", t02["GENERAL"]["Briefing_LAMBERT"]["th"])
        self.assertIn("Fifth Freedom", t02["GENERAL"]["Briefing_LAMBERT"]["th"])
        self.assertEqual(t02["P_02_CargoShip_Objectives"]["Objective_0018"]["th"], "กำจัด ฮูโก ลาแซร์ดา")
        self.assertEqual(t02["P_02_CargoShip_Objectives"]["Objective_0001"]["th"], "เก็บกู้ใบตราส่งสินค้าสำหรับการขนส่งอาวุธของลาแซร์ดา")
        self.assertEqual(t02["P_02_CargoShip_LambertComms"]["Speech_0012L"]["th"], "ฟิชเชอร์ - อย่าบอกนะว่า... สัญญาณเตือนภัยดังสามครั้งแล้วภารกิจล้มเหลว?")
        self.assertEqual(t02["P_02_CargoShip_LambertComms"]["Speech_0084L"]["th"], "ฟิชเชอร์ - ผมลืมเอาช่อดอกไม้ติดอกมาด้วยสิ")
        self.assertEqual(t02["P_02_CargoShip_InterogMShopSailor"]["Speech_0001L"]["th"], "ฟิชเชอร์ - จ๊ะเอ๋")
        self.assertEqual(t02["P_02_CargoShip_InterogOfficeSoldier"]["Speech_0003L"]["th"], "ฟิชเชอร์ - ฉันมีมีด... นายตอบก่อน")
        self.assertEqual(t02["P_02_CargoShip_AlarmManager"]["POPUPMESSAGE_0001"]["th"], "ระดับสัญญาณเตือนภัยขั้นที่หนึ่ง")
        self.assertEqual(t02["Email"]["EmailLacerdaFrom"]["th"], "ฮูโก ลาแซร์ดา ")
        self.assertEqual(t02["Email"]["EmailFloodedFrom"]["th"], "เฆราร์โด")
        self.assertIn("เจ้าหน้าที่ตรวจสอบ", t02["P_02_CargoShip_MemorableM"]["Speech_0003L"]["th"])
        self.assertIn("ไม่ใช่พระแม่", t02["P_02_CargoShip_InterogLacerda"]["Speech_0021L"]["th"])
        self.assertIn("บารมี", t02["P_02_CargoShip_InterogBodyGuards"]["Speech_0011L"]["th"])
        self.assertEqual(t02["P_02_CargoShip_Objectives"]["Objective_0006"]["th"], "ถอนกำลังไปยังจุดถอนกำลัง")

    def test_story_01_panama_translations_complete_and_cp874(self):
        """Test that co-op mission 01_Panama is 100% translated, CP874 encodable, and matches locked glossary."""
        story_dir = PROJECT_ROOT / "data" / "translations" / "story"
        fpath = story_dir / "01_Panama.json"
        self.assertTrue(fpath.exists(), "Missing 01_Panama.json")
        with open(fpath, "r", encoding="utf-8") as f:
            data = json.load(f)
        file_count = 0
        for sec, sd in data.get("sections", {}).items():
            for k, v in sd.items():
                if k.startswith("_"):
                    continue
                file_count += 1
                th = v.get("th", "")
                self.assertTrue(th.strip(), f"Missing Thai translation in 01_Panama [{sec}] {k}")
                for fc in ["“", "”", "‘", "’", "…"]:
                    self.assertNotIn(fc, th, f"Forbidden character found in 01_Panama [{sec}] {k}: {th}")
                self.assertNotIn("\n", th, f"Real newline in 01_Panama [{sec}] {k}")
                for b in th.encode("cp874"):
                    self.assertTrue(
                        b < 128 or (161 <= b <= 251),
                        f"Byte {b} out of range in 01_Panama [{sec}] {k}: {th}",
                    )
                # Leading/trailing spaces must mirror the English source exactly.
                en = v.get("en", "")
                self.assertEqual(
                    (len(en) - len(en.lstrip(" ")), len(en) - len(en.rstrip(" "))),
                    (len(th) - len(th.lstrip(" ")), len(th) - len(th.rstrip(" "))),
                    f"Whitespace mismatch in 01_Panama [{sec}] {k}",
                )
        self.assertEqual(file_count, 168, "String count mismatch in 01_Panama.json")

        t = data["sections"]
        self.assertEqual(t["GENERAL"]["MapName"]["th"], "ปานามา")
        self.assertIn("เด เมเดรอส", t["GENERAL"]["Briefing_LAMBERT"]["th"])
        self.assertIn("แลมเบิร์ต - ", t["GENERAL"]["Briefing_LAMBERT"]["th"])
        # The briefing and the in-mission radio line are the same English body; the
        # briefing alone carries the "LAMBERT - " prefix, so the bodies must match.
        briefing = t["GENERAL"]["Briefing_LAMBERT"]["th"]
        self.assertTrue(briefing.startswith("แลมเบิร์ต - "), "Briefing must mirror the English speaker prefix")
        self.assertEqual(
            t["P_01_Panama_Communications"]["Speech_0021L"]["th"], briefing[len("แลมเบิร์ต - "):]
        )
        self.assertEqual(t["P_01_Panama_Objectives"]["Objective_0023"]["th"], "ถอนกำลังกลับไปที่รถบรรทุกในลานด้านนอก")
        self.assertIn("สปลินเตอร์เซล", t["P_01_Panama_Communications"]["Speech_0015L"]["th"])
        self.assertEqual(t["P_01_Panama_AlarmSystem"]["POPUPMESSAGE_0001"]["th"], "ระดับสัญญาณเตือนภัยขั้นที่หนึ่ง")
        self.assertEqual(t["P_01_Panama_SoccerGame"]["Speech_0011L"]["th"], "ฉันอยากจะฆ่าตัวตายจริงๆ ให้ตายเถอะ")
        # Official in-game section-name typo ("PAnama") must stay as-is.
        self.assertIn("P_01_PAnama_TalkingToSecurityChief", t)
        self.assertTrue(t["P_01_PAnama_TalkingToSecurityChief"]["Speech_0003L"]["th"].strip())

        # Duplicated line: must stay byte-identical to the already-shipped UI loading screen.
        with open(PROJECT_ROOT / "data" / "translations" / "ui" / "loading_screens.json", "r", encoding="utf-8") as f:
            loading = json.load(f)["sections"]["01_panama"]["Overview"]["th"]
        self.assertEqual(t["P_01_Panama_Communications"]["Speech_0028L"]["th"], loading)
        self.assertEqual(t["P_01_Panama_MeetingRoom"]["Note_0004L"]["th"], loading)


class TestCompiler(unittest.TestCase):
    """Test compiling translations into .int files."""

    def test_compilation_output(self):
        from src.pipeline.compiler import compile_translations
        assets = compile_translations(verbose=False)
        self.assertEqual(len(assets), 52, f"Expected 52 compiled files, got {len(assets)}")
        self.assertIn(r"Data\System\Localization\00_Training.int", assets)
        self.assertIn(r"Data\System\Localization\P_00_Training.int", assets)
        self.assertIn(r"Data\System\Localization\01_Lighthouse.int", assets)
        self.assertIn(r"Data\System\Localization\P_01_Lighthouse.int", assets)
        self.assertIn(r"Data\System\Localization\02_CargoShip.int", assets)
        self.assertIn(r"Data\System\Localization\P_02_CargoShip.int", assets)

    def test_translation_whitespace_preservation(self):
        sample_ini = "[GENERAL]\r\nMapName=LIGHTHOUSE\r\n".encode("cp1252")
        doc = IniDocument.from_bytes(sample_ini)
        # Translation with intentional leading/trailing spaces
        translations = {"GENERAL": {"MapName": " ประภาคาร "}}
        doc.apply_translations(translations, fallback_to_english=True)
        self.assertEqual(doc.sections["GENERAL"].get("MapName"), " ประภาคาร ")
        serialized = doc.serialize(encoding="cp874")
        lines = [line for line in serialized.decode("cp874").splitlines() if line]
        self.assertEqual(lines, ["[GENERAL]", "MapName= ประภาคาร "])

    def test_main_menu_translations_and_cp874(self):
        """Test that main menu translations in pregame_pc.json and pregame_menus.json are populated and CP874 encodable."""
        pc_path = PROJECT_ROOT / "data" / "translations" / "ui" / "pregame_pc.json"
        with open(pc_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        # Essential main menu keys that must be translated in Thai
        checks = {
            ("MenuGameType", "Title"): "เลือกโหมดเกม",
            ("MenuGameType", "SinglePlayer"): "เล่นคนเดียว",
            ("MenuGameType", "Cooperative"): "ร่วมมือกัน",
            ("MenuSolo", "Title"): "เมนูหลัก",
            ("MenuSolo", "Continue"): "เล่นต่อ",
            ("MenuSolo", "NewGame"): "เริ่มเกมใหม่",
            ("MenuSolo", "Loadgame"): "โหลดเกม",
            ("MenuSolo", "Settings"): "ตั้งค่า",
            ("MenuSolo", "ProfileManagement"): "จัดการโปรไฟล์",
            ("MenuSolo", "Extras"): "เนื้อหาพิเศษ",
            ("MenuNewGame", "Title"): "ระดับความยาก",
            ("MenuLoadGame", "Title"): "โหลดเกม",
            ("MenuSaveGame", "Title"): "บันทึกเกม",
            ("MenuProfileManagement", "Title"): "โปรไฟล์",
            ("MenuPause", "Title"): "เมนูหยุดเกม",
            ("MenuPause", "ResumeGame"): "เล่นต่อ",
            ("MenuPause", "Quit"): "กลับสู่เมนูหลัก",
            ("MenuSettings", "Title"): "การตั้งค่า",
            ("MenuSettings", "Controls"): "การควบคุม",
            ("MenuSettings", "Display"): "การแสดงผล",
            ("MenuSettings", "Sounds"): "ระบบเสียง",
            ("Loading", "PressKey"): "กดปุ่มใดๆ เพื่อเล่นต่อ",
        }

        for (sec, key), expected_th in checks.items():
            val = data["sections"].get(sec, {}).get(key, {}).get("th", "")
            self.assertTrue(val, f"Missing translation for pregame_pc {sec}/{key}")
            self.assertEqual(val, expected_th)
            # Verify CP874 encodability
            raw = val.encode("cp874")
            self.assertTrue(len(raw) > 0)

        # Check pregame_menus.json
        menus_path = PROJECT_ROOT / "data" / "translations" / "ui" / "pregame_menus.json"
        with open(menus_path, "r", encoding="utf-8") as f:
            menus_data = json.load(f)

        menu_checks = {
            ("COMMON", "MainTitleSolo"): "เล่นคนเดียว",
            ("COMMON", "MainTitleCoop"): "ร่วมมือกัน",
            ("COMMON", "Accept"): "ยืนยัน",
            ("COMMON", "Back"): "ย้อนกลับ",
            ("COMMON", "Continue"): "เล่นต่อ",
            ("COMMON", "Select"): "เลือก",
            ("OPTIONS", "OptionsTitle"): "การตั้งค่า",
            ("OPTIONS", "ControllerTitle"): "การควบคุม",
            ("OPTIONSVALUE", "OptionYes"): "ใช่",
            ("OPTIONSVALUE", "OptionNo"): "ไม่",
            ("PROFILES", "Profiles"): "โปรไฟล์",
            ("PROFILES", "NewProfile"): "สร้างโปรไฟล์ใหม่",
            ("LOADSAVE", "LoadGame"): "โหลดเกม",
            ("LOADSAVE", "NewGame"): "เริ่มเกมใหม่",
        }

        for (sec, key), expected_th in menu_checks.items():
            val = menus_data["sections"].get(sec, {}).get(key, {}).get("th", "")
            self.assertTrue(val, f"Missing translation for pregame_menus {sec}/{key}")
            self.assertEqual(val, expected_th)
            raw = val.encode("cp874")
            self.assertTrue(len(raw) > 0)

    def test_chakra_petch_font_config_and_build(self):
        """Test that Chakra Petch font is properly configured and builds PCX fonts."""
        from src.pipeline.font_builder import build_thai_fonts
        cfg_path = PROJECT_ROOT / "config.json"
        with open(cfg_path, "r", encoding="utf-8") as f:
            cfg = json.load(f)
        self.assertIn("ChakraPetch", cfg.get("active_font", ""))

        stats = build_thai_fonts(verbose=False)
        self.assertEqual(stats["fonts_processed"], 5)
        for font_name in ["titre_regular_integration.pcx", "titre_bold_integration.pcx", "txt_integration.pcx"]:
            self.assertIn(font_name, stats["glyphs_injected"])
            self.assertGreater(stats["glyphs_injected"][font_name], 80)

    def test_magma_builder(self):
        """Test building Magma UI fonts with Chakra Petch glyph injection."""
        from src.pipeline.magma_builder import build_magma_fonts
        assets = build_magma_fonts(verbose=False)
        self.assertIn(r"Data\Magma\DataPC\Fonts\Bios Three Regular 20.mft", list(assets))
        self.assertIn(r"Data\Magma\DataPC\Fonts\Bios Three Regular 20 5.tga", list(assets))
        self.assertIn(r"Data\Magma\DataPC\Fonts\prototype regular 13.mft", list(assets))

        mft_data = assets[r"Data\Magma\DataPC\Fonts\Bios Three Regular 20.mft"]
        self.assertTrue(mft_data.startswith(b"Magma Font\x00"))
        from src.pipeline.magma_builder import read_mft
        records, pages, footer = read_mft(mft_data)
        self.assertGreater(len(records), 224)
        self.assertIn(0x0E, pages)
        self.assertIn(0xE0, pages)

    def test_dist_umd_integrity(self):
        """Test that repacked UMD in dist contains valid TOC, Thai localization, and Magma fonts."""
        dist_umd = PROJECT_ROOT / "dist" / "System" / "dynamic-pc.umd"
        if not dist_umd.exists():
            self.skipTest("dist UMD not built yet")

        archive = UMDArchive(dist_umd)
        self.assertEqual(len(archive.entries), 20252)

        # Check pregame_pc.int
        pc_entry = archive.find_entry(r"Data\System\Localization\pregame_pc.int")
        self.assertIsNotNone(pc_entry)
        from src.core.thai_shaper import create_ui_shaper
        data = create_ui_shaper().decode(archive.read_entry(pc_entry).decode("utf-16"))
        self.assertIn("เลือกโหมดเกม", data)
        self.assertIn("เมนูหลัก", data)

        # Check Magma font entry
        mft_entry = archive.find_entry(r"Data\Magma\DataPC\Fonts\Bios Three Regular 20.mft")
        self.assertIsNotNone(mft_entry)
        mft_bytes = archive.read_entry(mft_entry)
        self.assertTrue(mft_bytes.startswith(b"Magma Font\x00"))


if __name__ == "__main__":
    unittest.main()

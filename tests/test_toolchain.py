"""Comprehensive automated test suite for the Chaos Theory Thai Mod toolchain."""

from __future__ import annotations
import io
import json
import os
import sys
import unittest
from pathlib import Path

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


class TestCompiler(unittest.TestCase):
    """Test compiling translations into .int files."""

    def test_compilation_output(self):
        from src.pipeline.compiler import compile_translations
        assets = compile_translations(verbose=False)
        self.assertEqual(len(assets), 52, f"Expected 52 compiled files, got {len(assets)}")
        self.assertIn(r"Data\System\Localization\01_Lighthouse.int", assets)
        self.assertIn(r"Data\System\Localization\P_01_Lighthouse.int", assets)


if __name__ == "__main__":
    unittest.main()

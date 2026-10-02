"""Regression checks for Unicode lookup, atlas preservation and offline shaping."""

import io
import json
from pathlib import Path
import struct
import tempfile
import unittest

from PIL import Image

from src.core.ini_codec import IniDocument
from src.core.thai_shaper import ThaiShaper, create_ui_shaper, uses_unicode_pua
from src.pipeline.compiler import compile_translations, get_umd_internal_path
from src.pipeline.magma_builder import FONT_SPECS, GLYPH, build_magma_fonts, read_mft
from src.pipeline.validation import validate_localization_assets

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data/raw_official/fonts/magma"


def glyph_pixels(record, image):
    page = int(record[6])
    x = round((record[6] - page) * image.width - 0.5)
    y = round((record[7] - page) * image.height - 0.5)
    return image.crop((x, y, x + record[1], y + record[2])).tobytes()


class TestOfflineThai(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.shaper = create_ui_shaper()
        cls.assets = build_magma_fonts(verbose=False)
        cls.compiled = compile_translations(verbose=False)

    def test_every_compiled_pua_value_roundtrips_and_has_a_glyph(self):
        config = json.loads((ROOT / "config.json").read_text(encoding="utf-8"))
        fonts = [read_mft(data) for key, data in self.assets.items() if key.endswith(".mft")]
        for path in (ROOT / "data/translations").glob("*/*.json"):
            translation = json.loads(path.read_text(encoding="utf-8"))
            for section_name, section in translation["sections"].items():
                stem = section["_source"]
                if not uses_unicode_pua(config, stem):
                    continue
                data = self.compiled[get_umd_internal_path(stem)]
                self.assertTrue(data.startswith(b"\xff\xfe"))
                doc = IniDocument.from_bytes(data)
                for key, value in section.items():
                    if not isinstance(value, dict) or not value.get("th", "").strip():
                        continue
                    encoded = doc.get_section(section_name).get(key)
                    self.assertEqual(self.shaper.decode(encoded), value["th"], (stem, section_name, key))
                    for char in encoded:
                        if not 0xE000 <= ord(char) <= 0xF8FF:
                            continue
                        for records, pages, _ in fonts:
                            index = pages[ord(char) >> 8][ord(char) & 255]
                            self.assertNotEqual(index, 0)
                            self.assertEqual(records[index][0], ord(char))

    def test_all_mission_templates_use_unicode_without_an_individual_allowlist(self):
        config = json.loads((ROOT / "config.json").read_text(encoding="utf-8"))
        missions = [path for path in (ROOT / "data/raw_official/int").glob("*.int")
                    if path.stem[:2].isdigit() or path.stem.lower().startswith("p_")]
        self.assertEqual(len(missions), 38)
        for path in missions:
            self.assertTrue(uses_unicode_pua(config, path.stem), path.stem)
            self.assertTrue(self.compiled[get_umd_internal_path(path.stem)].startswith(b"\xff\xfe"))
        self.assertTrue(uses_unicode_pua(config, "P_99_FutureMission"))
        self.assertTrue(uses_unicode_pua(config, "99_FutureMission"))

    def test_new_bank_translation_is_shaped_and_has_glyphs_in_all_six_fonts(self):
        # Add a previously untranslated mission only in a temporary workspace.
        # No production translations, outputs or game files are changed.
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            config = json.loads((ROOT / "config.json").read_text(encoding="utf-8"))
            config["raw_dir"] = str(ROOT / "data/raw_official")
            config["active_font"] = str(ROOT / config["active_font"])
            config["translations_dir"] = str(root / "translations")
            config["dist_dir"] = str(root / "dist")
            source = json.loads((ROOT / "data/translations/story/03_Bank.json").read_text(encoding="utf-8"))
            selected = None
            for name, section in source["sections"].items():
                for key, value in section.items():
                    if isinstance(value, dict):
                        text = "ทดสอบคำแปลภารกิจใหม่ น้ำ ปู่ <KEY> %s \\n"
                        value["th"] = text
                        selected = (section["_source"], name, key, text)
                        break
                if selected:
                    break
            self.assertIsNotNone(selected)
            target = root / "translations/story/03_Bank.json"
            target.parent.mkdir(parents=True)
            target.write_text(json.dumps(source, ensure_ascii=False), encoding="utf-8")
            cfg = root / "config.json"
            cfg.write_text(json.dumps(config), encoding="utf-8")
            shaper = create_ui_shaper(cfg)
            compiled = compile_translations(cfg, verbose=False)
            fonts = build_magma_fonts(cfg, verbose=False)
            stem, section, key, expected = selected
            raw = compiled[get_umd_internal_path(stem)]
            self.assertTrue(raw.startswith(b"\xff\xfe"))
            actual = IniDocument.from_bytes(raw).get_section(section).get(key)
            self.assertEqual(shaper.decode(actual), expected)
            parsed_fonts = [read_mft(data) for name, data in fonts.items() if name.endswith(".mft")]
            self.assertEqual(len(parsed_fonts), 6)
            self.assertEqual(validate_localization_assets(compiled, fonts, cfg)["files"], 2)
            for char in actual:
                if ord(char) not in shaper.by_code:
                    continue
                for records, pages, _ in parsed_fonts:
                    index = pages[ord(char) >> 8][ord(char) & 255]
                    self.assertNotEqual(index, 0)
                    self.assertEqual(records[index][0], ord(char))

    def test_shared_messagebox_buttons_use_unicode_pua(self):
        data = self.compiled[get_umd_internal_path("System")]
        self.assertTrue(data.startswith(b"\xff\xfe"))
        section = IniDocument.from_bytes(data).get_section("MESSAGEBOX")
        for key, expected in (("Yes", "ใช่"), ("No", "ไม่"),
                              ("DefaultAccept", "ตกลง"), ("DefaultCancel", "ยกเลิก")):
            encoded = section.get(key)
            self.assertEqual(self.shaper.decode(encoded), expected)
            self.assertTrue(any(0xE000 <= ord(char) <= 0xF8FF for char in encoded))

    def test_build_validation_rejects_missing_font_and_corrupted_localization(self):
        fonts = dict(self.assets)
        fonts.pop(r"Data\Magma\DataPC\Fonts\Prototype Regular 36.mft")
        with self.assertRaisesRegex(ValueError, "Missing Magma font"):
            validate_localization_assets(self.compiled, fonts)
        compiled = dict(self.compiled)
        compiled[get_umd_internal_path("01_Lighthouse")] = b"broken"
        with self.assertRaisesRegex(ValueError, "UTF-16 BOM missing"):
            validate_localization_assets(compiled, self.assets)

    def test_build_validation_checks_all_current_localization(self):
        result = validate_localization_assets(self.compiled, self.assets)
        self.assertEqual(result["files"], 52)
        self.assertEqual(result["magma_fonts"], 6)
        self.assertEqual(result["values"], 8537)
        self.assertEqual(result["pua_clusters"], len(self.shaper.catalog))

    def test_build_validation_rejects_unshaped_thai_in_a_magma_file(self):
        path = get_umd_internal_path("01_Lighthouse")
        compiled = dict(self.compiled)
        document = IniDocument.from_bytes(compiled[path])
        section = document.get_section("GENERAL")
        section.set("Briefing_LAMBERT", self.shaper.decode(section.get("Briefing_LAMBERT")))
        compiled[path] = document.serialize(encoding="utf-16le", add_bom=True)
        with self.assertRaisesRegex(ValueError, "Compiled text mismatch"):
            validate_localization_assets(compiled, self.assets)

    def test_build_validation_rejects_a_missing_pua_lookup_in_one_font(self):
        path = r"Data\Magma\DataPC\Fonts\Prototype Regular 36.mft"
        fonts = dict(self.assets)
        raw = bytearray(fonts[path])
        records, _, _ = read_mft(raw)
        cursor = 90 + len(records) * GLYPH.size
        code = min(self.shaper.by_code)
        for page in range(256):
            present = raw[cursor]
            cursor += 1
            if present:
                if page == code >> 8:
                    struct.pack_into("<H", raw, cursor + (code & 255) * 2, 0)
                    break
                cursor += 512
        fonts[path] = bytes(raw)
        with self.assertRaisesRegex(ValueError, "Missing PUA"):
            validate_localization_assets(self.compiled, fonts)

    def test_equipment_hud_and_mission_content_use_unicode_pua(self):
        cases = (("Equipments", "FN7", "Name"),
                 ("01_Lighthouse", "GENERAL", "Briefing_LAMBERT"),
                 ("P_01_Lighthouse", "P_01_Lighthouse_Objectives", "Objective_0001"))
        for stem, section, key in cases:
            data = self.compiled[get_umd_internal_path(stem)]
            self.assertTrue(data.startswith(b"\xff\xfe"), stem)
            encoded = IniDocument.from_bytes(data).get_section(section).get(key)
            self.assertIsNotNone(encoded, (stem, section, key))
            self.assertTrue(any(0xE000 <= ord(char) <= 0xF8FF for char in encoded), stem)

    def test_original_latin_pixels_and_metrics_are_preserved(self):
        for filename, name, _ in FONT_SPECS:
            original, original_pages, original_footer = read_mft((RAW / filename).read_bytes())
            asset_name = "Bios Three Regular 20.mft" if name == "Bios Three Regular 20" else filename
            rebuilt, pages, footer = read_mft(self.assets[f"Data\\Magma\\DataPC\\Fonts\\{asset_name}"])
            self.assertEqual(pages[0], original_pages[0])
            last_page = original_footer[8] - 1
            old_image = Image.open(RAW / f"{name} {last_page}.tga").convert("L")
            image = Image.open(io.BytesIO(self.assets[f"Data\\Magma\\DataPC\\Fonts\\{name} {last_page}.tga"])).convert("L")
            self.assertEqual(image.crop((0, 0, *old_image.size)).tobytes(), old_image.tobytes())
            self.assertEqual(footer[:9], original_footer[:9])
            for old, new in zip(original, rebuilt):
                self.assertEqual(old[:6], new[:6])
                if int(old[6]) == last_page:
                    self.assertEqual(glyph_pixels(old, old_image), glyph_pixels(new, image), chr(old[0]))
                else:
                    self.assertEqual(old, new)

    def test_pua_pixels_match_harfbuzz_glyph_ids_and_positions(self):
        for filename, name, size in FONT_SPECS:
            asset_name = "Bios Three Regular 20.mft" if name == "Bios Three Regular 20" else filename
            records, pages, footer = read_mft(self.assets[f"Data\\Magma\\DataPC\\Fonts\\{asset_name}"])
            page = footer[8] - 1
            image = Image.open(io.BytesIO(self.assets[f"Data\\Magma\\DataPC\\Fonts\\{name} {page}.tga"])).convert("L")
            for code, cluster in self.shaper.by_code.items():
                expected, x, y, advance = self.shaper.render(cluster, size)
                record = records[pages[code >> 8][code & 255]]
                self.assertEqual(record[1:6], (*expected.size, x, y, advance))
                self.assertEqual(glyph_pixels(record, image), expected.tobytes())

    def test_gsub_gpos_and_sara_am_are_applied_before_remapping(self):
        samples = ["ปิด", "ปู่", "น้ำ", "ญู", "กิ่", "ปิ้"]
        shaper = ThaiShaper(ROOT / "data/fonts/ChakraPetch-Bold.ttf", samples)
        # The font substitutes the vowel after tall ป and splits sara am.
        normal_i = shaper.font.get_nominal_glyph(ord("ิ"))
        pi = shaper.shape_run("ปิ")[0]
        self.assertNotEqual(pi[1][1][0], normal_i)
        nam = shaper.shape_run("น้ำ")[0]
        self.assertTrue(any(glyph[3] or glyph[4] for glyph in nam[1]))
        self.assertNotIn(shaper.font.get_nominal_glyph(ord("ำ")), [g[0] for g in nam[1]])
        for sample in samples:
            encoded = shaper.encode(sample)
            self.assertEqual(shaper.decode(encoded), sample)
        text = "ปิด <KEY> %s \\n น้ำ"
        self.assertEqual(shaper.decode(shaper.encode(text)), text)

    def test_catalog_is_deterministic(self):
        other = create_ui_shaper()
        self.assertEqual(other.manifest(), self.shaper.manifest())


if __name__ == "__main__":
    unittest.main()

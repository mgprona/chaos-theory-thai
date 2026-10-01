"""Regression checks for Unicode lookup, atlas preservation and offline shaping."""

import io
import json
from pathlib import Path
import unittest

from PIL import Image

from src.core.ini_codec import IniDocument
from src.core.thai_shaper import ThaiShaper, create_ui_shaper
from src.pipeline.compiler import compile_translations
from src.pipeline.magma_builder import FONT_SPECS, build_magma_fonts, read_mft

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

    def test_every_compiled_ui_value_roundtrips_and_has_a_glyph(self):
        config = json.loads((ROOT / "config.json").read_text(encoding="utf-8"))
        fonts = [read_mft(data) for key, data in self.assets.items() if key.endswith(".mft")]
        for path in (ROOT / "data/translations/ui").glob("*.json"):
            translation = json.loads(path.read_text(encoding="utf-8"))
            for section_name, section in translation["sections"].items():
                stem = section["_source"]
                if stem not in config["unicode_ui_stems"]:
                    continue
                data = self.compiled[f"Data\\System\\Localization\\{stem}.int"]
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

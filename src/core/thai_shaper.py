"""Offline OpenType shaping: bake complete HarfBuzz clusters into PUA slots."""

from __future__ import annotations

from functools import lru_cache
from fnmatch import fnmatchcase
import hashlib
import json
from pathlib import Path
import re

import freetype
import uharfbuzz as hb
from PIL import Image, ImageChops

THAI_RUN = re.compile(r"[\u0e01-\u0e5b]+")
PUA_FIRST, PUA_LAST = 0xE000, 0xF8FF
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent


def uses_unicode_pua(config: dict, stem: str) -> bool:
    """Match renderer rules, including future mission stems, case-insensitively."""
    return any(fnmatchcase(stem.lower(), pattern.lower())
               for pattern in config.get("unicode_ui_stems", []))


class ThaiShaper:
    """Use one deterministic PUA catalog for localization and both UI fonts."""

    def __init__(self, font_path: Path, texts: list[str]):
        self.font_path = font_path
        font_data = font_path.read_bytes()
        self.font_hash = hashlib.sha256(font_data).hexdigest()
        face = hb.Face(font_data)
        self.upem = face.upem
        self.font = hb.Font(face)
        self.font.scale = (self.upem, self.upem)
        self.ft_face = freetype.Face(str(font_path))
        clusters = set()
        for text in texts:
            for match in THAI_RUN.finditer(text):
                clusters.update(self.shape_run(match.group()))
        if len(clusters) > PUA_LAST - PUA_FIRST + 1:
            raise ValueError("Thai PUA catalog exceeds the BMP private-use area")
        self.catalog = {cluster: PUA_FIRST + i for i, cluster in enumerate(sorted(clusters))}
        self.by_code = {code: cluster for cluster, code in self.catalog.items()}

    @lru_cache(maxsize=None)
    def shape_run(self, text: str) -> tuple:
        buffer = hb.Buffer()
        buffer.add_str(text)
        buffer.direction = "ltr"
        buffer.script = "Thai"
        buffer.language = "th"
        buffer.cluster_level = hb.BufferClusterLevel.MONOTONE_GRAPHEMES
        hb.shape(self.font, buffer)
        groups = {}
        for info, pos in zip(buffer.glyph_infos, buffer.glyph_positions):
            if info.codepoint == 0:
                raise ValueError(f"Chakra Petch is missing a glyph in {text!r}")
            groups.setdefault(info.cluster, []).append((info.codepoint, pos.x_advance, pos.y_advance, pos.x_offset, pos.y_offset))
        starts = sorted(groups)
        return tuple((text[start:end], tuple(groups[start])) for start, end in zip(starts, starts[1:] + [len(text)]))

    def encode(self, text: str) -> str:
        def replace(match):
            return "".join(chr(self.catalog[cluster]) for cluster in self.shape_run(match.group()))
        return THAI_RUN.sub(replace, text)

    def decode(self, text: str) -> str:
        return "".join(self.by_code[ord(c)][0] if ord(c) in self.by_code else c for c in text)

    def render(self, cluster: tuple, size: int) -> tuple[Image.Image, int, int, int]:
        """Rasterize glyph IDs at their GSUB/GPOS positions, on one baseline."""
        self.ft_face.set_pixel_sizes(0, size)
        scale = size / self.upem
        pen_x = pen_y = 0
        parts = []
        for gid, advance_x, advance_y, offset_x, offset_y in cluster[1]:
            self.ft_face.load_glyph(gid, freetype.FT_LOAD_RENDER | freetype.FT_LOAD_NO_HINTING)
            slot = self.ft_face.glyph
            bitmap = slot.bitmap
            if bitmap.width and bitmap.rows:
                pitch = abs(bitmap.pitch)
                raw = bytes(bitmap.buffer)
                rows = [raw[y * pitch:y * pitch + bitmap.width] for y in range(bitmap.rows)]
                if bitmap.pitch < 0:
                    rows.reverse()
                image = Image.frombytes("L", (bitmap.width, bitmap.rows), b"".join(rows))
                x = round((pen_x + offset_x) * scale) + slot.bitmap_left
                y = -round((pen_y + offset_y) * scale) - slot.bitmap_top
                parts.append((image, x, y))
            pen_x += advance_x
            pen_y += advance_y
        if not parts:
            raise ValueError(f"Empty Thai cluster: {cluster[0]!r}")
        left = min(x for _, x, _ in parts)
        top = min(y for _, _, y in parts)
        right = max(x + image.width for image, x, _ in parts)
        bottom = max(y + image.height for image, _, y in parts)
        canvas = Image.new("L", (right - left, bottom - top))
        for image, x, y in parts:
            layer = Image.new("L", canvas.size)
            layer.paste(image, (x - left, y - top))
            canvas = ImageChops.lighter(canvas, layer)
        return canvas, left, -top, round(pen_x * scale)

    def manifest(self) -> dict:
        return {"font_sha256": self.font_hash, "harfbuzz_version": hb.version_string(),
                "entries": [{"pua": f"U+{code:04X}", "text": cluster[0], "glyphs": cluster[1]}
                            for code, cluster in sorted(self.by_code.items())]}


def create_ui_shaper(config_path: str | Path = "config.json", custom_ttf_path: str | Path | None = None) -> ThaiShaper:
    config = json.loads((PROJECT_ROOT / config_path).read_text(encoding="utf-8"))
    font_path = PROJECT_ROOT / (custom_ttf_path or config["active_font"])
    texts = []
    for path in sorted((PROJECT_ROOT / config["translations_dir"]).glob("*/*.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        for section in data["sections"].values():
            if uses_unicode_pua(config, section.get("_source", path.stem)):
                texts.extend(v["th"] for v in section.values() if isinstance(v, dict) and v.get("th", "").strip())
    return ThaiShaper(font_path, texts)

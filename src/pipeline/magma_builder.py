"""Add Unicode Thai glyphs without destroying Magma's original Latin atlas.

The sparse Unicode lookup format is documented by FC2MFTConverter's
MFTFormat.cs. Chaos Theory uses a different, 23-byte glyph record.
"""

from __future__ import annotations

import json
import struct
from pathlib import Path
from typing import Dict, Optional, Union

from PIL import Image, ImageDraw, ImageFont
from ..core.thai_shaper import create_ui_shaper

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
GLYPH = struct.Struct("<HBBbbB4f")
FONT_SPECS = (
    ("bios three regular 20.mft", "Bios Three Regular 20", 15),
    ("prototype regular 13.mft", "Prototype Regular 13", 11),
)


def save_top_down_tga(image: Image.Image, filepath: Union[str, Path]) -> None:
    """Write the uncompressed grayscale, top-left TGA expected by Magma."""
    image = image.convert("L")
    w, h = image.size
    header = struct.pack("<3B5x4H2B", 0, 0, 3, 0, 0, w, h, 8, 0x20)
    path = Path(filepath)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(header + image.tobytes())


def read_mft(data: bytes) -> tuple[list[tuple], dict[int, list[int]], bytes]:
    """Read the supported Chaos Theory layout, retaining its footer."""
    if not data.startswith(b"Magma Font\0"):
        raise ValueError("Invalid Magma font signature")
    count = struct.unpack_from("<H", data, 88)[0]
    records = [GLYPH.unpack_from(data, 90 + i * GLYPH.size) for i in range(count)]
    cursor = 90 + count * GLYPH.size
    pages = {}
    for page in range(256):
        present = data[cursor]
        cursor += 1
        if present not in (0, 1):
            raise ValueError(f"Invalid Unicode lookup page {page}")
        if present:
            pages[page] = list(struct.unpack_from("<256H", data, cursor))
            cursor += 512
    footer = data[cursor:]
    if len(footer) < 9 or len(footer) < 9 + footer[8] * 4:
        raise ValueError("Truncated Magma texture dimensions")
    return records, pages, footer


def _render_glyph(font: ImageFont.FreeTypeFont, char: str) -> tuple[Image.Image, int, int, int]:
    # Crop actual ink relative to one baseline. getbbox(mark) in this TTF
    # includes blank space down to the baseline, so it is not an ink box.
    canvas = Image.new("L", (128, 128))
    origin = (64, 64)
    ImageDraw.Draw(canvas).text(origin, char, font=font, anchor="ls", fill=255)
    bounds = canvas.getbbox()
    if bounds is None:
        raise ValueError(f"Font has no visible glyph for U+{ord(char):04X}")
    advance = round(font.getlength(char))
    return canvas.crop(bounds), bounds[0] - origin[0], origin[1] - bounds[1], advance


def build_magma_fonts(
    config_path: Optional[str | Path] = "config.json",
    custom_ttf_path: Optional[str | Path] = None,
    output_dir: Optional[str | Path] = None,
    verbose: bool = True,
) -> Dict[str, bytes]:
    """Append Thai Unicode records and preserve every original glyph image."""
    cfg_file = PROJECT_ROOT / (config_path or "config.json")
    config = json.loads(cfg_file.read_text(encoding="utf-8"))
    ttf_path = PROJECT_ROOT / (custom_ttf_path or config.get("active_font", "data/fonts/ChakraPetch-Bold.ttf"))
    if not ttf_path.is_file():
        raise FileNotFoundError(f"Thai font not found: {ttf_path}")
    raw_dir = PROJECT_ROOT / config.get("raw_dir", "data/raw_official") / "fonts" / "magma"
    out_dir = Path(output_dir) if output_dir else PROJECT_ROOT / config.get("dist_dir", "dist") / "Data/Magma/DataPC/Fonts"
    out_dir.mkdir(parents=True, exist_ok=True)
    shaper = create_ui_shaper(cfg_file, custom_ttf_path)
    manifest_path = PROJECT_ROOT / config.get("dist_dir", "dist") / "thai_pua_map.json"
    manifest_path.write_text(json.dumps(shaper.manifest(), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    assets = {}

    for filename, texture_name, size in FONT_SPECS:
        template = raw_dir / filename
        if not template.is_file():
            raise FileNotFoundError(f"Magma font template not found: {template}")
        original = template.read_bytes()
        records, pages, footer_bytes = read_mft(original)
        footer = bytearray(footer_bytes)
        texture_index = footer[8] - 1
        old_w, old_h = struct.unpack_from("<HH", footer, 9 + texture_index * 4)
        texture_file = raw_dir / f"{texture_name} {texture_index}.tga"
        with Image.open(texture_file) as original_texture:
            if original_texture.size != (old_w, old_h):
                raise ValueError(f"Atlas size mismatch: {texture_file}")
            # Reuse an existing archive entry; repack does not add new entries.
            atlas = Image.new("L", (512, 512))
            atlas.paste(original_texture.convert("L"), (0, 0))

        # Rescale Latin UVs on the enlarged atlas. Keep the original metrics
        # and pixels, including i, j and other glyphs on the last texture.
        for index, record in enumerate(records):
            uv = record[6:]
            if int(uv[0]) == texture_index:
                scaled = tuple(texture_index + (v - texture_index) * dim / atlas.width for v, dim in zip(uv, (old_w, old_h, old_w, old_h)))
                records[index] = record[:6] + scaled

        font = ImageFont.truetype(str(ttf_path), size=size, layout_engine=ImageFont.Layout.BASIC)
        cursor_x, cursor_y, row_height = 2, old_h + 4, 0
        thai_count = 0
        rendered = []
        for code in range(161, 252):
            try:
                char = bytes([code]).decode("cp874")
            except UnicodeDecodeError:
                continue
            rendered.append((ord(char), *_render_glyph(font, char)))
        for code, cluster in sorted(shaper.by_code.items()):
            rendered.append((code, *shaper.render(cluster, size)))
        for codepoint, glyph, bearing_x, bearing_y, advance in rendered:
            w, h = glyph.size
            if cursor_x + w + 2 > atlas.width:
                cursor_x = 2
                cursor_y += row_height + 2
                row_height = 0
            if cursor_y + h + 2 > atlas.height:
                raise ValueError(f"Thai glyph atlas overflow for {filename}")
            atlas.paste(glyph, (cursor_x, cursor_y))
            uv = tuple(texture_index + p / atlas.width for p in (cursor_x + 0.5, cursor_y + 0.5, cursor_x + w + 0.5, cursor_y + h + 0.5))
            pages.setdefault(codepoint >> 8, [0] * 256)[codepoint & 255] = len(records)
            records.append((codepoint, w, h, bearing_x, bearing_y, advance, *uv))
            cursor_x += w + 2
            row_height = max(row_height, h)
            thai_count += 1

        header = bytearray(original[:90])
        struct.pack_into("<H", header, 88, len(records))
        lookup = bytearray()
        for page in range(256):
            lookup.append(int(page in pages))
            if page in pages:
                lookup.extend(struct.pack("<256H", *pages[page]))
        struct.pack_into("<HH", footer, 9 + texture_index * 4, atlas.width, atlas.height)
        mft_data = bytes(header) + b"".join(GLYPH.pack(*r) for r in records) + bytes(lookup) + bytes(footer)
        (out_dir / filename).write_bytes(mft_data)
        asset_filename = "Bios Three Regular 20.mft" if texture_name == "Bios Three Regular 20" else filename
        assets[f"Data\\Magma\\DataPC\\Fonts\\{asset_filename}"] = mft_data
        tga_out = out_dir / f"{texture_name} {texture_index}.tga"
        save_top_down_tga(atlas, tga_out)
        assets[f"Data\\Magma\\DataPC\\Fonts\\{tga_out.name}"] = tga_out.read_bytes()
        if texture_name == "Bios Three Regular 20":
            alias = out_dir / f"bios three regular 20 -{texture_index}-.tga"
            save_top_down_tga(atlas, alias)
            assets[f"Data\\Magma\\DataPC\\Fonts\\{alias.name}"] = alias.read_bytes()
        if verbose:
            print(f"[MagmaBuilder] {texture_name}: added {thai_count} Thai/PUA glyphs ({len(shaper.catalog)} shaped clusters); preserved {len(records) - thai_count} original glyphs")
    return assets

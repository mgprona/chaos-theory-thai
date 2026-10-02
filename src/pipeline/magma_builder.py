"""Add Unicode Thai glyphs without destroying Magma's original Latin atlas.

The sparse Unicode lookup format is documented by FC2MFTConverter's
MFTFormat.cs. Chaos Theory uses a different, 23-byte glyph record.
"""

from __future__ import annotations

import json
import struct
import time
from pathlib import Path
from typing import Dict, Optional, Union

from PIL import Image, ImageDraw, ImageFont
from ..core.thai_shaper import create_ui_shaper

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
GLYPH = struct.Struct("<HBBbbB4f")
FONT_SPECS = (
    ("bios three regular 20.mft", "Bios Three Regular 20", 15),
    ("Bios Three Regular 32.mft", "Bios Three Regular 32", 24),
    ("Bios Three Regular 48.mft", "Bios Three Regular 48", 36),
    ("prototype regular 13.mft", "Prototype Regular 13", 11),
    ("Prototype Regular 26.mft", "Prototype Regular 26", 22),
    ("Prototype Regular 36.mft", "Prototype Regular 36", 30),
)


def write_bytes_with_retry(path: Path, data: bytes, attempts: int = 5) -> None:
    """Write bytes, retrying transient Windows failures.

    File scanners and the search indexer occasionally hold a freshly written
    atlas file, which surfaces as ``OSError: [Errno 22]`` from ``write_bytes``.
    Retrying briefly makes the build deterministic without hiding real errors.
    """
    for attempt in range(attempts):
        try:
            path.write_bytes(data)
            return
        except OSError:
            if attempt == attempts - 1:
                raise
            time.sleep(0.2 * (attempt + 1))


def save_top_down_tga(image: Image.Image, filepath: Union[str, Path]) -> None:
    """Write the uncompressed grayscale, top-left TGA expected by Magma."""
    image = image.convert("L")
    w, h = image.size
    header = struct.pack("<3B5x4H2B", 0, 0, 3, 0, 0, w, h, 8, 0x20)
    path = Path(filepath)
    path.parent.mkdir(parents=True, exist_ok=True)
    write_bytes_with_retry(path, header + image.tobytes())


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


def _pack_glyphs(rendered: list, old_w: int, old_h: int, atlas_size: int = 1024) -> dict:
    """Pack glyphs into free rectangles beside and below the original atlas."""
    regions = [
        [old_w + 4, 2, atlas_size - 2, old_h + 2, old_w + 4, 2, 0],
        [2, old_h + 4, atlas_size - 2, atlas_size - 2, 2, old_h + 4, 0],
    ]
    positions = {}
    # Tall glyphs first prevents one large mark from inflating every shelf.
    ordered = sorted(rendered, key=lambda item: (-item[1].height, -item[1].width, item[0]))
    for codepoint, glyph, *_ in ordered:
        w, h = glyph.size
        for region in regions:
            left, top, right, bottom, x, y, row_height = region
            if w > right - left or h > bottom - top:
                continue
            if x + w > right:
                x, y, row_height = left, y + row_height + 2, 0
            if y + h > bottom:
                continue
            positions[codepoint] = (x, y)
            region[4:] = [x + w + 2, y, max(row_height, h)]
            break
        else:
            raise ValueError("Thai glyph atlas overflow")
    return positions


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
    manifest = json.dumps(shaper.manifest(), ensure_ascii=False, indent=2) + "\n"
    write_bytes_with_retry(manifest_path, manifest.encode("utf-8"))

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
            atlas = Image.new("L", (1024, 1024))
            atlas.paste(original_texture.convert("L"), (0, 0))

        # Rescale Latin UVs on the enlarged atlas. Keep the original metrics
        # and pixels, including i, j and other glyphs on the last texture.
        for index, record in enumerate(records):
            uv = record[6:]
            if int(uv[0]) == texture_index:
                scaled = tuple(texture_index + (v - texture_index) * dim / atlas.width for v, dim in zip(uv, (old_w, old_h, old_w, old_h)))
                records[index] = record[:6] + scaled

        font = ImageFont.truetype(str(ttf_path), size=size, layout_engine=ImageFont.Layout.BASIC)
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
        try:
            positions = _pack_glyphs(rendered, old_w, old_h, atlas.width)
        except ValueError as error:
            raise ValueError(f"Thai glyph atlas overflow for {filename}") from error
        for codepoint, glyph, bearing_x, bearing_y, advance in rendered:
            w, h = glyph.size
            cursor_x, cursor_y = positions[codepoint]
            atlas.paste(glyph, (cursor_x, cursor_y))
            uv = tuple(texture_index + p / atlas.width for p in (cursor_x + 0.5, cursor_y + 0.5, cursor_x + w + 0.5, cursor_y + h + 0.5))
            pages.setdefault(codepoint >> 8, [0] * 256)[codepoint & 255] = len(records)
            records.append((codepoint, w, h, bearing_x, bearing_y, advance, *uv))
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
        write_bytes_with_retry(out_dir / filename, mft_data)
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

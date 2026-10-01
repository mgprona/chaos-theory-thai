"""Preview the built MFT lookup, atlas and offsets, including PUA text."""

from pathlib import Path
import sys

from PIL import Image, ImageChops, ImageDraw

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from src.core.thai_shaper import create_ui_shaper
from src.pipeline.magma_builder import FONT_SPECS, read_mft


def render_line(text, name, shaper):
    folder = ROOT / "dist/Data/Magma/DataPC/Fonts"
    filename = name.lower() + ".mft"
    records, pages, footer = read_mft((folder / filename).read_bytes())
    canvas = Image.new("L", (900, 44))
    pen, baseline = 8, 25
    textures = {}
    for char in shaper.encode(text):
        page = pages.get(ord(char) >> 8)
        if page is None:
            raise ValueError(f"Missing lookup page for {char!r}")
        record = records[page[ord(char) & 255]]
        _, width, height, xoffset, bearing, advance, *uv = record
        texture_index = int(uv[0])
        if texture_index not in textures:
            image_path = folder / f"{name} {texture_index}.tga"
            if not image_path.exists():
                image_path = ROOT / "data/raw_official/fonts/magma" / image_path.name
            textures[texture_index] = Image.open(image_path).convert("L")
        atlas = textures[texture_index]
        x = round((uv[0] - texture_index) * atlas.width - 0.5)
        y = round((uv[1] - texture_index) * atlas.height - 0.5)
        glyph = atlas.crop((x, y, x + width, y + height))
        layer = Image.new("L", canvas.size)
        layer.paste(glyph, (pen + xoffset, baseline - bearing))
        canvas = ImageChops.lighter(canvas, layer)
        pen += advance
    return canvas.crop((0, 0, pen + 8, 44))


def main():
    # Preview only existing catalog entries; examples come from shipped menus.
    shaper = create_ui_shaper()
    lines = ["เลือกโหมดเกม", "การตั้งค่า", "การควบคุม", "โปรไฟล์ปัจจุบัน",
             "กดปุ่มใดๆ เพื่อเล่นต่อ", "การแสดงผล", "ระบบเสียง", "i j g y / F5"]
    result = Image.new("RGB", (1000, 850), (20, 23, 25))
    draw = ImageDraw.Draw(result)
    for column, (_, name, _) in enumerate(spec for spec in FONT_SPECS if spec[2] in (11, 15)):
        x = 20 + column * 500
        draw.text((x, 15), name + " - actual MFT / PUA", fill="white")
        for row, line in enumerate(lines):
            mask = render_line(line, name, shaper)
            mask = mask.resize((mask.width * 3, mask.height * 3), Image.Resampling.NEAREST)
            result.paste((225, 240, 230), (x, 45 + row * 95), mask)
    path = ROOT / "dist/magma_thai_pua_preview.png"
    result.save(path)
    print(path)


if __name__ == "__main__":
    main()

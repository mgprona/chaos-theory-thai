"""Unreal Engine 2 PCX bitmap font parser and builder for Chaos Theory.

Handles 8-bit indexed PCX font textures with delimiter bounding boxes
(color index 255 / RGB (107, 0, 219)), cell extraction, Thai glyph rendering,
and rebuilding of font textures.
"""

from __future__ import annotations
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union
import numpy as np
from PIL import Image, ImageDraw, ImageFont

DELIMITER_INDEX = 255
DELIMITER_RGB = (107, 0, 219)
FIRST_CHAR_CODE = 32  # ASCII 32 (space)
TOTAL_CELLS = 224     # ASCII 32..255


@dataclass
class PCXGlyph:
    """Represents a single character glyph within a PCX font."""
    index: int          # 0..223
    char_code: int      # 32..255
    char: str           # Single character
    bbox: Tuple[int, int, int, int]  # (x, y, width, height)
    image: Image.Image  # Cropped PIL Image (mode 'P' or 'L')


class PCXFont:
    """Parser and editor for Splinter Cell Chaos Theory PCX font bitmaps."""

    def __init__(self, filepath: Optional[Union[str, Path]] = None):
        self.filepath: Optional[Path] = Path(filepath) if filepath else None
        self.image: Optional[Image.Image] = None
        self.palette: Optional[List[int]] = None
        self.glyphs: List[PCXGlyph] = []
        self._glyph_map: Dict[int, PCXGlyph] = {}

        if self.filepath:
            self.load(self.filepath)

    def load(self, filepath: Union[str, Path]) -> None:
        """Load and parse a PCX font bitmap."""
        self.filepath = Path(filepath)
        if not self.filepath.exists():
            raise FileNotFoundError(f"PCX font file not found: {self.filepath}")

        raw_im = Image.open(self.filepath)
        if raw_im.mode != "P":
            raise ValueError(f"Expected indexed mode 'P', got {raw_im.mode}")

        self.image = raw_im.copy()
        self.palette = list(self.image.getpalette() or [])

        self._parse_cells()

    def _parse_cells(self) -> None:
        """Detect row and column delimiters and extract all 224 character cells."""
        if self.image is None:
            return

        arr = np.array(self.image)
        delim = DELIMITER_INDEX
        h, w = arr.shape

        self.glyphs = []
        self._glyph_map = {}

        y = 0
        cell_index = 0

        while y < h and cell_index < TOTAL_CELLS:
            # Check for horizontal delimiter line
            # A row delimiter starts with delimiter pixels at x=0, 1
            if arr[y, 0] == delim and arr[y, 1] == delim:
                y_top = y + 1
                y_bottom = y_top
                while y_bottom < h and not (arr[y_bottom, 0] == delim and arr[y_bottom, 1] == delim):
                    y_bottom += 1

                if y_bottom >= h:
                    break

                row_height = y_bottom - y_top
                # Find all vertical delimiter columns in this band
                band = arr[y_top:y_bottom, :]
                v_lines = np.where((band == delim).all(axis=0))[0]

                for i in range(len(v_lines) - 1):
                    if cell_index >= TOTAL_CELLS:
                        break
                    x_left = v_lines[i] + 1
                    x_right = v_lines[i + 1]
                    cell_width = x_right - x_left
                    if cell_width > 0 and row_height > 0:
                        char_code = FIRST_CHAR_CODE + cell_index
                        try:
                            # Try decoding as CP1252 or CP874
                            char = bytes([char_code]).decode("cp874")
                        except Exception:
                            char = chr(char_code)

                        crop_box = (x_left, y_top, x_right, y_bottom)
                        glyph_img = self.image.crop(crop_box)

                        glyph = PCXGlyph(
                            index=cell_index,
                            char_code=char_code,
                            char=char,
                            bbox=(x_left, y_top, cell_width, row_height),
                            image=glyph_img,
                        )
                        self.glyphs.append(glyph)
                        self._glyph_map[char_code] = glyph
                        cell_index += 1

                y = y_bottom
            else:
                y += 1

    def get_glyph(self, char_or_code: Union[str, int]) -> Optional[PCXGlyph]:
        """Retrieve a glyph by character or numeric code."""
        if isinstance(char_or_code, str):
            code = char_or_code.encode("cp874", errors="ignore")
            if not code:
                return None
            char_code = code[0]
        else:
            char_code = char_or_code
        return self._glyph_map.get(char_code)

    def _build_grayscale_lut(self) -> np.ndarray:
        """Build lookup table mapping grayscale (0..255) to valid palette indices."""
        pal = self.palette or []
        valid_indices = [i for i in range(256) if i != DELIMITER_INDEX]

        lums = []
        for i in valid_indices:
            r = pal[i * 3]
            g = pal[i * 3 + 1]
            b = pal[i * 3 + 2]
            lum = (r * 299 + g * 587 + b * 114) // 1000
            lums.append((i, lum))

        lut = np.zeros(256, dtype=np.uint8)
        for v in range(256):
            if v < 35:
                lut[v] = 0
            else:
                best_i, best_diff = 254, 9999
                for idx, lum in lums:
                    diff = abs(lum - v)
                    if diff < best_diff:
                        best_diff = diff
                        best_i = idx
                lut[v] = best_i
        return lut

    def inject_thai_glyphs(
        self,
        ttf_path: Union[str, Path],
        font_size: Optional[int] = None,
        char_codes: Optional[List[int]] = None,
        is_bold: bool = False,
    ) -> int:
        """Inject Thai glyphs from a TrueType font into CP874 slots (161..251)
        by laying out all 224 character cells with proper delimiter bounding boxes.

        Returns the number of Thai glyphs injected.
        """
        if not self.image or not self.palette:
            raise ValueError("No PCX image loaded")

        img_w, img_h = self.image.size
        pal = self.palette
        row_h = self.glyphs[0].bbox[3] if self.glyphs else 16

        if font_size is None:
            font_size = max(10, row_h - 3)

        ttf_font = ImageFont.truetype(str(ttf_path), size=font_size)
        dummy_draw = ImageDraw.Draw(Image.new("L", (10, 10)))
        lut = self._build_grayscale_lut()

        # Collect all 224 character cells (codes 32..255)
        # Min width is 6px to prevent squashing narrow vowels/tone marks
        min_w = 6
        glyphs_to_pack: List[Tuple[int, int, Image.Image]] = []
        injected = 0

        for code in range(FIRST_CHAR_CODE, FIRST_CHAR_CODE + TOTAL_CELLS):
            if code < 161:
                g = self.get_glyph(code)
                if g and g.image:
                    glyphs_to_pack.append((code, g.bbox[2], g.image))
                else:
                    blank = Image.new("P", (min_w, row_h), 0)
                    blank.putpalette(pal)
                    glyphs_to_pack.append((code, min_w, blank))
            elif 161 <= code <= 251:
                try:
                    char = bytes([code]).decode("cp874")
                    bb = dummy_draw.textbbox((0, 0), char, font=ttf_font)
                    gw = bb[2] - bb[0]
                    gh = bb[3] - bb[1]
                    cw = max(min_w, gw + 2)

                    canvas = Image.new("L", (cw, row_h), 0)
                    cdraw = ImageDraw.Draw(canvas)
                    pos_x = max(0, (cw - gw) // 2 - bb[0])
                    pos_y = max(0, (row_h - gh) // 2 - bb[1])
                    cdraw.text((pos_x, pos_y), char, fill=255, font=ttf_font)

                    c_arr = np.array(canvas)
                    p_arr = lut[c_arr]
                    glyph_img = Image.fromarray(p_arr, mode="P")
                    glyph_img.putpalette(pal)
                    glyphs_to_pack.append((code, cw, glyph_img))
                    injected += 1
                except Exception:
                    blank = Image.new("P", (min_w, row_h), 0)
                    blank.putpalette(pal)
                    glyphs_to_pack.append((code, min_w, blank))
            else:
                blank = Image.new("P", (min_w, row_h), 0)
                blank.putpalette(pal)
                glyphs_to_pack.append((code, min_w, blank))

        # Pack glyphs into image array with delimiter lines
        arr = np.zeros((img_h, img_w), dtype=np.uint8)
        y = 0

        # Initial top horizontal delimiter
        arr[y, :] = DELIMITER_INDEX
        y_top = y + 1
        y_bottom = y_top + row_h
        arr[y_top:y_bottom, 0] = DELIMITER_INDEX
        cur_x = 1

        for code, cw, gimg in glyphs_to_pack:
            if cur_x + cw + 1 > img_w:
                # Wrap to next row
                arr[y_top:y_bottom, cur_x:] = 0
                arr[y_bottom, :] = DELIMITER_INDEX
                y = y_bottom
                y_top = y + 1
                y_bottom = y_top + row_h
                if y_bottom >= img_h:
                    raise ValueError(f"PCX font texture height overflow: {img_h} at code {code}")
                arr[y_top:y_bottom, 0] = DELIMITER_INDEX
                cur_x = 1

            g_data = np.array(gimg)
            gh, gw = g_data.shape
            use_h = min(row_h, gh)
            use_w = min(cw, gw)
            arr[y_top:y_top + use_h, cur_x:cur_x + use_w] = g_data[:use_h, :use_w]

            cur_x += cw
            arr[y_top:y_bottom, cur_x] = DELIMITER_INDEX
            cur_x += 1

        # Close final row
        arr[y_bottom, :] = DELIMITER_INDEX

        new_image = Image.fromarray(arr, mode="P")
        new_image.putpalette(pal)
        self.image = new_image
        self._parse_cells()

        return injected

    def save(self, filepath: Union[str, Path]) -> None:
        """Save the PCX font to disk."""
        if not self.image:
            raise ValueError("No PCX image to save")
        dest = Path(filepath)
        dest.parent.mkdir(parents=True, exist_ok=True)
        self.image.save(dest, format="PCX")

    def export_preview(self, filepath: Union[str, Path], scale: int = 2) -> None:
        """Export an RGB preview image with character labels for verification."""
        if not self.image:
            raise ValueError("No PCX image loaded")
        rgb = self.image.convert("RGB")
        if scale > 1:
            rgb = rgb.resize((rgb.width * scale, rgb.height * scale), Image.NEAREST)
        dest = Path(filepath)
        dest.parent.mkdir(parents=True, exist_ok=True)
        rgb.save(dest)

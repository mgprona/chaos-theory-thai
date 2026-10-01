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

    def render_thai_character(
        self,
        char: str,
        font: ImageFont.FreeTypeFont,
        cell_bbox: Tuple[int, int, int, int],
        text_color_idx: int = 254,
        bg_color_idx: int = 0,
    ) -> Image.Image:
        """Render a single Thai character fitted to the given cell bounding box."""
        x, y, w, h = cell_bbox
        # Render high-resolution grayscale then downsample or render directly
        glyph_img = Image.new("P", (w, h), bg_color_idx)
        if self.palette:
            glyph_img.putpalette(self.palette)

        draw = ImageDraw.Draw(glyph_img)

        # Measure text
        bbox = draw.textbbox((0, 0), char, font=font)
        text_w = bbox[2] - bbox[0]
        text_h = bbox[3] - bbox[1]

        # Center horizontally and position vertically
        pos_x = max(0, (w - text_w) // 2 - bbox[0])
        pos_y = max(0, (h - text_h) // 2 - bbox[1])

        draw.text((pos_x, pos_y), char, fill=text_color_idx, font=font)
        return glyph_img

    def inject_thai_glyphs(
        self,
        ttf_path: Union[str, Path],
        font_size: Optional[int] = None,
        char_codes: Optional[List[int]] = None,
    ) -> int:
        """Inject Thai glyphs from a TrueType font into CP874 slots (161..251).

        Returns the number of glyphs injected.
        """
        if not self.image:
            raise ValueError("No PCX image loaded")

        if char_codes is None:
            # Thai range in CP874: 161 (0xA1, 'ก') to 251 (0xFB)
            char_codes = list(range(161, 252))

        # Determine reference cell height
        avg_h = int(np.median([g.bbox[3] for g in self.glyphs])) if self.glyphs else 16
        if font_size is None:
            font_size = max(10, avg_h - 2)

        ttf_font = ImageFont.truetype(str(ttf_path), size=font_size)

        # Identify text color index (most frequent non-black, non-delimiter index)
        colors = self.image.getcolors() or []
        sorted_colors = sorted(colors, key=lambda x: -x[0])
        text_idx = 254
        for _, idx in sorted_colors:
            if idx not in (0, DELIMITER_INDEX):
                text_idx = idx
                break

        injected = 0
        for code in char_codes:
            if code not in self._glyph_map:
                continue
            glyph = self._glyph_map[code]
            try:
                char = bytes([code]).decode("cp874")
            except Exception:
                continue

            rendered = self.render_thai_character(
                char=char,
                font=ttf_font,
                cell_bbox=glyph.bbox,
                text_color_idx=text_idx,
                bg_color_idx=0,
            )

            x, y, w, h = glyph.bbox
            self.image.paste(rendered, (x, y))
            glyph.image = rendered
            injected += 1

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

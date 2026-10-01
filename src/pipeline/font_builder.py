"""Thai font builder for Splinter Cell Chaos Theory.

Injects Thai glyphs (CP874 161..251) into the 5 PCX font bitmaps:
- txt_hud.pcx
- txt_mission.pcx
- txt_integration.pcx
- titre_regular_integration.pcx
- titre_bold_integration.pcx
"""

from __future__ import annotations
import json
import os
from pathlib import Path
from typing import Dict, List, Optional, Union
from ..core.pcx_font import PCXFont

PCX_FONT_NAMES = [
    "txt_hud.pcx",
    "txt_mission.pcx",
    "txt_integration.pcx",
    "titre_regular_integration.pcx",
    "titre_bold_integration.pcx",
]

DEFAULT_FALLBACK_FONTS = [
    r"C:\Windows\Fonts\tahoma.ttf",
    r"C:\Windows\Fonts\leelawad.ttf",
    r"C:\Windows\Fonts\arial.ttf",
]


def find_thai_ttf_font(custom_font_dir: Optional[Path] = None) -> Path:
    """Find a suitable TrueType font containing Thai glyphs."""
    if custom_font_dir and custom_font_dir.exists():
        for ttf in custom_font_dir.glob("*.ttf"):
            return ttf
        for otf in custom_font_dir.glob("*.otf"):
            return otf

    for font_path_str in DEFAULT_FALLBACK_FONTS:
        p = Path(font_path_str)
        if p.exists():
            return p

    raise FileNotFoundError("No suitable TrueType font with Thai support found.")


def build_thai_fonts(
    config_path: Optional[str | Path] = "config.json",
    custom_ttf_path: Optional[str | Path] = None,
    output_dir: Optional[str | Path] = None,
    export_previews: bool = True,
    verbose: bool = True,
) -> Dict[str, any]:
    """Generate Thai PCX font bitmaps from templates.

    Args:
        config_path: Path to config.json.
        custom_ttf_path: Optional custom TTF font to use.
        output_dir: Destination folder (default: dist/Data/Textures/Font).
        export_previews: Whether to export PNG previews alongside PCX.
        verbose: Whether to print progress.

    Returns:
        Statistics dictionary of built fonts.
    """
    cfg_file = Path(config_path) if config_path else Path("config.json")
    with open(cfg_file, "r", encoding="utf-8") as f:
        config = json.load(f)

    raw_pcx_dir = Path(config.get("raw_dir", "data/raw_official")) / "fonts" / "pcx"
    data_fonts_dir = Path(config.get("fonts_dir", "data/fonts"))
    dist_root = Path(config.get("dist_dir", "dist"))
    out_font_dir = Path(output_dir) if output_dir else dist_root / "Data" / "Textures" / "Font"
    out_font_dir.mkdir(parents=True, exist_ok=True)

    # Determine TTF font to use
    if custom_ttf_path and Path(custom_ttf_path).exists():
        ttf_font = Path(custom_ttf_path)
    else:
        ttf_font = find_thai_ttf_font(data_fonts_dir)

    if verbose:
        print(f"[FontBuilder] Using TrueType font: {ttf_font}")

    stats = {
        "fonts_processed": 0,
        "glyphs_injected": {},
        "output_files": [],
    }

    for font_name in PCX_FONT_NAMES:
        # Check source template in data/fonts/ or raw_pcx_dir
        src_template = data_fonts_dir / font_name
        if not src_template.exists():
            src_template = raw_pcx_dir / font_name

        if not src_template.exists():
            if verbose:
                print(f"[FontBuilder] Warning: Template {font_name} not found in {data_fonts_dir} or {raw_pcx_dir}")
            continue

        pcx = PCXFont(src_template)

        # Bold fonts can use bold TTF if available
        current_ttf = ttf_font
        if "bold" in font_name.lower():
            bold_fallback = Path(r"C:\Windows\Fonts\tahomabd.ttf")
            if bold_fallback.exists():
                current_ttf = bold_fallback

        injected = pcx.inject_thai_glyphs(current_ttf)
        dest_pcx = out_font_dir / font_name
        pcx.save(dest_pcx)

        stats["fonts_processed"] += 1
        stats["glyphs_injected"][font_name] = injected
        stats["output_files"].append(str(dest_pcx))

        if export_previews:
            preview_png = out_font_dir / f"{dest_pcx.stem}_preview.png"
            pcx.export_preview(preview_png)

        if verbose:
            print(f"[FontBuilder] {font_name}: injected {injected} Thai glyphs -> {dest_pcx.name}")

    if verbose:
        print(f"[FontBuilder] Successfully built {stats['fonts_processed']} PCX font bitmaps in {out_font_dir}")

    return stats

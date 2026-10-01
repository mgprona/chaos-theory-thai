"""Asset extractor for Splinter Cell Chaos Theory.

Extracts all official language files (.int, .fra, .deu, .esp, .ita) and font files
from dynamic-pc.umd and game folders into data/raw_official/.
"""

from __future__ import annotations
import json
import os
import shutil
from pathlib import Path
from typing import Dict, List, Optional
from ..core.umd_parser import UMDArchive, UMDEntry

LANG_EXTENSIONS = {"int", "fra", "deu", "esp", "ita"}


def extract_game_assets(
    config_path: Optional[str | Path] = "config.json",
    verbose: bool = True,
) -> Dict[str, any]:
    """Extract all official language files and fonts from the game files.

    Args:
        config_path: Path to config.json.
        verbose: Whether to print progress to stdout.

    Returns:
        Dictionary with extraction statistics.
    """
    cfg_file = Path(config_path) if config_path else Path("config.json")
    if not cfg_file.exists():
        raise FileNotFoundError(f"Configuration file not found: {cfg_file}")

    with open(cfg_file, "r", encoding="utf-8") as f:
        config = json.load(f)

    game_dir = Path(config["game_dir"])
    umd_path = game_dir / config.get("umd_subpath", r"System\dynamic-pc.umd")
    pcx_font_dir = game_dir / config.get("font_subpath", r"Data\Textures\Font")
    raw_root = Path(config.get("raw_dir", "data/raw_official"))
    data_fonts_dir = Path(config.get("fonts_dir", "data/fonts"))

    if not umd_path.exists():
        raise FileNotFoundError(f"UMD archive not found: {umd_path}")

    if verbose:
        print(f"[Extractor] Opening UMD archive: {umd_path}")

    archive = UMDArchive(umd_path)
    if verbose:
        print(f"[Extractor] Loaded UMD TOC: {len(archive.entries)} entries")

    stats = {
        "extracted_languages": {},
        "extracted_magma_fonts": 0,
        "copied_pcx_fonts": 0,
        "total_extracted": 0,
    }

    # 1. Extract official language files into data/raw_official/<lang>/
    for ext in LANG_EXTENSIONS:
        target_dir = raw_root / ext
        target_dir.mkdir(parents=True, exist_ok=True)
        stats["extracted_languages"][ext] = 0

    with open(archive.filepath, "rb") as f:
        for entry in archive.entries:
            ext = entry.extension
            if ext in LANG_EXTENSIONS:
                f.seek(entry.offset)
                data = f.read(entry.size)
                # Keep filename or relative path
                filename = Path(entry.name).name
                dest = raw_root / ext / filename
                dest.write_bytes(data)
                stats["extracted_languages"][ext] += 1
                stats["total_extracted"] += 1

            # 2. Extract Magma fonts
            elif "magma" in entry.name.lower() and "fonts" in entry.name.lower():
                magma_dir = raw_root / "fonts" / "magma"
                magma_dir.mkdir(parents=True, exist_ok=True)
                f.seek(entry.offset)
                data = f.read(entry.size)
                filename = Path(entry.name).name
                (magma_dir / filename).write_bytes(data)
                stats["extracted_magma_fonts"] += 1
                stats["total_extracted"] += 1

    # 3. Copy loose PCX fonts from Data\Textures\Font
    pcx_raw_dir = raw_root / "fonts" / "pcx"
    pcx_raw_dir.mkdir(parents=True, exist_ok=True)
    data_fonts_dir.mkdir(parents=True, exist_ok=True)

    if pcx_font_dir.exists():
        for pcx_file in pcx_font_dir.glob("*.pcx"):
            shutil.copy2(pcx_file, pcx_raw_dir / pcx_file.name)
            # Also copy to data/fonts as working copies
            shutil.copy2(pcx_file, data_fonts_dir / pcx_file.name)
            stats["copied_pcx_fonts"] += 1
            if verbose:
                print(f"[Extractor] Copied PCX font: {pcx_file.name}")
    else:
        if verbose:
            print(f"[Extractor] Warning: PCX font dir not found: {pcx_font_dir}")

    if verbose:
        print("[Extractor] Extraction summary:")
        for ext, count in stats["extracted_languages"].items():
            print(f"  - .{ext}: {count} files")
        print(f"  - Magma fonts: {stats['extracted_magma_fonts']} files")
        print(f"  - PCX fonts: {stats['copied_pcx_fonts']} files")
        print(f"  Total items processed: {stats['total_extracted'] + stats['copied_pcx_fonts']}")

    return stats

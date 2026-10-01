"""Translation compiler for Splinter Cell Chaos Theory.

Compiles JSON translations (with Thai text and English fallbacks) back into
official INI localization files (.int) with exact template preservation,
proper encoding (CP874 for Thai / UTF-16LE with BOM), and prepares
replacement files for UMD repacking.
"""

from __future__ import annotations
import json
import os
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union
from ..core.ini_codec import IniDocument

SYSTEM_STEMS = {"d3ddrv", "echelon", "engine", "window"}


def get_umd_internal_path(stem: str, ext: str = "int") -> str:
    """Return the canonical internal UMD archive path for a given file stem."""
    if stem.lower() in SYSTEM_STEMS:
        return f"System\\{stem}.{ext}"
    return f"Data\\System\\Localization\\{stem}.{ext}"


def compile_translations(
    config_path: Optional[str | Path] = "config.json",
    output_loose_dir: Optional[str | Path] = None,
    target_encoding: Optional[str] = None,
    verbose: bool = True,
) -> Dict[str, bytes]:
    """Compile all JSON translation files back into game localization files.

    Args:
        config_path: Path to config.json.
        output_loose_dir: Directory to save compiled loose files (default: dist/loose).
        target_encoding: Target text encoding (default from config: 'cp874').
        verbose: Whether to print compilation progress.

    Returns:
        Dictionary mapping internal UMD path to compiled file bytes:
        {"Data\\System\\Localization\\01_Lighthouse.int": b"..."}
    """
    cfg_file = Path(config_path) if config_path else Path("config.json")
    with open(cfg_file, "r", encoding="utf-8") as f:
        config = json.load(f)

    raw_dir = Path(config.get("raw_dir", "data/raw_official"))
    raw_int_dir = raw_dir / "int"
    trans_root = Path(config.get("translations_dir", "data/translations"))
    dist_root = Path(config.get("dist_dir", "dist"))
    loose_dir = Path(output_loose_dir) if output_loose_dir else dist_root / "loose"
    encoding = target_encoding or config.get("encoding", "cp874")

    # Map: stem -> {section: {key: new_value}}
    stem_translations: Dict[str, Dict[str, Dict[str, str]]] = defaultdict(lambda: defaultdict(dict))

    # Also track translation counts
    total_strings = 0
    thai_translated_strings = 0

    # 1. Read all JSON translation files from story, ui, opsat
    json_files = list(trans_root.glob("*/*.json"))
    if not json_files:
        if verbose:
            print(f"[Compiler] No JSON files found in {trans_root}")
        return {}

    for jf in json_files:
        with open(jf, "r", encoding="utf-8") as f:
            data = json.load(f)

        sections = data.get("sections", {})
        for sec_name, sec_dict in sections.items():
            source_stem = sec_dict.get("_source")
            for key, val_obj in sec_dict.items():
                if key.startswith("_"):
                    continue

                total_strings += 1
                if isinstance(val_obj, dict):
                    th_raw = val_obj.get("th", "")
                    en_text = val_obj.get("en", "")
                    if th_raw is not None and str(th_raw).strip() != "":
                        chosen_text = str(th_raw)
                        thai_translated_strings += 1
                    else:
                        chosen_text = en_text
                else:
                    chosen_text = str(val_obj)

                target_stem = source_stem or jf.stem
                stem_translations[target_stem][sec_name][key] = chosen_text

    if verbose:
        print(f"[Compiler] Loaded translations from {len(json_files)} JSON files.")
        print(f"[Compiler] Total strings: {total_strings}, Thai translated: {thai_translated_strings}")

    compiled_assets: Dict[str, bytes] = {}

    # 2. Compile each stem using its official .int as template
    for stem, translations in stem_translations.items():
        # Find matching template file in raw_int_dir
        template_file = None
        for cand in raw_int_dir.glob("*.int"):
            if cand.stem.lower() == stem.lower():
                template_file = cand
                break

        if not template_file or not template_file.exists():
            if verbose:
                print(f"[Compiler] Warning: Template file for stem '{stem}' not found in {raw_int_dir}")
            continue

        ini_doc = IniDocument.from_file(template_file)
        ini_doc.apply_translations(translations, fallback_to_english=True)

        # Check if any Thai characters (0x0E00..0x0E7F) are present in this stem
        stem_has_thai = False
        for s_dict in translations.values():
            for v in s_dict.values():
                if any(0x0E00 <= ord(c) <= 0x0E7F for c in str(v)):
                    stem_has_thai = True
                    break
            if stem_has_thai:
                break

        # If file has Thai or target encoding is CP874, use CP874 so the 224-cell
        # PCX font can render Thai characters. Only retain UTF-16LE if no Thai is
        # present and the file originally used UTF-16LE with unencodable characters (e.g. Credits.int).
        if stem_has_thai:
            out_encoding = encoding
            out_bom = False
        elif ini_doc.encoding == "utf-16le" or ini_doc.has_bom:
            try:
                # Test if all text is encodable in target encoding without replacement
                ini_doc.serialize(encoding=encoding, add_bom=False).decode(encoding)
                out_encoding = encoding
                out_bom = False
            except Exception:
                out_encoding = "utf-16le"
                out_bom = True
        else:
            out_encoding = encoding
            out_bom = False

        compiled_bytes = ini_doc.serialize(encoding=out_encoding, add_bom=out_bom)

        internal_path = get_umd_internal_path(template_file.stem, "int")
        compiled_assets[internal_path] = compiled_bytes

        # Also write loose file for direct game testing
        loose_file = loose_dir / internal_path
        loose_file.parent.mkdir(parents=True, exist_ok=True)
        loose_file.write_bytes(compiled_bytes)

    if verbose:
        print(f"[Compiler] Successfully compiled {len(compiled_assets)} localization files.")
        print(f"[Compiler] Loose files exported to: {loose_dir}")

    return compiled_assets

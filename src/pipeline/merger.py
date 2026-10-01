"""Multi-language merger for Splinter Cell Chaos Theory localization files.

Combines official .int (English), .fra (French), .deu (German), .esp (Spanish),
and .ita (Italian) files into structured, categorized JSON files ready for Thai translation:
- data/translations/story/ (19 missions combining main and P_ dialog files)
- data/translations/ui/ (HUD, menus, loadings, credits, xbox)
- data/translations/opsat/ (equipment, system, engine, low-level strings)

Each key contains: en, fr, de, es, it, and an empty th: "" (or existing th translation).
"""

from __future__ import annotations
import json
import os
from collections import OrderedDict
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union
from ..core.ini_codec import IniDocument

LANGUAGES = {
    "int": "en",
    "fra": "fr",
    "deu": "de",
    "esp": "es",
    "ita": "it",
}

STORY_MISSIONS: List[Tuple[str, List[str]]] = [
    ("00_Training", ["00_Training", "P_00_Training"]),
    ("00_Training_COOP", ["00_Training_COOP", "P_00_Training_COOP"]),
    ("01_Lighthouse", ["01_Lighthouse", "P_01_Lighthouse"]),
    ("01_Panama", ["01_Panama", "P_01_Panama"]),
    ("02_CargoShip", ["02_CargoShip", "P_02_CargoShip"]),
    ("02_Seoulthree", ["02_Seoulthree", "P_02_seoulthree"]),
    ("03_Bank", ["03_Bank", "P_03_Bank"]),
    ("03_ChemBunker", ["03_ChemBunker", "P_03_ChemBunker"]),
    ("04_GCS", ["04_GCS", "P_04_GCS"]),
    ("04_Penthouse", ["04_Penthouse", "P_04_Penthouse"]),
    ("05_Displace01", ["05_Displace01", "P_05_Displace01"]),
    ("05_NuclearPlant", ["05_NuclearPlant", "P_05_NuclearPlant"]),
    ("06_Hokkaido", ["06_Hokkaido", "P_06_Hokkaido"]),
    ("07_Battery", ["07_Battery", "P_07_Battery"]),
    ("07_UNhq", ["07_UNhq", "P_07_UNhq"]),
    ("08_SeoulOne", ["08_SeoulOne", "P_08_SeoulOne"]),
    ("09_SeoulTwo", ["09_SeoulTwo", "P_09_SeoulTwo"]),
    ("10_BathHouse", ["10_BathHouse", "P_10_Bathhouse"]),
    ("11_KokuboSosho", ["11_KokuboSosho", "P_11_KokuboSosho"]),
]

UI_FILES: Dict[str, List[str]] = {
    "hud": ["HUD"],
    "ingame_menus": ["InGameMenus"],
    "pregame_menus": ["PreGameMenus"],
    "pregame_pc": ["PreGame_PC"],
    "loading_screens": ["LoadingScreens"],
    "credits": ["Credits"],
    "xbox_live": ["XBOXLive"],
}

OPSAT_FILES: Dict[str, List[str]] = {
    "equipment": ["Equipments"],
    "system": ["System"],
    "training": ["Training"],
    "engine": ["Engine"],
    "window": ["Window"],
    "d3ddrv": ["D3DDrv"],
    "echelon": ["Echelon"],
}


def _find_stem_file(raw_dir: Path, ext: str, stem: str) -> Optional[Path]:
    """Find a raw file by stem name (case-insensitive) under raw_dir/<ext>/."""
    ext_dir = raw_dir / ext
    if not ext_dir.exists():
        return None

    stem_lower = stem.lower()
    for f in ext_dir.iterdir():
        if f.suffix.lower() == f".{ext}" and f.stem.lower() == stem_lower:
            return f
    return None


def _load_ini_docs(raw_dir: Path, stem: str) -> Dict[str, IniDocument]:
    """Load IniDocuments for all available languages for a given stem."""
    docs = {}
    for ext in LANGUAGES:
        fp = _find_stem_file(raw_dir, ext, stem)
        if fp and fp.exists():
            docs[ext] = IniDocument.from_file(fp)
    return docs


def _load_existing_th(output_json_path: Path) -> Dict[str, Dict[str, str]]:
    """Load existing 'th' translations if the JSON file already exists."""
    existing_th = {}
    if output_json_path.exists():
        try:
            with open(output_json_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            sections = data.get("sections", {})
            for sec_name, sec_dict in sections.items():
                for k, v in sec_dict.items():
                    if k.startswith("_"):
                        continue
                    if isinstance(v, dict) and "th" in v and v["th"].strip():
                        existing_th.setdefault(sec_name, {})[k] = v["th"]
        except Exception:
            pass
    return existing_th


def _merge_stems_to_json(
    stems: List[str],
    category: str,
    output_name: str,
    raw_dir: Path,
    output_dir: Path,
    include_nulls: bool = False,
) -> Tuple[Path, int]:
    """Merge a set of stems into a single JSON translation file.

    Returns (output_path, total_string_count).
    """
    output_path = output_dir / f"{output_name}.json"
    existing_th = _load_existing_th(output_path)

    sections_data: OrderedDict[str, OrderedDict] = OrderedDict()
    total_strings = 0

    for stem in stems:
        ini_docs = _load_ini_docs(raw_dir, stem)
        int_doc = ini_docs.get("int")
        if not int_doc:
            continue

        for sec_name, sec in int_doc.sections.items():
            sec_dict: OrderedDict[str, any] = OrderedDict()
            sec_dict["_source"] = stem

            for entry in sec.entries:
                if not entry.is_key_value or not entry.key:
                    continue

                en_val = entry.value or ""
                # Skip non-translatable dummy null placeholders
                if not include_nulls and en_val.strip().lower() == "(null)":
                    continue

                key = entry.key
                if key in sec_dict:
                    # Skip duplicate identical key in section
                    continue

                string_item: OrderedDict[str, str] = OrderedDict()
                string_item["en"] = en_val

                # Add other official translations
                for ext, lang_code in LANGUAGES.items():
                    if ext == "int":
                        continue
                    lang_doc = ini_docs.get(ext)
                    lang_sec = lang_doc.get_section(sec_name) if lang_doc else None
                    lang_val = lang_sec.get(key) if lang_sec else None
                    string_item[lang_code] = lang_val if lang_val is not None else ""

                # Preserve existing Thai translation if available
                prev_th = existing_th.get(sec_name, {}).get(key, "")
                string_item["th"] = prev_th

                sec_dict[key] = string_item
                total_strings += 1

            if len(sec_dict) > 1:  # More than just _source
                sections_data[sec_name] = sec_dict

    result_doc = OrderedDict()
    result_doc["_meta"] = {
        "category": category,
        "name": output_name,
        "sources": stems,
        "total_strings": total_strings,
    }
    result_doc["sections"] = sections_data

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result_doc, f, ensure_ascii=False, indent=2)

    return output_path, total_strings


def merge_translations(
    config_path: Optional[str | Path] = "config.json",
    include_nulls: bool = False,
    verbose: bool = True,
) -> Dict[str, any]:
    """Merge all extracted official language files into structured JSON files.

    Args:
        config_path: Path to config.json.
        include_nulls: Whether to include (null) dummy tokens in JSON.
        verbose: Whether to print progress.

    Returns:
        Statistics dictionary of merged files and string counts.
    """
    cfg_file = Path(config_path) if config_path else Path("config.json")
    with open(cfg_file, "r", encoding="utf-8") as f:
        config = json.load(f)

    raw_dir = Path(config.get("raw_dir", "data/raw_official"))
    trans_root = Path(config.get("translations_dir", "data/translations"))

    stats = {
        "story": {},
        "ui": {},
        "opsat": {},
        "total_strings": 0,
        "total_files": 0,
    }

    if verbose:
        print("[Merger] Starting multi-language JSON translation merge...")

    # 1. Story Missions
    story_dir = trans_root / "story"
    for out_name, stems in STORY_MISSIONS:
        out_path, count = _merge_stems_to_json(
            stems=stems,
            category="story",
            output_name=out_name,
            raw_dir=raw_dir,
            output_dir=story_dir,
            include_nulls=include_nulls,
        )
        stats["story"][out_name] = count
        stats["total_strings"] += count
        stats["total_files"] += 1
        if verbose:
            print(f"  [Story] {out_name}.json: {count} translatable strings")

    # 2. UI Files
    ui_dir = trans_root / "ui"
    for out_name, stems in UI_FILES.items():
        out_path, count = _merge_stems_to_json(
            stems=stems,
            category="ui",
            output_name=out_name,
            raw_dir=raw_dir,
            output_dir=ui_dir,
            include_nulls=include_nulls,
        )
        stats["ui"][out_name] = count
        stats["total_strings"] += count
        stats["total_files"] += 1
        if verbose:
            print(f"  [UI] {out_name}.json: {count} translatable strings")

    # 3. OPSAT / System Files
    opsat_dir = trans_root / "opsat"
    for out_name, stems in OPSAT_FILES.items():
        out_path, count = _merge_stems_to_json(
            stems=stems,
            category="opsat",
            output_name=out_name,
            raw_dir=raw_dir,
            output_dir=opsat_dir,
            include_nulls=include_nulls,
        )
        stats["opsat"][out_name] = count
        stats["total_strings"] += count
        stats["total_files"] += 1
        if verbose:
            print(f"  [OPSAT] {out_name}.json: {count} translatable strings")

    if verbose:
        print(f"[Merger] Successfully generated {stats['total_files']} JSON translation files.")
        print(f"[Merger] Total translatable strings extracted: {stats['total_strings']}")

    return stats

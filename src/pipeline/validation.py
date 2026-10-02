"""Verify serialized localization and font coverage before UMD repacking."""

from __future__ import annotations

import json
from pathlib import Path

from ..core.ini_codec import IniDocument
from ..core.thai_shaper import create_ui_shaper, uses_unicode_pua
from .compiler import get_umd_internal_path
from .magma_builder import FONT_SPECS, read_mft


def validate_localization_assets(
    compiled: dict[str, bytes],
    fonts: dict[str, bytes],
    config_path: str | Path = "config.json",
    custom_ttf_path: str | Path | None = None,
) -> dict[str, int]:
    """Reject lost text, missing templates and PUA glyphs before installation."""
    config = json.loads(Path(config_path).read_text(encoding="utf-8"))
    shaper = create_ui_shaper(config_path, custom_ttf_path)
    parsed_fonts = []
    for filename, name, _ in FONT_SPECS:
        filename = "Bios Three Regular 20.mft" if name == "Bios Three Regular 20" else filename
        path = f"Data\\Magma\\DataPC\\Fonts\\{filename}"
        if path not in fonts:
            raise ValueError(f"Missing Magma font: {path}")
        parsed_fonts.append((filename, read_mft(fonts[path])))
    for code in shaper.by_code:
        for filename, (records, pages, _) in parsed_fonts:
            index = pages.get(code >> 8, [0] * 256)[code & 255]
            if not index or index >= len(records) or records[index][0] != code:
                raise ValueError(f"Missing PUA U+{code:04X} in {filename}")

    documents = {}
    templates = {path.stem.lower(): path for path in (Path(config["raw_dir"]) / "int").glob("*.int")}
    original_documents = {}
    values = 0
    assets = {name.lower(): data for name, data in compiled.items()}
    for path in sorted(Path(config["translations_dir"]).glob("*/*.json")):
        source = json.loads(path.read_text(encoding="utf-8"))
        for name, section in source["sections"].items():
            stem = section.get("_source", path.stem)
            internal = get_umd_internal_path(stem).lower()
            if internal not in assets:
                raise ValueError(f"Missing compiled localization: {stem}")
            if internal not in documents:
                raw = assets[internal]
                if uses_unicode_pua(config, stem) and not raw.startswith(b"\xff\xfe"):
                    raise ValueError(f"UTF-16 BOM missing: {stem}")
                documents[internal] = IniDocument.from_bytes(raw, default_encoding=config["encoding"])
            compiled_section = documents[internal].get_section(name)
            if compiled_section is None:
                raise ValueError(f"Missing compiled section: {stem}/{name}")
            for key, value in section.items():
                if key.startswith("_"):
                    continue
                translated = None
                if isinstance(value, dict):
                    translated = value.get("th")
                    expected = str(translated) if translated is not None and str(translated).strip() else value.get("en", "")
                else:
                    expected = str(value)
                # Empty fallback values intentionally retain the official template.
                if expected is None or not str(expected).strip():
                    if stem.lower() not in original_documents:
                        original_documents[stem.lower()] = IniDocument.from_file(templates[stem.lower()])
                    expected = original_documents[stem.lower()].get_section(name).get(key)
                actual = compiled_section.get(key)
                if actual is None:
                    raise ValueError(f"Missing compiled key: {stem}/{name}/{key}")
                encoded_expected = expected
                if uses_unicode_pua(config, stem) and translated is not None and str(translated).strip():
                    encoded_expected = shaper.encode(expected)
                if actual != encoded_expected:
                    raise ValueError(f"Compiled text mismatch: {stem}/{name}/{key}")
                values += 1
    return {"files": len(documents), "values": values,
            "pua_clusters": len(shaper.catalog), "magma_fonts": len(parsed_fonts)}

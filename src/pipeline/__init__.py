"""Modding pipeline: extraction, merging, compilation, and font building."""
from .extractor import extract_game_assets
from .merger import merge_translations
from .compiler import compile_translations
from .font_builder import build_thai_fonts
from .magma_builder import build_magma_fonts

__all__ = [
    "extract_game_assets",
    "merge_translations",
    "compile_translations",
    "build_thai_fonts",
    "build_magma_fonts",
]

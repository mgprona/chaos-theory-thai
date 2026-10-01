"""Command Line Interface for Splinter Cell Chaos Theory Thai Translation Mod Toolchain.

Usage:
  python src/cli.py extract       Extract official language and font files from game
  python src/cli.py merge         Generate/update multi-language JSON translation files
  python src/cli.py compile       Compile JSON translations into game .int files
  python src/cli.py build-fonts   Build Thai PCX font bitmaps
  python src/cli.py build-umd     Compile and repack dynamic-pc.umd
  python src/cli.py build-all     Compile translations, build fonts, and repack UMD
  python src/cli.py stats         Display translation progress and statistics
  python src/cli.py backup        Create backup of original game files
  python src/cli.py install       Install compiled mod files into game directory
"""

from __future__ import annotations
import argparse
import json
import os
import shutil
import sys
import time
from pathlib import Path

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.core.umd_parser import UMDArchive
from src.pipeline.extractor import extract_game_assets
from src.pipeline.merger import merge_translations
from src.pipeline.compiler import compile_translations
from src.pipeline.font_builder import build_thai_fonts


def get_config(config_path: str = "config.json") -> dict:
    cfg_p = PROJECT_ROOT / config_path
    if not cfg_p.exists():
        print(f"Error: Configuration file not found at {cfg_p}")
        sys.exit(1)
    with open(cfg_p, "r", encoding="utf-8") as f:
        return json.load(f)


def cmd_extract(args: argparse.Namespace) -> None:
    print("=" * 60)
    print("Extraction: Pulling game assets from UMD and data folders")
    print("=" * 60)
    stats = extract_game_assets(config_path=PROJECT_ROOT / "config.json", verbose=True)
    print("\nExtraction complete!")


def cmd_merge(args: argparse.Namespace) -> None:
    print("=" * 60)
    print("Merge: Generating 5-language JSON translation files")
    print("=" * 60)
    stats = merge_translations(
        config_path=PROJECT_ROOT / "config.json",
        include_nulls=args.include_nulls,
        verbose=True,
    )
    print(f"\nMerge complete! {stats['total_strings']} strings across {stats['total_files']} files.")


def cmd_compile(args: argparse.Namespace) -> None:
    print("=" * 60)
    print("Compile: Compiling JSON translations to .int files")
    print("=" * 60)
    assets = compile_translations(
        config_path=PROJECT_ROOT / "config.json",
        target_encoding=args.encoding,
        verbose=True,
    )
    print(f"\nCompilation complete! {len(assets)} files compiled.")


def cmd_build_fonts(args: argparse.Namespace) -> None:
    print("=" * 60)
    print("Build Fonts: Generating Thai PCX font textures")
    print("=" * 60)
    stats = build_thai_fonts(
        config_path=PROJECT_ROOT / "config.json",
        custom_ttf_path=args.font,
        export_previews=True,
        verbose=True,
    )
    print(f"\nBuilt {stats['fonts_processed']} fonts successfully.")


def cmd_build_umd(args: argparse.Namespace) -> None:
    print("=" * 60)
    print("Build UMD: Compiling translations and repacking dynamic-pc.umd")
    print("=" * 60)
    config = get_config()
    game_dir = Path(config["game_dir"])
    src_umd = game_dir / config.get("umd_subpath", r"System\dynamic-pc.umd")
    out_umd = PROJECT_ROOT / config.get("dist_dir", "dist") / "System" / "dynamic-pc.umd"

    if not src_umd.exists():
        print(f"Error: Original UMD not found: {src_umd}")
        sys.exit(1)

    print("Step 1: Compiling translations...")
    compiled_assets = compile_translations(config_path=PROJECT_ROOT / "config.json", verbose=False)
    print(f"Compiled {len(compiled_assets)} localization files.")

    print(f"\nStep 2: Loading source UMD: {src_umd}...")
    archive = UMDArchive(src_umd)

    print(f"Step 3: Repacking to {out_umd}...")
    start_time = time.time()

    def progress(cur, total, name):
        pct = (cur / total) * 100
        print(f"\rRepacking: {pct:.1f}% ({cur}/{total} files) - {name[:30]}", end="", flush=True)

    final_size = archive.repack(
        output_path=out_umd,
        replacements=compiled_assets,
        progress_callback=progress,
    )
    elapsed = time.time() - start_time
    print(f"\n\nRepack complete in {elapsed:.2f} seconds!")
    print(f"Output UMD size: {final_size:,} bytes at {out_umd}")


def cmd_build_all(args: argparse.Namespace) -> None:
    print("=" * 60)
    print("Build All: Full mod build pipeline")
    print("=" * 60)
    cmd_compile(args)
    cmd_build_fonts(args)
    cmd_build_umd(args)
    print("\nAll build steps finished successfully!")


def cmd_stats(args: argparse.Namespace) -> None:
    print("=" * 60)
    print("Translation Statistics")
    print("=" * 60)
    config = get_config()
    trans_root = PROJECT_ROOT / config.get("translations_dir", "data/translations")

    total_all = 0
    translated_all = 0

    for cat in ["story", "ui", "opsat"]:
        cat_dir = trans_root / cat
        if not cat_dir.exists():
            continue
        print(f"\n[{cat.upper()}]")
        for jf in sorted(cat_dir.glob("*.json")):
            with open(jf, "r", encoding="utf-8") as f:
                data = json.load(f)
            file_total = 0
            file_trans = 0
            for sec_name, sec_dict in data.get("sections", {}).items():
                for k, v in sec_dict.items():
                    if k.startswith("_"):
                        continue
                    file_total += 1
                    if isinstance(v, dict) and v.get("th", "").strip():
                        file_trans += 1
            pct = (file_trans / file_total * 100) if file_total > 0 else 0
            bar_len = 20
            filled = int(bar_len * (file_trans / file_total)) if file_total > 0 else 0
            bar = "#" * filled + "-" * (bar_len - filled)
            print(f"  {jf.stem:25} [{bar}] {pct:5.1f}% ({file_trans}/{file_total})")
            total_all += file_total
            translated_all += file_trans

    pct_all = (translated_all / total_all * 100) if total_all > 0 else 0
    print("\n" + "-" * 60)
    print(f"TOTAL PROGRESS: {pct_all:.2f}% ({translated_all:,} / {total_all:,} strings translated)")
    print("-" * 60)


def cmd_backup(args: argparse.Namespace) -> None:
    print("=" * 60)
    print("Backup: Backing up official game files")
    print("=" * 60)
    config = get_config()
    game_dir = Path(config["game_dir"])
    backup_dir = PROJECT_ROOT / config.get("backups_dir", "backups")
    backup_dir.mkdir(parents=True, exist_ok=True)

    # 1. Backup UMD
    umd_src = game_dir / config.get("umd_subpath", r"System\dynamic-pc.umd")
    if umd_src.exists():
        umd_dst = backup_dir / "dynamic-pc.umd"
        if not umd_dst.exists():
            print(f"Backing up {umd_src} -> {umd_dst}...")
            shutil.copy2(umd_src, umd_dst)
            print("UMD backup created!")
        else:
            print("UMD backup already exists. Skipping.")

    # 2. Backup Fonts
    font_src_dir = game_dir / config.get("font_subpath", r"Data\Textures\Font")
    if font_src_dir.exists():
        font_dst_dir = backup_dir / "Fonts"
        font_dst_dir.mkdir(parents=True, exist_ok=True)
        for f in font_src_dir.glob("*.pcx"):
            dst = font_dst_dir / f.name
            if not dst.exists():
                shutil.copy2(f, dst)
        print("Font backups created in backups/Fonts/")

    # 3. Backup any existing loose localization files
    existing_loc = game_dir / "Data" / "System" / "Localization"
    if existing_loc.exists():
        loose_backup = backup_dir / "loose" / "Data" / "System" / "Localization"
        loose_backup.mkdir(parents=True, exist_ok=True)
        for f in existing_loc.glob("*.int"):
            dst = loose_backup / f.name
            if not dst.exists():
                shutil.copy2(f, dst)


def cmd_install(args: argparse.Namespace) -> None:
    print("=" * 60)
    print("Install: Installing mod to game folder")
    print("=" * 60)
    config = get_config()
    game_dir = Path(config["game_dir"])
    dist_dir = PROJECT_ROOT / config.get("dist_dir", "dist")

    # Ensure backups exist first
    cmd_backup(args)

    installed_anything = False

    # 1. Install UMD (if built)
    dist_umd = dist_dir / "System" / "dynamic-pc.umd"
    if dist_umd.exists():
        target_umd = game_dir / config.get("umd_subpath", r"System\dynamic-pc.umd")
        print(f"Installing {dist_umd} -> {target_umd}...")
        shutil.copy2(dist_umd, target_umd)
        print("UMD installed successfully!")
        installed_anything = True
    else:
        print(f"Note: dist UMD not found at {dist_umd} (using loose file mode or run 'build-umd').")

    # 2. Install loose localization files (if compiled)
    dist_loose = dist_dir / "loose"
    if dist_loose.exists():
        loose_files = list(dist_loose.rglob("*.int"))
        if loose_files:
            print(f"Installing {len(loose_files)} loose localization files to game directory...")
            for lf in loose_files:
                rel = lf.relative_to(dist_loose)
                dst = game_dir / rel
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(lf, dst)
            print(f"Loose localization files installed into {game_dir}!")
            installed_anything = True

    # 3. Install PCX Fonts
    dist_fonts = dist_dir / "Data" / "Textures" / "Font"
    if dist_fonts.exists():
        target_font_dir = game_dir / config.get("font_subpath", r"Data\Textures\Font")
        target_font_dir.mkdir(parents=True, exist_ok=True)
        font_count = 0
        for pcx in dist_fonts.glob("*.pcx"):
            dst = target_font_dir / pcx.name
            shutil.copy2(pcx, dst)
            font_count += 1
        print(f"Installed {font_count} PCX fonts into {target_font_dir}!")
        installed_anything = True

    if not installed_anything:
        print("Warning: No compiled mod files found in dist/. Run 'compile' or 'build-all' first.")
    else:
        print("\nMod installation completed successfully!")


def main():
    parser = argparse.ArgumentParser(
        description="Chaos Theory Thai Translation Mod Pipeline CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # extract
    subparsers.add_parser("extract", help="Extract game localization and font files")

    # merge
    p_merge = subparsers.add_parser("merge", help="Merge official languages into translation JSONs")
    p_merge.add_argument("--include-nulls", action="store_true", help="Include (null) dummy strings in JSON")

    # compile
    p_comp = subparsers.add_parser("compile", help="Compile JSON translations to game .int files")
    p_comp.add_argument("--encoding", default=None, help="Target text encoding (e.g. cp874, utf-16le)")

    # build-fonts
    p_fonts = subparsers.add_parser("build-fonts", help="Generate Thai PCX font textures")
    p_fonts.add_argument("--font", default=None, help="Path to custom TrueType font file")

    # build-umd
    subparsers.add_parser("build-umd", help="Compile translations and repack dynamic-pc.umd")

    # build-all
    p_all = subparsers.add_parser("build-all", help="Compile translations, build fonts, and repack UMD")
    p_all.add_argument("--encoding", default=None, help="Target text encoding")
    p_all.add_argument("--font", default=None, help="Custom TrueType font")

    # stats
    subparsers.add_parser("stats", help="Display translation progress")

    # backup
    subparsers.add_parser("backup", help="Backup original game files")

    # install
    subparsers.add_parser("install", help="Install compiled mod files into game directory")

    args = parser.parse_args()

    commands = {
        "extract": cmd_extract,
        "merge": cmd_merge,
        "compile": cmd_compile,
        "build-fonts": cmd_build_fonts,
        "build-umd": cmd_build_umd,
        "build-all": cmd_build_all,
        "stats": cmd_stats,
        "backup": cmd_backup,
        "install": cmd_install,
    }

    cmd_fn = commands.get(args.command)
    if cmd_fn:
        cmd_fn(args)


if __name__ == "__main__":
    main()

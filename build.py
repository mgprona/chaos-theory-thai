"""Splinter Cell Chaos Theory - Thai Translation Mod Build Script.

Runs the build toolchain to compile translations, generate Thai fonts,
and package the mod.

Examples:
  python build.py             # Compile translations and build fonts
  python build.py --umd       # Compile translations, build fonts, and repack UMD
  python build.py --stats     # Show translation progress stats
  python build.py --install   # Build and install mod directly to game folder
"""

import argparse
import sys
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.cli import (
    cmd_compile,
    cmd_build_fonts,
    cmd_build_umd,
    cmd_install,
    cmd_stats,
)


def main():
    parser = argparse.ArgumentParser(
        description="Chaos Theory Thai Mod - Build Script",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--umd", action="store_true", help="Repack dynamic-pc.umd with compiled translations")
    parser.add_argument("--fonts", action="store_true", help="Build Thai PCX fonts")
    parser.add_argument("--stats", action="store_true", help="Display translation progress")
    parser.add_argument("--install", action="store_true", help="Install compiled mod into game folder")
    parser.add_argument("--font", default=None, help="Path to custom TrueType font file")
    parser.add_argument("--encoding", default=None, help="Target encoding (default: cp874)")

    args = parser.parse_args()

    if args.stats:
        cmd_stats(args)
        return

    if args.install:
        if args.umd:
            cmd_build_umd(args)
        else:
            cmd_compile(args)
        cmd_build_fonts(args)
        cmd_install(args)
        return

    # Default build workflow:
    print("=" * 60)
    print("Chaos Theory Thai Mod: Starting Build Pipeline")
    print("=" * 60)

    # 1. Compile translations
    cmd_compile(args)

    # 2. Build fonts
    cmd_build_fonts(args)

    # 3. UMD repacking if requested
    if args.umd:
        cmd_build_umd(args)

    print("\n" + "=" * 60)
    print("Build Pipeline completed successfully!")
    print("=" * 60)


if __name__ == "__main__":
    main()

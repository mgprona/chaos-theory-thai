# Repository Guidelines

## Project Structure & Module Organization

This Python toolchain builds a Thai localization mod for Splinter Cell Chaos Theory (PC/Steam).

- `src/core/`: UMD/INI parsers, PCX handling, and offline Thai shaping.
- `src/pipeline/`: extraction, translation merging, compilation, and font generation.
- `src/cli.py` and `build.py`: command entry points.
- `data/translations/{story,ui,opsat}/`: editable translation JSON; `data/fonts/`: font assets.
- `data/raw_official/`: original templates; preserve these as build inputs.
- `dist/`: generated localization and fonts; `tests/`: regression tests; `tools/`: translation helpers and previews.
- `docs/THAI_FONT_MODDING.md` and `FONT_PIPELINE.md`: font architecture; `out/game-test/`: recorded game evidence.

## Build, Test, and Development Commands

Run commands from the repository root:

```powershell
python -m pip install -r requirements.txt
python build.py --stats
python build.py
python -m unittest discover -s tests -v
python tools/preview_magma.py
python src/cli.py install
```

These install dependencies, report translation progress, build localization/fonts/UMD, run tests, generate a font preview, and install existing outputs respectively. `python build.py --no-umd` skips archive repacking. Set `game_dir` in `config.json` for your installation; close the game before replacing its files. Full builds require original game inputs and a pristine UMD backup.

## Coding Style & Naming Conventions

Use four-space Python indentation, `snake_case` functions/modules, `PascalCase` classes, and `UPPER_CASE` constants. Follow existing type hints and use `pathlib.Path` for paths. No formatter or linter is configured.

Keep JSON UTF-8 and edit `th` values while preserving keys, `_source`, placeholders, escapes, and whitespace. Empty translations fall back to English. Preserve original asset filenames and archive paths.

## Testing Guidelines

Use standard-library `unittest`; name files `test_*.py` and methods `test_*`. Add regression checks for parser, encoding, lookup, metrics, or atlas changes. There is no percentage coverage target.

Rebuild localization and all six Magma font sizes together: PUA mappings must match. Verify round trips, glyph coverage, and original Latin pixels/metrics. For rendering changes, also capture in-game screenshots and document version, resolution, inspected screens, and untested areas; previews alone do not establish a pass.

## Commit & Pull Request Guidelines

Prefer the history's `feat(scope): ...`, `fix(scope): ...`, and `docs: ...` conventions. Keep commits focused. PR descriptions should explain behavior, affected translation/font paths, validation commands, and remaining limitations; link relevant issues and include screenshots for visual changes.

Include relevant generated assets when rebuilding. Keep backups, diagnostic archives, and large UMD builds excluded through `.gitignore`.

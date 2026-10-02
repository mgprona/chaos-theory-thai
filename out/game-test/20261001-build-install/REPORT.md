# UMD installation and game test — 2026-10-01

**บันทึกนี้เป็นผลทดสอบบิลด์ก่อนขยายกฎอัตโนมัติ:** ฉบับล่าสุดที่ติดตั้งครอบคลุมไฟล์ภารกิจทั้งหมดแล้ว ดู [ผลการขยายระบบและ hash ล่าสุด](AUTOMATIC_COVERAGE.md) ภาพในบันทึกนี้ยังเป็นหลักฐานของบิลด์ที่ระบุด้านล่าง

แพ็กและติดตั้งม็อดลง `C:\Program Files (x86)\Steam\steamapps\common\Splintercell Chaos Theory` แล้ว บิลด์และการตรวจไฟล์ผ่าน เปิดเกมและเข้าเล่นภารกิจประภาคารได้ ภาษาไทยที่เคยเพี้ยนในสรุปภารกิจ ชื่ออุปกรณ์ และปุ่มยืนยันแสดงถูกต้องหลังแก้ encoding พบชื่อ SC-20K ยาวเกินช่อง HUD ซึ่งยังต้องปรับความยาวข้อความต่อ

## Environment and installed build

- Game UI version: **1.05**; Steam app **13570**, installed build ID **252084**.
- Test display: **1600×900 windowed**, existing WidescreenFix configuration; language `int` and `UseDynamicDataFile=true`.
- Toolchain: repository `.venv`, Python **3.11.15**. Global Python 3.14 lacks the project's dependencies; use the commands below.
- Translation coverage reported by the build: **3,812 / 8,537 (44.65%)**. Empty translations retain English fallback.
- Installed payloads: **71 files** = UMD + 52 localization files + 5 PCX fonts + 13 Magma assets (six font sizes and one atlas alias).
- Final UMD: **617,897,143 bytes**, SHA-256 `7750e78aadd9ecc7c41013062e151d2f0ddae24b67d4986e6c124afd542c968b`.

## Repairs included

Magma screens interpreted the previously compiled CP874 bytes as Latin glyphs. Added `System`, `Equipments`, `Training`, and the translated Training/Lighthouse/Panama/CargoShip files plus their `P_` files to the existing UTF-16/PUA pipeline. Source translation JSON and `data/raw_official` were preserved.

The expanded catalog contains **529 PUA clusters**. Prototype 36 originally overflowed the atlas with this catalog. The font builder now packs tall glyphs first into the free areas beside and below the original bitmap, keeping the 1024×1024 atlas. All six Magma fonts and localization were rebuilt together. Tests verify original Latin pixels and metrics, PUA lookup coverage, shaped glyph bitmaps, and text round trips.

The translation validator now reads the configured encoding and decodes PUA before comparing compiled values with the four translated story sources.

## Validation

Run from the repository root after closing the game:

```powershell
$env:PYTHONIOENCODING = 'utf-8'
.\.venv\Scripts\python.exe build.py --umd --install
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
.\.venv\Scripts\python.exe tools/validate_translations.py
.\.venv\Scripts\python.exe out/game-test/20261001-build-install/verify_integrity.py
git diff --check
```

| Check | Result |
| --- | --- |
| Full build and installation | Passed |
| Regression suite | 28 tests passed |
| Four translated story sources and compiled values | Passed |
| UMD entries and metadata/order | 20,252 entries verified |
| Replacement payloads against generated files | 65 verified |
| Other UMD payloads against preserved original archive | 20,187 byte-identical |
| Installed files against generated files | 71 SHA-256 matches |
| Original backup UMD and game executable | Original hashes retained |
| Source translation/raw input diff | No changes |
| Whitespace check | Passed |

The reproducible archive/install checks and per-file hashes are in [verify_integrity.py](verify_integrity.py) and [integrity.json](integrity.json). Local `build.log`, `tests.log`, and `translations.log` are diagnostic outputs excluded from Git.

## Direct game observations

Screenshots **15–20** were captured with the final installed build identified above. Screenshots **01–14** document the initial and intermediate builds, including the original defects; older filenames containing `final` in this range do not identify the final UMD hash.

| Final-build screen | Observation | Evidence |
| --- | --- | --- |
| Lighthouse loading | Thai mission text/tip readable | [15](15-final-loading.png) |
| Lighthouse briefing | Thai speaker names and briefing readable; text scrolls | [16](16-final-briefing.png) |
| Recommended equipment | Thai equipment names readable, including SC-20K attachments | [17](17-final-equipment.png) |
| Lighthouse gameplay start | Mission loaded, HUD renders Thai; long SC-20K label clips at the right edge | [18](18-final-gameplay-hud.png) |
| OPSAT objectives | Primary objectives readable in Thai | [19](19-final-opsat-objectives.png) |
| Exit confirmation | Thai question and Yes/No buttons readable | [20](20-final-yes-no-dialog.png) |

Earlier observations also covered the mode menu, main menu, display settings, pause menu, and Grim's briefing. Defect evidence: [original confirmation buttons](04-settings-dialog-mojibake.png), [original briefing](05-briefing-mojibake.png), [equipment before encoding repair](11-equipment-mojibake.png), and [HUD before encoding repair](12-gameplay-equipment-mojibake.png).

The game was left open on the Lighthouse OPSAT objectives screen after testing. No manual save was created and no existing save was overwritten.

## Remaining limits

- **Known layout issue:** the SC-20K HUD name is longer than the available single-line area. Encoding is corrected, but the full label is not visible. Source translations were retained for a separate wording/layout pass.
- Training, Panama, and CargoShip have automated encoding/round-trip coverage, but were not visually inspected in this run.
- Dialogue subtitles, all OPSAT information/equipment details, contextual interactions, complete mission playthroughs, co-op/network screens, save/load behavior, and other resolutions remain unverified.
- A successful archive check and startup do not establish whole-game rendering or complete translation coverage.

## Preserved originals

The pristine UMD is retained at `backups/dynamic-pc.umd`, SHA-256 `f42c884dcef45fea70489c213e31fd1176c3d84ce27265da6cd718a8414005af`. The original five PCX fonts are retained in `backups/Fonts/` and the additional pre-install snapshot `backups/preinstall-20261001/`. The latter also records existing game/settings/WidescreenFix INI files and a manifest.

Original executable SHA-256: `54df25b238356024248085ca7fa6af9005b0be4ec40beef3c32faa8c06b6d4e5`; installation did not replace it. [preinstall.json](preinstall.json) records the original UMD, executable, and loose font hashes.

Repeated installs may populate `backups/loose/` with already installed mod files; that directory should not be treated as a pristine loose localization snapshot. Reverting the mod requires restoring the preserved UMD/PCX files and removing the added loose localization and Magma overrides. No automatic uninstall was performed or verified in this run.

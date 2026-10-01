# In-game Thai font verification — 2026-10-01

Result: **PASS for the inspected main menu and settings screens**.

Tested the installed Steam PC game, version 1.05, fullscreen 1920×1080,
with the final generated UMD and matching loose localization/font assets.
These PNG files were captured directly from the running game, not from the
offline preview renderer.

| Screen | Observation | Evidence |
|---|---|---|
| Game mode selection | Thai title and all five mode/action labels visible | [04](04-thai-mode-menu.png) |
| Single-player main menu | Thai title, profile label and menu actions visible | [05](05-thai-main-menu.png) |
| Display settings | Thai tab labels, brightness, contrast, resolution and buttons visible; numeric values intact | [06](06-thai-display-settings.png) |
| Control settings | Thai movement labels, arrow names, mouse labels and off value visible; Latin key names intact | [07](07-thai-control-settings.png) |
| Sound settings | Thai sound labels and no values visible; numbers and logos intact | [08](08-thai-sound-settings.png) |
| Exit confirmation | Thai heading and complete question visible with punctuation | [09](09-thai-exit-dialog.png) |

The inspected Thai text has no missing-glyph squares, garbled Latin aliases,
blank translated labels, detached combining marks or visible label clipping.
Examples include stacked marks in ตั้งค่า, lower vowels in ปัจจุบัน and
multi-mark labels such as ผู้สร้าง. Disabled labels retain the game's dim style.
Keyboard navigation and opening all three settings tabs worked. No settings
were saved or changed. The game was left open on sound settings.

## Root cause and repair

The first build changed only Bios 20 and Prototype 13. At the tested resolution,
Thai/PUA labels were blank despite UTF-16 ASCII displaying correctly. A Latin
slot diagnostic also retained its original glyph, showing that those modified
font sizes were not the ones rendering the screen. See [01](01-blank-menu.png),
[02](02-unicode-diagnostic.png) and [03](03-unpatched-scale-alias.png).

Adding the same HarfBuzz-shaped PUA catalog to Bios 32/48 and Prototype 26/36,
and expanding the last atlas of all six fonts to 1024×1024, made the final
translated UI visible. Diagnostic text and Latin-slot edits are absent from
the final installed build. The game executable was not modified.

## Automated verification

`python -m unittest discover -s tests -v`: **22 tests passed** after the six-font
build. Tests cover source/PUA round trips, lookup coverage, preserved original
Latin metrics/pixels, rendered PUA images matching HarfBuzz positions, GSUB/GPOS
cases and deterministic mappings across all six font variants.

## Limits and remaining translation work

- YES/NO in the exit confirmation remain English; the Thai question renders correctly.
- DEFAULT is the existing profile name. Key names such as Shift, W and KP 8 remain Latin.
- Advanced display options, scrolled control rows, other resolutions, gameplay
  HUD, OPSAT, subtitles and story text were not visually verified in this run.
- This pass verifies the existing translated menu/settings labels. It does not
  claim that every game string has been translated or every Thai word is tested.
- Rebuild fonts and localization together whenever translations change so the
  deterministic PUA catalog stays synchronized.

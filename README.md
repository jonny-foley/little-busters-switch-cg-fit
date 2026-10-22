# Little Busters! Converted Edition (Switch) – event CGs in full 4:3

An [Atmosphere](https://github.com/Atmosphere-NX/Atmosphere) exefs patch for **Little Busters! Converted Edition on Nintendo Switch** (title ID `0100943010310000`, version **1.0.0**).

The Switch release crops its 4:3 event CGs to fill a 16:9 screen, and the full image only shows if you scroll it with the stick. This patch shows them whole instead, in their original 4:3 framing with black bars at the sides:

- in the story, as soon as a CG appears, and after every expression change
- in the stick-scroll view
- in the CG gallery

Backgrounds, sprites, the UI and the few event CGs that aren't 4:3 (tall or panoramic ones) are left as they are.

> This is an unofficial fan patch. It is not affiliated with Key, Visual Arts, Prototype or NIS America. No game data is included: the patch only changes the game's code in memory, and you need your own copy of the game.

## Requirements

- A Switch running custom firmware with **Atmosphere**
- Little Busters! Converted Edition at **version 1.0.0** (no update). To check, highlight the game on the HOME menu, press **+**, and look at the version. Atmosphere ignores the patch on any other version.

## Install

1. Download the `lb-cg-fit-*.zip` file from the [latest release](https://github.com/jonny-foley/little-busters-switch-cg-fit/releases/latest).
2. Extract it to the root of your SD card, merging its `atmosphere` folder with the one already there. You should end up with:
   ```
   sd:/atmosphere/exefs_patches/lb_cg_fit/DF3FAB24E1D0C6E8F5EBB006009A2B1CCAAEFF0D.ips
   ```
3. Boot into Atmosphere and start the game.

To uninstall, delete `sd:/atmosphere/exefs_patches/lb_cg_fit/`. Atmosphere applies the patch in memory each time the game starts, so no game files are modified.

### Yuzu and other emulators

Put the same `.ips` file at `load/0100943010310000/lb_cg_fit/exefs/DF3FAB24E1D0C6E8F5EBB006009A2B1CCAAEFF0D.ips` in the emulator's user folder. In Yuzu, right-click the game and choose **Open Mod Data Location**.

## What changes

| Where | Unpatched | Patched |
|---|---|---|
| Story, when a 4:3 event CG appears | Cropped to 16:9 | Whole 4:3 image with side bars, from the first frame |
| Story, expression changes on a CG | Cropped | Stay whole and aligned |
| Story, tilting the stick on a CG | Scrolls the cropped view | Opens on the full view, and stays that way when you leave the scroll view |
| CG gallery | Cropped, scroll with the stick | Opens on the whole image; zooming in still works |
| Backgrounds, sprites, UI, non-4:3 CGs | — | Unchanged |

## How it works

The game runs on Prototype's LUCA System engine, like the Switch release of CLANNAD. It renders at 1280×720 and its event CGs are 1280×960. CGs are handed to the engine's CG scroller (`cEvScroll`), which already has a zoom-out mode: a zoom value `z` from −1 to 0, where `z = −1` draws the whole image scaled to fit the screen height. On Switch only the gallery can reach it, and nothing starts zoomed out.

The patch adds a small routine in the unused padding after the game's code (`main+0x38d2c0`). It "fits" a CG by clearing its crop and the port's default crop offset, and giving it a scale of `screenH / imageH` (0.75) around the top-centre of the screen. The routine is called from a few places in the engine:

| Site (`main+`) | Change |
|---|---|
| `0x38d2c0` | New code. `is_fit_cg` decides whether an image is a 4:3 event CG; `fit_image` fits it, using the engine's own transform setter. |
| `0x38d800` | A bitmap of the 319 `EVENTCG.PAK` IDs drawn on a 1280×960 canvas: the 174 full-size CGs and the 145 expression parts. The engine draws a CG and its current expression part as one image, which carries the part's ID. |
| `0x264168` | When the story shows a CG (including each expression change, which reloads it), it's fitted straight away. |
| `0x18ebe8` | The CG scroller starts fitted CGs fully zoomed out (`z = −1`), for both the stick-scroll view and the gallery. |
| `0x192914`, `0x191cb8` | When the stick-scroll view closes, the CG is fitted again. |
| `0x191984`, `0x1919c0`, `0x1919d8` | The scroll view's "zoom back in" animation is skipped in the story. |

Loading a new image into the same slot resets its transform, so a fitted CG can't leave a shrunken background behind. Unlike the CLANNAD port, Little Busters! adds no camera pans over its CGs, so nothing has to be cancelled.

## Building the patch yourself

`make_patch.py` rebuilds the `.ips` file from your own dump of the game's 1.0.0 exefs `main`. Before writing anything it checks the original bytes at every patch site, and it refuses any other build.

```bash
python -m pip install lz4
```
```bash
python make_patch.py "path/to/exefs/main" .
```

It also writes an IPSwitch-style `.pchtxt` file listing the same patches.

## Status

Tested on a Switch OLED with Atmosphere and in Yuzu (with a debugger attached): story CGs on load, expression changes, the stick-scroll view (open, scroll, close) and the CG gallery. If you find a CG that's mis-framed or mis-aligned, please open an issue and include the scene or CG.

## License

[MIT](LICENSE)

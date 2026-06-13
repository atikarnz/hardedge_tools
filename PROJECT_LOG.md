# HardEdge Tools Project Log

## 2026-05-12

Current version: `2.1.3`

## Completed

- Fixed seam conversion so existing UV seams are preserved by default.
- Added `Preserve Existing Seams` checkbox to the Sharp Marks panel.
- Added hard-edge preview support.
- Changed the main Preview button into a one-click toggle:
  - Off state: `Preview`
  - On state: `Hide Preview`
- Removed extra preview buttons from the Select section.
- Removed icons from the Select section buttons.
- Disabled the unsafe in-addon reload behavior that could crash Blender.
- Removed the visible `Reload Addon` button from the main panel.
- Added `README.md`.
- Created installable release zips in `dist/`.

Latest release zip:

```text
E:\TestClaude\hardedge_tools\dist\hardedge_tools-2.1.3_20260512033110.zip
```

## Install Reminder

Before installing a new zip, delete the old installed addon folder:

```text
C:\Users\atika\AppData\Roaming\Blender Foundation\Blender\5.1\scripts\addons\hardedge_tools
```

Then install the newest zip from `dist/`.

Do not use the old Reload Addon button. After replacing files, use Blender's `F3 > Reload Scripts` command or restart Blender.

## Recommended Roadmap

### Version 2.2.0

- Add `Cleanup Prep` button:
  - Select hard edges.
  - Mark selected hard edges as Sharp.
  - Convert hard/sharp edges to UV seams.
  - Respect `Preserve Existing Seams`.
- Add compact live stats near the angle slider:
  - Example: `Hard: 124 / 930 | Avg 47.2 deg`
  - Goal: make angle tuning easier without manually pressing Refresh Stats.

### Version 2.3.0

- Improve overlay controls with overlay modes:
  - `Hard`
  - `Boundary`
  - `Sharp`
  - `Seams`
- Make Preview use the chosen overlay mode.
- Goal: make the overlay useful as a mesh diagnosis tool, not only a hard-edge preview.

### Version 2.4.0

- Add workflow/export presets:
  - `Unity`
  - `Unreal`
  - `SubD Cleanup`
  - `UV Prep`
  - `Hard Surface`
- Presets may adjust:
  - angle threshold
  - boundary behavior
  - seam preserve behavior
  - overlay style
  - bevel weight

### Version 2.5.0

- Add `Select Problem Edges`.
- Detect likely cleanup issues:
  - non-manifold edges
  - zero-length or very tiny edges
  - boundary edges
  - extreme-angle edges
  - possible degenerate faces

## Next Suggested Step

Start with `2.2.0`: add `Cleanup Prep` and compact live stats.

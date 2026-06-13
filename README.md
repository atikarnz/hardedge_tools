# HardEdge Tools

HardEdge Tools is a Blender 5.0+ mesh addon for selecting, marking, previewing, and converting hard edges in edit mode.

## Features

- Select hard edges by face angle.
- Preview matching hard edges without changing selection.
- Include boundary edges and existing sharp marks when selecting.
- Select soft edges, sharp-marked edges, and hard-edge loops.
- Mark hard edges as Sharp or clear Sharp marks.
- Convert hard edges or Sharp marks to UV seams.
- Preserve existing UV seams by default.
- Assign bevel weights to hard edges or selected edges.
- Show a viewport hard-edge highlight overlay.
- Show simple edge and face measurements in edit mode.
- Run game-ready prep and batch sharp marking tools.

## Install

1. Zip the `hardedge_tools` folder.
2. In Blender, open `Edit > Preferences > Add-ons`.
3. Click `Install`, choose the zip file, and enable `HardEdge Tools`.
4. Open a mesh in edit mode and use `View3D > Sidebar > Hard Edges`.

For development, copy or symlink this folder to:

```text
%APPDATA%\Blender Foundation\Blender\5.x\scripts\addons\
```

## Basic Workflow

1. Select a mesh and enter edit mode.
2. Set the angle threshold in the Hard Edges panel.
3. Click `Preview` to inspect matching hard edges without changing the mesh. Click it again to hide the preview.
4. Click `Select` to select matching hard edges.
5. Click `Mark` to mark matching edges as Sharp.
6. Keep `Preserve Existing Seams` enabled if you want seam conversion tools to add seams without clearing the current UV seam layout.
7. Use `Hard Edges -> UV Seams` or `Sharp Marks -> UV Seams` when preparing UV cuts.

## Notes

- Boundary edges count as hard edges when `Include Boundary` is enabled.
- `Preserve Existing Seams` is enabled by default.
- Disable `Preserve Existing Seams` only when you want seam conversion to replace the current seam set.
- After replacing addon files, use Blender's `F3 > Reload Scripts` command or restart Blender.

## Version

Current version: `2.1.3`

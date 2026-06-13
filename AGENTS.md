# HardEdge Tools — Blender Addon

**Author:** atikarnz  
**Blender:** 5.0+  
**Category:** Mesh

## Project Structure

```
hardedge_tools/
├── __init__.py      # bl_info, register/unregister, imports
├── constants.py     # PRESET_DATA (angle presets)
├── utils.py         # Core math helpers (edge angle detection, filtering)
├── overlays.py      # Viewport draw handlers (GPU overlay, measurements)
├── properties.py    # HardEdgeProperties, HardEdgeStats PropertyGroups
├── operators.py     # All MESH_OT_* operator classes
└── panels.py        # All VIEW3D_PT_* panels + edge context menu (Ctrl+E)
```

Original single-file version lives at:  
`C:\Users\atika\Downloads\select_hard_edges_v2.py`

## Key Concepts

- **Hard edge** = edge whose adjacent face normals exceed `angle_threshold` (radians; shown as degrees via the `ANGLE` prop subtype)
- **Boundary edge** = edge with only one linked face (treated as hard when `include_boundary=True`)
- All scene-level settings are stored in `context.scene.hard_edge_props` (`HardEdgeProperties`)
- Stats are stored in `context.scene.hard_edge_stats` (`HardEdgeStats`)

## Operator Conventions

- All edit-mesh operators use `_poll_edit_mesh(context)` from `utils.py`
- Operators read defaults from `context.scene.hard_edge_props` in `invoke()`, then apply in `execute()`
- All operators have `{'REGISTER', 'UNDO'}` in `bl_options`

## Adding a New Operator

1. Define the class in `operators.py`, import `_poll_edit_mesh` and helpers from `utils.py`
2. Add it to the `classes` tuple in `__init__.py`
3. Add a button for it in the appropriate panel in `panels.py`
4. If it should appear in the Ctrl+E edge menu, add it to `edge_menu_draw()` in `panels.py`

## Adding a New Panel

1. Define the class in `panels.py`
2. Add it to the `classes` tuple in `__init__.py` — **parent panels must come before child panels**

## Installing in Blender

- **Dev workflow:** Symlink or copy the `hardedge_tools/` folder to:  
  `%APPDATA%\Blender Foundation\Blender\5.x\scripts\addons\`
- **Distribution:** Zip the `hardedge_tools/` folder and install via  
  Preferences > Add-ons > Install
- Use the **Reload Addon** button in the panel to reload without reinstalling

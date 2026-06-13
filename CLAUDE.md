# HardEdge Tools — Blender Addon

**Author:** atikarnz  
**Blender:** 5.0+  
**Category:** Mesh  
**Version:** 2.2.0

## Project Structure

```
hardedge_tools/
├── __init__.py      # bl_info, register/unregister, imports
├── constants.py     # PRESET_DATA (angle presets), NO_MAX_LENGTH sentinel
├── utils.py         # Core math helpers (edge angle detection, filtering, op helpers)
├── overlays.py      # Viewport draw handlers (GPU overlay, measurements)
├── properties.py    # HardEdgeProperties, HardEdgeStats PropertyGroups
├── operators.py     # All MESH_OT_* operator classes
├── panels.py        # All VIEW3D_PT_* panels + edge context menu (Ctrl+E)
└── tests/           # pytest suite (run under Blender's Python — see tests/README.md)
```

Original single-file version lives at:  
`C:\Users\atika\Downloads\select_hard_edges_v2.py`

## Key Concepts

- **Hard edge** = edge whose adjacent face normals exceed `angle_threshold` (radians; shown as degrees via the `ANGLE` prop subtype)
- **Boundary edge** = edge with only one linked face (treated as hard when `include_boundary=True`); carries the sentinel angle `math.pi` in the returned tuple
- All scene-level settings are stored in `context.scene.hard_edge_props` (`HardEdgeProperties`)
- Stats are stored in `context.scene.hard_edge_stats` (`HardEdgeStats`)
- `constants.NO_MAX_LENGTH` (`float('inf')`) is the canonical "no upper bound" length filter

## Operator Conventions

- All edit-mesh operators use `poll_edit_mesh(context)` from `utils.py`
- Operators read defaults from `context.scene.hard_edge_props` in `invoke()`, then apply in `execute()`
- All operators have `{'REGISTER', 'UNDO'}` in `bl_options`
- Operators that switch modes must capture `context.mode` up front and restore in a `finally:` block

## Shared Helpers (in `utils.py`)

The unprefixed names are the canonical public API; the leading-underscore
aliases (`_poll_edit_mesh`, etc.) are kept for backwards compatibility with any
external scripts and may be removed in a future release.

- `poll_edit_mesh(context)` — poll helper
- `edit_bmesh(obj)` — bmesh with edge lookup table ready
- `get_hard_edges(bm, angle, ...)` — core matcher; returns `[(edge, angle_rad), ...]`
- `props_to_hard_edges(bm, p)` — convenience wrapper using scene props
- `get_bevel_layer(bm)` — get-or-create the `bevel_weight_edge` float layer
- `fill_select_op_props(op, p)` — copy scene props onto a Select operator (shared by invoke + panel)
- `expand_edge_loops(bm)` — bmesh-native loop expansion
- `edge_face_angle(edge)` — clamp-safe angle in radians
- `angle_to_color(angle, alpha)` — green→red gradient

## Adding a New Operator

1. Define the class in `operators.py`, import `poll_edit_mesh` and helpers from `utils.py`
2. Add it to the `classes` tuple in `__init__.py`
3. Add a button for it in the appropriate panel in `panels.py`
4. If it should appear in the Ctrl+E edge menu, add it to `edge_menu_draw()` in `panels.py`
5. Add a focused unit test in `tests/` if the operator has non-trivial pure logic

## Adding a New Panel

1. Define the class in `panels.py`
2. Add it to the `classes` tuple in `__init__.py` — **parent panels must come before child panels**

## Installing in Blender

- **Dev workflow:** Symlink or copy the `hardedge_tools/` folder to:  
  `%APPDATA%\Blender Foundation\Blender\5.x\scripts\addons\`
- **Distribution:** Zip the `hardedge_tools/` folder and install via  
  Preferences > Add-ons > Install
- Use the **Reload Addon** button in the Pipeline panel; it calls
  `bpy.ops.script.reload()` which is the closest thing to a safe in-place
  reload. If the panel still looks stale afterwards, restart Blender.

## Testing

See `tests/README.md`. The suite has to run under Blender's bundled Python
(not a system Python) because it depends on `bmesh`.

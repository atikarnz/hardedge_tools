# Changelog

## 2.2.2 — 2026-06-17

Performance + correctness pass driven by the latest code/UI review.

### Fixed
- **Viewport lag from the 1dp measurement overlay.** The measurement draw
  handler scanned the whole mesh every frame. It now early-outs using
  Blender's `total_edge_sel` / `total_face_sel` counters, and caps work via a
  new **Label Limit** (default 500): past the limit the per-element labels are
  hidden and a single viewport warning is drawn instead, keeping dense meshes
  responsive.
- **Select Soft Edges** now honours **Extend Selection** and excludes boundary
  edges (a single-face edge could previously count as both not-hard and soft).
- **Hard-edge loop expansion** now stops at non-manifold edges, matching its
  documented behaviour.
- Unified the two overlay-cache invalidators and completed the backwards-compat
  helper aliases in `utils`.

### Added
- **Label Limit** control and an in-panel warning in *Geometry & Measurements*
  noting that measurement labels redraw every frame.

### Changed
- Angle preset buttons show full names in a 2-wide grid instead of truncating
  (e.g. "Hard Surface" was shown as "Hard").
- The empty "Edit Mode Overlays" parent panel now shows an orientation hint.
- Panel "to UV Seams" buttons use ASCII `->` to avoid font-fallback glyph issues.

## 2.2.1 — 2026-05-12

### Fixed
- **"Mark as Sharp" now respects the current selection.** Previously the
  operator always re-marked edges by angle threshold and ignored any
  selected edges, which made the button look broken when users selected
  specific edges and clicked Mark. Now: if edges are selected when the
  button is clicked, those exact edges are marked Sharp (additive — other
  sharp marks are preserved). If nothing is selected, falls back to the
  previous angle-based behavior. A `Use Selection` toggle in the redo
  panel lets you flip between the two modes after the fact.

## 2.2.0 — 2026-05-12

Cleanup release driven by the code review report.

### Fixed
- **`MESH_OT_reload_addon`** is no longer a no-op. It now calls
  `bpy.ops.script.reload()` (the same thing F3 → Reload Scripts does) and
  reports a real error on failure.
- **`MESH_OT_game_ready_prep`** now saves and restores the user's original
  mode in a `try`/`finally`, so invoking it from edit mode no longer dumps
  the user into object mode. The `poll` returns a real `bool` now too.
- **`MESH_OT_apply_preset`** reports a warning and returns `{'CANCELLED'}`
  on unknown preset names instead of silently returning `{'FINISHED'}`.
- **`MESH_OT_select_soft_edges`** short-circuits `edge.calc_length()` when
  the length filter is off, matching the pattern in `get_hard_edges`.
- **`MESH_OT_batch_process`** verifies the active object is a mesh before
  trying to restore EDIT mode.

### Changed
- Replaced the magic `1e9` "no max length" sentinel everywhere with
  `NO_MAX_LENGTH = float('inf')` from `constants.py`.
- Renamed the cross-module helpers in `utils.py` to drop their leading
  underscore: `poll_edit_mesh`, `edit_bmesh`, `props_to_hard_edges`,
  `get_bevel_layer`. The old underscore-prefixed names remain as aliases.
- Added `fill_select_op_props` helper in `utils.py`; the panel and the
  `MESH_OT_select_hard_edges.invoke` now use the same code path.
- `_draw_hard_edges` / `_draw_custom_measurements` import `gpu` and `blf`
  at module load instead of on every redraw.
- Statistics now expose a `boundary_count` field, and the panel notes that
  avg/max angle figures are interior-only.

### Added
- `tests/` directory with a `pytest` suite covering `edge_face_angle`,
  `get_hard_edges` (including the length and boundary filters), the
  `NO_MAX_LENGTH` sentinel, and the `angle_to_color` gradient.
- Type hints on the public helpers in `utils.py`.
- Property descriptions / tooltips on every prop that was missing one.
- `CHANGELOG.md` (this file).

### Internal
- `__init__.py` version bumped from `(2, 1, 3)` to `(2, 2, 0)`.
- `CLAUDE.md` updated to reflect new structure and helper names.

## 2.1.3 — Prior release

Initial multi-module refactor from `select_hard_edges_v2.py`.

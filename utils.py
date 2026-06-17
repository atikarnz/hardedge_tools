"""Math + bmesh helpers shared by operators, panels, and the GPU overlay.

Public helpers (no leading underscore) are intentionally importable across the
package — the previous underscore-prefixed names were misleading.
"""
import math
from typing import List, Optional, Tuple

import bmesh

from .constants import NO_MAX_LENGTH


# ──────────────────────────────────────────────────────────────────
#  Context / bmesh access
# ──────────────────────────────────────────────────────────────────

def poll_edit_mesh(context) -> bool:
    """True iff the active object is a mesh and we're in edit mode."""
    obj = context.active_object
    return obj is not None and obj.type == 'MESH' and context.mode == 'EDIT_MESH'


def edit_bmesh(obj):
    """Get the edit-mode bmesh for *obj* with an up-to-date edge lookup table."""
    bm = bmesh.from_edit_mesh(obj.data)
    bm.edges.ensure_lookup_table()
    return bm


# ──────────────────────────────────────────────────────────────────
#  Edge math
# ──────────────────────────────────────────────────────────────────

def edge_face_angle(edge) -> Optional[float]:
    """Angle (radians) between the two faces sharing *edge*, or None."""
    linked = edge.link_faces
    if len(linked) == 2:
        n1, n2 = linked[0].normal, linked[1].normal
        # A degenerate (zero-area) face has a zero-length normal; we can't form
        # a meaningful angle from it, so report None (treated as not-hard).
        if n1.length > 0 and n2.length > 0:
            dot = max(-1.0, min(1.0, n1.dot(n2)))
            return math.acos(dot)
    return None


def angle_to_color(angle_rad: float, alpha: float = 1.0) -> Tuple[float, float, float, float]:
    """Map an angle (0..pi) to a green→red gradient color."""
    t = min(1.0, angle_rad / math.pi)
    return (t, 1.0 - t, 0.0, alpha)


# ──────────────────────────────────────────────────────────────────
#  Hard edge detection
# ──────────────────────────────────────────────────────────────────

def get_hard_edges(
    bm,
    angle_threshold_rad: float,
    include_boundary: bool = True,
    use_existing_sharp: bool = False,
    min_length: float = 0.0,
    max_length: float = NO_MAX_LENGTH,
    uv_seams_only: bool = False,
) -> List[Tuple[object, float]]:
    """Return list of (edge, angle_radians) tuples passing all active filters.

    Boundary edges (single-linked-face) carry the sentinel angle *math.pi*.
    """
    result: List[Tuple[object, float]] = []
    angle_rad = angle_threshold_rad
    length_filter_active = min_length > 0.0 or max_length < NO_MAX_LENGTH
    for edge in bm.edges:
        if length_filter_active:
            length = edge.calc_length()
            if length < min_length or length > max_length:
                continue
        if uv_seams_only and not edge.seam:
            continue
        if use_existing_sharp and not edge.smooth:
            a = edge_face_angle(edge)
            if a is None:
                a = math.pi if len(edge.link_faces) == 1 else angle_rad
            result.append((edge, a))
            continue
        a = edge_face_angle(edge)
        if a is not None:
            if a > angle_rad:
                result.append((edge, a))
        elif include_boundary and len(edge.link_faces) == 1:
            result.append((edge, math.pi))
    return result


def props_to_hard_edges(bm, p) -> List[Tuple[object, float]]:
    """Convenience: call :func:`get_hard_edges` using scene-level props."""
    return get_hard_edges(
        bm,
        p.angle_threshold,
        p.include_boundary,
        p.include_sharp_mark,
        p.min_edge_length if p.use_length_filter else 0.0,
        p.max_edge_length if p.use_length_filter else NO_MAX_LENGTH,
        p.uv_seams_only,
    )


# ──────────────────────────────────────────────────────────────────
#  Bevel weight layer
# ──────────────────────────────────────────────────────────────────

def get_bevel_layer(bm):
    """Return the 'bevel_weight_edge' float layer, creating it if absent."""
    fl = bm.edges.layers.float
    return fl.get("bevel_weight_edge") or fl.new("bevel_weight_edge")


# ──────────────────────────────────────────────────────────────────
#  Operator helpers
# ──────────────────────────────────────────────────────────────────

def fill_select_op_props(op, p) -> None:
    """Copy scene-level hard-edge props onto a Select operator instance.

    Shared by :class:`operators.MESH_OT_select_hard_edges.invoke` and the
    panel button setup so the two paths can't drift apart.
    """
    op.angle_threshold    = p.angle_threshold
    op.select_boundary    = p.include_boundary
    op.extend             = p.extend_selection
    op.use_existing_sharp = p.include_sharp_mark
    op.min_length         = p.min_edge_length if p.use_length_filter else 0.0
    op.max_length         = p.max_edge_length if p.use_length_filter else NO_MAX_LENGTH
    op.uv_seams_only      = p.uv_seams_only


# ──────────────────────────────────────────────────────────────────
#  Edge-loop expansion
# ──────────────────────────────────────────────────────────────────

def expand_edge_loops(bm) -> None:
    """Extend the current edge selection to full edge loops.

    Mirrors ``bpy.ops.mesh.loop_multi_select(ring=False)``, but implemented
    directly on bmesh so it doesn't depend on operator availability.
    Walks through quad faces; stops at non-quad, boundary, or non-manifold.
    """
    seeds   = [e for e in bm.edges if e.select]
    visited = set(seeds)

    def _cross(edge, from_loop):
        for l in edge.link_loops:
            if l.face is not from_loop.face:
                return l
        return None

    def _walk(start_loop):
        loop = start_loop
        while True:
            if len(loop.face.verts) != 4:
                return
            nxt_loop = loop.link_loop_next.link_loop_next
            nxt_edge = nxt_loop.edge
            # Stop at non-manifold edges (boundary = 1 face, or 3+ faces) — a
            # loop is only well-defined across exactly two quad faces. Without
            # this guard _cross() would pick an arbitrary neighbouring face.
            if len(nxt_edge.link_faces) != 2:
                return
            if nxt_edge in visited:
                return
            visited.add(nxt_edge)
            nxt_edge.select = True
            crossed = _cross(nxt_edge, nxt_loop)
            if crossed is None:
                return
            loop = crossed

    for edge in seeds:
        for lp in list(edge.link_loops):
            _walk(lp)


# ──────────────────────────────────────────────────────────────────
#  Backwards-compatible aliases
# ──────────────────────────────────────────────────────────────────
# Keep the old underscore-prefixed names importable so any external scripts
# that referenced them won't break. New code should prefer the unprefixed
# versions above.

_poll_edit_mesh      = poll_edit_mesh
_edit_bmesh          = edit_bmesh
_get_hard_edges      = get_hard_edges
_props_to_hard_edges = props_to_hard_edges
_get_bevel_layer     = get_bevel_layer
_edge_face_angle     = edge_face_angle
_angle_to_color      = angle_to_color
_fill_select_op_props = fill_select_op_props
_expand_edge_loops   = expand_edge_loops

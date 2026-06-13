import math
import bpy
import bmesh

from .utils import edit_bmesh, props_to_hard_edges, angle_to_color, edge_face_angle


# Module-load-time GPU imports; failures here just mean the overlay is a no-op.
try:
    import gpu
    from gpu_extras.batch import batch_for_shader
    _GPU_OK = True
except ImportError:
    gpu = None
    batch_for_shader = None
    _GPU_OK = False

try:
    import blf
    from bpy_extras.view3d_utils import location_3d_to_region_2d
    _BLF_OK = True
except ImportError:
    blf = None
    location_3d_to_region_2d = None
    _BLF_OK = False


_draw_handle         = None
_draw_handle_measure = None

# Cached GPU batch for the hard-edge overlay. Rebuilt only when the active
# object's mesh geometry changes (caught by the depsgraph handler) or when
# a prop that feeds into the computed edge set changes (caught by the
# signature check in _draw_hard_edges). Coords are stored in local space
# so moving/rotating the object does not invalidate the cache.
_overlay_cache = {
    "batch":     None,
    "shader":    None,
    "obj_ptr":   None,
    "props_sig": None,
    "valid":     False,
}


def _invalidate_overlay_cache():
    _overlay_cache["batch"]     = None
    _overlay_cache["shader"]    = None
    _overlay_cache["obj_ptr"]   = None
    _overlay_cache["props_sig"] = None
    _overlay_cache["valid"]     = False


def mark_overlay_dirty(*_args, **_kwargs):
    """Public invalidator used by PropertyGroup update callbacks."""
    _overlay_cache["batch"] = None
    _overlay_cache["valid"] = False


def _props_signature(p):
    return (
        p.angle_threshold, p.include_boundary, p.include_sharp_mark,
        p.use_length_filter, p.min_edge_length, p.max_edge_length,
        p.uv_seams_only, p.overlay_gradient, p.overlay_alpha,
        tuple(p.overlay_color),
    )


def _on_depsgraph_update(_scene, depsgraph):
    obj = bpy.context.active_object
    if obj is None:
        return
    obj_data = obj.data
    for update in depsgraph.updates:
        updated_id = update.id.original
        if (updated_id == obj or updated_id == obj_data) and update.is_updated_geometry:
            _overlay_cache["batch"] = None
            _overlay_cache["valid"] = False
            return


def _rebuild_overlay_cache(obj, props):
    bm   = edit_bmesh(obj)
    hard = props_to_hard_edges(bm, props)
    if not hard:
        _overlay_cache["batch"]  = None
        _overlay_cache["shader"] = None
        _overlay_cache["valid"]  = True
        return
    flat_color     = (*props.overlay_color, props.overlay_alpha)
    coords, colors = [], []
    for edge, angle in hard:
        coords.extend([edge.verts[0].co.copy(), edge.verts[1].co.copy()])
        c = angle_to_color(angle, props.overlay_alpha) if props.overlay_gradient else flat_color
        colors.extend([c, c])
    shader = gpu.shader.from_builtin('SMOOTH_COLOR')
    _overlay_cache["batch"]  = batch_for_shader(shader, 'LINES',
                                                {"pos": coords, "color": colors})
    _overlay_cache["shader"] = shader
    _overlay_cache["valid"]  = True


def _draw_hard_edges():
    if not _GPU_OK:
        return

    context = bpy.context
    if not hasattr(context.scene, "hard_edge_props"):
        return
    props = context.scene.hard_edge_props
    if not props.overlay_enabled:
        return
    obj = context.active_object
    if obj is None or obj.type != 'MESH' or context.mode != 'EDIT_MESH':
        return

    obj_ptr = obj.as_pointer()
    sig     = _props_signature(props)
    if (not _overlay_cache["valid"]
            or _overlay_cache["obj_ptr"]   != obj_ptr
            or _overlay_cache["props_sig"] != sig):
        _rebuild_overlay_cache(obj, props)
        _overlay_cache["obj_ptr"]   = obj_ptr
        _overlay_cache["props_sig"] = sig

    batch = _overlay_cache["batch"]
    if batch is None:
        return
    shader = _overlay_cache["shader"]

    gpu.state.line_width_set(props.overlay_line_width)
    gpu.state.depth_test_set('LESS_EQUAL')
    gpu.state.blend_set('ALPHA')
    gpu.matrix.push()
    gpu.matrix.multiply_matrix(obj.matrix_world)
    shader.bind()
    batch.draw(shader)
    gpu.matrix.pop()
    gpu.state.blend_set('NONE')
    gpu.state.line_width_set(1.0)


def _draw_custom_measurements():
    if not _BLF_OK:
        return

    context = bpy.context
    if not hasattr(context.scene, "hard_edge_props"):
        return
    props = context.scene.hard_edge_props
    obj   = context.active_object
    if obj is None or obj.type != 'MESH' or context.mode != 'EDIT_MESH':
        return

    show_len   = props.custom_measure_length
    show_eang  = props.custom_measure_edge_angle
    show_fang  = props.custom_measure_face_angle
    show_farea = props.custom_measure_face_area
    if not any((show_len, show_eang, show_fang, show_farea)):
        return

    region = context.region
    rv3d   = context.region_data
    if region is None or rv3d is None:
        return

    bm    = bmesh.from_edit_mesh(obj.data)
    mat   = obj.matrix_world
    scale = context.scene.unit_settings.scale_length
    fid   = 0
    lh    = props.custom_measure_font_size + 2
    blf.size(fid, props.custom_measure_font_size)
    blf.enable(fid, blf.SHADOW)
    blf.shadow(fid, 3, 0.0, 0.0, 0.0, 0.9)
    blf.color(fid, *props.custom_measure_font_color, 1.0)

    def draw_stack(p2d, lines):
        for i, txt in enumerate(lines):
            blf.position(fid, p2d.x + 6, p2d.y + 4 + i * lh, 0)
            blf.draw(fid, txt)

    if show_len or show_eang:
        bm.edges.ensure_lookup_table()
        for edge in bm.edges:
            if not edge.select:
                continue
            v0 = mat @ edge.verts[0].co
            v1 = mat @ edge.verts[1].co
            p2d = location_3d_to_region_2d(region, rv3d, (v0 + v1) / 2.0)
            if p2d is None:
                continue
            lines = []
            if show_len:
                lines.append(f"{(v1 - v0).length * scale:.1f}")
            if show_eang:
                a = edge_face_angle(edge)
                if a is not None:
                    lines.append(f"{math.degrees(a):.1f}")
            draw_stack(p2d, lines)

    if show_fang or show_farea:
        bm.faces.ensure_lookup_table()
        for face in bm.faces:
            if not face.select:
                continue
            p2d = location_3d_to_region_2d(region, rv3d, mat @ face.calc_center_median())
            if p2d is None:
                continue
            lines = []
            if show_farea:
                lines.append(f"{face.calc_area() * scale * scale:.1f}")
            if show_fang:
                verts = face.verts[:]
                n = len(verts)
                max_a = 0.0
                for i in range(n):
                    d1 = verts[(i - 1) % n].co - verts[i].co
                    d2 = verts[(i + 1) % n].co - verts[i].co
                    if d1.length == 0.0 or d2.length == 0.0:
                        continue
                    d1.normalize()
                    d2.normalize()
                    a = math.degrees(math.acos(max(-1.0, min(1.0, d1.dot(d2)))))
                    if a > max_a:
                        max_a = a
                lines.append(f"{max_a:.1f}")
            draw_stack(p2d, lines)

    blf.disable(fid, blf.SHADOW)


def register_draw_handler():
    global _draw_handle, _draw_handle_measure
    if not _GPU_OK:
        return
    if _draw_handle is None:
        _draw_handle = bpy.types.SpaceView3D.draw_handler_add(
            _draw_hard_edges, (), 'WINDOW', 'POST_VIEW')
    if _draw_handle_measure is None:
        _draw_handle_measure = bpy.types.SpaceView3D.draw_handler_add(
            _draw_custom_measurements, (), 'WINDOW', 'POST_PIXEL')
    if _on_depsgraph_update not in bpy.app.handlers.depsgraph_update_post:
        bpy.app.handlers.depsgraph_update_post.append(_on_depsgraph_update)


def unregister_draw_handler():
    global _draw_handle, _draw_handle_measure
    if _on_depsgraph_update in bpy.app.handlers.depsgraph_update_post:
        bpy.app.handlers.depsgraph_update_post.remove(_on_depsgraph_update)
    if _draw_handle is not None:
        bpy.types.SpaceView3D.draw_handler_remove(_draw_handle, 'WINDOW')
        _draw_handle = None
    if _draw_handle_measure is not None:
        bpy.types.SpaceView3D.draw_handler_remove(_draw_handle_measure, 'WINDOW')
        _draw_handle_measure = None
    _invalidate_overlay_cache()

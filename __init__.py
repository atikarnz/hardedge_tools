bl_info = {
    "name": "HardEdge Tools",
    "author": "atikarnz",
    "version": (2, 2, 1),
    "blender": (5, 0, 0),
    "location": "View3D > Sidebar > Hard Edges  |  Edit Mode > Edge menu (Ctrl+E)",
    "description": "Select hard edges by angle with overlay, UV tools, and game-ready pipeline",
    "category": "Mesh",
}

import bpy

from .properties import HardEdgeProperties, HardEdgeStats
from .operators import (
    MESH_OT_select_hard_edges,
    MESH_OT_select_soft_edges,
    MESH_OT_select_hard_edge_loops,
    MESH_OT_select_by_sharp_mark,
    MESH_OT_mark_hard_edges_sharp,
    MESH_OT_clear_all_sharp,
    MESH_OT_auto_bevel_weights,
    MESH_OT_hard_edges_to_seams,
    MESH_OT_sharp_to_seams,
    MESH_OT_batch_process,
    MESH_OT_game_ready_prep,
    MESH_OT_hard_edge_stats,
    MESH_OT_apply_preset,
    MESH_OT_overlays_edge_all_on,
    MESH_OT_overlays_edge_all_off,
)
from .operators_extra import (
    MESH_OT_preview_hard_edges,
    MESH_OT_hide_hard_edge_preview,
    MESH_OT_toggle_hard_edge_preview,
    MESH_OT_reload_addon,
)
from .panels import (
    VIEW3D_PT_hard_edges,
    VIEW3D_PT_hard_edges_settings,
    VIEW3D_PT_hard_edges_select,
    VIEW3D_PT_hard_edges_sharp,
    VIEW3D_PT_hard_edges_pipeline,
    VIEW3D_PT_hard_edges_overlays,
    VIEW3D_PT_ov_highlight,
    VIEW3D_PT_ov_edges,
    VIEW3D_PT_ov_face_normals,
    VIEW3D_PT_ov_geometry,
    VIEW3D_PT_hard_edges_stats,
    edge_menu_draw,
)
from .overlays import register_draw_handler, unregister_draw_handler


classes = (
    HardEdgeProperties,
    HardEdgeStats,
    MESH_OT_select_hard_edges,
    MESH_OT_select_soft_edges,
    MESH_OT_select_hard_edge_loops,
    MESH_OT_select_by_sharp_mark,
    MESH_OT_mark_hard_edges_sharp,
    MESH_OT_clear_all_sharp,
    MESH_OT_auto_bevel_weights,
    MESH_OT_hard_edges_to_seams,
    MESH_OT_sharp_to_seams,
    MESH_OT_batch_process,
    MESH_OT_game_ready_prep,
    MESH_OT_hard_edge_stats,
    MESH_OT_apply_preset,
    MESH_OT_overlays_edge_all_on,
    MESH_OT_overlays_edge_all_off,
    MESH_OT_preview_hard_edges,
    MESH_OT_hide_hard_edge_preview,
    MESH_OT_toggle_hard_edge_preview,
    MESH_OT_reload_addon,
    VIEW3D_PT_hard_edges,
    VIEW3D_PT_hard_edges_settings,
    VIEW3D_PT_hard_edges_select,
    VIEW3D_PT_hard_edges_sharp,
    VIEW3D_PT_hard_edges_pipeline,
    VIEW3D_PT_hard_edges_overlays,
    VIEW3D_PT_ov_highlight,
    VIEW3D_PT_ov_edges,
    VIEW3D_PT_ov_face_normals,
    VIEW3D_PT_ov_geometry,
    VIEW3D_PT_hard_edges_stats,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.hard_edge_props = bpy.props.PointerProperty(type=HardEdgeProperties)
    bpy.types.Scene.hard_edge_stats = bpy.props.PointerProperty(type=HardEdgeStats)
    bpy.types.VIEW3D_MT_edit_mesh_edges.append(edge_menu_draw)
    register_draw_handler()


def unregister():
    unregister_draw_handler()
    bpy.types.VIEW3D_MT_edit_mesh_edges.remove(edge_menu_draw)
    del bpy.types.Scene.hard_edge_stats
    del bpy.types.Scene.hard_edge_props
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

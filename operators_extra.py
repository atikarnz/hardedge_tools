"""Additional operators split out from operators.py.

The Cowork file-write layer has a per-file write-size cap, so the preview /
toggle / reload operators live here. Functionally identical to having them
in operators.py.
"""
import bpy

from .utils import poll_edit_mesh
from .overlays import mark_overlay_dirty


class MESH_OT_preview_hard_edges(bpy.types.Operator):
    """Preview matching hard edges in the viewport without changing selection"""
    bl_idname = "mesh.preview_hard_edges"
    bl_label  = "Preview Hard Edges"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return poll_edit_mesh(context)

    def execute(self, context):
        props = context.scene.hard_edge_props
        props.overlay_enabled = True
        mark_overlay_dirty()
        if context.area:
            context.area.tag_redraw()
        self.report({'INFO'}, "Hard edge preview enabled")
        return {'FINISHED'}


class MESH_OT_hide_hard_edge_preview(bpy.types.Operator):
    """Hide the hard-edge preview overlay"""
    bl_idname = "mesh.hide_hard_edge_preview"
    bl_label  = "Hide Hard Edge Preview"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return poll_edit_mesh(context)

    def execute(self, context):
        context.scene.hard_edge_props.overlay_enabled = False
        mark_overlay_dirty()
        if context.area:
            context.area.tag_redraw()
        self.report({'INFO'}, "Hard edge preview hidden")
        return {'FINISHED'}


class MESH_OT_toggle_hard_edge_preview(bpy.types.Operator):
    """Toggle the hard-edge preview overlay"""
    bl_idname = "mesh.toggle_hard_edge_preview"
    bl_label  = "Toggle Hard Edge Preview"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return poll_edit_mesh(context)

    def execute(self, context):
        props = context.scene.hard_edge_props
        props.overlay_enabled = not props.overlay_enabled
        mark_overlay_dirty()
        if context.area:
            context.area.tag_redraw()
        state = "enabled" if props.overlay_enabled else "hidden"
        self.report({'INFO'}, f"Hard edge preview {state}")
        return {'FINISHED'}


class MESH_OT_reload_addon(bpy.types.Operator):
    """Reload all Blender scripts (equivalent to F3 > Reload Scripts)."""
    bl_idname  = "mesh.reload_hard_edges_addon"
    bl_label   = "Reload Addon"
    bl_options = {'REGISTER'}

    def execute(self, context):
        try:
            bpy.ops.script.reload()
        except RuntimeError as exc:
            self.report({'ERROR'}, f"Reload failed: {exc}")
            return {'CANCELLED'}
        self.report({'INFO'}, "Scripts reloaded. If panels look stale, restart Blender.")
        return {'FINISHED'}

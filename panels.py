import bpy

from .constants import PRESET_DATA
from .utils import fill_select_op_props


# ══════════════════════════════════════════════════════════════════
#  Main Panel
# ══════════════════════════════════════════════════════════════════

class VIEW3D_PT_hard_edges(bpy.types.Panel):
    bl_label       = "Hard Edges"
    bl_idname      = "VIEW3D_PT_hard_edges"
    bl_space_type  = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category    = "Hard Edges"
    bl_context     = "mesh_edit"

    def draw(self, context):
        layout = self.layout
        props  = context.scene.hard_edge_props

        row = layout.row(align=True)
        row.scale_y = 1.2
        row.prop(props, "angle_threshold", slider=True)

        col = layout.column(align=True)
        for i in range(0, len(PRESET_DATA), 2):
            row = col.row(align=True)
            for name in list(PRESET_DATA)[i:i + 2]:
                op = row.operator("mesh.apply_hard_edge_preset",
                                  text=name, icon='DOT')
                op.preset = name

        layout.separator(factor=0.3)

        row = layout.row(align=True)
        row.scale_y = 1.3
        preview_icon = 'HIDE_ON' if props.overlay_enabled else 'HIDE_OFF'
        preview_text = "Hide Preview" if props.overlay_enabled else "Preview"
        row.operator("mesh.toggle_hard_edge_preview",
                     icon=preview_icon, text=preview_text)
        fill_select_op_props(row.operator("mesh.select_hard_edges",
                                          icon='EDGESEL', text="Select"), props)
        op = row.operator("mesh.mark_hard_edges_sharp", icon='SNAP_EDGE', text="Mark")
        op.angle_threshold = props.angle_threshold
        row.operator("mesh.clear_all_sharp", icon='X', text="Clear")


class VIEW3D_PT_hard_edges_settings(bpy.types.Panel):
    bl_label       = "Settings"
    bl_idname      = "VIEW3D_PT_hard_edges_settings"
    bl_parent_id   = "VIEW3D_PT_hard_edges"
    bl_space_type  = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_options     = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        props  = context.scene.hard_edge_props
        col = layout.column(align=True)
        col.prop(props, "include_boundary",   icon='EDGESEL')
        col.prop(props, "extend_selection",   icon='SELECT_EXTEND')
        col.prop(props, "include_sharp_mark", icon='SHARPCURVE')
        col.prop(props, "uv_seams_only",      icon='UV')
        col.separator()
        col.prop(props, "use_length_filter",  icon='DRIVER_DISTANCE')
        if props.use_length_filter:
            row = col.row(align=True)
            row.prop(props, "min_edge_length")
            row.prop(props, "max_edge_length")


class VIEW3D_PT_hard_edges_select(bpy.types.Panel):
    bl_label       = "Select"
    bl_idname      = "VIEW3D_PT_hard_edges_select"
    bl_parent_id   = "VIEW3D_PT_hard_edges"
    bl_space_type  = 'VIEW_3D'
    bl_region_type = 'UI'

    def draw(self, context):
        layout = self.layout
        props  = context.scene.hard_edge_props
        col = layout.column(align=True)
        fill_select_op_props(col.operator("mesh.select_hard_edges",
                                          text="Select Hard Edges"), props)
        col.operator("mesh.select_soft_edges",
                     text="Select Soft Edges")
        col.operator("mesh.select_hard_edge_loops",
                     text="Select Hard Edge Loops")
        col.operator("mesh.select_by_sharp_mark",
                     text="Select Sharp Edges")


class VIEW3D_PT_hard_edges_sharp(bpy.types.Panel):
    bl_label       = "Sharp Marks"
    bl_idname      = "VIEW3D_PT_hard_edges_sharp"
    bl_parent_id   = "VIEW3D_PT_hard_edges"
    bl_space_type  = 'VIEW_3D'
    bl_region_type = 'UI'

    def draw(self, context):
        layout = self.layout
        props  = context.scene.hard_edge_props
        col = layout.column(align=True)
        op = col.operator("mesh.mark_hard_edges_sharp",
                          icon='SNAP_EDGE', text="Mark as Sharp")
        op.angle_threshold = props.angle_threshold
        col.operator("mesh.clear_all_sharp", icon='X', text="Clear All Sharp")
        col.separator()
        col.prop(props, "preserve_existing_seams", icon='UV')
        op = col.operator("mesh.hard_edges_to_seams",
                          icon='UV', text="Hard Edges -> UV Seams")
        op.clear_existing = not props.preserve_existing_seams
        op = col.operator("mesh.sharp_to_seams",
                          icon='EDGE_SEAM', text="Sharp Marks -> UV Seams")
        op.clear_existing = not props.preserve_existing_seams
        col.separator()
        col.prop(props, "bevel_weight", slider=True, text="Weight")
        col.prop(props, "bevel_use_selection")
        col.operator("mesh.auto_bevel_weights",
                     icon='MOD_BEVEL', text="Set Bevel Weights")


class VIEW3D_PT_hard_edges_pipeline(bpy.types.Panel):
    bl_label       = "Pipeline"
    bl_idname      = "VIEW3D_PT_hard_edges_pipeline"
    bl_parent_id   = "VIEW3D_PT_hard_edges"
    bl_space_type  = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_options     = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        props  = context.scene.hard_edge_props
        col = layout.column(align=True)
        col.operator("mesh.game_ready_prep", icon='CHECKMARK',
                     text="Game-Ready (Unity)").engine = 'UNITY'
        col.operator("mesh.game_ready_prep", icon='CHECKMARK',
                     text="Game-Ready (Unreal)").engine = 'UNREAL'
        col.separator()
        col.prop(props, "batch_clear_first")
        col.operator("mesh.batch_hard_edges",
                     icon='FILE_REFRESH', text="Batch Mark Sharp")
        col.separator()
        col.operator("mesh.reload_hard_edges_addon",
                     icon='FILE_REFRESH', text="Reload Addon")


# ══════════════════════════════════════════════════════════════════
#  Overlays Panel
# ══════════════════════════════════════════════════════════════════

class VIEW3D_PT_hard_edges_overlays(bpy.types.Panel):
    bl_label       = "Edit Mode Overlays"
    bl_idname      = "VIEW3D_PT_hard_edges_overlays"
    bl_space_type  = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category    = "Hard Edges"
    bl_context     = "mesh_edit"
    bl_options     = {'DEFAULT_CLOSED'}

    def draw(self, context):
        # This panel is mainly a parent/header for the child panels below, but
        # an empty body reads as "broken", so give it a one-line orientation hint.
        self.layout.label(text="Toggle viewport overlays below", icon='OVERLAY')


class VIEW3D_PT_ov_highlight(bpy.types.Panel):
    bl_label       = "Hard Edge Highlight"
    bl_idname      = "VIEW3D_PT_ov_highlight"
    bl_parent_id   = "VIEW3D_PT_hard_edges_overlays"
    bl_space_type  = 'VIEW_3D'
    bl_region_type = 'UI'

    def draw_header(self, context):
        self.layout.prop(context.scene.hard_edge_props, "overlay_enabled", text="")

    def draw(self, context):
        layout = self.layout
        props  = context.scene.hard_edge_props
        row = layout.row(align=True)
        row.operator("mesh.preview_hard_edges",
                     icon='HIDE_OFF', text="Preview")
        row.operator("mesh.hide_hard_edge_preview",
                     icon='HIDE_ON', text="Hide")
        col = layout.column(align=True)
        col.active = props.overlay_enabled
        col.prop(props, "overlay_gradient", icon='COLOR')
        if not props.overlay_gradient:
            col.prop(props, "overlay_color", text="Color")
        col.prop(props, "overlay_alpha",      text="Opacity",    slider=True)
        col.prop(props, "overlay_line_width", text="Line Width", slider=True)


class VIEW3D_PT_ov_edges(bpy.types.Panel):
    bl_label       = "Edge Overlays"
    bl_idname      = "VIEW3D_PT_ov_edges"
    bl_parent_id   = "VIEW3D_PT_hard_edges_overlays"
    bl_space_type  = 'VIEW_3D'
    bl_region_type = 'UI'

    def draw(self, context):
        layout  = self.layout
        overlay = context.space_data.overlay
        col = layout.column(align=True)
        col.prop(overlay, "show_edge_sharp",       text="Sharp Edges",   icon='EDGE_SHARP')
        col.prop(overlay, "show_edge_seams",        text="UV Seams",      icon='EDGE_SEAM')
        col.prop(overlay, "show_edge_bevel_weight", text="Bevel Weights", icon='MOD_BEVEL')
        col.prop(overlay, "show_edge_crease",       text="Edge Crease",   icon='EDGE_CREASE')
        row = layout.row(align=True)
        row.operator("mesh.overlays_edge_all_on",  icon='HIDE_OFF', text="All On")
        row.operator("mesh.overlays_edge_all_off", icon='HIDE_ON',  text="All Off")


class VIEW3D_PT_ov_face_normals(bpy.types.Panel):
    bl_label       = "Face & Normals"
    bl_idname      = "VIEW3D_PT_ov_face_normals"
    bl_parent_id   = "VIEW3D_PT_hard_edges_overlays"
    bl_space_type  = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_options     = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout  = self.layout
        overlay = context.space_data.overlay
        col = layout.column(align=True)
        col.prop(overlay, "show_face_orientation", text="Face Orientation", icon='NORMALS_FACE')
        col.prop(overlay, "show_faces",            text="Faces",            icon='FACESEL')
        col.separator()
        col.prop(overlay, "show_vertex_normals",   text="Vertex Normals",   icon='NORMALS_VERTEX')
        col.prop(overlay, "show_split_normals",    text="Split Normals",    icon='NORMALS_VERTEX_FACE')
        col.prop(overlay, "show_face_normals",     text="Face Normals",     icon='NORMALS_FACE')
        sub = col.column(align=True)
        sub.active = (overlay.show_vertex_normals or
                      overlay.show_split_normals  or
                      overlay.show_face_normals)
        sub.prop(overlay, "normals_length", text="Size", slider=True)


class VIEW3D_PT_ov_geometry(bpy.types.Panel):
    bl_label       = "Geometry & Measurements"
    bl_idname      = "VIEW3D_PT_ov_geometry"
    bl_parent_id   = "VIEW3D_PT_hard_edges_overlays"
    bl_space_type  = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_options     = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout  = self.layout
        overlay = context.space_data.overlay
        props   = context.scene.hard_edge_props
        col = layout.column(align=True)
        col.prop(overlay, "show_wireframes",   text="Wireframe",      icon='SHADING_WIRE')
        col.prop(overlay, "show_occlude_wire", text="Hide Back Edges")
        col.separator()
        col.label(text="1dp Measurements")
        col.prop(props, "custom_measure_length",     text="Edge Length")
        col.prop(props, "custom_measure_edge_angle", text="Edge Angle")
        col.prop(props, "custom_measure_face_angle", text="Face Angle")
        col.prop(props, "custom_measure_face_area",  text="Face Area")
        any_on = any((props.custom_measure_length,     props.custom_measure_edge_angle,
                      props.custom_measure_face_angle, props.custom_measure_face_area))
        sub = col.column(align=True)
        sub.active = any_on
        sub.prop(props, "custom_measure_font_size",  text="Font Size",  slider=True)
        sub.prop(props, "custom_measure_font_color", text="Color")
        sub.prop(props, "custom_measure_label_limit", text="Label Limit")
        if any_on:
            box = col.box()
            wcol = box.column(align=True)
            wcol.label(text="Labels redraw every frame.", icon='ERROR')
            wcol.label(text="Large selections lag dense meshes —")
            wcol.label(text="labels auto-hide past the Label Limit.")


# ══════════════════════════════════════════════════════════════════
#  Statistics Panel
# ══════════════════════════════════════════════════════════════════

class VIEW3D_PT_hard_edges_stats(bpy.types.Panel):
    bl_label       = "Statistics"
    bl_idname      = "VIEW3D_PT_hard_edges_stats"
    bl_space_type  = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category    = "Hard Edges"
    bl_context     = "mesh_edit"
    bl_options     = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        st     = context.scene.hard_edge_stats
        layout.operator("mesh.hard_edge_stats", icon='INFO', text="Refresh Stats")
        if st.total_edges > 0:
            box = layout.box()
            col = box.column(align=True)
            col.label(text=f"Total Edges    :  {st.total_edges}")
            col.label(text=f"Hard Edges     :  {st.hard_count}  ({st.hard_percent:.1f} %)")
            col.label(text=f"Boundary Edges :  {st.boundary_count}")
            col.separator()
            col.label(text="(Avg/Max angles are interior-only)")
            col.label(text=f"Avg Angle      :  {st.avg_angle:.1f}")
            col.label(text=f"Max Angle      :  {st.max_angle:.1f}")


# ══════════════════════════════════════════════════════════════════
#  Edge Context Menu (Ctrl+E)
# ══════════════════════════════════════════════════════════════════

def edge_menu_draw(self, context):
    layout = self.layout
    props = context.scene.hard_edge_props
    layout.separator()
    layout.label(text="Hard Edges", icon='EDGESEL')
    layout.operator("mesh.select_hard_edges",      icon='EDGESEL')
    preview_icon = 'HIDE_ON' if props.overlay_enabled else 'HIDE_OFF'
    preview_text = "Hide Preview" if props.overlay_enabled else "Preview"
    layout.operator("mesh.toggle_hard_edge_preview",
                    icon=preview_icon, text=preview_text)
    layout.operator("mesh.select_soft_edges",       icon='RADIOBUT_OFF')
    layout.operator("mesh.select_hard_edge_loops",  icon='EDGESEL')
    layout.separator()
    layout.operator("mesh.mark_hard_edges_sharp",   icon='SNAP_EDGE')
    layout.operator("mesh.select_by_sharp_mark",    icon='SHARPCURVE')
    layout.operator("mesh.clear_all_sharp",         icon='X')
    layout.separator()
    op = layout.operator("mesh.hard_edges_to_seams", icon='UV')
    op.clear_existing = not props.preserve_existing_seams
    op = layout.operator("mesh.sharp_to_seams", icon='EDGE_SEAM')
    op.clear_existing = not props.preserve_existing_seams
    layout.operator("mesh.auto_bevel_weights",      icon='MOD_BEVEL')

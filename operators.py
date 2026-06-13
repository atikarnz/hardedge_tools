import math
import bpy
import bmesh
from bpy.props import FloatProperty, BoolProperty, EnumProperty, StringProperty

from .constants import NO_MAX_LENGTH, PRESET_DATA
from .utils import (
    poll_edit_mesh, edit_bmesh,
    get_hard_edges, props_to_hard_edges, get_bevel_layer,
    expand_edge_loops,
)
from .overlays import mark_overlay_dirty


# ══════════════════════════════════════════════════════════════════
#  Selection
# ══════════════════════════════════════════════════════════════════

class MESH_OT_select_hard_edges(bpy.types.Operator):
    """Select edges whose face angle exceeds the threshold"""
    bl_idname  = "mesh.select_hard_edges"
    bl_label   = "Select Hard Edges"
    bl_options = {'REGISTER', 'UNDO'}

    angle_threshold:    FloatProperty(name="Angle Threshold",
                            default=math.radians(30.0), min=0.0, max=math.pi,
                            subtype='ANGLE', unit='ROTATION')
    select_boundary:    BoolProperty(name="Include Boundary",    default=True)
    extend:             BoolProperty(name="Extend Selection",    default=False)
    use_existing_sharp: BoolProperty(name="Include Sharp Marks", default=False)
    min_length:         FloatProperty(name="Min Length", default=0.0, min=0.0)
    max_length:         FloatProperty(name="Max Length", default=NO_MAX_LENGTH, min=0.0)
    uv_seams_only:      BoolProperty(name="UV Seams Only",       default=False)

    @classmethod
    def poll(cls, context):
        return poll_edit_mesh(context)

    def execute(self, context):
        obj = context.active_object
        context.tool_settings.mesh_select_mode = (False, True, False)
        if not self.extend:
            bpy.ops.mesh.select_all(action='DESELECT')
        bm = edit_bmesh(obj)
        hard = get_hard_edges(bm, self.angle_threshold,
                              self.select_boundary, self.use_existing_sharp,
                              self.min_length, self.max_length, self.uv_seams_only)
        for edge, _ in hard:
            edge.select = True
        bmesh.update_edit_mesh(obj.data)
        self.report({'INFO'}, f"Selected {len(hard)} hard edge(s)")
        return {'FINISHED'}

    def invoke(self, context, event):
        from .utils import fill_select_op_props
        fill_select_op_props(self, context.scene.hard_edge_props)
        return self.execute(context)


class MESH_OT_select_soft_edges(bpy.types.Operator):
    """Select all soft edges — inverse of Select Hard Edges"""
    bl_idname  = "mesh.select_soft_edges"
    bl_label   = "Select Soft Edges"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return poll_edit_mesh(context)

    def execute(self, context):
        obj = context.active_object
        p   = context.scene.hard_edge_props
        context.tool_settings.mesh_select_mode = (False, True, False)
        bpy.ops.mesh.select_all(action='DESELECT')
        bm = edit_bmesh(obj)
        hard_ids = {e.index for e, _ in props_to_hard_edges(bm, p)}

        length_filter_active = p.use_length_filter
        min_len = p.min_edge_length if length_filter_active else 0.0
        max_len = p.max_edge_length if length_filter_active else NO_MAX_LENGTH
        uv_only = p.uv_seams_only

        count = 0
        for edge in bm.edges:
            if edge.index in hard_ids:
                continue
            if length_filter_active:
                length = edge.calc_length()
                if length < min_len or length > max_len:
                    continue
            if uv_only and not edge.seam:
                continue
            edge.select = True
            count += 1
        bmesh.update_edit_mesh(obj.data)
        self.report({'INFO'}, f"Selected {count} soft edge(s)")
        return {'FINISHED'}


class MESH_OT_select_hard_edge_loops(bpy.types.Operator):
    """Select full edge loops through hard edges"""
    bl_idname  = "mesh.select_hard_edge_loops"
    bl_label   = "Select Hard Edge Loops"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return poll_edit_mesh(context)

    def execute(self, context):
        obj = context.active_object
        p   = context.scene.hard_edge_props
        context.tool_settings.mesh_select_mode = (False, True, False)
        bpy.ops.mesh.select_all(action='DESELECT')
        bm = edit_bmesh(obj)
        for edge, _ in props_to_hard_edges(bm, p):
            edge.select = True
        expand_edge_loops(bm)
        bm.select_flush_mode()
        bmesh.update_edit_mesh(obj.data)
        count = sum(1 for e in bm.edges if e.select)
        self.report({'INFO'}, f"Selected {count} edge(s) along hard-edge loops")
        return {'FINISHED'}


class MESH_OT_select_by_sharp_mark(bpy.types.Operator):
    """Select edges marked as Sharp"""
    bl_idname  = "mesh.select_by_sharp_mark"
    bl_label   = "Select Sharp Edges"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return poll_edit_mesh(context)

    def execute(self, context):
        obj = context.active_object
        context.tool_settings.mesh_select_mode = (False, True, False)
        bpy.ops.mesh.select_all(action='DESELECT')
        bm = edit_bmesh(obj)
        count = 0
        for e in bm.edges:
            if not e.smooth:
                e.select = True
                count += 1
        bmesh.update_edit_mesh(obj.data)
        self.report({'INFO'}, f"Selected {count} sharp-marked edge(s)")
        return {'FINISHED'}


# ══════════════════════════════════════════════════════════════════
#  Sharp Marks
# ══════════════════════════════════════════════════════════════════

class MESH_OT_mark_hard_edges_sharp(bpy.types.Operator):
    """Mark edges as Sharp.

    If 'Use Selection' is on (the default when edges are selected on invoke),
    marks the current selection as Sharp — additive, leaves other sharp marks
    alone. Otherwise marks every edge whose face angle exceeds the threshold,
    and (by default) clears any previous sharp marks first.
    """
    bl_idname  = "mesh.mark_hard_edges_sharp"
    bl_label   = "Mark as Sharp"
    bl_options = {'REGISTER', 'UNDO'}

    angle_threshold: FloatProperty(name="Angle Threshold",
                         default=math.radians(30.0), min=0.0, max=math.pi,
                         subtype='ANGLE', unit='ROTATION')
    use_selection:   BoolProperty(name="Use Selection", default=False,
                         description="Mark the currently selected edges instead of all hard edges")
    clear_existing:  BoolProperty(name="Clear Existing Sharp First", default=True,
                         description="Reset all edges to smooth before marking. "
                                     "Ignored when 'Use Selection' is on (selection is additive)")

    @classmethod
    def poll(cls, context):
        return poll_edit_mesh(context)

    def execute(self, context):
        obj = context.active_object
        bm  = edit_bmesh(obj)

        if self.use_selection:
            targets = [e for e in bm.edges if e.select]
            if not targets:
                self.report({'WARNING'}, "No edges selected")
                return {'CANCELLED'}
            # Additive: don't clear other sharp marks when honoring selection.
            for edge in targets:
                edge.smooth = False
            mode = "selected"
        else:
            if self.clear_existing:
                for e in bm.edges:
                    e.smooth = True
            targets = [e for e, _ in get_hard_edges(bm, self.angle_threshold)]
            for edge in targets:
                edge.smooth = False
            mode = "hard"

        bmesh.update_edit_mesh(obj.data)
        self.report({'INFO'}, f"Marked {len(targets)} {mode} edge(s) as Sharp")
        return {'FINISHED'}

    def invoke(self, context, event):
        # If the user has edges selected when triggering this op, default to
        # marking the selection (which is what they almost certainly want).
        # Otherwise default to angle-based marking.
        obj = context.active_object
        has_selection = False
        if obj is not None and obj.type == 'MESH' and context.mode == 'EDIT_MESH':
            bm = edit_bmesh(obj)
            has_selection = any(e.select for e in bm.edges)
        self.use_selection    = has_selection
        self.angle_threshold  = context.scene.hard_edge_props.angle_threshold
        return self.execute(context)


class MESH_OT_clear_all_sharp(bpy.types.Operator):
    """Remove Sharp mark from all edges"""
    bl_idname  = "mesh.clear_all_sharp"
    bl_label   = "Clear All Sharp"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return poll_edit_mesh(context)

    def execute(self, context):
        obj = context.active_object
        bm  = edit_bmesh(obj)
        for e in bm.edges:
            e.smooth = True
        bmesh.update_edit_mesh(obj.data)
        self.report({'INFO'}, "Cleared all Sharp marks")
        return {'FINISHED'}


# ══════════════════════════════════════════════════════════════════
#  Workflow
# ══════════════════════════════════════════════════════════════════

class MESH_OT_auto_bevel_weights(bpy.types.Operator):
    """Write bevel weights to hard edges, or only to selected edges if 'Only Selected' is on"""
    bl_idname  = "mesh.auto_bevel_weights"
    bl_label   = "Set Bevel Weights"
    bl_options = {'REGISTER', 'UNDO'}

    weight:        FloatProperty(name="Bevel Weight", default=1.0, min=0.0, max=1.0)
    use_selection: BoolProperty(name="Only Selected", default=False,
                       description="Write to currently selected edges instead of all hard edges")

    @classmethod
    def poll(cls, context):
        return poll_edit_mesh(context)

    def execute(self, context):
        obj = context.active_object
        p   = context.scene.hard_edge_props
        bm  = edit_bmesh(obj)
        bevel_layer = get_bevel_layer(bm)
        if self.use_selection:
            targets = [e for e in bm.edges if e.select]
            mode    = "selected"
        else:
            targets = [e for e, _ in props_to_hard_edges(bm, p)]
            mode    = "hard"
        if not targets:
            self.report({'WARNING'},
                        "No selected edges" if self.use_selection else "No hard edges matched")
            return {'CANCELLED'}
        for edge in targets:
            edge[bevel_layer] = self.weight
        bmesh.update_edit_mesh(obj.data)
        self.report({'INFO'},
                    f"Set bevel weight {self.weight:.2f} on {len(targets)} {mode} edge(s)")
        return {'FINISHED'}

    def invoke(self, context, event):
        p = context.scene.hard_edge_props
        self.weight        = p.bevel_weight
        self.use_selection = p.bevel_use_selection
        return self.execute(context)


class MESH_OT_hard_edges_to_seams(bpy.types.Operator):
    """Convert hard edges to UV seams"""
    bl_idname  = "mesh.hard_edges_to_seams"
    bl_label   = "Hard Edges -> UV Seams"
    bl_options = {'REGISTER', 'UNDO'}

    clear_existing: BoolProperty(name="Clear Existing Seams First", default=False)

    @classmethod
    def poll(cls, context):
        return poll_edit_mesh(context)

    def execute(self, context):
        obj = context.active_object
        p   = context.scene.hard_edge_props
        bm  = edit_bmesh(obj)
        hard = props_to_hard_edges(bm, p)
        if not hard:
            self.report({'WARNING'}, "No hard edges matched")
            return {'CANCELLED'}
        if self.clear_existing:
            for e in bm.edges:
                e.seam = False
        for edge, _ in hard:
            edge.seam = True
        bmesh.update_edit_mesh(obj.data)
        self.report({'INFO'}, f"Set {len(hard)} UV seam(s) from hard edges")
        return {'FINISHED'}


class MESH_OT_sharp_to_seams(bpy.types.Operator):
    """Set UV seams from Sharp-marked edges"""
    bl_idname  = "mesh.sharp_to_seams"
    bl_label   = "Sharp Marks -> UV Seams"
    bl_options = {'REGISTER', 'UNDO'}

    clear_existing: BoolProperty(name="Clear Existing Seams First", default=False)
    also_select:    BoolProperty(name="Select Result",               default=False)

    @classmethod
    def poll(cls, context):
        return poll_edit_mesh(context)

    def execute(self, context):
        obj = context.active_object
        bm  = edit_bmesh(obj)
        targets = [e for e in bm.edges if not e.smooth]
        if not targets:
            self.report({'WARNING'}, "No sharp-marked edges found. Use 'Mark as Sharp' first.")
            return {'CANCELLED'}
        if self.clear_existing:
            for e in bm.edges:
                e.seam = False
        for e in targets:
            e.seam = True
            if self.also_select:
                e.select = True
        bmesh.update_edit_mesh(obj.data)
        self.report({'INFO'}, f"Set {len(targets)} UV seam(s) from sharp marks")
        return {'FINISHED'}


class MESH_OT_batch_process(bpy.types.Operator):
    """Mark hard edges on all selected mesh objects"""
    bl_idname  = "mesh.batch_hard_edges"
    bl_label   = "Batch Mark Sharp"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return any(o.type == 'MESH' for o in context.selected_objects)

    def execute(self, context):
        p             = context.scene.hard_edge_props
        mesh_objects  = [o for o in context.selected_objects if o.type == 'MESH']
        original_mode = context.mode
        active_obj    = context.view_layer.objects.active
        total         = 0
        if original_mode != 'OBJECT':
            bpy.ops.object.mode_set(mode='OBJECT')
        seen = set()
        for obj in mesh_objects:
            mesh = obj.data
            if mesh.name in seen:
                continue
            seen.add(mesh.name)
            bm = bmesh.new()
            bm.from_mesh(mesh)
            if p.batch_clear_first:
                for e in bm.edges:
                    e.smooth = True
            hard = get_hard_edges(bm, p.angle_threshold, p.include_boundary, p.include_sharp_mark)
            for edge, _ in hard:
                edge.smooth = False
            total += len(hard)
            bm.to_mesh(mesh)
            bm.free()
            mesh.update()
        # Only restore EDIT mode if we started there *and* the active object can enter it.
        if original_mode == 'EDIT_MESH' and active_obj is not None and active_obj.type == 'MESH':
            bpy.ops.object.mode_set(mode='EDIT')
        self.report({'INFO'},
                    f"Processed {len(seen)} mesh(es) across {len(mesh_objects)} object(s), "
                    f"marked {total} hard edge(s)")
        return {'FINISHED'}


class MESH_OT_game_ready_prep(bpy.types.Operator):
    """Smooth shading + mark sharps + Edge Split modifier in one click"""
    bl_idname  = "mesh.game_ready_prep"
    bl_label   = "Game-Ready Prep"
    bl_options = {'REGISTER', 'UNDO'}

    engine: EnumProperty(
        name="Engine",
        items=[
            ('UNITY',   "Unity",   ""),
            ('UNREAL',  "Unreal",  ""),
            ('GENERIC', "Generic", ""),
        ],
        default='GENERIC',
    )

    @classmethod
    def poll(cls, context):
        return bool(context.active_object and context.active_object.type == 'MESH')

    def execute(self, context):
        obj = context.active_object
        p   = context.scene.hard_edge_props

        # Remember the user's starting mode so we can restore it at the end.
        original_mode = context.mode
        # `context.mode` uses 'EDIT_MESH' but mode_set wants 'EDIT'.
        mode_back = 'EDIT' if original_mode == 'EDIT_MESH' else original_mode

        try:
            bpy.ops.object.mode_set(mode='OBJECT')
            bpy.ops.object.shade_smooth()
            bpy.ops.object.mode_set(mode='EDIT')
            bm = edit_bmesh(obj)
            for e in bm.edges:
                e.smooth = True
            for edge, _ in get_hard_edges(bm, p.angle_threshold, p.include_boundary):
                edge.smooth = False
            bmesh.update_edit_mesh(obj.data)
            bpy.ops.object.mode_set(mode='OBJECT')

            # Replace any existing GameReadySplit modifier with a fresh one.
            for mod in list(obj.modifiers):
                if mod.type == 'EDGE_SPLIT':
                    obj.modifiers.remove(mod)
            mod = obj.modifiers.new(name="GameReadySplit", type='EDGE_SPLIT')
            mod.split_angle    = p.angle_threshold
            mod.use_edge_angle = True
            mod.use_edge_sharp = True
        finally:
            # Always try to restore the original mode, even on error.
            try:
                if mode_back not in ('OBJECT',):
                    bpy.ops.object.mode_set(mode=mode_back)
            except (RuntimeError, TypeError):
                pass

        hints = {
            'UNREAL':  " | Enable 'Import Normals' in UE5",
            'UNITY':   " | Match angle in Unity import settings",
            'GENERIC': "",
        }
        self.report({'INFO'}, f"Game-ready prep done ({self.engine}){hints[self.engine]}")
        return {'FINISHED'}


# ══════════════════════════════════════════════════════════════════
#  Stats / Presets / Edge Overlays / Reload
# ══════════════════════════════════════════════════════════════════

class MESH_OT_hard_edge_stats(bpy.types.Operator):
    """Refresh hard edge statistics"""
    bl_idname = "mesh.hard_edge_stats"
    bl_label  = "Refresh Stats"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return poll_edit_mesh(context)

    def execute(self, context):
        obj    = context.active_object
        p      = context.scene.hard_edge_props
        bm     = edit_bmesh(obj)
        hard   = props_to_hard_edges(bm, p)
        total  = len(bm.edges)
        interior_angles = [math.degrees(a) for _, a in hard if a < math.pi]
        boundary_count  = sum(1 for _, a in hard if a >= math.pi)
        st = context.scene.hard_edge_stats
        st.total_edges    = total
        st.hard_count     = len(hard)
        st.boundary_count = boundary_count
        st.hard_percent   = (len(hard) / total * 100) if total else 0.0
        st.avg_angle      = sum(interior_angles) / len(interior_angles) if interior_angles else 0.0
        st.max_angle      = max(interior_angles) if interior_angles else 0.0
        self.report({'INFO'},
                    f"{st.hard_count}/{total} ({st.hard_percent:.1f}%) | "
                    f"Boundary: {boundary_count} | "
                    f"Avg: {st.avg_angle:.1f} Max: {st.max_angle:.1f}")
        return {'FINISHED'}


class MESH_OT_apply_preset(bpy.types.Operator):
    """Apply angle threshold preset"""
    bl_idname = "mesh.apply_hard_edge_preset"
    bl_label  = "Apply Preset"
    bl_options = {'REGISTER', 'UNDO'}

    preset: StringProperty(default="Hard Surface")

    def execute(self, context):
        angle = PRESET_DATA.get(self.preset)
        if angle is None:
            valid = ", ".join(PRESET_DATA.keys())
            self.report({'WARNING'},
                        f"Unknown preset '{self.preset}'. Valid: {valid}")
            return {'CANCELLED'}
        context.scene.hard_edge_props.angle_threshold = angle
        self.report({'INFO'}, f"Preset '{self.preset}' - {math.degrees(angle):.0f} deg")
        return {'FINISHED'}


class MESH_OT_overlays_edge_all_on(bpy.types.Operator):
    """Enable all edge overlays"""
    bl_idname = "mesh.overlays_edge_all_on"
    bl_label  = "All On"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return poll_edit_mesh(context)

    def execute(self, context):
        ov = context.space_data.overlay
        ov.show_edge_sharp = ov.show_edge_seams = True
        ov.show_edge_bevel_weight = ov.show_edge_crease = True
        return {'FINISHED'}


class MESH_OT_overlays_edge_all_off(bpy.types.Operator):
    """Disable all edge overlays"""
    bl_idname = "mesh.overlays_edge_all_off"
    bl_label  = "All Off"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return poll_edit_mesh(context)

    def execute(self, context):
        ov = context.space_data.overlay
        ov.show_edge_sharp = ov.show_edge_seams = False
        ov.show_edge_bevel_weight = ov.show_edge_crease = False
        return {'FINISHED'}


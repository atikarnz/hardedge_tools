import math

import bpy
from bpy.props import (
    FloatProperty, BoolProperty, IntProperty, FloatVectorProperty,
)

from .constants import NO_MAX_LENGTH


def _invalidate_overlay(self, context):
    from .overlays import mark_overlay_dirty
    mark_overlay_dirty()


class HardEdgeProperties(bpy.types.PropertyGroup):
    # Threshold & filters  (stored in radians, shown as degrees via ANGLE subtype)
    angle_threshold:    FloatProperty(name="Angle",
                            default=math.radians(30.0), min=0.0, max=math.pi,
                            subtype='ANGLE', unit='ROTATION',
                            description="Face-angle threshold above which an edge counts as hard",
                            update=_invalidate_overlay)
    include_boundary:   BoolProperty(name="Include Boundary",    default=True,
                            description="Treat edges with a single linked face as hard",
                            update=_invalidate_overlay)
    extend_selection:   BoolProperty(name="Extend Selection",    default=False,
                            description="Add to the current selection instead of replacing it")
    include_sharp_mark: BoolProperty(name="Include Sharp Marks", default=False,
                            description="Also include edges marked as Sharp regardless of angle",
                            update=_invalidate_overlay)
    uv_seams_only:      BoolProperty(name="UV Seams Only",       default=False,
                            description="Restrict matching to edges that already have a UV seam",
                            update=_invalidate_overlay)
    use_length_filter:  BoolProperty(name="Filter by Length",    default=False,
                            description="Enable the Min/Max edge-length filter",
                            update=_invalidate_overlay)
    min_edge_length:    FloatProperty(name="Min", default=0.0,   min=0.0,
                            subtype='DISTANCE', unit='LENGTH',
                            description="Minimum edge length to include",
                            update=_invalidate_overlay)
    max_edge_length:    FloatProperty(name="Max", default=NO_MAX_LENGTH, min=0.0,
                            subtype='DISTANCE', unit='LENGTH',
                            description="Maximum edge length to include",
                            update=_invalidate_overlay)

    # Hard edge overlay
    overlay_enabled:    BoolProperty(name="Highlight Hard Edges", default=False,
                            description="Show the GPU preview of currently-matching hard edges")
    overlay_gradient:   BoolProperty(name="Angle Gradient",       default=False,
                            description="Color green to red by sharpness",
                            update=_invalidate_overlay)
    overlay_color:      FloatVectorProperty(name="Color", subtype='COLOR',
                            default=(1.0, 0.2, 0.0), min=0.0, max=1.0, size=3,
                            description="Solid color used when Angle Gradient is off",
                            update=_invalidate_overlay)
    overlay_alpha:      FloatProperty(name="Opacity",    default=0.9, min=0.1, max=1.0,
                            description="Overlay line opacity",
                            update=_invalidate_overlay)
    overlay_line_width: FloatProperty(name="Line Width", default=2.0, min=1.0, max=10.0,
                            description="Overlay line width in pixels")

    # 1dp measurements
    custom_measure_length:     BoolProperty(name="Edge Length", default=False,
                            description="Show length of selected edges (1 decimal place)")
    custom_measure_edge_angle: BoolProperty(name="Edge Angle",  default=False,
                            description="Show face-pair angle for selected edges")
    custom_measure_face_angle: BoolProperty(name="Face Angle",  default=False,
                            description="Show largest interior angle of selected faces")
    custom_measure_face_area:  BoolProperty(name="Face Area",   default=False,
                            description="Show area of selected faces")
    custom_measure_font_size:  IntProperty( name="Font Size",   default=14, min=14, max=36,
                            description="Font size for measurement labels")
    custom_measure_font_color: FloatVectorProperty(name="Color", subtype='COLOR',
                            default=(1.0, 1.0, 0.2), min=0.0, max=1.0, size=3,
                            description="Color of measurement labels")
    custom_measure_label_limit: IntProperty(name="Label Limit", default=500, min=0, max=100000,
                            description="Maximum number of selected elements to label at once. "
                                        "Measurement labels are re-projected and redrawn every "
                                        "frame, so a large selection on a dense mesh slows the "
                                        "viewport. Above this count the labels are hidden and a "
                                        "viewport warning is shown instead. Set to 0 to never cap")

    # Bevel weight assigned by "Set Bevel Weights"
    bevel_weight:        FloatProperty(name="Bevel Weight", default=1.0, min=0.0, max=1.0,
                            description="Weight written to edges by 'Set Bevel Weights'")
    bevel_use_selection: BoolProperty(name="Only Selected", default=False,
                            description="Write the weight only to currently selected edges "
                                        "instead of all hard edges — use to build per-edge "
                                        "variation by running multiple times with different weights")

    preserve_existing_seams: BoolProperty(name="Preserve Existing Seams", default=True,
                            description="Keep current UV seams when converting hard or sharp edges "
                                        "to seams")

    # Batch
    batch_clear_first: BoolProperty(name="Clear Existing Sharp First", default=True,
                            description="Reset all edges to smooth before marking new hard edges")


class HardEdgeStats(bpy.types.PropertyGroup):
    total_edges:    IntProperty(  name="Total Edges",    default=0)
    hard_count:     IntProperty(  name="Hard Edges",     default=0)
    boundary_count: IntProperty(  name="Boundary Edges", default=0)
    hard_percent:   FloatProperty(name="Percentage",     default=0.0)
    avg_angle:      FloatProperty(name="Avg Angle",      default=0.0)
    max_angle:      FloatProperty(name="Max Angle",      default=0.0)

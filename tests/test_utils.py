"""Unit tests for hardedge_tools.utils.

Must be run under Blender's bundled Python (so `bmesh` is importable).
See tests/README.md.
"""
import math

import pytest

bmesh = pytest.importorskip("bmesh")

from hardedge_tools.constants import NO_MAX_LENGTH  # noqa: E402
from hardedge_tools.utils import (                  # noqa: E402
    edge_face_angle,
    get_hard_edges,
    angle_to_color,
)


# ──────────────────────────────────────────────────────────────────
#  Fixtures
# ──────────────────────────────────────────────────────────────────

def _make_cube_bm(size: float = 1.0):
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=size)
    bm.edges.ensure_lookup_table()
    bm.faces.ensure_lookup_table()
    return bm


def _make_flat_plane_bm(size: float = 1.0):
    """Single quad with two adjacent quads on each side — all coplanar."""
    bm = bmesh.new()
    bmesh.ops.create_grid(bm, x_segments=2, y_segments=2, size=size)
    bm.edges.ensure_lookup_table()
    return bm


def _make_open_strip_bm():
    """Two coplanar quads sharing one edge — gives us 6 boundary edges + 1 interior."""
    bm = bmesh.new()
    v1 = bm.verts.new((0.0, 0.0, 0.0))
    v2 = bm.verts.new((1.0, 0.0, 0.0))
    v3 = bm.verts.new((1.0, 1.0, 0.0))
    v4 = bm.verts.new((0.0, 1.0, 0.0))
    v5 = bm.verts.new((2.0, 0.0, 0.0))
    v6 = bm.verts.new((2.0, 1.0, 0.0))
    bm.faces.new((v1, v2, v3, v4))
    bm.faces.new((v2, v5, v6, v3))
    bm.edges.ensure_lookup_table()
    return bm


# ──────────────────────────────────────────────────────────────────
#  Tests
# ──────────────────────────────────────────────────────────────────

class TestEdgeFaceAngle:
    def test_cube_edges_are_90_degrees(self):
        bm = _make_cube_bm()
        try:
            for edge in bm.edges:
                a = edge_face_angle(edge)
                assert a is not None
                assert math.isclose(a, math.pi / 2, abs_tol=1e-5)
        finally:
            bm.free()

    def test_coplanar_edges_are_zero(self):
        bm = _make_flat_plane_bm()
        try:
            interior_edges = [e for e in bm.edges if len(e.link_faces) == 2]
            assert interior_edges, "fixture should have interior edges"
            for edge in interior_edges:
                a = edge_face_angle(edge)
                assert a is not None
                assert math.isclose(a, 0.0, abs_tol=1e-5)
        finally:
            bm.free()

    def test_boundary_edge_returns_none(self):
        bm = _make_open_strip_bm()
        try:
            boundary = [e for e in bm.edges if len(e.link_faces) == 1]
            assert boundary, "fixture should have boundary edges"
            for edge in boundary:
                assert edge_face_angle(edge) is None
        finally:
            bm.free()


class TestGetHardEdges:
    def test_cube_at_30deg_returns_all_12(self):
        bm = _make_cube_bm()
        try:
            hard = get_hard_edges(bm, math.radians(30.0))
            assert len(hard) == 12
            for _, a in hard:
                assert math.isclose(a, math.pi / 2, abs_tol=1e-5)
        finally:
            bm.free()

    def test_cube_above_threshold_returns_zero(self):
        bm = _make_cube_bm()
        try:
            hard = get_hard_edges(bm, math.radians(91.0), include_boundary=False)
            assert hard == []
        finally:
            bm.free()

    def test_flat_plane_returns_zero(self):
        bm = _make_flat_plane_bm()
        try:
            hard = get_hard_edges(bm, math.radians(30.0), include_boundary=False)
            assert hard == []
        finally:
            bm.free()

    def test_boundary_edges_included_with_sentinel_pi(self):
        bm = _make_open_strip_bm()
        try:
            hard = get_hard_edges(bm, math.radians(30.0), include_boundary=True)
            # All boundary edges should be present with angle == pi.
            boundary_indices = {e.index for e in bm.edges if len(e.link_faces) == 1}
            hard_indices     = {e.index for e, a in hard if math.isclose(a, math.pi)}
            assert boundary_indices == hard_indices
        finally:
            bm.free()

    def test_boundary_edges_excluded_when_flag_false(self):
        bm = _make_open_strip_bm()
        try:
            hard = get_hard_edges(bm, math.radians(30.0), include_boundary=False)
            assert hard == []
        finally:
            bm.free()

    def test_length_filter_min(self):
        bm = _make_cube_bm(size=2.0)
        try:
            # Each cube edge is length 2; min_length=3 should exclude everything.
            hard = get_hard_edges(bm, math.radians(30.0), min_length=3.0)
            assert hard == []
        finally:
            bm.free()

    def test_length_filter_max(self):
        bm = _make_cube_bm(size=2.0)
        try:
            hard = get_hard_edges(bm, math.radians(30.0), max_length=1.0)
            assert hard == []
        finally:
            bm.free()

    def test_no_max_length_is_infinity(self):
        assert NO_MAX_LENGTH == float('inf')
        # And a cube with default max_length should still match all 12 edges.
        bm = _make_cube_bm()
        try:
            hard = get_hard_edges(bm, math.radians(30.0))
            assert len(hard) == 12
        finally:
            bm.free()


class TestAngleToColor:
    def test_zero_is_green(self):
        r, g, b, a = angle_to_color(0.0)
        assert r == 0.0 and g == 1.0 and b == 0.0 and a == 1.0

    def test_pi_is_red(self):
        r, g, b, a = angle_to_color(math.pi)
        assert math.isclose(r, 1.0) and math.isclose(g, 0.0) and b == 0.0

    def test_alpha_passes_through(self):
        _, _, _, a = angle_to_color(0.5, alpha=0.42)
        assert a == 0.42

    def test_clamped_above_pi(self):
        # Sentinel-pi-plus shouldn't blow past the 0..1 color range.
        r, g, b, a = angle_to_color(math.pi * 2)
        assert 0.0 <= r <= 1.0 and 0.0 <= g <= 1.0

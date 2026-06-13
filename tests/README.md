# Tests

These tests exercise the pure helpers in `utils.py` against a hand-built
`bmesh.new()` mesh. Because they need the `bmesh` module, they have to be run
under Blender's bundled Python — `pytest` from a system Python install will
fail at import time.

## Running

From the directory containing the `hardedge_tools/` folder:

```bash
blender --background --python-expr "import pytest, sys; sys.exit(pytest.main(['-q', 'hardedge_tools/tests']))"
```

Or, if `pytest` isn't shipped with your Blender, install it first:

```bash
blender --background --python-expr "import sys, subprocess; subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'pytest'])"
```

## What's covered

- `edge_face_angle` returns a sensible angle for a fold, None for a wire edge.
- `get_hard_edges` finds the 12 edges of a cube at the default 30° threshold,
  none at 90°+1°.
- `get_hard_edges` honors the length filter and the `include_boundary` flag.
- `NO_MAX_LENGTH` behaves as `+inf`.

import math

# Sentinel for "no upper bound" on edge-length filters.
# Using +inf instead of a literal magic number (was 1e9) so the filter is
# correct at any scene scale.
NO_MAX_LENGTH = float('inf')

# Values in radians. Displayed as degrees via ANGLE subtype on the prop.
PRESET_DATA = {
    "Hard Surface":  math.radians(30.0),
    "Organic":       math.radians(60.0),
    "Game Asset":    math.radians(20.0),
    "Architectural": math.radians(45.0),
}

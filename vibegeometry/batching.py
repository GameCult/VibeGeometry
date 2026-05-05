"""Mesh batching helpers for dense procedural detail."""

from __future__ import annotations

import math


def append_box_parts(verts, faces, loc, axes, size):
    """Append an oriented box to shared mesh arrays."""
    from mathutils import Vector

    origin = Vector(loc)
    ax = [Vector(axis).normalized() for axis in axes]
    sx, sy, sz = (value * 0.5 for value in size)
    base = len(verts)
    for dx, dy, dz in [
        (-sx, -sy, -sz),
        (sx, -sy, -sz),
        (sx, sy, -sz),
        (-sx, sy, -sz),
        (-sx, -sy, sz),
        (sx, -sy, sz),
        (sx, sy, sz),
        (-sx, sy, sz),
    ]:
        v = origin + ax[0] * dx + ax[1] * dy + ax[2] * dz
        verts.append((v.x, v.y, v.z))
    faces.extend(
        [
            (base + 0, base + 1, base + 2, base + 3),
            (base + 4, base + 7, base + 6, base + 5),
            (base + 0, base + 4, base + 5, base + 1),
            (base + 1, base + 5, base + 6, base + 2),
            (base + 2, base + 6, base + 7, base + 3),
            (base + 3, base + 7, base + 4, base + 0),
        ]
    )


def append_cylindrical_ring_band(verts, faces, x, inner_radius, outer_radius, segments=96, start_angle=-math.pi, end_angle=math.pi):
    """Append an annular band in the Y/Z plane at axial coordinate x."""
    span = end_angle - start_angle
    base = len(verts)
    for i in range(segments):
        a = start_angle + span * i / segments
        verts.append((x, inner_radius * math.cos(a), inner_radius * math.sin(a)))
        verts.append((x, outer_radius * math.cos(a), outer_radius * math.sin(a)))
    for i in range(segments):
        j = (i + 1) % segments
        faces.append((base + i * 2, base + j * 2, base + j * 2 + 1, base + i * 2 + 1))


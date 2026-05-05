"""Reusable procedural-scene helpers for VibeGeometry examples."""

from .batching import append_box_parts, append_cylindrical_ring_band
from .blender import (
    add_box,
    add_curve_polyline,
    add_cylinder_between,
    add_material,
    add_mesh_parts,
    add_multi_polyline_curve,
    aim_camera,
    clear_scene,
)
from .coordinates import CylinderFrame
from .fields import fbm_2d, hash01, smoothstep, value_noise_2d
from .verify import assert_objects_exist, assert_render_artifacts, assert_scene_density

__all__ = [
    "CylinderFrame",
    "add_box",
    "add_curve_polyline",
    "add_cylinder_between",
    "add_material",
    "add_mesh_parts",
    "add_multi_polyline_curve",
    "aim_camera",
    "append_box_parts",
    "append_cylindrical_ring_band",
    "assert_objects_exist",
    "assert_render_artifacts",
    "assert_scene_density",
    "clear_scene",
    "fbm_2d",
    "hash01",
    "smoothstep",
    "value_noise_2d",
]

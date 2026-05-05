"""Verification helpers for generated Blender scenes."""

from __future__ import annotations

from pathlib import Path


def assert_objects_exist(bpy_module, names):
    missing = sorted(name for name in names if name not in bpy_module.data.objects)
    if missing:
        raise AssertionError(f"Missing required objects: {missing}")


def assert_render_artifacts(paths, min_size=10_000):
    for path in paths:
        artifact = Path(path)
        if not artifact.exists():
            raise AssertionError(f"Missing generated artifact {artifact}")
        if artifact.stat().st_size <= min_size:
            raise AssertionError(f"Generated artifact is suspiciously small: {artifact}")


def assert_scene_density(bpy_module, min_geometry_objects):
    mesh_objects = [obj for obj in bpy_module.data.objects if obj.type in {"MESH", "CURVE", "FONT"}]
    if len(mesh_objects) < min_geometry_objects:
        raise AssertionError(f"Expected a populated scene, found {len(mesh_objects)} geometry/text objects")
    return mesh_objects

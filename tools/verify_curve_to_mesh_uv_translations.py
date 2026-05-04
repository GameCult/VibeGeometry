"""Compare small CurveToMeshUV utility groups against Geometry Script translations."""

from __future__ import annotations

import importlib.util
import json
import math
import sys
from pathlib import Path

import bpy


ROOT = Path(__file__).resolve().parents[1]
TRANSLATION = ROOT / "examples" / "geometry_script" / "quellenform_curve_to_mesh_uv.py"
AUTO_SMOOTH_CASE = {"Angle": 0.75}


def _load_translation() -> None:
    spec = importlib.util.spec_from_file_location("vg_curve_to_mesh_uv_translation", TRANSLATION)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load translation script: {TRANSLATION}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)


def _socket_by_name(sockets, name: str):
    for socket in sockets:
        if socket.name == name:
            return socket
    raise KeyError(name)


def _new_geometry_group(name: str) -> bpy.types.GeometryNodeTree:
    if name in bpy.data.node_groups:
        bpy.data.node_groups.remove(bpy.data.node_groups[name])
    group = bpy.data.node_groups.new(name, "GeometryNodeTree")
    group.is_modifier = True
    group.interface.new_socket(name="Geometry", in_out="INPUT", socket_type="NodeSocketGeometry")
    group.interface.new_socket(name="Geometry", in_out="OUTPUT", socket_type="NodeSocketGeometry")
    return group


def _build_auto_smooth_wrapper(name: str, source_group: bpy.types.GeometryNodeTree, inputs: dict[str, object]):
    wrapper = _new_geometry_group(name)
    nodes = wrapper.nodes
    links = wrapper.links

    cube = nodes.new("GeometryNodeMeshCube")
    _socket_by_name(cube.inputs, "Size").default_value = (1.0, 1.0, 1.0)

    group_node = nodes.new("GeometryNodeGroup")
    group_node.node_tree = source_group
    links.new(_socket_by_name(cube.outputs, "Mesh"), _socket_by_name(group_node.inputs, "Geometry"))
    for socket in group_node.inputs:
        if socket.name in inputs:
            socket.default_value = inputs[socket.name]

    group_output = nodes.new("NodeGroupOutput")
    links.new(_socket_by_name(group_node.outputs, "Geometry"), _socket_by_name(group_output.inputs, "Geometry"))
    return wrapper


def _evaluated_mesh_summary(group: bpy.types.GeometryNodeTree):
    mesh = bpy.data.meshes.new(group.name + " Input Mesh")
    obj = bpy.data.objects.new(group.name + " Object", mesh)
    bpy.context.collection.objects.link(obj)
    modifier = obj.modifiers.new(group.name + " Modifier", "NODES")
    modifier.node_group = group
    depsgraph = bpy.context.evaluated_depsgraph_get()
    evaluated = obj.evaluated_get(depsgraph)
    evaluated_mesh = evaluated.to_mesh()
    try:
        vertices = [tuple(vertex.co) for vertex in evaluated_mesh.vertices]
        polygons = [polygon.use_smooth for polygon in evaluated_mesh.polygons]
        return {
            "vertices": vertices,
            "polygon_smooth": polygons,
        }
    finally:
        evaluated.to_mesh_clear()


def main() -> int:
    _load_translation()
    source = _evaluated_mesh_summary(
        _build_auto_smooth_wrapper("VG Verify Source Auto Smooth", bpy.data.node_groups["Auto Smooth"], AUTO_SMOOTH_CASE)
    )
    translated = _evaluated_mesh_summary(
        _build_auto_smooth_wrapper("VG Verify Translated Auto Smooth", bpy.data.node_groups["VG Auto Smooth"], AUTO_SMOOTH_CASE)
    )
    max_delta = max(
        (math.dist(a, b) for a, b in zip(sorted(source["vertices"]), sorted(translated["vertices"]))),
        default=0.0,
    )
    result = {
        "case": "auto_smooth_cube",
        "source_vertex_count": len(source["vertices"]),
        "translated_vertex_count": len(translated["vertices"]),
        "max_sorted_vertex_delta": max_delta,
        "source_smooth_faces": sum(source["polygon_smooth"]),
        "translated_smooth_faces": sum(translated["polygon_smooth"]),
    }
    result["ok"] = (
        result["source_vertex_count"] == result["translated_vertex_count"]
        and max_delta <= 1e-6
        and source["polygon_smooth"] == translated["polygon_smooth"]
    )
    payload = {"ok": result["ok"], "results": [result]}
    print("VG_CURVE_TO_MESH_UV_TRANSLATION_BEHAVIOR " + json.dumps(payload, sort_keys=True))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

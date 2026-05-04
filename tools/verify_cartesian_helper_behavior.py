"""Compare source and Geometry Script cartesian helper behavior.

Run with Blender from the repository root:

    blender --background experiments/source-blends/shriinivas-cartesian.blend --python tools/verify_cartesian_helper_behavior.py
"""

from __future__ import annotations

import importlib.util
import json
import math
import sys
from pathlib import Path

import bpy


ROOT = Path(__file__).resolve().parents[1]
TRANSLATION = ROOT / "examples" / "geometry_script" / "shriinivas_cartesian_helper.py"

TEST_INPUTS = {
    "Count": 25,
    "Start": (-0.45, 0.0, 0.0),
    "End": (0.45, 0.0, 0.0),
    "r": 0.6,
    "Value": 1.25,
}


def _load_translation() -> None:
    spec = importlib.util.spec_from_file_location("vg_cartesian_helper_translation", TRANSLATION)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load translation script: {TRANSLATION}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)


def _new_geometry_group(name: str) -> bpy.types.GeometryNodeTree:
    if name in bpy.data.node_groups:
        bpy.data.node_groups.remove(bpy.data.node_groups[name])
    group = bpy.data.node_groups.new(name, "GeometryNodeTree")
    group.is_modifier = True
    group.interface.new_socket(name="Geometry", in_out="INPUT", socket_type="NodeSocketGeometry")
    group.interface.new_socket(name="Geometry", in_out="OUTPUT", socket_type="NodeSocketGeometry")
    return group


def _socket_by_name(sockets, name: str):
    for socket in sockets:
        if socket.name == name:
            return socket
    raise KeyError(name)


def _set_input_defaults(group_node, values: dict[str, object]) -> None:
    for name, value in values.items():
        socket = _socket_by_name(group_node.inputs, name)
        socket.default_value = value


def _build_wrapper(name: str, helper_group: bpy.types.GeometryNodeTree) -> bpy.types.GeometryNodeTree:
    wrapper = _new_geometry_group(name)
    nodes = wrapper.nodes
    links = wrapper.links

    group_input = nodes.new("NodeGroupInput")
    group_input.location = (-900, 0)
    group_output = nodes.new("NodeGroupOutput")
    group_output.location = (500, 0)

    helper = nodes.new("GeometryNodeGroup")
    helper.node_tree = helper_group
    helper.location = (-700, 0)
    _set_input_defaults(helper, TEST_INPUTS)

    set_position = nodes.new("GeometryNodeSetPosition")
    set_position.location = (-350, 0)
    profile = nodes.new("GeometryNodeCurvePrimitiveCircle")
    profile.location = (-350, -220)
    _socket_by_name(profile.inputs, "Resolution").default_value = 8
    _socket_by_name(profile.inputs, "Radius").default_value = 0.01

    curve_to_mesh = nodes.new("GeometryNodeCurveToMesh")
    curve_to_mesh.location = (80, 0)

    links.new(_socket_by_name(helper.outputs, "Curve"), _socket_by_name(set_position.inputs, "Geometry"))
    links.new(_socket_by_name(helper.outputs, "Vector"), _socket_by_name(set_position.inputs, "Position"))
    links.new(_socket_by_name(set_position.outputs, "Geometry"), _socket_by_name(curve_to_mesh.inputs, "Curve"))
    links.new(_socket_by_name(profile.outputs, "Curve"), _socket_by_name(curve_to_mesh.inputs, "Profile Curve"))
    links.new(_socket_by_name(curve_to_mesh.outputs, "Mesh"), _socket_by_name(group_output.inputs, "Geometry"))
    return wrapper


def _evaluated_vertices(group: bpy.types.GeometryNodeTree) -> list[tuple[float, float, float]]:
    mesh = bpy.data.meshes.new(group.name + " Input Mesh")
    obj = bpy.data.objects.new(group.name + " Object", mesh)
    bpy.context.collection.objects.link(obj)
    modifier = obj.modifiers.new(group.name + " Modifier", "NODES")
    modifier.node_group = group

    depsgraph = bpy.context.evaluated_depsgraph_get()
    evaluated = obj.evaluated_get(depsgraph)
    evaluated_mesh = evaluated.to_mesh()
    try:
        return [tuple(vertex.co) for vertex in evaluated_mesh.vertices]
    finally:
        evaluated.to_mesh_clear()


def _bounds(vertices: list[tuple[float, float, float]]) -> dict[str, list[float]]:
    return {
        "min": [min(vertex[i] for vertex in vertices) for i in range(3)],
        "max": [max(vertex[i] for vertex in vertices) for i in range(3)],
    }


def _compare(source_vertices, translated_vertices) -> dict[str, object]:
    if len(source_vertices) != len(translated_vertices):
        return {
            "ok": False,
            "reason": "vertex_count_mismatch",
            "source_vertex_count": len(source_vertices),
            "translated_vertex_count": len(translated_vertices),
        }
    max_delta = 0.0
    total_delta = 0.0
    for source, translated in zip(source_vertices, translated_vertices):
        delta = math.dist(source, translated)
        max_delta = max(max_delta, delta)
        total_delta += delta
    return {
        "ok": max_delta <= 1e-6,
        "source_vertex_count": len(source_vertices),
        "translated_vertex_count": len(translated_vertices),
        "max_vertex_delta": max_delta,
        "mean_vertex_delta": total_delta / len(source_vertices) if source_vertices else 0.0,
        "source_bounds": _bounds(source_vertices),
        "translated_bounds": _bounds(translated_vertices),
    }


def main() -> int:
    source_helper = bpy.data.node_groups.get("NodeGroup.001")
    if source_helper is None:
        raise RuntimeError("Source helper node group 'NodeGroup.001' was not found.")

    _load_translation()
    translated_helper = bpy.data.node_groups.get("VG Cartesian Helper")
    if translated_helper is None:
        raise RuntimeError("Translated helper node group 'VG Cartesian Helper' was not found.")

    source_wrapper = _build_wrapper("VG Verify Source Cartesian Helper", source_helper)
    translated_wrapper = _build_wrapper("VG Verify Translated Cartesian Helper", translated_helper)
    result = _compare(_evaluated_vertices(source_wrapper), _evaluated_vertices(translated_wrapper))
    print("VG_CARTESIAN_HELPER_BEHAVIOR " + json.dumps(result, sort_keys=True))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

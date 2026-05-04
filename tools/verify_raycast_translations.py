"""Compare compact raycast minigame groups against Geometry Script translations."""

from __future__ import annotations

import importlib.util
import json
import math
import sys
from pathlib import Path

import bpy


ROOT = Path(__file__).resolve().parents[1]
TRANSLATION = ROOT / "examples" / "geometry_script" / "blender_raycast_minigame.py"


def _load_translation() -> None:
    spec = importlib.util.spec_from_file_location("vg_raycast_translation", TRANSLATION)
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


def _socket_key(name: str) -> str:
    return name.lower().replace(" ", "").replace("_", "")


def _set_inputs(group_node: bpy.types.GeometryNode, inputs: dict[str, object]) -> None:
    normalized = {_socket_key(key): value for key, value in inputs.items()}
    for socket in group_node.inputs:
        key = _socket_key(socket.name)
        if key in normalized:
            socket.default_value = normalized[key]


def _new_geometry_group(name: str) -> bpy.types.GeometryNodeTree:
    if name in bpy.data.node_groups:
        bpy.data.node_groups.remove(bpy.data.node_groups[name])
    group = bpy.data.node_groups.new(name, "GeometryNodeTree")
    group.is_modifier = True
    group.interface.new_socket(name="Geometry", in_out="INPUT", socket_type="NodeSocketGeometry")
    group.interface.new_socket(name="Geometry", in_out="OUTPUT", socket_type="NodeSocketGeometry")
    return group


def _points_to_vertices(nodes, links, curve_socket):
    points = nodes.new("GeometryNodeCurveToPoints")
    points.mode = "EVALUATED"
    links.new(curve_socket, _socket_by_name(points.inputs, "Curve"))
    vertices = nodes.new("GeometryNodePointsToVertices")
    links.new(_socket_by_name(points.outputs, "Points"), _socket_by_name(vertices.inputs, "Points"))
    return _socket_by_name(vertices.outputs, "Mesh")


def _build_initial_direction_wrapper(name: str, source_group: bpy.types.GeometryNodeTree):
    wrapper = _new_geometry_group(name)
    nodes = wrapper.nodes
    links = wrapper.links
    line = nodes.new("GeometryNodeMeshLine")
    line.mode = "OFFSET"
    line.count_mode = "TOTAL"
    _socket_by_name(line.inputs, "Count").default_value = 1

    group_node = nodes.new("GeometryNodeGroup")
    group_node.node_tree = source_group
    _set_inputs(group_node, {"Rotation": (0.0, 0.0, 0.7853981852531433)})

    set_position = nodes.new("GeometryNodeSetPosition")
    links.new(_socket_by_name(line.outputs, "Mesh"), _socket_by_name(set_position.inputs, "Geometry"))
    links.new(_socket_by_name(group_node.outputs, "Vector"), _socket_by_name(set_position.inputs, "Position"))
    group_output = nodes.new("NodeGroupOutput")
    links.new(_socket_by_name(set_position.outputs, "Geometry"), _socket_by_name(group_output.inputs, "Geometry"))
    return wrapper


def _build_line_wrapper(name: str, source_group: bpy.types.GeometryNodeTree):
    wrapper = _new_geometry_group(name)
    nodes = wrapper.nodes
    links = wrapper.links
    group_node = nodes.new("GeometryNodeGroup")
    group_node.node_tree = source_group
    _set_inputs(group_node, {"Start Pos": (0.25, -0.125, 0.0), "Line Size": 5})
    mesh_socket = _points_to_vertices(nodes, links, _socket_by_name(group_node.outputs, "Line"))
    group_output = nodes.new("NodeGroupOutput")
    links.new(mesh_socket, _socket_by_name(group_output.inputs, "Geometry"))
    return wrapper


def _build_cast_rays_wrapper(name: str, source_group: bpy.types.GeometryNodeTree, target=None):
    wrapper = _new_geometry_group(name)
    nodes = wrapper.nodes
    links = wrapper.links

    line_group = nodes.new("GeometryNodeGroup")
    line_group.node_tree = bpy.data.node_groups["Line to be Casted"]
    _set_inputs(line_group, {"Start Pos": (0.0, 0.0, 0.0), "Line Size": 4})

    group_node = nodes.new("GeometryNodeGroup")
    group_node.node_tree = source_group
    _set_inputs(
        group_node,
        {
            "Ray Direction": (1.0, 0.25, 0.0),
            "Traveled Distance": 0.0,
            "Hit Index": 1,
            "Target": target,
        },
    )
    links.new(_socket_by_name(line_group.outputs, "Line"), _socket_by_name(group_node.inputs, "Line"))
    mesh_socket = _points_to_vertices(nodes, links, _socket_by_name(group_node.outputs, "Line"))

    group_output = nodes.new("NodeGroupOutput")
    links.new(mesh_socket, _socket_by_name(group_output.inputs, "Geometry"))
    return wrapper


def _evaluated_vertices(group: bpy.types.GeometryNodeTree):
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


def _compare(case: str, source_group, translated_group, source_builder, translated_builder=None):
    translated_builder = translated_builder or source_builder
    source = _evaluated_vertices(source_builder(f"VG Verify Source {case}", source_group))
    translated = _evaluated_vertices(translated_builder(f"VG Verify Translated {case}", translated_group))
    max_delta = (
        max((math.dist(a, b) for a, b in zip(sorted(source), sorted(translated))), default=0.0)
        if len(source) == len(translated)
        else math.inf
    )
    return {
        "case": case,
        "source_vertex_count": len(source),
        "translated_vertex_count": len(translated),
        "max_sorted_vertex_delta": max_delta,
        "ok": len(source) == len(translated) and max_delta <= 1e-6,
    }


def main() -> int:
    _load_translation()
    target = bpy.data.objects.get("Field and Boundaries")
    results = [
        _compare("initial_direction", bpy.data.node_groups["Initial Direction"], bpy.data.node_groups["VG Initial Direction"], _build_initial_direction_wrapper),
        _compare("line_to_be_casted", bpy.data.node_groups["Line to be Casted"], bpy.data.node_groups["VG Line To Be Casted"], _build_line_wrapper),
        _compare(
            "cast_rays",
            bpy.data.node_groups["Cast Rays"],
            bpy.data.node_groups["VG Cast Rays"],
            lambda name, group: _build_cast_rays_wrapper(name, group),
            lambda name, group: _build_cast_rays_wrapper(name, group, target),
        ),
    ]
    payload = {"ok": all(result["ok"] for result in results), "results": results}
    print("VG_RAYCAST_TRANSLATION_BEHAVIOR " + json.dumps(payload, sort_keys=True))
    return 0 if payload["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

"""Compare selected IRCSS French Houses groups against Geometry Script translations."""

from __future__ import annotations

import importlib.util
import json
import math
import sys
from pathlib import Path

import bpy


ROOT = Path(__file__).resolve().parents[1]
TRANSLATION = ROOT / "examples" / "geometry_script" / "ircss_french_houses.py"
CASE = {
    "Frequency": 12.0,
    "Radius": 1.0,
    "Height": 3.0,
    "HeightRadiusGain": 0.25,
}


def _load_translation() -> None:
    spec = importlib.util.spec_from_file_location("vg_ircss_french_houses_translation", TRANSLATION)
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


def _build_spiral_wrapper(name: str, group: bpy.types.GeometryNodeTree):
    wrapper = _new_geometry_group(name)
    nodes = wrapper.nodes
    links = wrapper.links
    group_node = nodes.new("GeometryNodeGroup")
    group_node.node_tree = group
    _set_inputs(group_node, CASE)

    points = nodes.new("GeometryNodeCurveToPoints")
    points.mode = "EVALUATED"
    links.new(_socket_by_name(group_node.outputs, "Geometry"), _socket_by_name(points.inputs, "Curve"))
    vertices = nodes.new("GeometryNodePointsToVertices")
    links.new(_socket_by_name(points.outputs, "Points"), _socket_by_name(vertices.inputs, "Points"))

    group_output = nodes.new("NodeGroupOutput")
    links.new(_socket_by_name(vertices.outputs, "Mesh"), _socket_by_name(group_output.inputs, "Geometry"))
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


def main() -> int:
    _load_translation()
    source = _evaluated_vertices(_build_spiral_wrapper("VG Verify Source MakeSpiral", bpy.data.node_groups["MakeSpiral"]))
    translated = _evaluated_vertices(
        _build_spiral_wrapper("VG Verify Translated MakeSpiral", bpy.data.node_groups["VG Make Spiral"])
    )
    max_delta = (
        max((math.dist(a, b) for a, b in zip(source, translated)), default=0.0)
        if len(source) == len(translated)
        else math.inf
    )
    result = {
        "case": "make_spiral_curve_points",
        "source_vertex_count": len(source),
        "translated_vertex_count": len(translated),
        "max_ordered_vertex_delta": max_delta,
    }
    result["ok"] = len(source) == len(translated) and max_delta <= 1e-6
    payload = {"ok": result["ok"], "results": [result]}
    print("VG_IRCSS_FRENCH_HOUSES_TRANSLATION_BEHAVIOR " + json.dumps(payload, sort_keys=True))
    return 0 if payload["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

"""Compare compact index_of_nearest demo helpers against Geometry Script translations."""

from __future__ import annotations

import importlib.util
import json
import math
import sys
from pathlib import Path

import bpy


ROOT = Path(__file__).resolve().parents[1]
TRANSLATION = ROOT / "examples" / "geometry_script" / "blender_index_of_nearest.py"


def _load_translation() -> None:
    spec = importlib.util.spec_from_file_location("vg_index_of_nearest_translation", TRANSLATION)
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


def _add_line(nodes, *, count: int = 6, offset=(0.024000000208616257, 0.017999999225139618, 0.0)):
    line = nodes.new("GeometryNodeMeshLine")
    line.mode = "OFFSET"
    line.count_mode = "TOTAL"
    _socket_by_name(line.inputs, "Count").default_value = count
    _socket_by_name(line.inputs, "Offset").default_value = offset
    return line


def _build_geometry_wrapper(name: str, source_group: bpy.types.GeometryNodeTree, inputs: dict[str, object] | None = None):
    wrapper = _new_geometry_group(name)
    nodes = wrapper.nodes
    links = wrapper.links
    line = _add_line(nodes)

    group_node = nodes.new("GeometryNodeGroup")
    group_node.node_tree = source_group
    links.new(_socket_by_name(line.outputs, "Mesh"), _socket_by_name(group_node.inputs, "Geometry"))
    _set_inputs(group_node, inputs or {})

    group_output = nodes.new("NodeGroupOutput")
    links.new(_socket_by_name(group_node.outputs, "Geometry"), _socket_by_name(group_output.inputs, "Geometry"))
    return wrapper


def _build_velocity_wrapper(name: str, source_group: bpy.types.GeometryNodeTree):
    wrapper = _new_geometry_group(name)
    nodes = wrapper.nodes
    links = wrapper.links
    line = _add_line(nodes, count=4, offset=(0.020000000298023224, 0.0, 0.0))

    group_node = nodes.new("GeometryNodeGroup")
    group_node.node_tree = source_group
    _set_inputs(
        group_node,
        {
            "Current Velocity": (0.0020000000949949026, 0.004000000189989805, 0.0),
            "Last Position": (0.009999999776482582, 0.0, 0.0),
        },
    )

    set_position = nodes.new("GeometryNodeSetPosition")
    links.new(_socket_by_name(line.outputs, "Mesh"), _socket_by_name(set_position.inputs, "Geometry"))
    links.new(_socket_by_name(group_node.outputs, "velocity"), _socket_by_name(set_position.inputs, "Position"))

    group_output = nodes.new("NodeGroupOutput")
    links.new(_socket_by_name(set_position.outputs, "Geometry"), _socket_by_name(group_output.inputs, "Geometry"))
    return wrapper


def _build_collision_wrapper(name: str, source_group: bpy.types.GeometryNodeTree):
    wrapper = _new_geometry_group(name)
    nodes = wrapper.nodes
    links = wrapper.links
    line = _add_line(nodes, count=5, offset=(0.003000000026077032, 0.0, 0.0))
    points = nodes.new("GeometryNodeMeshToPoints")
    points.mode = "VERTICES"
    links.new(_socket_by_name(line.outputs, "Mesh"), _socket_by_name(points.inputs, "Mesh"))
    radius = nodes.new("GeometryNodeSetPointRadius")
    _socket_by_name(radius.inputs, "Radius").default_value = 0.02500000037252903
    links.new(_socket_by_name(points.outputs, "Points"), _socket_by_name(radius.inputs, "Points"))

    group_node = nodes.new("GeometryNodeGroup")
    group_node.node_tree = source_group
    links.new(_socket_by_name(radius.outputs, "Points"), _socket_by_name(group_node.inputs, "Geometry"))

    vertices = nodes.new("GeometryNodePointsToVertices")
    links.new(_socket_by_name(group_node.outputs, "Geometry"), _socket_by_name(vertices.inputs, "Points"))

    group_output = nodes.new("NodeGroupOutput")
    links.new(_socket_by_name(vertices.outputs, "Mesh"), _socket_by_name(group_output.inputs, "Geometry"))
    return wrapper


def _build_collider_wrapper(name: str, source_group: bpy.types.GeometryNodeTree, inputs: dict[str, object] | None = None):
    return _build_geometry_wrapper(name, source_group, inputs)


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


def _compare(case: str, source_group, translated_group, builder, source_inputs=None, translated_inputs=None):
    source = _evaluated_vertices(builder(f"VG Verify Source {case}", source_group, source_inputs or {}) if builder != _build_velocity_wrapper and builder != _build_collision_wrapper else builder(f"VG Verify Source {case}", source_group))
    translated = _evaluated_vertices(
        builder(f"VG Verify Translated {case}", translated_group, translated_inputs or {})
        if builder != _build_velocity_wrapper and builder != _build_collision_wrapper
        else builder(f"VG Verify Translated {case}", translated_group)
    )
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
    collider = bpy.data.objects.get("Icosphere")
    results = [
        _compare(
            "boundary_step",
            bpy.data.node_groups["boundary_step"],
            bpy.data.node_groups["VG Boundary Step"],
            _build_geometry_wrapper,
            {"Vector": (0.0, 0.0, 0.0), "B": 0.05000000074505806},
            {"Vector": (0.0, 0.0, 0.0), "B": 0.05000000074505806},
        ),
        _compare("update_velocity", bpy.data.node_groups["update_velocity"], bpy.data.node_groups["VG Update Velocity"], _build_velocity_wrapper),
        _compare("collision_step", bpy.data.node_groups["collision_step"], bpy.data.node_groups["VG Collision Step"], _build_collision_wrapper),
        _compare(
            "collider_step",
            bpy.data.node_groups["collider_step"],
            bpy.data.node_groups["VG Collider Step"],
            _build_collider_wrapper,
            {},
            {"Collider": collider},
        ),
    ]
    payload = {"ok": all(result["ok"] for result in results), "results": results}
    print("VG_INDEX_OF_NEAREST_TRANSLATION_BEHAVIOR " + json.dumps(payload, sort_keys=True))
    return 0 if payload["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

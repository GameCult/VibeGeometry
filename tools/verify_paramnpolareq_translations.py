"""Compare Shriinivas param/polar equation groups against Geometry Script translations."""

from __future__ import annotations

import importlib.util
import json
import math
import sys
from pathlib import Path

import bpy


ROOT = Path(__file__).resolve().parents[1]
TRANSLATION = ROOT / "examples" / "geometry_script" / "shriinivas_paramnpolareq.py"

SCALAR_CASE = {"a": 0.8, "b": 0.35, "t": 1.25, "theta": 1.25}
ARCHIMEDES_CASE = {"Resolution": 64, "No of Rounds": 2.5, "a": 0.25, "b": 0.15}
EPICYCLOID_CASE = {"Resolution": 80, "maxT": 12.0, "a": 0.8, "b": 0.3}
ROOT_SPIRAL_CASE = {"a": 0.2, "Round Count": 4.0, "Resolution": 96.0}
PARAM_CURVE_CASE = {
    "Curve Type": 3,
    "a": 0.8,
    "b": 0.5,
    "c": 1.0,
    "z": 0.125,
    "maxT": 12.0,
    "Resolution": 64.0,
    "showlabel": False,
    "thickness": 0.01,
}


def _load_translation() -> None:
    spec = importlib.util.spec_from_file_location("vg_paramnpolareq_translation", TRANSLATION)
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


def _normalized_key(name: str) -> str:
    return name.lower().replace(" ", "")


def _new_geometry_group(name: str) -> bpy.types.GeometryNodeTree:
    if name in bpy.data.node_groups:
        bpy.data.node_groups.remove(bpy.data.node_groups[name])
    group = bpy.data.node_groups.new(name, "GeometryNodeTree")
    group.is_modifier = True
    group.interface.new_socket(name="Geometry", in_out="INPUT", socket_type="NodeSocketGeometry")
    group.interface.new_socket(name="Geometry", in_out="OUTPUT", socket_type="NodeSocketGeometry")
    return group


def _build_scalar_position_wrapper(name: str, source_group: bpy.types.GeometryNodeTree, inputs: dict[str, object], output: str):
    wrapper = _new_geometry_group(name)
    nodes = wrapper.nodes
    links = wrapper.links
    group_node = nodes.new("GeometryNodeGroup")
    group_node.node_tree = source_group
    lower_inputs = {key.lower(): value for key, value in inputs.items()}
    normalized_inputs = {_normalized_key(key): value for key, value in inputs.items()}
    for socket in group_node.inputs:
        if socket.name in inputs:
            socket.default_value = inputs[socket.name]
        elif socket.name.lower() in lower_inputs:
            socket.default_value = lower_inputs[socket.name.lower()]
        elif _normalized_key(socket.name) in normalized_inputs:
            socket.default_value = normalized_inputs[_normalized_key(socket.name)]

    line = nodes.new("GeometryNodeMeshLine")
    line.mode = "OFFSET"
    line.count_mode = "TOTAL"
    _socket_by_name(line.inputs, "Count").default_value = 1
    _socket_by_name(line.inputs, "Offset").default_value = (1.0, 0.0, 0.0)

    vector = nodes.new("ShaderNodeCombineXYZ")
    links.new(_socket_by_name(group_node.outputs, output), _socket_by_name(vector.inputs, "X"))

    set_position_node = nodes.new("GeometryNodeSetPosition")
    links.new(_socket_by_name(line.outputs, "Mesh"), _socket_by_name(set_position_node.inputs, "Geometry"))
    links.new(_socket_by_name(vector.outputs, "Vector"), _socket_by_name(set_position_node.inputs, "Position"))

    group_output = nodes.new("NodeGroupOutput")
    links.new(_socket_by_name(set_position_node.outputs, "Geometry"), _socket_by_name(group_output.inputs, "Geometry"))
    return wrapper


def _build_xy_position_wrapper(name: str, source_group: bpy.types.GeometryNodeTree, inputs: dict[str, object]):
    wrapper = _new_geometry_group(name)
    nodes = wrapper.nodes
    links = wrapper.links
    group_node = nodes.new("GeometryNodeGroup")
    group_node.node_tree = source_group
    lower_inputs = {key.lower(): value for key, value in inputs.items()}
    normalized_inputs = {_normalized_key(key): value for key, value in inputs.items()}
    for socket in group_node.inputs:
        if socket.name in inputs:
            socket.default_value = inputs[socket.name]
        elif socket.name.lower() in lower_inputs:
            socket.default_value = lower_inputs[socket.name.lower()]
        elif _normalized_key(socket.name) in normalized_inputs:
            socket.default_value = normalized_inputs[_normalized_key(socket.name)]

    line = nodes.new("GeometryNodeMeshLine")
    line.mode = "OFFSET"
    line.count_mode = "TOTAL"
    _socket_by_name(line.inputs, "Count").default_value = 1
    _socket_by_name(line.inputs, "Offset").default_value = (1.0, 0.0, 0.0)

    vector = nodes.new("ShaderNodeCombineXYZ")
    links.new(_socket_by_name(group_node.outputs, "x"), _socket_by_name(vector.inputs, "X"))
    links.new(_socket_by_name(group_node.outputs, "y"), _socket_by_name(vector.inputs, "Y"))

    set_position_node = nodes.new("GeometryNodeSetPosition")
    links.new(_socket_by_name(line.outputs, "Mesh"), _socket_by_name(set_position_node.inputs, "Geometry"))
    links.new(_socket_by_name(vector.outputs, "Vector"), _socket_by_name(set_position_node.inputs, "Position"))

    group_output = nodes.new("NodeGroupOutput")
    links.new(_socket_by_name(set_position_node.outputs, "Geometry"), _socket_by_name(group_output.inputs, "Geometry"))
    return wrapper


def _build_geometry_wrapper(name: str, source_group: bpy.types.GeometryNodeTree, inputs: dict[str, object]):
    wrapper = _new_geometry_group(name)
    nodes = wrapper.nodes
    links = wrapper.links
    group_node = nodes.new("GeometryNodeGroup")
    group_node.node_tree = source_group
    lower_inputs = {key.lower(): value for key, value in inputs.items()}
    normalized_inputs = {_normalized_key(key): value for key, value in inputs.items()}
    for socket in group_node.inputs:
        if socket.name in inputs:
            socket.default_value = inputs[socket.name]
        elif socket.name.lower() in lower_inputs:
            socket.default_value = lower_inputs[socket.name.lower()]
        elif _normalized_key(socket.name) in normalized_inputs:
            socket.default_value = normalized_inputs[_normalized_key(socket.name)]
    group_output = nodes.new("NodeGroupOutput")
    links.new(_socket_by_name(group_node.outputs, "Geometry"), _socket_by_name(group_output.inputs, "Geometry"))
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


def _compare_vertices(case: str, source_group: str, translated_group: str, inputs: dict[str, object]):
    source_vertices = _evaluated_vertices(
        _build_geometry_wrapper(f"VG Verify Source {case}", bpy.data.node_groups[source_group], inputs)
    )
    translated_vertices = _evaluated_vertices(
        _build_geometry_wrapper(f"VG Verify Translated {case}", bpy.data.node_groups[translated_group], inputs)
    )
    max_delta = max(
        (math.dist(a, b) for a, b in zip(sorted(source_vertices), sorted(translated_vertices))),
        default=0.0,
    )
    return {
        "case": case,
        "source_vertex_count": len(source_vertices),
        "translated_vertex_count": len(translated_vertices),
        "max_sorted_vertex_delta": max_delta,
        "ok": len(source_vertices) == len(translated_vertices) and max_delta <= 1e-6,
    }


def main() -> int:
    _load_translation()
    results = []
    scalar_pairs = [
        ("epicycloid_x", "NodeGroup", "VG Param Epicycloid X", "x", "x", {"a": SCALAR_CASE["a"], "b": SCALAR_CASE["b"], "t": SCALAR_CASE["t"]}),
        ("epicycloid_y", "NodeGroup.001", "VG Param Epicycloid Y", "x", "y", {"a": SCALAR_CASE["a"], "b": SCALAR_CASE["b"], "t": SCALAR_CASE["t"]}),
        ("polar_x", "NodeGroup.002", "VG Polar Spiral X", "x", "x", {"a": SCALAR_CASE["a"], "b": SCALAR_CASE["b"], "theta": SCALAR_CASE["theta"]}),
        ("polar_y", "NodeGroup.003", "VG Polar Spiral Y", "y", "y", {"a": SCALAR_CASE["a"], "b": SCALAR_CASE["b"], "theta": SCALAR_CASE["theta"]}),
    ]
    for case, source_name, translated_name, source_output, translated_output, inputs in scalar_pairs:
        source_vertices = _evaluated_vertices(
            _build_scalar_position_wrapper(f"VG Verify Source {case}", bpy.data.node_groups[source_name], inputs, source_output)
        )
        translated_vertices = _evaluated_vertices(
            _build_scalar_position_wrapper(f"VG Verify Translated {case}", bpy.data.node_groups[translated_name], inputs, translated_output)
        )
        max_delta = max(
            (math.dist(a, b) for a, b in zip(sorted(source_vertices), sorted(translated_vertices))),
            default=0.0,
        )
        results.append(
            {
                "case": case,
                "source_vertex": source_vertices[0] if source_vertices else None,
                "translated_vertex": translated_vertices[0] if translated_vertices else None,
                "max_sorted_vertex_delta": max_delta,
                "ok": len(source_vertices) == len(translated_vertices) and max_delta <= 1e-6,
            }
        )

    results.append(_compare_vertices("archimedes_spiral", "Archimedes Spiral", "VG Archimedes Spiral", ARCHIMEDES_CASE))
    results.append(_compare_vertices("epicycloid", "Epicycloid", "VG Epicycloid", EPICYCLOID_CASE))
    results.append(_compare_vertices("mirrored_root_spiral", "Geometry Nodes Group.002", "VG Mirrored Root Spiral", ROOT_SPIRAL_CASE))
    for curve_type in range(5):
        inputs = {"a": 0.8, "b": 0.35, "c": 1.1, "t": 1.25, "Curve Type": curve_type}
        source_vertices = _evaluated_vertices(
            _build_xy_position_wrapper(f"VG Verify Source Param XY {curve_type}", bpy.data.node_groups["getxy.001"], inputs)
        )
        translated_vertices = _evaluated_vertices(
            _build_xy_position_wrapper(f"VG Verify Translated Param XY {curve_type}", bpy.data.node_groups["VG Param XY"], inputs)
        )
        max_delta = max(
            (math.dist(a, b) for a, b in zip(sorted(source_vertices), sorted(translated_vertices))),
            default=0.0,
        )
        results.append(
            {
                "case": {"param_xy_curve_type": curve_type},
                "source_vertex": source_vertices[0] if source_vertices else None,
                "translated_vertex": translated_vertices[0] if translated_vertices else None,
                "max_sorted_vertex_delta": max_delta,
                "ok": len(source_vertices) == len(translated_vertices) and max_delta <= 1e-6,
            }
        )
    results.append(_compare_vertices("param_curve_wrapper", "Geometry Nodes Group", "VG Param Curve", PARAM_CURVE_CASE))

    ok = all(result["ok"] for result in results)
    print("VG_PARAMNPOLAREQ_TRANSLATION_BEHAVIOR " + json.dumps({"ok": ok, "results": results}, sort_keys=True))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())

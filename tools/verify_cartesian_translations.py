"""Compare Shriinivas cartesian source graphs against Geometry Script translations.

Run with Blender from the repository root:

    blender --background experiments/source-blends/shriinivas-cartesian.blend --python tools/verify_cartesian_translations.py
"""

from __future__ import annotations

import importlib.util
import json
import math
import sys
from pathlib import Path
from typing import Any

import bpy


ROOT = Path(__file__).resolve().parents[1]
TRANSLATION = ROOT / "examples" / "geometry_script" / "shriinivas_cartesian_helper.py"


HELPER_INPUTS = {
    "Count": 25,
    "Start": (-0.45, 0.0, 0.0),
    "End": (0.45, 0.0, 0.0),
    "r": 0.6,
    "Value": 1.25,
}

GRAPH_CASES = [
    {
        "case": "line",
        "source": "Geometry Nodes Line",
        "translated": "VG Cartesian Line",
        "inputs": {
            "Resolution": 17,
            "Length": 1.15,
            "m": -0.35,
            "Value": 0.25,
            "Thickness": 0.035,
        },
    },
    {
        "case": "parabola",
        "source": "Geometry Nodes Parabola",
        "translated": "VG Cartesian Parabola",
        "inputs": {
            "Resolution": 31,
            "Sample Resolution": 31,
            "Start": -0.7,
            "End": 0.8,
            "a": 0.55,
            "b": -0.25,
            "c": 0.1,
            "Thickness": 0.025,
        },
    },
    {
        "case": "circle",
        "source": "Geometry Nodes Circle",
        "translated": "VG Cartesian Circle",
        "inputs": {
            "Resolution": 37,
            "r": 0.65,
            "Thickness": 0.02,
        },
    },
]


def _load_translation() -> None:
    spec = importlib.util.spec_from_file_location("vg_cartesian_translation", TRANSLATION)
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


def _socket_by_name(sockets: Any, name: str):
    for socket in sockets:
        if socket.name == name:
            return socket
    raise KeyError(name)


def _set_inputs(group_node: bpy.types.GeometryNode, values: dict[str, object]) -> None:
    for socket in group_node.inputs:
        if socket.name not in values:
            continue
        value = values[socket.name]
        if isinstance(value, list):
            socket.default_value = value.pop(0)
        else:
            socket.default_value = value


def _build_helper_eval_wrapper(name: str, helper_group: bpy.types.GeometryNodeTree) -> bpy.types.GeometryNodeTree:
    wrapper = _new_geometry_group(name)
    nodes = wrapper.nodes
    links = wrapper.links

    group_output = nodes.new("NodeGroupOutput")
    helper = nodes.new("GeometryNodeGroup")
    helper.node_tree = helper_group
    _set_inputs(helper, HELPER_INPUTS)

    set_position = nodes.new("GeometryNodeSetPosition")
    profile = nodes.new("GeometryNodeCurvePrimitiveCircle")
    _socket_by_name(profile.inputs, "Resolution").default_value = 8
    _socket_by_name(profile.inputs, "Radius").default_value = 0.01
    curve_to_mesh = nodes.new("GeometryNodeCurveToMesh")

    links.new(_socket_by_name(helper.outputs, "Curve"), _socket_by_name(set_position.inputs, "Geometry"))
    links.new(_socket_by_name(helper.outputs, "Vector"), _socket_by_name(set_position.inputs, "Position"))
    links.new(_socket_by_name(set_position.outputs, "Geometry"), _socket_by_name(curve_to_mesh.inputs, "Curve"))
    links.new(_socket_by_name(profile.outputs, "Curve"), _socket_by_name(curve_to_mesh.inputs, "Profile Curve"))
    links.new(_socket_by_name(curve_to_mesh.outputs, "Mesh"), _socket_by_name(group_output.inputs, "Geometry"))
    return wrapper


def _build_group_eval_wrapper(
    name: str,
    graph_group: bpy.types.GeometryNodeTree,
    inputs: dict[str, object],
) -> bpy.types.GeometryNodeTree:
    wrapper = _new_geometry_group(name)
    nodes = wrapper.nodes
    links = wrapper.links

    group_input = nodes.new("NodeGroupInput")
    group_output = nodes.new("NodeGroupOutput")
    graph = nodes.new("GeometryNodeGroup")
    graph.node_tree = graph_group
    _set_inputs(graph, inputs)

    if any(socket.name == "Geometry" for socket in graph.inputs):
        links.new(_socket_by_name(group_input.outputs, "Geometry"), _socket_by_name(graph.inputs, "Geometry"))
    links.new(_socket_by_name(graph.outputs, "Geometry"), _socket_by_name(group_output.inputs, "Geometry"))
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


def _compare(case: str, source_vertices, translated_vertices) -> dict[str, object]:
    if len(source_vertices) != len(translated_vertices):
        return {
            "case": case,
            "ok": False,
            "reason": "vertex_count_mismatch",
            "source_vertex_count": len(source_vertices),
            "translated_vertex_count": len(translated_vertices),
            "source_bounds": _bounds(source_vertices) if source_vertices else None,
            "translated_bounds": _bounds(translated_vertices) if translated_vertices else None,
        }
    max_delta = 0.0
    total_delta = 0.0
    for source, translated in zip(source_vertices, translated_vertices):
        delta = math.dist(source, translated)
        max_delta = max(max_delta, delta)
        total_delta += delta
    sorted_source = sorted(source_vertices)
    sorted_translated = sorted(translated_vertices)
    max_sorted_delta = 0.0
    total_sorted_delta = 0.0
    for source, translated in zip(sorted_source, sorted_translated):
        delta = math.dist(source, translated)
        max_sorted_delta = max(max_sorted_delta, delta)
        total_sorted_delta += delta
    return {
        "case": case,
        "ok": max_delta <= 1e-6 or max_sorted_delta <= 1e-6,
        "source_vertex_count": len(source_vertices),
        "translated_vertex_count": len(translated_vertices),
        "max_vertex_delta": max_delta,
        "mean_vertex_delta": total_delta / len(source_vertices) if source_vertices else 0.0,
        "max_sorted_vertex_delta": max_sorted_delta,
        "mean_sorted_vertex_delta": total_sorted_delta / len(source_vertices) if source_vertices else 0.0,
        "source_bounds": _bounds(source_vertices),
        "translated_bounds": _bounds(translated_vertices),
    }


def main() -> int:
    _load_translation()
    results = []

    source_helper = bpy.data.node_groups.get("NodeGroup.001")
    translated_helper = bpy.data.node_groups.get("VG Cartesian Helper")
    if source_helper is None or translated_helper is None:
        raise RuntimeError("Source or translated helper group was not found.")
    results.append(
        _compare(
            "helper",
            _evaluated_vertices(_build_helper_eval_wrapper("VG Verify Source Helper", source_helper)),
            _evaluated_vertices(_build_helper_eval_wrapper("VG Verify Translated Helper", translated_helper)),
        )
    )

    for case in GRAPH_CASES:
        source = bpy.data.node_groups.get(case["source"])
        translated = bpy.data.node_groups.get(case["translated"])
        if source is None or translated is None:
            raise RuntimeError(f"Missing group for case {case['case']}: {case['source']} / {case['translated']}")
        results.append(
            _compare(
                case["case"],
                _evaluated_vertices(
                    _build_group_eval_wrapper("VG Verify Source " + case["case"], source, case["inputs"])
                ),
                _evaluated_vertices(
                    _build_group_eval_wrapper("VG Verify Translated " + case["case"], translated, case["inputs"])
                ),
            )
        )

    ok = all(result["ok"] for result in results)
    print("VG_CARTESIAN_TRANSLATION_BEHAVIOR " + json.dumps({"ok": ok, "results": results}, sort_keys=True))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())

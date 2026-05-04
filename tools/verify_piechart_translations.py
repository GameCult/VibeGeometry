"""Compare Shriinivas pie chart source graphs against Geometry Script translations."""

from __future__ import annotations

import importlib.util
import json
import math
import sys
from pathlib import Path
from typing import Any

import bpy


ROOT = Path(__file__).resolve().parents[1]
TRANSLATION = ROOT / "examples" / "geometry_script" / "shriinivas_piechart.py"


def _load_translation() -> None:
    spec = importlib.util.spec_from_file_location("vg_piechart_translation", TRANSLATION)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load translation script: {TRANSLATION}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)


def _socket_by_name(sockets: Any, name: str):
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


def _set_inputs(group_node: bpy.types.GeometryNode, values: dict[str, object]) -> None:
    lower_values = {name.lower(): value for name, value in values.items()}
    normalized_values = {name.lower().replace(" ", ""): value for name, value in values.items()}
    for socket in group_node.inputs:
        if socket.name in values:
            socket.default_value = values[socket.name]
        elif socket.name.lower() in lower_values:
            socket.default_value = lower_values[socket.name.lower()]
        elif socket.name.lower().replace(" ", "") in normalized_values:
            socket.default_value = normalized_values[socket.name.lower().replace(" ", "")]


def _build_segment_wrapper(name: str, group: bpy.types.GeometryNodeTree, inputs: dict[str, object]):
    wrapper = _new_geometry_group(name)
    nodes = wrapper.nodes
    links = wrapper.links
    group_node = nodes.new("GeometryNodeGroup")
    group_node.node_tree = group
    _set_inputs(group_node, inputs)
    group_output = nodes.new("NodeGroupOutput")
    links.new(_socket_by_name(group_node.outputs, "Curve"), _socket_by_name(group_output.inputs, "Geometry"))
    return wrapper


def _build_chart_wrapper(name: str, group: bpy.types.GeometryNodeTree, inputs: dict[str, object]):
    wrapper = _new_geometry_group(name)
    nodes = wrapper.nodes
    links = wrapper.links
    group_input = nodes.new("NodeGroupInput")
    group_node = nodes.new("GeometryNodeGroup")
    group_node.node_tree = group
    _set_inputs(group_node, inputs)
    group_output = nodes.new("NodeGroupOutput")
    if any(socket.name == "Geometry" for socket in group_node.inputs):
        links.new(_socket_by_name(group_input.outputs, "Geometry"), _socket_by_name(group_node.inputs, "Geometry"))
    links.new(_socket_by_name(group_node.outputs, "Geometry"), _socket_by_name(group_output.inputs, "Geometry"))
    return wrapper


def _build_extended_segment_wrapper(name: str, group: bpy.types.GeometryNodeTree, inputs: dict[str, object]):
    wrapper = _new_geometry_group(name)
    nodes = wrapper.nodes
    links = wrapper.links
    group_node = nodes.new("GeometryNodeGroup")
    group_node.node_tree = group
    _set_inputs(group_node, inputs)
    group_output = nodes.new("NodeGroupOutput")
    links.new(_socket_by_name(group_node.outputs, "Pie"), _socket_by_name(group_output.inputs, "Geometry"))
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
    for source, translated in zip(sorted(source_vertices), sorted(translated_vertices)):
        max_delta = max(max_delta, math.dist(source, translated))
    return {
        "case": case,
        "ok": max_delta <= 1e-6,
        "source_vertex_count": len(source_vertices),
        "translated_vertex_count": len(translated_vertices),
        "max_sorted_vertex_delta": max_delta,
        "source_bounds": _bounds(source_vertices),
        "translated_bounds": _bounds(translated_vertices),
    }


def main() -> int:
    _load_translation()
    text_material = bpy.data.materials.get("Text Material") or bpy.data.materials.new("Text Material")
    mat1 = bpy.data.materials.get("Material 1") or bpy.data.materials.new("Material 1")
    mat2 = bpy.data.materials.get("Material 2") or bpy.data.materials.new("Material 2")
    mat3 = bpy.data.materials.get("Material 3") or bpy.data.materials.new("Material 3")
    materials = {
        f"Material {index}": bpy.data.materials.get(f"Material {index}") or bpy.data.materials.new(f"Material {index}")
        for index in range(1, 11)
    }

    segment_inputs = {
        "Start": 0.35,
        "Value": 0.8,
        "Total": 2.4,
        "Shift": 0.2,
        "Segment Material": mat1,
        "Text Material": text_material,
    }
    chart_inputs = {
        "A": 0.8,
        "A Shift": 0.2,
        "A Material": mat1,
        "B": 1.1,
        "B Shift": 0.05,
        "B Material": mat2,
        "C": 0.5,
        "C Shift": 0.0,
        "C Material": mat3,
        "Text Material": text_material,
    }
    extended_segment_inputs = {
        "Radius": 1.0,
        "Pie Height": 0.1,
        "Text Height": 0.005,
        "Text Size": 0.08,
        "Text Material": text_material,
        "Text Offset": 0.7,
        "Pie Material": mat1,
        "Include Percentage": True,
        "Value": 20.0,
        "Total": 120.0,
        "Start Angle": 0.25,
        "Shift": 0.15,
        "Text": "Lorem",
    }
    extended_chart_inputs = {
        "Title": "Extended Pie Chart",
        "Title Size": 0.2,
        "Title Material": mat2,
        "Title Offset": 0.18,
        "Segment Count": 10,
        "Radius": 1.0,
        "Pie Height": 0.1,
        "Text Height": 0.005,
        "Text Size": 0.08,
        "Text Material": text_material,
        "Text Offset": 0.7,
        "Include Percentage": True,
        "Value 1": 20.0,
        "Label 1": "Lorem",
        "Shift 1": 0.2,
        "Value 2": 30.0,
        "Label 2": "Ipsum",
        "Shift 2": 0.0,
        "Value 3": 27.0,
        "Label 3": "Dolor",
        "Shift 3": 0.0,
        "Value 4": 25.0,
        "Label 4": "Sit",
        "Shift 4": 0.0,
        "Value 5": 55.0,
        "Label 5": "Amet",
        "Shift 5": 0.0,
        "Value 6": 45.0,
        "Label 6": "Consectetur",
        "Shift 6": 0.0,
        "Value 7": 25.0,
        "Label 7": "Adipiscing",
        "Shift 7": 0.0,
        "Value 8": 35.0,
        "Label 8": "Elit",
        "Shift 8": 0.0,
        "Value 9": 58.0,
        "Label 9": "Sed",
        "Shift 9": 0.0,
        "Value 10": 32.0,
        "Label 10": "Do",
        "Shift 10": 0.0,
    }
    for index in range(1, 11):
        extended_chart_inputs[f"Material {index}"] = materials[f"Material {index}"]

    cases = [
        (
            "segment",
            _build_segment_wrapper("VG Verify Source Pie Segment", bpy.data.node_groups["NodeGroup"], segment_inputs),
            _build_segment_wrapper("VG Verify Translated Pie Segment", bpy.data.node_groups["VG Pie Segment"], segment_inputs),
        ),
        (
            "chart",
            _build_chart_wrapper("VG Verify Source Pie Chart", bpy.data.node_groups["Pie Chart"], chart_inputs),
            _build_chart_wrapper("VG Verify Translated Pie Chart", bpy.data.node_groups["VG Pie Chart"], chart_inputs),
        ),
        (
            "extended_segment",
            _build_extended_segment_wrapper("VG Verify Source Extended Segment", bpy.data.node_groups["getPie.012"], extended_segment_inputs),
            _build_extended_segment_wrapper(
                "VG Verify Translated Extended Segment",
                bpy.data.node_groups["VG Extended Pie Segment"],
                extended_segment_inputs,
            ),
        ),
        (
            "extended_chart",
            _build_chart_wrapper("VG Verify Source Extended Pie Chart", bpy.data.node_groups["Extended Pie Chart"], extended_chart_inputs),
            _build_chart_wrapper(
                "VG Verify Translated Extended Pie Chart",
                bpy.data.node_groups["VG Extended Pie Chart"],
                extended_chart_inputs,
            ),
        ),
    ]
    results = [_compare(case, _evaluated_vertices(source), _evaluated_vertices(translated)) for case, source, translated in cases]
    ok = all(result["ok"] for result in results)
    print("VG_PIECHART_TRANSLATION_BEHAVIOR " + json.dumps({"ok": ok, "results": results}, sort_keys=True))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())

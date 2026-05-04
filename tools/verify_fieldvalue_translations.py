"""Compare Shriinivas fieldvalue scalar helpers against Geometry Script translations."""

from __future__ import annotations

import importlib.util
import json
import math
import sys
from pathlib import Path

import bpy


ROOT = Path(__file__).resolve().parents[1]
TRANSLATION = ROOT / "examples" / "geometry_script" / "shriinivas_fieldvalue.py"

CASES = [
    {"Number": 1234.0, "Position": 0},
    {"Number": 1234.0, "Position": 1},
    {"Number": 98765.0, "Position": 2},
    {"Number": 120305.0, "Position": 3},
]
NEXT_DIGIT_CASES = [
    {"Whole Part": 1234.0, "Fraction Part": 5678.0, "Max Precision": 2, "Position": 0},
    {"Whole Part": 1234.0, "Fraction Part": 5678.0, "Max Precision": 2, "Position": 1},
    {"Whole Part": 1234.0, "Fraction Part": 5678.0, "Max Precision": 2, "Position": 2},
    {"Whole Part": 98765.0, "Fraction Part": 4321.0, "Max Precision": 3, "Position": 4},
]

DECIMAL_CASE = {"Vertical Segment Size": 2.4, "radius": 0.18}
SEGMENT_CASES = [
    {
        "X Major": True,
        "Segment Length Along X": 2.0,
        "Segment Length Along Y": 0.45,
        "Secondary Axis Segment Thickness": 0.45,
        "Sharpness": 0.75,
        "offset": (0.2, -0.1, 0.0),
    },
    {
        "X Major": False,
        "Segment Length Along X": 0.4,
        "Segment Length Along Y": 1.8,
        "Secondary Axis Segment Thickness": 0.4,
        "Sharpness": 1.0,
        "offset": (-0.3, 0.25, 0.0),
    },
]
SEVEN_SEGMENTS_CASE = {
    "Horizontal Segment Size": 2.2,
    "Horizontal Segment Thickness": 0.42,
    "Vertical Segment Size": 1.7,
    "Vertical Segment Thickness": 0.36,
    "X Separation": 0.13,
    "Y Seperation": 0.17,
    "Tip Sharpness": 0.8,
}
DELETE_DIGITS = range(0, 13)
DELETE_SEGMENT_POSITIONS = range(0, 15)


def _load_translation() -> None:
    spec = importlib.util.spec_from_file_location("vg_fieldvalue_translation", TRANSLATION)
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


def _build_count_wrapper(name: str, digit_group: bpy.types.GeometryNodeTree, inputs: dict[str, object]):
    wrapper = _new_geometry_group(name)
    nodes = wrapper.nodes
    links = wrapper.links
    digit = nodes.new("GeometryNodeGroup")
    digit.node_tree = digit_group
    for socket in digit.inputs:
        if socket.name in inputs:
            socket.default_value = inputs[socket.name]

    line = nodes.new("GeometryNodeMeshLine")
    line.mode = "OFFSET"
    line.count_mode = "TOTAL"
    _socket_by_name(line.inputs, "Offset").default_value = (1.0, 0.0, 0.0)
    links.new(_socket_by_name(digit.outputs, "Result"), _socket_by_name(line.inputs, "Count"))

    group_output = nodes.new("NodeGroupOutput")
    links.new(_socket_by_name(line.outputs, "Mesh"), _socket_by_name(group_output.inputs, "Geometry"))
    return wrapper


def _build_bool_count_wrapper(name: str, bool_group: bpy.types.GeometryNodeTree, inputs: dict[str, object]):
    wrapper = _new_geometry_group(name)
    nodes = wrapper.nodes
    links = wrapper.links
    bool_node = nodes.new("GeometryNodeGroup")
    bool_node.node_tree = bool_group
    for socket in bool_node.inputs:
        if socket.name in inputs:
            socket.default_value = inputs[socket.name]

    switch_node = nodes.new("GeometryNodeSwitch")
    switch_node.input_type = "INT"
    _socket_by_name(switch_node.inputs, "False").default_value = 0
    _socket_by_name(switch_node.inputs, "True").default_value = 1
    links.new(_socket_by_name(bool_node.outputs, "result"), _socket_by_name(switch_node.inputs, "Switch"))

    line = nodes.new("GeometryNodeMeshLine")
    line.mode = "OFFSET"
    line.count_mode = "TOTAL"
    _socket_by_name(line.inputs, "Offset").default_value = (1.0, 0.0, 0.0)
    links.new(_socket_by_name(switch_node.outputs, "Output"), _socket_by_name(line.inputs, "Count"))

    group_output = nodes.new("NodeGroupOutput")
    links.new(_socket_by_name(line.outputs, "Mesh"), _socket_by_name(group_output.inputs, "Geometry"))
    return wrapper


def _build_geometry_wrapper(name: str, source_group: bpy.types.GeometryNodeTree, inputs: dict[str, object], output: str):
    wrapper = _new_geometry_group(name)
    nodes = wrapper.nodes
    links = wrapper.links
    group_node = nodes.new("GeometryNodeGroup")
    group_node.node_tree = source_group
    lower_inputs = {key.lower(): value for key, value in inputs.items()}
    for socket in group_node.inputs:
        if socket.name in inputs:
            socket.default_value = inputs[socket.name]
        elif socket.name.lower() in lower_inputs:
            socket.default_value = lower_inputs[socket.name.lower()]
    group_output = nodes.new("NodeGroupOutput")
    links.new(_socket_by_name(group_node.outputs, output), _socket_by_name(group_output.inputs, "Geometry"))
    return wrapper


def _evaluated_vertex_count(group: bpy.types.GeometryNodeTree) -> int:
    mesh = bpy.data.meshes.new(group.name + " Input Mesh")
    obj = bpy.data.objects.new(group.name + " Object", mesh)
    bpy.context.collection.objects.link(obj)
    modifier = obj.modifiers.new(group.name + " Modifier", "NODES")
    modifier.node_group = group
    depsgraph = bpy.context.evaluated_depsgraph_get()
    evaluated = obj.evaluated_get(depsgraph)
    evaluated_mesh = evaluated.to_mesh()
    try:
        return len(evaluated_mesh.vertices)
    finally:
        evaluated.to_mesh_clear()


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


def main() -> int:
    _load_translation()
    source = bpy.data.node_groups["Digit At"]
    translated = bpy.data.node_groups["VG Digit At"]
    results = []
    source_decimal = _evaluated_vertices(
        _build_geometry_wrapper("VG Verify Source Decimal", bpy.data.node_groups["Create Decimal"], DECIMAL_CASE, "Dot")
    )
    translated_decimal = _evaluated_vertices(
        _build_geometry_wrapper("VG Verify Translated Decimal", bpy.data.node_groups["VG Create Decimal"], DECIMAL_CASE, "Dot")
    )
    results.append(
        {
            "case": "create_decimal",
            "source_vertex_count": len(source_decimal),
            "translated_vertex_count": len(translated_decimal),
            "max_sorted_vertex_delta": max(
                (math.dist(a, b) for a, b in zip(sorted(source_decimal), sorted(translated_decimal))),
                default=0.0,
            ),
        }
    )
    results[-1]["ok"] = (
        results[-1]["source_vertex_count"] == results[-1]["translated_vertex_count"]
        and results[-1]["max_sorted_vertex_delta"] <= 1e-6
    )
    for index, inputs in enumerate(SEGMENT_CASES):
        source_segment = _evaluated_vertices(
            _build_geometry_wrapper(
                f"VG Verify Source Segment {index}",
                bpy.data.node_groups["Create Segment"],
                inputs,
                "Segment",
            )
        )
        translated_segment = _evaluated_vertices(
            _build_geometry_wrapper(
                f"VG Verify Translated Segment {index}",
                bpy.data.node_groups["VG Create Segment"],
                inputs,
                "Segment",
            )
        )
        max_delta = max(
            (math.dist(a, b) for a, b in zip(sorted(source_segment), sorted(translated_segment))),
            default=0.0,
        )
        results.append(
            {
                "case": {"create_segment": index, **inputs},
                "source_vertex_count": len(source_segment),
                "translated_vertex_count": len(translated_segment),
                "max_sorted_vertex_delta": max_delta,
                "ok": len(source_segment) == len(translated_segment) and max_delta <= 1e-6,
            }
        )
    source_seven_segments = _evaluated_vertices(
        _build_geometry_wrapper(
            "VG Verify Source Seven Segments",
            bpy.data.node_groups["Seven Segments"],
            SEVEN_SEGMENTS_CASE,
            "bars",
        )
    )
    translated_seven_segments = _evaluated_vertices(
        _build_geometry_wrapper(
            "VG Verify Translated Seven Segments",
            bpy.data.node_groups["VG Seven Segments"],
            SEVEN_SEGMENTS_CASE,
            "bars",
        )
    )
    seven_segments_delta = max(
        (math.dist(a, b) for a, b in zip(sorted(source_seven_segments), sorted(translated_seven_segments))),
        default=0.0,
    )
    results.append(
        {
            "case": {"seven_segments": SEVEN_SEGMENTS_CASE},
            "source_vertex_count": len(source_seven_segments),
            "translated_vertex_count": len(translated_seven_segments),
            "max_sorted_vertex_delta": seven_segments_delta,
            "ok": len(source_seven_segments) == len(translated_seven_segments) and seven_segments_delta <= 1e-6,
        }
    )
    for index, inputs in enumerate(CASES):
        source_count = _evaluated_vertex_count(_build_count_wrapper(f"VG Verify Source Digit {index}", source, inputs))
        translated_count = _evaluated_vertex_count(
            _build_count_wrapper(f"VG Verify Translated Digit {index}", translated, inputs)
        )
        results.append(
            {
                "case": inputs,
                "source_count": source_count,
                "translated_count": translated_count,
                "ok": source_count == translated_count,
            }
        )
    source_next_digit = bpy.data.node_groups["Next Digit"]
    translated_next_digit = bpy.data.node_groups["VG Next Digit"]
    for index, inputs in enumerate(NEXT_DIGIT_CASES):
        source_count = _evaluated_vertex_count(
            _build_count_wrapper(f"VG Verify Source Next Digit {index}", source_next_digit, inputs)
        )
        translated_count = _evaluated_vertex_count(
            _build_count_wrapper(f"VG Verify Translated Next Digit {index}", translated_next_digit, inputs)
        )
        results.append(
            {
                "case": {"next_digit": inputs},
                "source_count": source_count,
                "translated_count": translated_count,
                "ok": source_count == translated_count,
            }
        )
    delete_mismatches = []
    source_delete = bpy.data.node_groups["Delete Segments"]
    translated_delete = bpy.data.node_groups["VG Delete Segments"]
    checked = 0
    for digit in DELETE_DIGITS:
        for segment_position in DELETE_SEGMENT_POSITIONS:
            inputs = {"Digit": digit, "Segment Position": segment_position}
            source_count = _evaluated_vertex_count(
                _build_bool_count_wrapper(f"VG Verify Source Delete {digit}-{segment_position}", source_delete, inputs)
            )
            translated_count = _evaluated_vertex_count(
                _build_bool_count_wrapper(
                    f"VG Verify Translated Delete {digit}-{segment_position}",
                    translated_delete,
                    inputs,
                )
            )
            checked += 1
            if source_count != translated_count:
                delete_mismatches.append(
                    {
                        "digit": digit,
                        "segment_position": segment_position,
                        "source_count": source_count,
                        "translated_count": translated_count,
                    }
                )
    results.append(
        {
            "case": "delete_segments_grid",
            "checked": checked,
            "mismatches": delete_mismatches[:10],
            "mismatch_count": len(delete_mismatches),
            "ok": not delete_mismatches,
        }
    )
    ok = all(result["ok"] for result in results)
    print("VG_FIELDVALUE_TRANSLATION_BEHAVIOR " + json.dumps({"ok": ok, "results": results}, sort_keys=True))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())

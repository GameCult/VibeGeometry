"""Compare Shriinivas fieldvalue scalar helpers against Geometry Script translations."""

from __future__ import annotations

import importlib.util
import json
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


def main() -> int:
    _load_translation()
    source = bpy.data.node_groups["Digit At"]
    translated = bpy.data.node_groups["VG Digit At"]
    results = []
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
    ok = all(result["ok"] for result in results)
    print("VG_FIELDVALUE_TRANSLATION_BEHAVIOR " + json.dumps({"ok": ok, "results": results}, sort_keys=True))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())

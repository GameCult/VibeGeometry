"""Compare Blender's shortest-path labyrinth graph against the Geometry Script translation."""

from __future__ import annotations

import importlib.util
import json
import math
import sys
from pathlib import Path

import bpy


ROOT = Path(__file__).resolve().parents[1]
TRANSLATION = ROOT / "examples" / "geometry_script" / "blender_labyrinth_shortest_path.py"
CASES = {
    "small_unsolved": {"Size": 8, "Seed": 13, "Solve": 0.0},
    "small_solved": {"Size": 8, "Seed": 13, "Solve": 1.0},
}


def _load_translation() -> None:
    spec = importlib.util.spec_from_file_location("vg_labyrinth_translation", TRANSLATION)
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


def _build_wrapper(name: str, source_group: bpy.types.GeometryNodeTree, inputs: dict[str, object]):
    wrapper = _new_geometry_group(name)
    nodes = wrapper.nodes
    links = wrapper.links
    group_node = nodes.new("GeometryNodeGroup")
    group_node.node_tree = source_group
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
        return {
            "vertices": [tuple(vertex.co) for vertex in evaluated_mesh.vertices],
            "edges": [tuple(edge.vertices) for edge in evaluated_mesh.edges],
            "polygons": [tuple(polygon.vertices) for polygon in evaluated_mesh.polygons],
        }
    finally:
        evaluated.to_mesh_clear()


def main() -> int:
    _load_translation()
    results = []
    for case_name, inputs in CASES.items():
        source = _evaluated_mesh_summary(
            _build_wrapper(f"VG Verify Source Labyrinth {case_name}", bpy.data.node_groups["Solvable Labyrinth Generator"], inputs)
        )
        translated = _evaluated_mesh_summary(
            _build_wrapper(
                f"VG Verify Translated Labyrinth {case_name}",
                bpy.data.node_groups["VG Solvable Labyrinth Generator"],
                inputs,
            )
        )
        max_delta = (
            max(
                (math.dist(a, b) for a, b in zip(sorted(source["vertices"]), sorted(translated["vertices"]))),
                default=0.0,
            )
            if len(source["vertices"]) == len(translated["vertices"])
            else math.inf
        )
        result = {
            "case": f"labyrinth_{case_name}",
            "source_vertex_count": len(source["vertices"]),
            "translated_vertex_count": len(translated["vertices"]),
            "source_edge_count": len(source["edges"]),
            "translated_edge_count": len(translated["edges"]),
            "source_polygon_count": len(source["polygons"]),
            "translated_polygon_count": len(translated["polygons"]),
            "max_sorted_vertex_delta": max_delta,
        }
        result["ok"] = (
            result["source_vertex_count"] == result["translated_vertex_count"]
            and result["source_edge_count"] == result["translated_edge_count"]
            and result["source_polygon_count"] == result["translated_polygon_count"]
            and max_delta <= 1e-6
        )
        results.append(result)
    payload = {"ok": all(result["ok"] for result in results), "results": results}
    print("VG_LABYRINTH_TRANSLATION_BEHAVIOR " + json.dumps(payload, sort_keys=True))
    return 0 if payload["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

"""Compare Blender's instance attributes demo against the Geometry Script translation."""

from __future__ import annotations

import importlib.util
import json
import math
import sys
from pathlib import Path

import bpy


ROOT = Path(__file__).resolve().parents[1]
TRANSLATION = ROOT / "examples" / "geometry_script" / "blender_instance_attributes.py"
CASES = {
    "default": {
        "Height": 0.20000000298023224,
        "Radius": 0.05000000074505806,
        "Density": 1.0,
        "Thickness": 0.009999999776482582,
        "Curl": 0.5,
        "Seed": 0,
    },
    "wider_curlier_seeded": {
        "Height": 0.24000000953674316,
        "Radius": 0.07000000029802322,
        "Density": 0.75,
        "Thickness": 0.00800000037997961,
        "Curl": 0.8500000238418579,
        "Seed": 11,
    },
}


def _load_translation() -> None:
    spec = importlib.util.spec_from_file_location("vg_instance_attributes_translation", TRANSLATION)
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
        vertices = [tuple(vertex.co) for vertex in evaluated_mesh.vertices]
        edges = [tuple(edge.vertices) for edge in evaluated_mesh.edges]
        polygons = [tuple(polygon.vertices) for polygon in evaluated_mesh.polygons]
        return {
            "vertices": vertices,
            "edges": edges,
            "polygons": polygons,
            "polygon_smooth": [polygon.use_smooth for polygon in evaluated_mesh.polygons],
        }
    finally:
        evaluated.to_mesh_clear()


def _max_sorted_vertex_delta(source_vertices, translated_vertices) -> float:
    if len(source_vertices) != len(translated_vertices):
        return math.inf
    return max(
        (math.dist(a, b) for a, b in zip(sorted(source_vertices), sorted(translated_vertices))),
        default=0.0,
    )


def main() -> int:
    _load_translation()
    results = []
    for case_name, inputs in CASES.items():
        source = _evaluated_mesh_summary(
            _build_wrapper(f"VG Verify Source Grass Tuft {case_name}", bpy.data.node_groups["Grass Tuft Generator"], inputs)
        )
        translated = _evaluated_mesh_summary(
            _build_wrapper(
                f"VG Verify Translated Grass Tuft {case_name}",
                bpy.data.node_groups["VG Grass Tuft Generator"],
                inputs,
            )
        )
        max_delta = _max_sorted_vertex_delta(source["vertices"], translated["vertices"])
        result = {
            "case": f"grass_tuft_generator_{case_name}",
            "source_vertex_count": len(source["vertices"]),
            "translated_vertex_count": len(translated["vertices"]),
            "source_edge_count": len(source["edges"]),
            "translated_edge_count": len(translated["edges"]),
            "source_polygon_count": len(source["polygons"]),
            "translated_polygon_count": len(translated["polygons"]),
            "source_smooth_faces": sum(source["polygon_smooth"]),
            "translated_smooth_faces": sum(translated["polygon_smooth"]),
            "max_sorted_vertex_delta": max_delta,
        }
        result["ok"] = (
            result["source_vertex_count"] == result["translated_vertex_count"]
            and result["source_edge_count"] == result["translated_edge_count"]
            and result["source_polygon_count"] == result["translated_polygon_count"]
            and source["polygon_smooth"] == translated["polygon_smooth"]
            and max_delta <= 1e-6
        )
        results.append(result)
    payload = {"ok": all(result["ok"] for result in results), "results": results}
    print("VG_INSTANCE_ATTRIBUTES_TRANSLATION_BEHAVIOR " + json.dumps(payload, sort_keys=True))
    return 0 if payload["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

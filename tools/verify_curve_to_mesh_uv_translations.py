"""Compare small CurveToMeshUV utility groups against Geometry Script translations."""

from __future__ import annotations

import importlib.util
import json
import math
import sys
from pathlib import Path

import bpy


ROOT = Path(__file__).resolve().parents[1]
TRANSLATION = ROOT / "examples" / "geometry_script" / "quellenform_curve_to_mesh_uv.py"
AUTO_SMOOTH_CASE = {"Angle": 0.75}
CURVE_TO_MESH_UV_CASE = {
    "Fill Caps": True,
    "• Lock Caps UV-Scaling": False,
    "Hole Tolerant": False,
    "• Smooth Angle": 3.1415927410125732,
    "Free U-Space": False,
    "• Lock U-Scaling": False,
    "Free V-Space": False,
    "• Lock V-Scaling": False,
    "Sides UV Scale": (1.0, 1.0, 0.0),
    "Sides UV Offset": (0.0, 0.0, 0.0),
    "Sides UV Z-Rotation": 0.0,
    "Caps UV Scale": (1.0, 1.0, 0.0),
    "Caps UV Offset": (0.0, 0.0, 0.0),
    "Caps UV Z-Rotation": 0.0,
    "Store Attributes": False,
}


def _load_translation() -> None:
    spec = importlib.util.spec_from_file_location("vg_curve_to_mesh_uv_translation", TRANSLATION)
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


def _build_auto_smooth_wrapper(name: str, source_group: bpy.types.GeometryNodeTree, inputs: dict[str, object]):
    wrapper = _new_geometry_group(name)
    nodes = wrapper.nodes
    links = wrapper.links

    cube = nodes.new("GeometryNodeMeshCube")
    _socket_by_name(cube.inputs, "Size").default_value = (1.0, 1.0, 1.0)

    group_node = nodes.new("GeometryNodeGroup")
    group_node.node_tree = source_group
    links.new(_socket_by_name(cube.outputs, "Mesh"), _socket_by_name(group_node.inputs, "Geometry"))
    for socket in group_node.inputs:
        if socket.name in inputs:
            socket.default_value = inputs[socket.name]

    group_output = nodes.new("NodeGroupOutput")
    links.new(_socket_by_name(group_node.outputs, "Geometry"), _socket_by_name(group_output.inputs, "Geometry"))
    return wrapper


def _normalized_key(name: str) -> str:
    return name.lower().replace(" ", "").replace("•", "").replace("-", "")


def _set_inputs(group_node: bpy.types.GeometryNode, inputs: dict[str, object]):
    normalized = {_normalized_key(key): value for key, value in inputs.items()}
    for socket in group_node.inputs:
        key = _normalized_key(socket.name)
        if socket.name in inputs:
            socket.default_value = inputs[socket.name]
        elif key in normalized:
            socket.default_value = normalized[key]


def _build_curve_to_mesh_uv_wrapper(
    name: str,
    source_group: bpy.types.GeometryNodeTree,
    inputs: dict[str, object],
    output_mode: str = "mesh",
):
    wrapper = _new_geometry_group(name)
    nodes = wrapper.nodes
    links = wrapper.links

    curve = nodes.new("GeometryNodeCurvePrimitiveCircle")
    curve.mode = "RADIUS"
    _socket_by_name(curve.inputs, "Resolution").default_value = 24
    _socket_by_name(curve.inputs, "Radius").default_value = 1.2

    profile = nodes.new("GeometryNodeCurvePrimitiveCircle")
    profile.mode = "RADIUS"
    _socket_by_name(profile.inputs, "Resolution").default_value = 8
    _socket_by_name(profile.inputs, "Radius").default_value = 0.2

    group_node = nodes.new("GeometryNodeGroup")
    group_node.node_tree = source_group
    links.new(_socket_by_name(curve.outputs, "Curve"), _socket_by_name(group_node.inputs, "Curve"))
    links.new(_socket_by_name(profile.outputs, "Curve"), _socket_by_name(group_node.inputs, "Profile Curve"))
    _set_inputs(group_node, inputs)

    output_geometry = _socket_by_name(group_node.outputs, "Mesh")
    if output_mode == "uv":
        set_position = nodes.new("GeometryNodeSetPosition")
        links.new(_socket_by_name(group_node.outputs, "Mesh"), _socket_by_name(set_position.inputs, "Geometry"))
        links.new(_socket_by_name(group_node.outputs, "UV Map"), _socket_by_name(set_position.inputs, "Position"))
        output_geometry = _socket_by_name(set_position.outputs, "Geometry")
    elif output_mode == "caps":
        delete = nodes.new("GeometryNodeDeleteGeometry")
        delete.mode = "ALL"
        delete.domain = "FACE"
        links.new(_socket_by_name(group_node.outputs, "Mesh"), _socket_by_name(delete.inputs, "Geometry"))
        links.new(_socket_by_name(group_node.outputs, "Caps Mask"), _socket_by_name(delete.inputs, "Selection"))
        output_geometry = _socket_by_name(delete.outputs, "Geometry")

    group_output = nodes.new("NodeGroupOutput")
    links.new(output_geometry, _socket_by_name(group_output.inputs, "Geometry"))
    return wrapper


def _build_no_input_geometry_wrapper(name: str, source_group: bpy.types.GeometryNodeTree):
    wrapper = _new_geometry_group(name)
    nodes = wrapper.nodes
    links = wrapper.links
    group_node = nodes.new("GeometryNodeGroup")
    group_node.node_tree = source_group
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
        polygons = [polygon.use_smooth for polygon in evaluated_mesh.polygons]
        return {
            "vertices": vertices,
            "polygon_smooth": polygons,
        }
    finally:
        evaluated.to_mesh_clear()


def main() -> int:
    _load_translation()
    source = _evaluated_mesh_summary(
        _build_auto_smooth_wrapper("VG Verify Source Auto Smooth", bpy.data.node_groups["Auto Smooth"], AUTO_SMOOTH_CASE)
    )
    translated = _evaluated_mesh_summary(
        _build_auto_smooth_wrapper("VG Verify Translated Auto Smooth", bpy.data.node_groups["VG Auto Smooth"], AUTO_SMOOTH_CASE)
    )
    max_delta = max(
        (math.dist(a, b) for a, b in zip(sorted(source["vertices"]), sorted(translated["vertices"]))),
        default=0.0,
    )
    auto_smooth_result = {
        "case": "auto_smooth_cube",
        "source_vertex_count": len(source["vertices"]),
        "translated_vertex_count": len(translated["vertices"]),
        "max_sorted_vertex_delta": max_delta,
        "source_smooth_faces": sum(source["polygon_smooth"]),
        "translated_smooth_faces": sum(translated["polygon_smooth"]),
    }
    auto_smooth_result["ok"] = (
        auto_smooth_result["source_vertex_count"] == auto_smooth_result["translated_vertex_count"]
        and max_delta <= 1e-6
        and source["polygon_smooth"] == translated["polygon_smooth"]
    )
    results = [auto_smooth_result]
    for mode in ("mesh", "uv", "caps"):
        source_uv = _evaluated_mesh_summary(
            _build_curve_to_mesh_uv_wrapper(
                f"VG Verify Source Curve To Mesh UV {mode}",
                bpy.data.node_groups["Curve to Mesh UV"],
                CURVE_TO_MESH_UV_CASE,
                output_mode=mode,
            )
        )
        translated_uv = _evaluated_mesh_summary(
            _build_curve_to_mesh_uv_wrapper(
                f"VG Verify Translated Curve To Mesh UV {mode}",
                bpy.data.node_groups["VG Curve To Mesh UV"],
                CURVE_TO_MESH_UV_CASE,
                output_mode=mode,
            )
        )
        uv_delta = max(
            (math.dist(a, b) for a, b in zip(sorted(source_uv["vertices"]), sorted(translated_uv["vertices"]))),
            default=0.0,
        )
        uv_result = {
            "case": f"curve_to_mesh_uv_{mode}",
            "source_vertex_count": len(source_uv["vertices"]),
            "translated_vertex_count": len(translated_uv["vertices"]),
            "max_sorted_vertex_delta": uv_delta,
        }
        uv_result["ok"] = uv_result["source_vertex_count"] == uv_result["translated_vertex_count"] and uv_delta <= 1e-6
        results.append(uv_result)
    for case, source_name, translated_name in (
        ("curve_to_mesh_uv_demo", "_258246", "VG Curve To Mesh UV Demo"),
        ("curve_to_mesh_uv_title", "_Title", "VG Curve To Mesh UV Title"),
    ):
        source_demo = _evaluated_mesh_summary(_build_no_input_geometry_wrapper(f"VG Verify Source {case}", bpy.data.node_groups[source_name]))
        translated_demo = _evaluated_mesh_summary(
            _build_no_input_geometry_wrapper(f"VG Verify Translated {case}", bpy.data.node_groups[translated_name])
        )
        demo_delta = max(
            (math.dist(a, b) for a, b in zip(sorted(source_demo["vertices"]), sorted(translated_demo["vertices"]))),
            default=0.0,
        )
        demo_result = {
            "case": case,
            "source_vertex_count": len(source_demo["vertices"]),
            "translated_vertex_count": len(translated_demo["vertices"]),
            "max_sorted_vertex_delta": demo_delta,
        }
        demo_result["ok"] = (
            demo_result["source_vertex_count"] == demo_result["translated_vertex_count"] and demo_delta <= 1e-6
        )
        results.append(demo_result)
    payload = {"ok": all(result["ok"] for result in results), "results": results}
    print("VG_CURVE_TO_MESH_UV_TRANSLATION_BEHAVIOR " + json.dumps(payload, sort_keys=True))
    return 0 if payload["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

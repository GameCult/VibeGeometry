"""Geometry Script footholds from quellenform/blender-CurveToMeshUV."""

try:
    from tools.geometry_script_loader import load_repo_geometry_script
except ModuleNotFoundError:
    import sys
    from pathlib import Path

    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
    from tools.geometry_script_loader import load_repo_geometry_script

load_repo_geometry_script()

from geometry_script import *  # noqa: F403 - Geometry Script exposes node functions as DSL globals.


@tree("VG Auto Smooth")
def vg_auto_smooth(geometry: Geometry, angle: Float = 0.0):
    shallow_enough = compare(
        operation=Compare.Operation.LESS_EQUAL,
        data_type=Compare.DataType.FLOAT,
        mode=Compare.Mode.ELEMENT,
        a=edge_angle().unsigned_angle,
        b=angle,
    )
    preserve_smooth_face = boolean_math(
        operation=BooleanMath.Operation.AND,
        boolean=(shallow_enough, is_face_smooth()),
    )
    edge_pass = set_shade_smooth(
        domain=SetShadeSmooth.Domain.EDGE,
        mesh=geometry,
        selection=is_edge_smooth(),
        shade_smooth=preserve_smooth_face,
    )
    face_pass = set_shade_smooth(
        domain=SetShadeSmooth.Domain.FACE,
        mesh=edge_pass,
        selection=True,
        shade_smooth=True,
    )
    return {"Geometry": face_pass}


def _finalize_groups():
    import bpy

    group = bpy.data.node_groups.get("VG Auto Smooth")
    if group:
        group.use_fake_user = True
        return [group]
    return []


_finalize_groups()


if __name__ == "__main__":
    for group in _finalize_groups():
        print(
            "VG_CURVE_TO_MESH_UV_GROUP",
            group.name,
            len(group.nodes),
            len(group.links),
            sorted(set(node.bl_idname for node in group.nodes)),
        )

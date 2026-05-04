"""Geometry Script footholds from IRCSS/Blender-Geometry-Node-French-Houses."""

try:
    from tools.geometry_script_loader import load_repo_geometry_script
except ModuleNotFoundError:
    import sys
    from pathlib import Path

    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
    from tools.geometry_script_loader import load_repo_geometry_script

load_repo_geometry_script()

from geometry_script import *  # noqa: F403 - Geometry Script exposes node functions as DSL globals.
@tree("VG Make Spiral")
def vg_make_spiral(
    frequency: Float = 12.0,
    radius: Float = 1.0,
    height: Float = 3.0,
    height_radius_gain: Float = 0.0,
):
    rail = curve_line(mode=CurveLine.Mode.POINTS, start=(0.0, 0.0, 0.0), end=(0.0, 0.0, 1.0))
    samples = resample_curve(keep_last_segment=True, curve=rail, mode="Count", count=200, length=0.10000000149011612)
    point_count = domain_size(component="CURVE", geometry=samples).point_count
    t = math(operation=Math.Operation.DIVIDE, value=(index(), point_count))
    theta = math(operation=Math.Operation.MULTIPLY, value=(t, frequency))
    expanding_radius = math(
        operation=Math.Operation.ADD,
        value=(radius, math(operation=Math.Operation.MULTIPLY, value=(t, height_radius_gain))),
    )
    x = math(
        operation=Math.Operation.MULTIPLY,
        value=(math(operation=Math.Operation.SINE, value=theta), expanding_radius),
    )
    y = math(
        operation=Math.Operation.MULTIPLY,
        value=(math(operation=Math.Operation.COSINE, value=theta), expanding_radius),
    )
    z = math(operation=Math.Operation.MULTIPLY, value=(t, height))
    return {"Geometry": set_position(geometry=samples, position=combine_xyz(x=x, y=y, z=z), offset=(0.0, 0.0, 0.0))}


def _finalize_groups():
    import bpy

    groups = []
    for name in ("VG Make Spiral",):
        group = bpy.data.node_groups.get(name)
        if group:
            group.use_fake_user = True
            groups.append(group)
    return groups


_finalize_groups()


if __name__ == "__main__":
    for group in _finalize_groups():
        print(
            "VG_IRCSS_GROUP",
            group.name,
            len(group.nodes),
            len(group.links),
            sorted(set(node.bl_idname for node in group.nodes)),
        )

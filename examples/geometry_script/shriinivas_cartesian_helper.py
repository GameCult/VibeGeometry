"""Geometry Script recreation of a helper group from Shriinivas/cartesian.blend.

Source:
    https://github.com/Shriinivas/geometrynodes/blob/main/cartesian.blend

The source group is named ``NodeGroup.001``. It creates a resampled curve line
and a vector field where Y is lifted by ``sqrt(r^2 - x^2) * value`` while X and
Z are preserved from the current position.
"""

import addon_utils

addon_utils.enable("geometry-script-main", default_set=False, persistent=False)

from geometry_script import *  # noqa: F403 - Geometry Script exposes node functions as DSL globals.


@tree("VG Cartesian Helper")
def vg_cartesian_helper(
    count: Int = 10,
    start: Vector = (0.0, 0.0, 0.0),
    end: Vector = (0.0, 0.0, 1.0),
    r: Float = 1.0,
    value: Float = 1.0,
):
    curve = curve_line(mode=CurveLine.Mode.POINTS, start=start, end=end)
    sampled_curve = curve.resample_curve(count=count)

    position_parts = separate_xyz(vector=position())
    radius_squared = math(operation=Math.Operation.POWER, value=(r, 2.0))
    x_squared = math(operation=Math.Operation.POWER, value=(position_parts.x, 2.0))
    y = math(
        operation=Math.Operation.MULTIPLY,
        value=(
            math(
                operation=Math.Operation.SQRT,
                value=math(operation=Math.Operation.SUBTRACT, value=(radius_squared, x_squared)),
            ),
            value,
        ),
    )
    vector = combine_xyz(x=position_parts.x, y=y, z=position_parts.z)

    return {"Curve": sampled_curve, "Vector": vector}


def _finalize_group():
    import bpy

    group = bpy.data.node_groups.get("VG Cartesian Helper")
    if not group:
        return None
    group.use_fake_user = True
    if hasattr(group, "interface"):
        for item in group.interface.items_tree:
            if item.item_type == "SOCKET" and item.in_out == "INPUT" and item.name == "R":
                item.name = "r"
    return group


_finalize_group()


if __name__ == "__main__":
    group = _finalize_group()
    print(
        "VG_CARTESIAN_HELPER",
        bool(group),
        len(group.nodes) if group else -1,
        len(group.links) if group else -1,
        sorted(node.bl_idname for node in group.nodes) if group else [],
    )

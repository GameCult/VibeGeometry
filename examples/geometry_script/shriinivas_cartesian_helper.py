"""Geometry Script recreation of a helper group from Shriinivas/cartesian.blend.

Source:
    https://github.com/Shriinivas/geometrynodes/blob/main/cartesian.blend

The first source group is named ``NodeGroup.001``. It creates a resampled curve
line and a vector field where Y is lifted by ``sqrt(r^2 - x^2) * value`` while
X and Z are preserved from the current position. The other groups in this file
translate the scene-facing line, parabola, and circle node groups from the same
source file.
"""

try:
    from tools.geometry_script_loader import load_repo_geometry_script
except ModuleNotFoundError:
    import sys
    from pathlib import Path

    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
    from tools.geometry_script_loader import load_repo_geometry_script

load_repo_geometry_script()

from geometry_script import *  # noqa: F403 - Geometry Script exposes node functions as DSL globals.


def _cartesian_helper_nodes(count: Int, start: Vector, end: Vector, r: Float, value: Float):
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

    return sampled_curve, vector


@tree("VG Cartesian Helper")
def vg_cartesian_helper(
    count: Int = 10,
    start: Vector = (0.0, 0.0, 0.0),
    end: Vector = (0.0, 0.0, 1.0),
    r: Float = 1.0,
    value: Float = 1.0,
):
    sampled_curve, vector = _cartesian_helper_nodes(count=count, start=start, end=end, r=r, value=value)
    return {"Curve": sampled_curve, "Vector": vector}


def _radius_scale():
    radius = named_attribute(data_type=NamedAttribute.DataType.FLOAT, name="radius")
    return switch(
        input_type=Switch.InputType.FLOAT,
        switch=radius.exists,
        false=1.0,
        true=radius.attribute,
    )


def _tube_curve(curve: Geometry, thickness: Float):
    profile = curve_circle(mode=CurveCircle.Mode.RADIUS, resolution=32, radius=thickness)
    return curve.curve_to_mesh(profile_curve=profile, scale=_radius_scale())


@tree("VG Cartesian Line")
def vg_cartesian_line(
    geometry: Geometry,
    resolution: Int = 10,
    length: Float = 0.5,
    m: Float = 0.5,
    value: Float = 0.5,
    thickness: Float = 1.0,
):
    del geometry, resolution

    end = combine_xyz(x=length, y=0.0, z=0.0)
    curve = curve_line(mode=CurveLine.Mode.POINTS, start=(0.0, 0.0, 0.0), end=end)
    parts = separate_xyz(vector=position())
    y = math(
        operation=Math.Operation.ADD,
        value=(math(operation=Math.Operation.MULTIPLY, value=(parts.x, m)), value),
    )
    vector = combine_xyz(x=parts.x, y=y, z=parts.z)
    positioned = curve.set_position(position=vector)
    return _tube_curve(positioned, thickness)


@tree("VG Cartesian Parabola")
def vg_cartesian_parabola(
    geometry: Geometry,
    resolution: Int = 10,
    sample_resolution: Int = 100,
    start: Float = 0.0,
    end: Float = 0.0,
    a: Float = 2.0,
    b: Float = 2.0,
    c: Float = 0.5,
    thickness: Float = 1.0,
):
    del geometry, resolution

    curve_start = combine_xyz(x=start, y=0.0, z=0.0)
    curve_end = combine_xyz(x=end, y=0.0, z=0.0)
    curve = curve_line(mode=CurveLine.Mode.POINTS, start=curve_start, end=curve_end)
    sampled = curve.resample_curve(count=sample_resolution)

    parts = separate_xyz(vector=position())
    x_squared = math(operation=Math.Operation.POWER, value=(parts.x, 2.0))
    ax_squared = math(operation=Math.Operation.MULTIPLY, value=(x_squared, a))
    bx = math(operation=Math.Operation.MULTIPLY, value=(parts.x, b))
    y = math(
        operation=Math.Operation.ADD,
        value=(math(operation=Math.Operation.ADD, value=(ax_squared, bx)), c),
    )
    vector = combine_xyz(x=parts.x, y=y, z=parts.z)
    positioned = sampled.set_position(position=vector)
    return _tube_curve(positioned, thickness)


@tree("VG Cartesian Circle")
def vg_cartesian_circle(
    geometry: Geometry,
    resolution: Int = 10,
    r: Float = 0.5,
    thickness: Float = 1.0,
):
    del geometry

    left = combine_xyz(x=math(operation=Math.Operation.MULTIPLY, value=(r, -1.0)), y=0.0, z=0.0)
    right = combine_xyz(x=r, y=0.0, z=0.0)
    upper_curve, upper_vector = vg_cartesian_helper(
        count=resolution,
        start=left,
        end=right,
        r=r,
        value=1.0,
    )
    lower_curve, lower_vector = vg_cartesian_helper(
        count=resolution,
        start=left,
        end=right,
        r=r,
        value=-1.0,
    )

    upper = upper_curve.set_position(position=upper_vector)
    lower = lower_curve.set_position(position=lower_vector)
    return _tube_curve(join_geometry(geometry=[upper, lower]), thickness)


def _finalize_group():
    import bpy

    groups = []
    for name in ("VG Cartesian Helper", "VG Cartesian Line", "VG Cartesian Parabola", "VG Cartesian Circle"):
        group = bpy.data.node_groups.get(name)
        if not group:
            continue
        group.use_fake_user = True
        if hasattr(group, "interface"):
            for item in group.interface.items_tree:
                if item.item_type == "SOCKET" and item.in_out == "INPUT" and item.name == "R":
                    item.name = "r"
                if item.item_type == "SOCKET" and item.in_out == "INPUT" and item.name in {"M", "A", "B", "C"}:
                    item.name = item.name.lower()
                if (
                    item.item_type == "SOCKET"
                    and item.in_out == "OUTPUT"
                    and item.name == "Result"
                    and name != "VG Cartesian Helper"
                ):
                    item.name = "Geometry"
        groups.append(group)
    return groups


_finalize_group()


if __name__ == "__main__":
    for group in _finalize_group():
        print(
            "VG_CARTESIAN_GROUP",
            group.name,
            len(group.nodes),
            len(group.links),
            sorted(set(node.bl_idname for node in group.nodes)),
        )

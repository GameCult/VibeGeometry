"""Geometry Script recreation of a scalar helper from Shriinivas/fieldvalue.blend."""

try:
    from tools.geometry_script_loader import load_repo_geometry_script
except ModuleNotFoundError:
    import sys
    from pathlib import Path

    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
    from tools.geometry_script_loader import load_repo_geometry_script

load_repo_geometry_script()

from geometry_script import *  # noqa: F403 - Geometry Script exposes node functions as DSL globals.


@tree("VG Create Decimal")
def vg_create_decimal(vertical_segment_size: Float = 2.0, radius: Float = 0.0):
    dot = mesh_circle(fill_type=MeshCircle.FillType.NGON, vertices=32, radius=radius)
    offset = combine_xyz(
        x=0.0,
        y=math(operation=Math.Operation.MULTIPLY, value=(-1.0, vertical_segment_size)),
        z=0.0,
    )
    return {"Dot": dot.set_position(offset=offset)}


@tree("VG Digit At")
def vg_digit_at(number: Float = 0.0, position: Int = 0):
    shifted_position = math(operation=Math.Operation.ADD, value=(position, 1.0))
    upper_scale = math(operation=Math.Operation.POWER, value=(10.0, shifted_position))
    shifted_number = math(operation=Math.Operation.DIVIDE, value=(number, upper_scale))
    fractional_window = math(operation=Math.Operation.FRACT, value=shifted_number)
    digit_window = math(operation=Math.Operation.MULTIPLY, value=(10.0, fractional_window))

    position_scale = math(operation=Math.Operation.POWER, value=(10.0, position))
    rounded_scaled_window = math(
        operation=Math.Operation.ROUND,
        value=math(operation=Math.Operation.MULTIPLY, value=(digit_window, position_scale)),
    )
    digit_value = math(operation=Math.Operation.DIVIDE, value=(rounded_scaled_window, position_scale))

    is_ones_position = compare(
        operation=Compare.Operation.EQUAL,
        data_type=Compare.DataType.INT,
        mode=Compare.Mode.ELEMENT,
        a=position,
        b=0,
    )
    return switch(
        input_type=Switch.InputType.INT,
        switch=is_ones_position,
        false=math(operation=Math.Operation.FLOOR, value=digit_value),
        true=math(operation=Math.Operation.ROUND, value=digit_value),
    )


def _finalize_groups():
    import bpy

    groups = []
    for name in ("VG Create Decimal", "VG Digit At"):
        group = bpy.data.node_groups.get(name)
        if not group:
            continue
        group.use_fake_user = True
        groups.append(group)
    return groups


_finalize_groups()


if __name__ == "__main__":
    for group in _finalize_groups():
        print(
            "VG_FIELDVALUE_GROUP",
            group.name,
            len(group.nodes),
            len(group.links),
            sorted(set(node.bl_idname for node in group.nodes)),
        )

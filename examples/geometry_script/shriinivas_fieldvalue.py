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


@tree("VG Create Segment")
def vg_create_segment(
    x_major: Bool = False,
    segment_length_along_x: Float = 0.0,
    segment_length_along_y: Float = 0.0,
    secondary_axis_segment_thickness: Float = 0.0,
    sharpness: Float = 0.0,
    offset: Vector = (0.0, 0.0, 0.0),
):
    position_parts = separate_xyz(vector=position())
    major_axis = switch(input_type=Switch.InputType.FLOAT, switch=x_major, false=position_parts.y, true=position_parts.x)
    secondary_axis = switch(
        input_type=Switch.InputType.FLOAT,
        switch=x_major,
        false=position_parts.x,
        true=position_parts.y,
    )

    not_x_major = math(operation=Math.Operation.SUBTRACT, value=(1.0, x_major))
    vertices_x = math(operation=Math.Operation.ADD, value=(2.0, not_x_major))
    vertices_y = math(operation=Math.Operation.ADD, value=(2.0, x_major))

    tip_amount = math(
        operation=Math.Operation.MULTIPLY,
        value=(
            math(operation=Math.Operation.MULTIPLY, value=(0.5, sharpness)),
            secondary_axis_segment_thickness,
        ),
    )
    tip_vector = combine_xyz(
        x=math(operation=Math.Operation.MULTIPLY, value=(x_major, tip_amount)),
        y=math(operation=Math.Operation.MULTIPLY, value=(not_x_major, tip_amount)),
        z=0.0,
    )

    has_secondary_axis = compare(
        operation=Compare.Operation.NOT_EQUAL,
        data_type=Compare.DataType.FLOAT,
        mode=Compare.Mode.ELEMENT,
        a=secondary_axis,
        b=0.0,
    )
    negative_tip_gate = math(
        operation=Math.Operation.MULTIPLY,
        value=(math(operation=Math.Operation.LESS_THAN, value=(major_axis, 0.0)), has_secondary_axis),
    )
    positive_tip_gate = math(
        operation=Math.Operation.MULTIPLY,
        value=(math(operation=Math.Operation.GREATER_THAN, value=(major_axis, 0.0)), has_secondary_axis),
    )
    negative_tip = vector_math(operation=VectorMath.Operation.MULTIPLY, vector=(-1.0, tip_vector))
    positive_gate_vector = combine_xyz(x=positive_tip_gate, y=positive_tip_gate, z=positive_tip_gate)
    negative_gate_vector = combine_xyz(x=negative_tip_gate, y=negative_tip_gate, z=negative_tip_gate)
    positive_end_offset = vector_math(operation=VectorMath.Operation.MULTIPLY, vector=(negative_tip, positive_gate_vector))
    negative_end_offset = vector_math(operation=VectorMath.Operation.MULTIPLY, vector=(tip_vector, negative_gate_vector))
    total_offset = vector_math(
        operation=VectorMath.Operation.ADD,
        vector=(
            vector_math(operation=VectorMath.Operation.ADD, vector=(offset, positive_end_offset)),
            negative_end_offset,
        ),
    )

    segment = grid(
        size_x=segment_length_along_x,
        size_y=segment_length_along_y,
        vertices_x=vertices_x,
        vertices_y=vertices_y,
    ).mesh
    return {"Segment": segment.set_position(offset=total_offset)}


def _finalize_groups():
    import bpy

    groups = []
    for name in ("VG Create Decimal", "VG Digit At", "VG Create Segment"):
        group = bpy.data.node_groups.get(name)
        if not group:
            continue
        group.use_fake_user = True
        if hasattr(group, "interface"):
            for item in group.interface.items_tree:
                if item.item_type == "SOCKET" and item.in_out == "INPUT" and item.name == "X Major":
                    item.name = "X Major"
                if item.item_type == "SOCKET" and item.in_out == "INPUT" and item.name in {"Radius", "Offset"}:
                    item.name = item.name.lower()
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

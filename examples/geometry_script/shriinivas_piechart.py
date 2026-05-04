"""Geometry Script recreation of the small pie chart from Shriinivas/piechart.blend."""

try:
    from tools.geometry_script_loader import load_repo_geometry_script
except ModuleNotFoundError:
    import sys
    from pathlib import Path

    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
    from tools.geometry_script_loader import load_repo_geometry_script

load_repo_geometry_script()

from geometry_script import *  # noqa: F403 - Geometry Script exposes node functions as DSL globals.

TAU = 6.2831854820251465


@tree("VG Pie Segment")
def vg_pie_segment(
    start: Float = TAU,
    value: Float = 0.5,
    total: Float = 0.5,
    shift: Float = 0.5,
    segment_material: Material = None,
    text_material: Material = None,
):
    fraction = math(operation=Math.Operation.DIVIDE, value=(value, total))
    sweep = math(operation=Math.Operation.MULTIPLY, value=(fraction, TAU))
    end = math(operation=Math.Operation.ADD, value=(start, sweep))

    percentage = math(operation=Math.Operation.MULTIPLY, value=(fraction, 100.0))
    percentage_string = value_to_string(data_type=ValueToString.DataType.FLOAT, value=percentage, decimals=2)
    label = join_strings(delimiter="", strings=[percentage_string, string(string="%")])

    arc_curve = arc(
        mode=Arc.Mode.RADIUS,
        resolution=64,
        radius=1.0,
        start_angle=start,
        sweep_angle=sweep,
        connect_center=True,
    )
    face = arc_curve.fill_curve()
    extruded_face = face.extrude_mesh(mode=ExtrudeMesh.Mode.FACES, offset_scale=-0.1)

    text_curve = string_to_curves(string=label, size=0.2, align_x="Center", align_y="Middle").curve_instances
    text_face = text_curve.fill_curve()
    text_mesh = text_face.extrude_mesh(mode=ExtrudeMesh.Mode.FACES, offset_scale=0.025).mesh
    face_center = attribute_statistic(
        data_type=AttributeStatistic.DataType.FLOAT_VECTOR,
        domain=AttributeStatistic.Domain.FACE,
        geometry=face,
        attribute=position(),
    ).mean
    positioned_text = text_mesh.set_position(offset=face_center).set_material(material=text_material)

    mid_angle = math(operation=Math.Operation.ADD, value=(start, math(operation=Math.Operation.DIVIDE, value=(sweep, 2.0))))
    shift_vector = combine_xyz(
        x=math(operation=Math.Operation.MULTIPLY, value=(math(operation=Math.Operation.COSINE, value=mid_angle), shift)),
        y=math(operation=Math.Operation.MULTIPLY, value=(math(operation=Math.Operation.SINE, value=mid_angle), shift)),
        z=0.0,
    )

    segment = extruded_face.mesh.set_material(material=segment_material)
    cap = face.set_material(material=segment_material)
    geometry = join_geometry(geometry=[positioned_text, segment, cap]).set_position(offset=shift_vector)
    return {"Curve": geometry, "End": end}


@tree("VG Pie Chart")
def vg_pie_chart(
    geometry: Geometry,
    a: Float = 0.5,
    a_shift: Float = 0.5,
    a_material: Material = None,
    b: Float = 0.5,
    b_shift: Float = 0.0,
    b_material: Material = None,
    c: Float = 0.5,
    c_shift: Float = 0.0,
    c_material: Material = None,
    text_material: Material = None,
):
    del geometry

    total = math(operation=Math.Operation.ADD, value=(math(operation=Math.Operation.ADD, value=(a, b)), c))
    a_geometry, a_end = vg_pie_segment(
        start=0.0,
        value=a,
        total=total,
        shift=a_shift,
        segment_material=a_material,
        text_material=text_material,
    )
    b_geometry, b_end = vg_pie_segment(
        start=a_end,
        value=b,
        total=total,
        shift=b_shift,
        segment_material=b_material,
        text_material=text_material,
    )
    c_geometry, _c_end = vg_pie_segment(
        start=b_end,
        value=c,
        total=total,
        shift=c_shift,
        segment_material=c_material,
        text_material=text_material,
    )
    return join_geometry(geometry=[a_geometry, b_geometry, c_geometry])


def _empty_geometry():
    return mesh_line(
        mode=MeshLine.Mode.OFFSET,
        count_mode=MeshLine.CountMode.TOTAL,
        count=0,
        offset=(0.0, 0.0, 1.0),
    )


@tree("VG Extended Pie Segment")
def vg_extended_pie_segment(
    radius: Float = 0.0,
    pie_height: Float = 0.0,
    text_height: Float = 0.0,
    text_size: Float = 0.0,
    text_material: Material = None,
    text_offset: Float = 0.0,
    pie_material: Material = None,
    include_percentage: Bool = True,
    value: Float = 0.0,
    total: Float = 0.0,
    start_angle: Float = 0.0,
    shift: Float = 0.0,
    text: String = "",
):
    fraction = math(operation=Math.Operation.DIVIDE, value=(value, total))
    sweep = math(operation=Math.Operation.MULTIPLY, value=(fraction, TAU))
    end_angle = math(operation=Math.Operation.ADD, value=(start_angle, sweep))
    mid_angle = math(operation=Math.Operation.ADD, value=(start_angle, math(operation=Math.Operation.DIVIDE, value=(sweep, 2.0))))

    percentage = value_to_string(
        data_type=ValueToString.DataType.FLOAT,
        value=math(operation=Math.Operation.MULTIPLY, value=(fraction, 100.0)),
        decimals=2,
    )
    percentage_line = join_strings(delimiter="", strings=[string(string="%"), percentage])
    label_with_percentage = join_strings(delimiter=special_characters().line_break, strings=[percentage_line, text])
    label = switch(input_type=Switch.InputType.STRING, switch=include_percentage, false=text, true=label_with_percentage)

    shift_vector = combine_xyz(
        x=math(operation=Math.Operation.MULTIPLY, value=(shift, math(operation=Math.Operation.COSINE, value=mid_angle))),
        y=math(operation=Math.Operation.MULTIPLY, value=(shift, math(operation=Math.Operation.SINE, value=mid_angle))),
        z=0.0,
    )
    label_radius = math(operation=Math.Operation.MULTIPLY, value=(text_offset, radius))
    label_offset = vector_math(
        operation=VectorMath.Operation.ADD,
        vector=(
            shift_vector,
            combine_xyz(
                x=math(operation=Math.Operation.MULTIPLY, value=(label_radius, math(operation=Math.Operation.COSINE, value=mid_angle))),
                y=math(operation=Math.Operation.MULTIPLY, value=(label_radius, math(operation=Math.Operation.SINE, value=mid_angle))),
                z=0.0,
            ),
        ),
    )

    text_curves = string_to_curves(
        string=label,
        size=text_size,
        align_x="Center",
        align_y="Middle",
        pivot_point="Bottom Left",
    ).curve_instances
    text_face = fill_curve(curve=text_curves, mode="Triangles", fill_rule="Even-Odd")
    placed_text = set_position(geometry=text_face.set_material(material=text_material), offset=label_offset)
    extruded_text = extrude_mesh(
        mode=ExtrudeMesh.Mode.FACES,
        mesh=placed_text,
        offset=combine_xyz(x=0.0, y=0.0, z=math(operation=Math.Operation.ADD, value=(text_height, pie_height))),
        offset_scale=1.0,
        individual=True,
    ).mesh.set_material(material=text_material)

    arc_curve = arc(
        mode=Arc.Mode.RADIUS,
        resolution=64,
        radius=radius,
        start_angle=start_angle,
        sweep_angle=sweep,
        connect_center=True,
    )
    shifted_arc = transform_geometry(geometry=arc_curve, translation=shift_vector)
    pie_face = fill_curve(curve=shifted_arc, mode="Triangles", fill_rule="Even-Odd").set_material(
        material=pie_material
    )
    extruded_pie = extrude_mesh(
        mode=ExtrudeMesh.Mode.FACES,
        mesh=pie_face,
        offset=combine_xyz(x=0.0, y=0.0, z=pie_height),
        offset_scale=1.0,
        individual=True,
    ).mesh.set_material(material=pie_material)

    return {"End Angle": end_angle, "Pie": join_geometry(geometry=[extruded_text, extruded_pie, placed_text, pie_face])}


@tree("VG Extended Pie Chart")
def vg_extended_pie_chart(
    title: String = "Extended Pie Chart",
    title_size: Float = 0.20000000298023224,
    title_material: Material = None,
    title_offset: Float = 0.18000000715255737,
    segment_count: Int = 10,
    radius: Float = 1.0,
    pie_height: Float = 0.10000000149011612,
    text_height: Float = 0.004999999888241291,
    text_size: Float = 0.07999999821186066,
    text_material: Material = None,
    text_offset: Float = 0.699999988079071,
    include_percentage: Bool = True,
    value_1: Float = 20.0,
    label_1: String = "Lorem",
    shift_1: Float = 0.20000000298023224,
    material_1: Material = None,
    value_2: Float = 30.0,
    label_2: String = "Ipsum",
    shift_2: Float = 0.0,
    material_2: Material = None,
    value_3: Float = 27.0,
    label_3: String = "Dolor",
    shift_3: Float = 0.0,
    material_3: Material = None,
    value_4: Float = 25.0,
    label_4: String = "Sit",
    shift_4: Float = 0.0,
    material_4: Material = None,
    value_5: Float = 55.0,
    label_5: String = "Amet",
    shift_5: Float = 0.0,
    material_5: Material = None,
    value_6: Float = 45.0,
    label_6: String = "Consectetur",
    shift_6: Float = 0.0,
    material_6: Material = None,
    value_7: Float = 25.0,
    label_7: String = "Adipiscing",
    shift_7: Float = 0.0,
    material_7: Material = None,
    value_8: Float = 35.0,
    label_8: String = "Elit",
    shift_8: Float = 0.0,
    material_8: Material = None,
    value_9: Float = 58.0,
    label_9: String = "Sed",
    shift_9: Float = 0.0,
    material_9: Material = None,
    value_10: Float = 32.0,
    label_10: String = "Do",
    shift_10: Float = 0.0,
    material_10: Material = None,
):
    values = [value_1, value_2, value_3, value_4, value_5, value_6, value_7, value_8, value_9, value_10]
    labels = [label_1, label_2, label_3, label_4, label_5, label_6, label_7, label_8, label_9, label_10]
    shifts = [shift_1, shift_2, shift_3, shift_4, shift_5, shift_6, shift_7, shift_8, shift_9, shift_10]
    materials = [
        material_1,
        material_2,
        material_3,
        material_4,
        material_5,
        material_6,
        material_7,
        material_8,
        material_9,
        material_10,
    ]

    total = value_1
    for index, segment_value in enumerate(values[1:], start=2):
        total = math(
            operation=Math.Operation.ADD,
            value=(
                total,
                switch(
                    input_type=Switch.InputType.FLOAT,
                    switch=math(operation=Math.Operation.GREATER_THAN, value=(segment_count, index - 1.0)),
                    false=0.0,
                    true=segment_value,
                ),
            ),
        )

    empty = _empty_geometry()
    start_angle = 0.0
    segments = []
    for index, (segment_value, label, segment_shift, segment_material) in enumerate(
        zip(values, labels, shifts, materials),
        start=1,
    ):
        end_angle, segment_geometry = vg_extended_pie_segment(
            radius=radius,
            pie_height=pie_height,
            text_height=text_height,
            text_size=text_size,
            text_material=text_material,
            text_offset=text_offset,
            pie_material=segment_material,
            include_percentage=include_percentage,
            value=segment_value,
            total=total,
            start_angle=start_angle,
            shift=segment_shift,
            text=label,
        )
        if index == 1:
            segments.append(segment_geometry)
        else:
            segments.append(
                switch(
                    input_type=Switch.InputType.GEOMETRY,
                    switch=math(operation=Math.Operation.GREATER_THAN, value=(segment_count, index - 1.0)),
                    false=empty,
                    true=segment_geometry,
                )
            )
        start_angle = end_angle

    title_curves = string_to_curves(
        string=title,
        size=title_size,
        align_x="Center",
        align_y="Middle",
        pivot_point="Bottom Left",
    ).curve_instances
    title_face = fill_curve(curve=title_curves, mode="Triangles", fill_rule="Even-Odd")
    title_position = combine_xyz(
        x=0.0,
        y=math(
            operation=Math.Operation.SUBTRACT,
            value=(math(operation=Math.Operation.MULTIPLY, value=(-1.0, math(operation=Math.Operation.ADD, value=(radius, title_size)))), title_offset),
        ),
        z=0.0,
    )
    placed_title = transform_geometry(geometry=title_face, translation=title_position).set_material(material=title_material)
    extruded_title = extrude_mesh(
        mode=ExtrudeMesh.Mode.FACES,
        mesh=placed_title,
        offset=combine_xyz(x=0.0, y=0.0, z=text_height),
        offset_scale=1.0,
        individual=True,
    ).mesh.set_material(material=title_material)
    return {"Geometry": join_geometry(geometry=[*segments, placed_title, extruded_title])}


def _finalize_groups():
    import bpy

    groups = []
    for name in ("VG Pie Segment", "VG Pie Chart", "VG Extended Pie Segment", "VG Extended Pie Chart"):
        group = bpy.data.node_groups.get(name)
        if not group:
            continue
        group.use_fake_user = True
        if hasattr(group, "interface"):
            for item in group.interface.items_tree:
                if item.item_type == "SOCKET" and item.in_out == "OUTPUT" and item.name == "Result":
                    item.name = "Geometry"
                if item.item_type == "SOCKET" and item.in_out == "INPUT" and item.name in {"A", "B", "C"}:
                    item.name = item.name.lower()
        groups.append(group)
    return groups


_finalize_groups()


if __name__ == "__main__":
    for group in _finalize_groups():
        print(
            "VG_PIE_GROUP",
            group.name,
            len(group.nodes),
            len(group.links),
            sorted(set(node.bl_idname for node in group.nodes)),
        )

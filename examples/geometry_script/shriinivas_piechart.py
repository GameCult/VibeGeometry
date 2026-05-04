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


def _finalize_groups():
    import bpy

    groups = []
    for name in ("VG Pie Segment", "VG Pie Chart"):
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

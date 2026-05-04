"""Geometry Script recreations from Shriinivas/paramnpolareq.blend."""

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


def _accumulated_parameter(resolution, max_value):
    step = math(
        operation=Math.Operation.DIVIDE,
        value=(max_value, math(operation=Math.Operation.SUBTRACT, value=(resolution, 1.0))),
    )
    return accumulate_field(
        data_type=AccumulateField.DataType.FLOAT,
        domain=AccumulateField.Domain.POINT,
        value=step,
    ).trailing


def _choose_float(curve_type, val0, val1, val2, val3, val4, val5=0.0):
    selected = switch(
        input_type=Switch.InputType.FLOAT,
        switch=compare(
            operation=Compare.Operation.EQUAL,
            data_type=Compare.DataType.INT,
            mode=Compare.Mode.ELEMENT,
            a=curve_type,
            b=4,
        ),
        false=val5,
        true=val4,
    )
    for index, value in reversed(list(enumerate([val0, val1, val2, val3]))):
        selected = switch(
            input_type=Switch.InputType.FLOAT,
            switch=compare(
                operation=Compare.Operation.EQUAL,
                data_type=Compare.DataType.INT,
                mode=Compare.Mode.ELEMENT,
                a=curve_type,
                b=index,
            ),
            false=selected,
            true=value,
        )
    return selected


def _choose_string(curve_type, val0, val1, val2, val3, val4, val5=""):
    selected = switch(
        input_type=Switch.InputType.STRING,
        switch=compare(
            operation=Compare.Operation.EQUAL,
            data_type=Compare.DataType.INT,
            mode=Compare.Mode.ELEMENT,
            a=curve_type,
            b=4,
        ),
        false=val5,
        true=val4,
    )
    for index, value in reversed(list(enumerate([val0, val1, val2, val3]))):
        selected = switch(
            input_type=Switch.InputType.STRING,
            switch=compare(
                operation=Compare.Operation.EQUAL,
                data_type=Compare.DataType.INT,
                mode=Compare.Mode.ELEMENT,
                a=curve_type,
                b=index,
            ),
            false=selected,
            true=value,
        )
    return selected


@tree("VG Choose Float Val")
def vg_choose_float_val(
    curve_type: Int = 0,
    val0: Float = 0.0,
    val1: Float = 0.0,
    val2: Float = 0.0,
    val3: Float = 0.0,
    val4: Float = 0.0,
    val5: Float = 0.0,
):
    return {"val": _choose_float(curve_type, val0, val1, val2, val3, val4, val5)}


@tree("VG Choose Str Val")
def vg_choose_str_val(
    curve_type: Int = 0,
    val0: String = "",
    val1: String = "",
    val2: String = "",
    val3: String = "",
    val4: String = "",
    val5: String = "",
):
    return {"val": _choose_string(curve_type, val0, val1, val2, val3, val4, val5)}


@tree("VG Param Epicycloid X")
def vg_param_epicycloid_x(a: Float = 0.5, b: Float = 0.5, t: Float = 1.0):
    ratio_plus_one = math(
        operation=Math.Operation.ADD,
        value=(math(operation=Math.Operation.DIVIDE, value=(a, b)), 1.0),
    )
    inner = math(
        operation=Math.Operation.MULTIPLY,
        value=(b, math(operation=Math.Operation.COSINE, value=math(operation=Math.Operation.MULTIPLY, value=(ratio_plus_one, t)))),
    )
    outer = math(
        operation=Math.Operation.MULTIPLY,
        value=(math(operation=Math.Operation.ADD, value=(a, b)), math(operation=Math.Operation.COSINE, value=t)),
    )
    return {"x": math(operation=Math.Operation.SUBTRACT, value=(outer, inner))}


@tree("VG Param Epicycloid Y")
def vg_param_epicycloid_y(a: Float = 0.5, b: Float = 0.5, t: Float = 1.0):
    ratio_plus_one = math(
        operation=Math.Operation.ADD,
        value=(math(operation=Math.Operation.DIVIDE, value=(a, b)), 1.0),
    )
    inner = math(
        operation=Math.Operation.MULTIPLY,
        value=(b, math(operation=Math.Operation.SINE, value=math(operation=Math.Operation.MULTIPLY, value=(ratio_plus_one, t)))),
    )
    outer = math(
        operation=Math.Operation.MULTIPLY,
        value=(math(operation=Math.Operation.ADD, value=(a, b)), math(operation=Math.Operation.SINE, value=t)),
    )
    return {"y": math(operation=Math.Operation.SUBTRACT, value=(outer, inner))}


@tree("VG Polar Spiral X")
def vg_polar_spiral_x(a: Float = 0.5, b: Float = 0.5, theta: Float = 1.0):
    radius = math(operation=Math.Operation.ADD, value=(a, math(operation=Math.Operation.MULTIPLY, value=(b, theta))))
    return {"x": math(operation=Math.Operation.MULTIPLY, value=(math(operation=Math.Operation.COSINE, value=theta), radius))}


@tree("VG Polar Spiral Y")
def vg_polar_spiral_y(a: Float = 0.5, b: Float = 0.5, theta: Float = 1.0):
    radius = math(operation=Math.Operation.ADD, value=(a, math(operation=Math.Operation.MULTIPLY, value=(b, theta))))
    return {"y": math(operation=Math.Operation.MULTIPLY, value=(math(operation=Math.Operation.SINE, value=theta), radius))}


@tree("VG Param XY")
def vg_param_xy(a: Float = 0.0, b: Float = 0.0, c: Float = 0.0, t: Float = 0.0, curve_type: Int = 0):
    normalized_curve_type = math(
        operation=Math.Operation.MODULO,
        value=(math(operation=Math.Operation.ABSOLUTE, value=curve_type), 5.0),
    )

    epi_x = vg_param_epicycloid_x(a=a, b=b, t=t)
    epi_y = vg_param_epicycloid_y(a=a, b=b, t=t)
    epitrochoid_x = math(
        operation=Math.Operation.SUBTRACT,
        value=(
            math(operation=Math.Operation.MULTIPLY, value=(math(operation=Math.Operation.ADD, value=(a, b)), math(operation=Math.Operation.COSINE, value=t))),
            math(
                operation=Math.Operation.MULTIPLY,
                value=(
                    c,
                    math(
                        operation=Math.Operation.COSINE,
                        value=math(
                            operation=Math.Operation.MULTIPLY,
                            value=(math(operation=Math.Operation.ADD, value=(math(operation=Math.Operation.DIVIDE, value=(a, b)), 1.0)), t),
                        ),
                    ),
                ),
            ),
        ),
    )
    epitrochoid_y = math(
        operation=Math.Operation.SUBTRACT,
        value=(
            math(operation=Math.Operation.MULTIPLY, value=(math(operation=Math.Operation.ADD, value=(a, b)), math(operation=Math.Operation.SINE, value=t))),
            math(
                operation=Math.Operation.MULTIPLY,
                value=(
                    c,
                    math(
                        operation=Math.Operation.SINE,
                        value=math(
                            operation=Math.Operation.MULTIPLY,
                            value=(math(operation=Math.Operation.ADD, value=(math(operation=Math.Operation.DIVIDE, value=(a, b)), 1.0)), t),
                        ),
                    ),
                ),
            ),
        ),
    )
    hypo_x = math(
        operation=Math.Operation.ADD,
        value=(
            math(operation=Math.Operation.MULTIPLY, value=(math(operation=Math.Operation.SUBTRACT, value=(a, b)), math(operation=Math.Operation.COSINE, value=t))),
            math(
                operation=Math.Operation.MULTIPLY,
                value=(
                    b,
                    math(
                        operation=Math.Operation.COSINE,
                        value=math(
                            operation=Math.Operation.MULTIPLY,
                            value=(math(operation=Math.Operation.SUBTRACT, value=(math(operation=Math.Operation.DIVIDE, value=(a, b)), 1.0)), t),
                        ),
                    ),
                ),
            ),
        ),
    )
    hypo_y = math(
        operation=Math.Operation.SUBTRACT,
        value=(
            math(operation=Math.Operation.MULTIPLY, value=(math(operation=Math.Operation.SUBTRACT, value=(a, b)), math(operation=Math.Operation.SINE, value=t))),
            math(
                operation=Math.Operation.MULTIPLY,
                value=(
                    b,
                    math(
                        operation=Math.Operation.SINE,
                        value=math(
                            operation=Math.Operation.MULTIPLY,
                            value=(math(operation=Math.Operation.SUBTRACT, value=(math(operation=Math.Operation.DIVIDE, value=(a, b)), 1.0)), t),
                        ),
                    ),
                ),
            ),
        ),
    )
    hypotrochoid_x = math(
        operation=Math.Operation.ADD,
        value=(
            math(operation=Math.Operation.MULTIPLY, value=(math(operation=Math.Operation.SUBTRACT, value=(a, b)), math(operation=Math.Operation.COSINE, value=t))),
            math(
                operation=Math.Operation.MULTIPLY,
                value=(
                    c,
                    math(
                        operation=Math.Operation.COSINE,
                        value=math(
                            operation=Math.Operation.MULTIPLY,
                            value=(math(operation=Math.Operation.SUBTRACT, value=(math(operation=Math.Operation.DIVIDE, value=(a, b)), 1.0)), t),
                        ),
                    ),
                ),
            ),
        ),
    )
    hypotrochoid_y = math(
        operation=Math.Operation.SUBTRACT,
        value=(
            math(operation=Math.Operation.MULTIPLY, value=(math(operation=Math.Operation.SUBTRACT, value=(a, b)), math(operation=Math.Operation.SINE, value=t))),
            math(
                operation=Math.Operation.MULTIPLY,
                value=(
                    c,
                    math(
                        operation=Math.Operation.SINE,
                        value=math(
                            operation=Math.Operation.MULTIPLY,
                            value=(math(operation=Math.Operation.SUBTRACT, value=(math(operation=Math.Operation.DIVIDE, value=(a, b)), 1.0)), t),
                        ),
                    ),
                ),
            ),
        ),
    )
    arch_radius = math(operation=Math.Operation.ADD, value=(a, math(operation=Math.Operation.MULTIPLY, value=(b, t))))
    arch_x = math(operation=Math.Operation.MULTIPLY, value=(arch_radius, math(operation=Math.Operation.COSINE, value=t)))
    arch_y = math(operation=Math.Operation.MULTIPLY, value=(arch_radius, math(operation=Math.Operation.SINE, value=t)))

    linebreak = special_characters().line_break
    eq = _choose_string(
        normalized_curve_type,
        join_strings(
            delimiter=linebreak,
            strings=[
                string(string="y = ((a + b) * sin(t)) - (b * sin((a/b + 1) * t))"),
                string(string="x = ((a + b) * cos(t)) - (b * cos((a/b + 1) * t))"),
                string(string="Epicycloid"),
            ],
        ),
        join_strings(
            delimiter=linebreak,
            strings=[
                string(string="y = ((a + b) * sin(t)) - (c * sin((a/b + 1) * t))"),
                string(string="x = ((a + b) * cos(t)) - (c * cos((a/b + 1) * t))"),
                string(string="Epitrochoid"),
            ],
        ),
        join_strings(
            delimiter=linebreak,
            strings=[
                string(string="y = ((a - b) * sin(t)) + (b * sin((a/b - 1) * t))"),
                string(string="x = ((a - b) * cos(t)) + (b * cos((a/b - 1) * t))"),
                string(string="Hypocycloid"),
            ],
        ),
        join_strings(
            delimiter=linebreak,
            strings=[
                string(string="y = ((a - b) * sin(t)) + (c * sin((a/b - 1) * t))"),
                string(string="x = ((a - b) * cos(t)) + (c * cos((a/b - 1) * t))"),
                string(string="Hypotrochoid"),
            ],
        ),
        join_strings(
            delimiter=linebreak,
            strings=[
                string(string="r = a + b theta"),
                string(string="Archimedes Spiral"),
            ],
        ),
    )

    return {
        "x": _choose_float(normalized_curve_type, epi_x, epitrochoid_x, hypo_x, hypotrochoid_x, arch_x),
        "y": _choose_float(normalized_curve_type, epi_y, epitrochoid_y, hypo_y, hypotrochoid_y, arch_y),
        "eq": eq,
    }


@tree("VG Archimedes Spiral")
def vg_archimedes_spiral(
    resolution: Int = 10,
    no_of_rounds: Float = 0.5,
    a: Float = 0.5,
    b: Float = 0.5,
):
    mesh = mesh_line(
        mode=MeshLine.Mode.OFFSET,
        count_mode=MeshLine.CountMode.TOTAL,
        count=resolution,
        start_location=(0.0, 0.0, 0.0),
        offset=(0.0, 0.0, 1.0),
    )
    theta = _accumulated_parameter(
        resolution=resolution,
        max_value=math(operation=Math.Operation.MULTIPLY, value=(no_of_rounds, TAU)),
    )
    positioned = mesh.set_position(
        position=combine_xyz(
            x=vg_polar_spiral_x(a=a, b=b, theta=theta),
            y=vg_polar_spiral_y(a=a, b=b, theta=theta),
            z=0.0,
        )
    )
    return {"Geometry": positioned}


@tree("VG Epicycloid")
def vg_epicycloid(
    resolution: Int = 10,
    max_t: Float = 0.5,
    a: Float = 0.5,
    b: Float = 0.5,
):
    mesh = mesh_line(
        mode=MeshLine.Mode.OFFSET,
        count_mode=MeshLine.CountMode.TOTAL,
        count=resolution,
        start_location=(0.0, 0.0, 0.0),
        offset=(0.0, 0.0, 1.0),
    )
    t = _accumulated_parameter(resolution=resolution, max_value=max_t)
    positioned = mesh.set_position(
        position=combine_xyz(
            x=vg_param_epicycloid_x(a=a, b=b, t=t),
            y=vg_param_epicycloid_y(a=a, b=b, t=t),
            z=0.0,
        )
    )
    return {"Geometry": positioned}


@tree("VG Mirrored Root Spiral")
def vg_mirrored_root_spiral(a: Float = 0.30000001192092896, round_count: Float = 5.0, resolution: Float = 500.0):
    mesh = mesh_line(
        mode=MeshLine.Mode.OFFSET,
        count_mode=MeshLine.CountMode.TOTAL,
        count=resolution,
        start_location=(0.0, 0.0, 0.0),
        offset=(0.0, 0.0, 1.0),
    )
    theta = _accumulated_parameter(
        resolution=resolution,
        max_value=math(operation=Math.Operation.MULTIPLY, value=(math(operation=Math.Operation.MULTIPLY, value=(round_count, 3.1415927410125732)), 2.0)),
    )
    radius = math(operation=Math.Operation.MULTIPLY, value=(a, math(operation=Math.Operation.POWER, value=(theta, 0.5))))
    x = math(operation=Math.Operation.MULTIPLY, value=(radius, math(operation=Math.Operation.COSINE, value=theta)))
    y = math(operation=Math.Operation.MULTIPLY, value=(radius, math(operation=Math.Operation.SINE, value=theta)))
    forward = mesh.set_position(position=combine_xyz(x=x, y=y, z=0.0))
    mirrored = mesh.set_position(
        position=combine_xyz(
            x=math(operation=Math.Operation.MULTIPLY, value=(-1.0, x)),
            y=math(operation=Math.Operation.MULTIPLY, value=(-1.0, y)),
            z=0.0,
        )
    )
    return {"Geometry": join_geometry(geometry=[mirrored, forward])}


def _empty_curve_geometry():
    return mesh_line(
        mode=MeshLine.Mode.OFFSET,
        count_mode=MeshLine.CountMode.TOTAL,
        count=0,
        offset=(0.0, 0.0, 1.0),
    )


@tree("VG Param Curve")
def vg_param_curve(
    curve_type: Int = 0,
    a: Float = 0.800000011920929,
    b: Float = 0.5,
    c: Float = 1.0,
    z: Float = 0.0,
    max_t: Float = 32.5,
    resolution: Float = 500.0,
    showlabel: Bool = True,
    thickness: Float = 0.009999999776482582,
    curve_material: Material = None,
    text_material: Material = None,
):
    t = _accumulated_parameter(resolution=resolution, max_value=max_t)
    x, y, equation = vg_param_xy(a=a, b=b, c=c, t=t, curve_type=curve_type)

    text_curve = string_to_curves(
        string=equation,
        size=2.0,
        align_x="Center",
        align_y="Middle",
        pivot_point="Bottom Left",
    ).curve_instances
    label = transform_geometry(
        geometry=fill_curve(curve=text_curve, mode="Triangles", fill_rule="Even-Odd").set_material(material=text_material),
        translation=(0.0, 0.0, 0.30000001192092896),
    )
    label_or_empty = switch(input_type=Switch.InputType.GEOMETRY, switch=showlabel, false=_empty_curve_geometry(), true=label)

    rail_seed = mesh_line(
        mode=MeshLine.Mode.OFFSET,
        count_mode=MeshLine.CountMode.TOTAL,
        count=resolution,
        start_location=(0.0, 0.0, 0.0),
        offset=(0.0, 0.0, 1.0),
    )
    rail = mesh_to_curve(mode=MeshToCurve.Mode.EDGES, mesh=rail_seed).set_position(position=combine_xyz(x=x, y=y, z=z))
    profile = curve_circle(mode=CurveCircle.Mode.RADIUS, resolution=32, radius=thickness)
    radius_attribute = named_attribute(data_type=NamedAttribute.DataType.FLOAT, name="radius")
    radius_scale = switch(input_type=Switch.InputType.FLOAT, switch=radius_attribute.exists, false=1.0, true=radius_attribute.attribute)
    curve_mesh = rail.curve_to_mesh(profile_curve=profile, scale=radius_scale, fill_caps=False).set_material(material=curve_material)
    return {"Geometry": join_geometry(geometry=[label_or_empty, curve_mesh])}


def _finalize_groups():
    import bpy

    groups = []
    for name in (
        "VG Param Epicycloid X",
        "VG Param Epicycloid Y",
        "VG Polar Spiral X",
        "VG Polar Spiral Y",
        "VG Choose Float Val",
        "VG Choose Str Val",
        "VG Param XY",
        "VG Archimedes Spiral",
        "VG Epicycloid",
        "VG Mirrored Root Spiral",
        "VG Param Curve",
    ):
        group = bpy.data.node_groups.get(name)
        if group:
            group.use_fake_user = True
            groups.append(group)
    return groups


_finalize_groups()


if __name__ == "__main__":
    for group in _finalize_groups():
        print(
            "VG_PARAMNPOLAREQ_GROUP",
            group.name,
            len(group.nodes),
            len(group.links),
            sorted(set(node.bl_idname for node in group.nodes)),
        )

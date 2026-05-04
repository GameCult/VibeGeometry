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


def _finalize_groups():
    import bpy

    groups = []
    for name in (
        "VG Param Epicycloid X",
        "VG Param Epicycloid Y",
        "VG Polar Spiral X",
        "VG Polar Spiral Y",
        "VG Archimedes Spiral",
        "VG Epicycloid",
        "VG Mirrored Root Spiral",
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

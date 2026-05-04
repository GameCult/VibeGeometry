"""Geometry Script footholds from Blender's raycast minigame demo."""

try:
    from tools.geometry_script_loader import load_repo_geometry_script
except ModuleNotFoundError:
    import sys
    from pathlib import Path

    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
    from tools.geometry_script_loader import load_repo_geometry_script

load_repo_geometry_script()

from geometry_script import *  # noqa: F403 - Geometry Script exposes node functions as DSL globals.


@tree("VG Initial Direction")
def vg_initial_direction(rotation: Vector = (0.0, 0.0, 0.0)):
    forward = combine_xyz(x=1.0, y=0.0, z=0.0)
    return {
        "Vector": vector_rotate(
            rotation_type="EULER_XYZ",
            invert=False,
            vector=forward,
            center=(0.0, 0.0, 0.0),
            rotation=rotation,
        )
    }


@tree("VG Line To Be Casted")
def vg_line_to_be_casted(
    start_pos: Vector = (0.0, 0.0, 0.0),
    line_size: Int = 3,
):
    seed_line = curve_line(mode=CurveLine.Mode.POINTS, start=(0.0, 0.0, 0.0), end=(0.0, 0.0, 0.0))
    placed = set_position(geometry=seed_line, position=start_pos, offset=(0.0, 0.0, 0.0))
    return {
        "Line": resample_curve(
            keep_last_segment=False,
            curve=placed,
            mode="Count",
            count=line_size,
            length=0.10000000149011612,
        )
    }


@tree("VG Cast Rays")
def vg_cast_rays(
    line: Geometry,
    ray_direction: Vector = (0.0, 0.0, 0.0),
    traveled_distance: Float = 0.0,
    hit_index: Int = 1,
    target: Object = None,
):
    active_point = compare(
        operation=Compare.Operation.EQUAL,
        data_type=Compare.DataType.INT,
        mode=Compare.Mode.ELEMENT,
        a=index(),
        b=hit_index,
    )
    target_info = object_info(transform_space="RELATIVE", object=target, as_instance=False)
    previous_index = math(operation=Math.Operation.SUBTRACT, value=(hit_index, integer(integer=1)))
    previous_position = sample_index(
        data_type=SampleIndex.DataType.FLOAT_VECTOR,
        domain=SampleIndex.Domain.POINT,
        clamp=True,
        geometry=line,
        value=position(),
        index=previous_index,
    )
    hit = raycast(
        data_type="FLOAT_VECTOR",
        target_geometry=target_info.geometry,
        interpolation="Nearest",
        source_position=previous_position,
        ray_direction=ray_direction,
        ray_length=20.0,
    )
    hit_position = vector_math(operation=VectorMath.Operation.SCALE, vector=hit.hit_position, scale=0.9990000128746033)
    updated_line = set_position(geometry=line, selection=active_point, position=hit_position, offset=(0.0, 0.0, 0.0))
    return {
        "Line": updated_line,
        "Reflected Direction": vector_math(operation=VectorMath.Operation.REFLECT, vector=(ray_direction, hit.hit_normal)),
        "Traveled Distance": math(operation=Math.Operation.ADD, value=(hit.hit_distance, traveled_distance)),
        "Next Hit Index": math(operation=Math.Operation.ADD, value=(hit_index, integer(integer=1))),
    }


def _finalize_groups():
    import bpy

    groups = []
    for name in ("VG Initial Direction", "VG Line To Be Casted", "VG Cast Rays"):
        group = bpy.data.node_groups.get(name)
        if group:
            group.use_fake_user = True
            groups.append(group)
    return groups


_finalize_groups()


if __name__ == "__main__":
    for group in _finalize_groups():
        print(
            "VG_RAYCAST_GROUP",
            group.name,
            len(group.nodes),
            len(group.links),
            sorted(set(node.bl_idname for node in group.nodes)),
        )

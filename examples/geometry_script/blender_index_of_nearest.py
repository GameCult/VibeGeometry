"""Geometry Script footholds from Blender's index_of_nearest demo."""

try:
    from tools.geometry_script_loader import load_repo_geometry_script
except ModuleNotFoundError:
    import sys
    from pathlib import Path

    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
    from tools.geometry_script_loader import load_repo_geometry_script

load_repo_geometry_script()

from geometry_script import *  # noqa: F403 - Geometry Script exposes node functions as DSL globals.


@tree("VG Boundary Step")
def vg_boundary_step(
    geometry: Geometry,
    vector: Vector = (0.0, 0.0, 0.0),
    b: Float = 0.05000000074505806,
):
    from_center = vector_math(operation=VectorMath.Operation.SUBTRACT, vector=(position(), vector))
    distance = vector_math(operation=VectorMath.Operation.LENGTH, vector=from_center)
    outside = compare(
        operation=Compare.Operation.GREATER_THAN,
        data_type=Compare.DataType.FLOAT,
        mode=Compare.Mode.ELEMENT,
        a=distance,
        b=b,
    )
    clamped_xy = vector_math(
        operation=VectorMath.Operation.MULTIPLY,
        vector=(vector_math(operation=VectorMath.Operation.SCALE, vector=vector_math(operation=VectorMath.Operation.NORMALIZE, vector=from_center), scale=b), (1.0, 1.0, 0.0)),
    )
    return {"Geometry": set_position(geometry=geometry, selection=outside, position=clamped_xy, offset=(0.0, 0.0, 0.0))}


@tree("VG Update Velocity")
def vg_update_velocity(
    current_velocity: Vector = (0.0, 0.0, 0.0),
    last_position: Vector = (0.0, 0.0, 0.0),
):
    movement = vector_math(operation=VectorMath.Operation.SUBTRACT, vector=(position(), last_position))
    damped_movement = vector_math(operation=VectorMath.Operation.SCALE, vector=movement, scale=0.9599999785423279)
    planar_movement = vector_math(operation=VectorMath.Operation.MULTIPLY, vector=(damped_movement, (1.0, 1.0, 0.0)))
    fast_enough = compare(
        operation=Compare.Operation.GREATER_THAN,
        data_type=Compare.DataType.FLOAT,
        mode=Compare.Mode.ELEMENT,
        a=vector_math(operation=VectorMath.Operation.LENGTH, vector=planar_movement),
        b=0.009999999776482582,
    )
    blended = vector_math(
        operation=VectorMath.Operation.ADD,
        vector=(
            vector_math(operation=VectorMath.Operation.SCALE, vector=current_velocity, scale=0.75),
            vector_math(operation=VectorMath.Operation.SCALE, vector=planar_movement, scale=0.25),
        ),
    )
    capped = vector_math(
        operation=VectorMath.Operation.SCALE,
        vector=vector_math(operation=VectorMath.Operation.NORMALIZE, vector=damped_movement),
        scale=0.009999999776482582,
    )
    return {"velocity": switch(input_type=Switch.InputType.VECTOR, switch=fast_enough, false=blended, true=capped)}


@tree("VG Collision Step")
def vg_collision_step(geometry: Geometry):
    current_position = position()
    neighbor = index_of_nearest(position=position())
    neighbor_position = evaluate_at_index(
        domain="POINT",
        data_type="FLOAT_VECTOR",
        value=position(),
        index=neighbor.index,
    )
    from_neighbor = vector_math(operation=VectorMath.Operation.SUBTRACT, vector=(current_position, neighbor_position))
    too_close = compare(
        operation=Compare.Operation.LESS_THAN,
        data_type=Compare.DataType.FLOAT,
        mode=Compare.Mode.ELEMENT,
        a=vector_math(operation=VectorMath.Operation.LENGTH, vector=from_neighbor),
        b=radius(),
    )
    push_strength = math(operation=Math.Operation.MULTIPLY, value=(too_close, 0.02500000037252903))
    push = vector_math(
        operation=VectorMath.Operation.MULTIPLY,
        vector=(vector_math(operation=VectorMath.Operation.SCALE, vector=from_neighbor, scale=push_strength), (1.0, 1.0, 0.0)),
    )
    return {"Geometry": set_position(geometry=geometry, offset=push)}


@tree("VG Collider Step")
def vg_collider_step(geometry: Geometry, collider: Object = None):
    collider_info = object_info(transform_space="ORIGINAL", object=collider, as_instance=False)
    from_collider = vector_math(operation=VectorMath.Operation.SUBTRACT, vector=(position(), collider_info.location))
    collider_radius = vector_math(operation=VectorMath.Operation.ABSOLUTE, vector=collider_info.scale)
    inside = compare(
        operation=Compare.Operation.LESS_THAN,
        data_type=Compare.DataType.FLOAT,
        mode=Compare.Mode.ELEMENT,
        a=vector_math(operation=VectorMath.Operation.LENGTH, vector=from_collider),
        b=collider_radius,
    )
    clamped = vector_math(
        operation=VectorMath.Operation.ADD,
        vector=(
            vector_math(
                operation=VectorMath.Operation.SCALE,
                vector=vector_math(operation=VectorMath.Operation.NORMALIZE, vector=from_collider),
                scale=collider_radius,
            ),
            collider_info.location,
        ),
    )
    planar_clamped = vector_math(operation=VectorMath.Operation.MULTIPLY, vector=(clamped, (1.0, 1.0, 0.0)))
    return {"Geometry": set_position(geometry=geometry, selection=inside, position=planar_clamped, offset=(0.0, 0.0, 0.0))}


def _finalize_groups():
    import bpy

    groups = []
    for name in (
        "VG Boundary Step",
        "VG Update Velocity",
        "VG Collision Step",
        "VG Collider Step",
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
            "VG_INDEX_OF_NEAREST_GROUP",
            group.name,
            len(group.nodes),
            len(group.links),
            sorted(set(node.bl_idname for node in group.nodes)),
        )

"""Geometry Script recreation of Blender's instance_attribtues.blend demo graph."""

try:
    from tools.geometry_script_loader import load_repo_geometry_script
except ModuleNotFoundError:
    import sys
    from pathlib import Path

    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
    from tools.geometry_script_loader import load_repo_geometry_script

load_repo_geometry_script()

from geometry_script import *  # noqa: F403 - Geometry Script exposes node functions as DSL globals.
from geometry_script.api.node_mapper import OutputsList, set_or_create_link
from geometry_script.api.state import State
from geometry_script.api.types import Type


def _capture_attribute_item(data_type: str, domain: str, geometry, value, name: str):
    node = State.current_node_tree.nodes.new("GeometryNodeCaptureAttribute")
    node.capture_items.new(data_type, name)
    node.active_index = 0
    node.domain = domain
    set_or_create_link(geometry, node.inputs[0])
    set_or_create_link(value, node.inputs[1])
    return OutputsList({"geometry": Type(node.outputs[0]), name.lower().replace(" ", "_"): Type(node.outputs[1])})


@tree("VG Grass Tuft Generator")
def vg_grass_tuft_generator(
    geometry: Geometry,
    height: Float = 0.20000000298023224,
    radius: Float = 0.05000000074505806,
    density: Float = 1.0,
    thickness: Float = 0.009999999776482582,
    curl: Float = 0.5,
    seed: Int = 0,
):
    del geometry

    base_disc = mesh_circle(fill_type=MeshCircle.FillType.TRIANGLE_FAN, vertices=12, radius=radius)
    scattered_surface = subdivide_mesh(mesh=base_disc, level=3)
    radial_distance = vector_math(operation=VectorMath.Operation.LENGTH, vector=position())
    radial_falloff = map_range(
        clamp=True,
        interpolation_type="SMOOTHSTEP",
        data_type="FLOAT",
        value=radial_distance,
        from_min=0.0,
        from_max=radius,
        to_min=1.0,
        to_max=0.38999998569488525,
    )
    points = distribute_points_on_faces(
        distribute_method="POISSON",
        use_legacy_normal=True,
        mesh=scattered_surface,
        distance_min=math(
            operation=Math.Operation.DIVIDE,
            value=(math(operation=Math.Operation.MULTIPLY, value=(thickness, 2.0)), density),
        ),
        density_max=math(operation=Math.Operation.MULTIPLY, value=(density, 5000.0)),
        density_factor=radial_falloff,
        seed=seed,
    )

    blade_spine = mesh_line(
        mode=MeshLine.Mode.END_POINTS,
        count_mode=MeshLine.CountMode.TOTAL,
        count=5,
        start_location=(0.0, 0.0, 0.0),
        offset=combine_xyz(x=0.0, y=0.0, z=height),
    )
    blade_curve = mesh_to_curve(mode="EDGES", mesh=blade_spine)
    taper = math(operation=Math.Operation.SUBTRACT, value=(1.0, spline_parameter().factor))
    tapered_blade = set_curve_radius(curve=blade_curve, radius=taper)

    instances = instance_on_points(
        points=points.points,
        instance=tapered_blade,
        pick_instance=False,
        rotation=(0.0, 0.0, 0.0),
        scale=(1.0, 1.0, 1.0),
    )
    scaled_instances = scale_instances(
        instances=instances,
        scale=radial_falloff,
        center=(0.0, 0.0, 0.0),
        local_space=True,
    )
    roots = _capture_attribute_item("VECTOR", "INSTANCE", scaled_instances, position(), "Value")
    realized_blades = realize_instances(
        realize_to_point_domain=True,
        geometry=roots.geometry,
        realize_all=True,
        depth=0,
    )

    root_position = roots.value
    tangent_axis = vector_rotate(
        rotation_type="Z_AXIS",
        invert=False,
        vector=vector_math(operation=VectorMath.Operation.NORMALIZE, vector=root_position),
        center=(0.0, 0.0, 0.0),
        angle=1.5707963705062866,
    )
    root_distance = vector_math(operation=VectorMath.Operation.LENGTH, vector=root_position)
    curl_falloff = map_range(
        clamp=True,
        interpolation_type="SMOOTHSTEP",
        data_type="FLOAT",
        value=root_distance,
        from_min=0.0,
        from_max=radius,
        to_min=0.20000000298023224,
        to_max=2.0,
    )
    curl_angle = math(
        operation=Math.Operation.MULTIPLY,
        value=(math(operation=Math.Operation.MULTIPLY, value=(spline_parameter().factor, curl)), curl_falloff),
    )
    curled_position = vector_rotate(
        rotation_type="AXIS_ANGLE",
        invert=False,
        vector=position(),
        center=root_position,
        axis=tangent_axis,
        angle=curl_angle,
    )
    curled_blades = set_position(geometry=realized_blades, position=curled_position, offset=(0.0, 0.0, 0.0))

    profile = curve_circle(mode=CurveCircle.Mode.RADIUS, resolution=3, radius=thickness)
    radius_attribute = named_attribute(data_type=NamedAttribute.DataType.FLOAT, name="radius")
    radius_scale = switch(input_type=Switch.InputType.FLOAT, switch=radius_attribute.exists, false=1.0, true=radius_attribute.attribute)
    mesh = curve_to_mesh(curve=curled_blades, profile_curve=profile, scale=radius_scale, fill_caps=False)
    smooth_mesh = set_shade_smooth(domain=SetShadeSmooth.Domain.FACE, mesh=mesh, shade_smooth=False)
    return {"Geometry": set_material(geometry=smooth_mesh, material=None)}


def _finalize_groups():
    import bpy

    groups = []
    for name in ("VG Grass Tuft Generator",):
        group = bpy.data.node_groups.get(name)
        if group:
            group.use_fake_user = True
            groups.append(group)
    return groups


_finalize_groups()


if __name__ == "__main__":
    for group in _finalize_groups():
        print(
            "VG_INSTANCE_ATTRIBUTES_GROUP",
            group.name,
            len(group.nodes),
            len(group.links),
            sorted(set(node.bl_idname for node in group.nodes)),
        )

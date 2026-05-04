"""Geometry Script footholds from IRCSS/Blender-Geometry-Node-French-Houses."""

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


@tree("VG Make Spiral")
def vg_make_spiral(
    frequency: Float = 12.0,
    radius: Float = 1.0,
    height: Float = 3.0,
    height_radius_gain: Float = 0.0,
):
    rail = curve_line(mode=CurveLine.Mode.POINTS, start=(0.0, 0.0, 0.0), end=(0.0, 0.0, 1.0))
    samples = resample_curve(keep_last_segment=True, curve=rail, mode="Count", count=200, length=0.10000000149011612)
    point_count = domain_size(component="CURVE", geometry=samples).point_count
    t = math(operation=Math.Operation.DIVIDE, value=(index(), point_count))
    theta = math(operation=Math.Operation.MULTIPLY, value=(t, frequency))
    expanding_radius = math(
        operation=Math.Operation.ADD,
        value=(radius, math(operation=Math.Operation.MULTIPLY, value=(t, height_radius_gain))),
    )
    x = math(
        operation=Math.Operation.MULTIPLY,
        value=(math(operation=Math.Operation.SINE, value=theta), expanding_radius),
    )
    y = math(
        operation=Math.Operation.MULTIPLY,
        value=(math(operation=Math.Operation.COSINE, value=theta), expanding_radius),
    )
    z = math(operation=Math.Operation.MULTIPLY, value=(t, height))
    return {"Geometry": set_position(geometry=samples, position=combine_xyz(x=x, y=y, z=z), offset=(0.0, 0.0, 0.0))}


@tree("VG Pointy Gothic Cone")
def vg_pointy_gothic_cone(
    geometry: Geometry,
    column_radius: Float = 0.3,
    peak_height: Float = 1.0,
    gothic_detail_density: Float = 0.6,
    detail_scale: Float = 0.1,
    spawn_details: Bool = True,
    rotation: Rotation = (0.0, 0.0, 0.0),
):
    point_positions = _capture_attribute_item("VECTOR", "POINT", geometry, position(), "source position")

    cone_seed = cylinder(fill_type="NGON", vertices=6, side_segments=1, fill_segments=1, radius=1.0, depth=1.0)
    raised_cone = set_position(geometry=cone_seed.mesh, offset=(0.0, 0.0, 0.5))
    tapered_cone = scale_elements(
        domain="FACE",
        geometry=raised_cone,
        selection=cone_seed.top,
        scale=0.10000002384185791,
        scale_mode="Uniform",
        axis=(1.0, 0.0, 0.0),
    )

    not_side = boolean_math(operation="NOT", boolean=cone_seed.side)
    cap_or_body_edge = boolean_math(
        operation="OR",
        boolean=(boolean_math(operation="OR", boolean=(not_side, cone_seed.top)), cone_seed.bottom),
    )
    cone_edge_flags = _capture_attribute_item("BOOLEAN", "EDGE", tapered_cone, cap_or_body_edge, "edge trim")

    scaled_cone_position = vector_math(
        operation="MULTIPLY",
        vector=(position(), combine_xyz(x=1.0, y=1.0, z=peak_height)),
    )
    shaped_cone = set_position(geometry=cone_edge_flags.geometry, position=scaled_cone_position, offset=(0.0, 0.0, 0.0))

    skirt_depth = math(
        operation="MINIMUM",
        value=(math(operation="MULTIPLY", value=(peak_height, 0.20000000298023224)), 1.0),
    )
    cone_with_skirt = extrude_mesh(
        mode="FACES",
        mesh=shaped_cone,
        selection=cone_seed.bottom,
        offset_scale=skirt_depth,
        individual=False,
    )

    cone_scale = combine_xyz(x=column_radius, y=column_radius, z=1.0)
    cone_instances = instance_on_points(
        points=point_positions.geometry,
        instance=cone_with_skirt.mesh,
        pick_instance=False,
        rotation=rotation,
        scale=cone_scale,
    )
    realized_cones = realize_instances(
        realize_to_point_domain=True,
        geometry=cone_instances,
        realize_all=True,
        depth=0,
    )

    details_disabled = boolean_math(operation="NOT", boolean=spawn_details)
    cone_for_detail_edges = delete_geometry(mode="ALL", domain="POINT", geometry=realized_cones, selection=details_disabled)
    cone_ribs = delete_geometry(mode="ALL", domain="EDGE", geometry=cone_for_detail_edges, selection=cone_edge_flags.edge_trim)
    rib_curve = mesh_to_curve(mode="EDGES", mesh=cone_ribs)
    detail_points = resample_curve(
        keep_last_segment=True,
        curve=rib_curve,
        mode="Length",
        count=5,
        length=gothic_detail_density,
    )

    from_source_point = vector_math(operation="SUBTRACT", vector=(position(), point_positions.source_position))
    z_from_source = separate_xyz(vector=from_source_point)
    below_peak = compare(
        operation="LESS_THAN",
        data_type="FLOAT",
        mode="ELEMENT",
        a=math(operation="SUBTRACT", value=(math(operation="ABSOLUTE", value=z_from_source.z), peak_height)),
        b=-0.09999924898147583,
    )

    detail_seed = cylinder(fill_type="NGON", vertices=5, side_segments=1, fill_segments=1, radius=1.0, depth=1.0)
    detail_taper = scale_elements(
        domain="FACE",
        geometry=detail_seed.mesh,
        selection=detail_seed.top,
        scale=0.20000001788139343,
        scale_mode="Uniform",
        axis=(1.0, 0.0, 0.0),
    )
    raised_detail = set_position(geometry=detail_taper, offset=(0.0, 0.0, 0.30000001192092896))
    stretched_detail = set_position(
        geometry=raised_detail,
        position=vector_math(operation="MULTIPLY", vector=(position(), (1.0, 1.0, 2.0))),
        offset=(0.0, 0.0, 0.0),
    )
    horizontal_rib_direction = vector_math(operation="MULTIPLY", vector=(from_source_point, (1.0, 1.0, 0.0)))
    detail_rotation = align_rotation_to_vector(axis="Z", pivot_axis="AUTO", factor=1.0, vector=horizontal_rib_direction)
    detail_instances = instance_on_points(
        points=detail_points,
        selection=below_peak,
        instance=stretched_detail,
        pick_instance=False,
        rotation=detail_rotation,
        scale=detail_scale,
    )
    realized_details = realize_instances(
        realize_to_point_domain=True,
        geometry=detail_instances,
        realize_all=True,
        depth=0,
    )
    return {"Geometry": join_geometry(geometry=[realized_cones, realized_details])}


def _finalize_groups():
    import bpy

    groups = []
    for name in ("VG Make Spiral", "VG Pointy Gothic Cone"):
        group = bpy.data.node_groups.get(name)
        if group:
            group.use_fake_user = True
            groups.append(group)
    return groups


_finalize_groups()


if __name__ == "__main__":
    for group in _finalize_groups():
        print(
            "VG_IRCSS_GROUP",
            group.name,
            len(group.nodes),
            len(group.links),
            sorted(set(node.bl_idname for node in group.nodes)),
        )

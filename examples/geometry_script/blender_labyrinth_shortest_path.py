"""Geometry Script recreation of Blender's shortest-path labyrinth demo."""

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
    return OutputsList({"geometry": Type(node.outputs[0]), name.lower().replace(" ", "_").replace("/", "_"): Type(node.outputs[1])})


@tree("VG Solvable Labyrinth Generator")
def vg_solvable_labyrinth_generator(
    geometry: Geometry,
    size: Int = 20,
    seed: Int = 247,
    solve: Float = 1.0,
):
    del geometry

    base = grid(size_x=1.0, size_y=1.0, vertices_x=size, vertices_y=size)
    base_with_uv = store_named_attribute(
        data_type=StoreNamedAttribute.DataType.FLOAT_VECTOR,
        domain=StoreNamedAttribute.Domain.CORNER,
        geometry=base.mesh,
        name="uv_map",
        value=base.uv_map,
    )

    start_vertex = compare(
        operation=Compare.Operation.EQUAL,
        data_type=Compare.DataType.INT,
        mode=Compare.Mode.ELEMENT,
        a=index(),
        b=0,
    )
    sparse_edges = compare(
        operation=Compare.Operation.LESS_THAN,
        data_type=Compare.DataType.INT,
        mode=Compare.Mode.ELEMENT,
        a=edge_neighbors(),
        b=2,
    )
    random_cost = random_value(data_type=RandomValue.DataType.BOOLEAN, probability=0.5, seed=seed)
    edge_cost = switch(input_type=Switch.InputType.FLOAT, switch=sparse_edges, false=random_cost, true=0.0)
    random_paths = shortest_edge_paths(end_vertex=start_vertex, edge_cost=edge_cost)
    random_path_selection = edge_paths_to_selection(next_vertex_index=random_paths.next_vertex_index)
    captured_maze_edges = _capture_attribute_item("BOOLEAN", "EDGE", base_with_uv, random_path_selection, "Path")

    subdivided = subdivide_mesh(mesh=captured_maze_edges.geometry, level=1)
    carved_walkable = delete_geometry(
        mode=DeleteGeometry.Mode.ALL,
        domain=DeleteGeometry.Domain.POINT,
        geometry=subdivided,
        selection=captured_maze_edges.path,
    )

    parts = separate_xyz(vector=position())
    direct_paths = shortest_edge_paths(end_vertex=start_vertex)
    direct_selection = edge_paths_to_selection(next_vertex_index=direct_paths.next_vertex_index)
    x_stats_on_path = attribute_statistic(
        data_type=AttributeStatistic.DataType.FLOAT,
        domain=AttributeStatistic.Domain.POINT,
        geometry=carved_walkable,
        selection=direct_selection,
        attribute=parts.x,
    )
    far_x_vertices = compare(
        operation=Compare.Operation.EQUAL,
        data_type=Compare.DataType.FLOAT,
        mode=Compare.Mode.ELEMENT,
        a=parts.x,
        b=x_stats_on_path.max,
        epsilon=0.0010000000474974513,
    )
    solution_curves = edge_paths_to_curves(
        mesh=carved_walkable,
        start_vertices=far_x_vertices,
        next_vertex_index=direct_paths.next_vertex_index,
    )

    marker_radius = math(operation=Math.Operation.DIVIDE, value=(0.10000000149011612, size))
    marker_mesh = ico_sphere(radius=marker_radius, subdivisions=3)
    marker_with_uv = store_named_attribute(
        data_type=StoreNamedAttribute.DataType.FLOAT_VECTOR,
        domain=StoreNamedAttribute.Domain.CORNER,
        geometry=marker_mesh.mesh,
        name="UVMap",
        value=marker_mesh.uv_map,
    )
    endpoint_markers = instance_on_points(
        points=solution_curves,
        selection=endpoint_selection(start_size=1, end_size=1),
        instance=marker_with_uv,
        pick_instance=False,
        rotation=(0.0, 0.0, 0.0),
        scale=3.0,
    )
    marker_indices = _capture_attribute_item("INT", "INSTANCE", endpoint_markers, index(), "Start End")
    realized_markers = realize_instances(
        realize_to_point_domain=True,
        geometry=marker_indices.geometry,
        realize_all=True,
        depth=0,
    )
    marker_geometry = set_material(geometry=realized_markers, material=None)

    trimmed_solution = trim_curve(mode=TrimCurve.Mode.FACTOR, curve=solution_curves, start=0.0, end=solve)
    captured_solution = _capture_attribute_item("BOOLEAN", "CURVE", trimmed_solution, True, "Path")
    maze_walls_source = delete_geometry(
        mode=DeleteGeometry.Mode.ALL,
        domain=DeleteGeometry.Domain.POINT,
        geometry=subdivided,
        selection=boolean_math(operation=BooleanMath.Operation.NOT, boolean=captured_maze_edges.path),
    )
    wall_curves = mesh_to_curve(mode="EDGES", mesh=maze_walls_source)
    all_curves = join_geometry(geometry=[captured_solution.geometry, wall_curves])
    filleted = fillet_curve(curve=all_curves, radius=0.004999999888241291, limit_radius=True, mode="Poly", count=6)
    curve_radius = switch(input_type=Switch.InputType.FLOAT, switch=captured_solution.path, false=2.0, true=1.0)
    radius_curves = set_curve_radius(curve=filleted, radius=curve_radius)

    smoothed_marker = set_shade_smooth(domain=SetShadeSmooth.Domain.FACE, mesh=marker_with_uv, shade_smooth=True)
    curve_endpoint_markers = instance_on_points(
        points=radius_curves,
        selection=endpoint_selection(start_size=1, end_size=1),
        instance=smoothed_marker,
        pick_instance=False,
        rotation=(0.0, 0.0, 0.0),
        scale=radius(),
    )
    realized_curve_markers = realize_instances(
        realize_to_point_domain=True,
        geometry=curve_endpoint_markers,
        realize_all=True,
        depth=0,
    )
    profile = curve_circle(mode=CurveCircle.Mode.RADIUS, resolution=16, radius=marker_radius)
    radius_attribute = named_attribute(data_type=NamedAttribute.DataType.FLOAT, name="radius")
    profile_scale = switch(input_type=Switch.InputType.FLOAT, switch=radius_attribute.exists, false=1.0, true=radius_attribute.attribute)
    path_mesh = curve_to_mesh(curve=radius_curves, profile_curve=profile, scale=profile_scale, fill_caps=False)
    curve_geometry = set_material(geometry=join_geometry(geometry=[realized_curve_markers, path_mesh]), material=None)
    base_geometry = set_material(geometry=base_with_uv, material=None)
    return {
        "Geometry": join_geometry(geometry=[marker_geometry, curve_geometry, base_geometry]),
        "Path": captured_solution.path,
        "Start/End": marker_indices.start_end,
    }


def _finalize_groups():
    import bpy

    groups = []
    for name in ("VG Solvable Labyrinth Generator",):
        group = bpy.data.node_groups.get(name)
        if group:
            group.use_fake_user = True
            groups.append(group)
    return groups


_finalize_groups()


if __name__ == "__main__":
    for group in _finalize_groups():
        print(
            "VG_LABYRINTH_GROUP",
            group.name,
            len(group.nodes),
            len(group.links),
            sorted(set(node.bl_idname for node in group.nodes)),
        )

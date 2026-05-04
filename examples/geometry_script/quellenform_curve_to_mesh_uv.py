"""Geometry Script footholds from quellenform/blender-CurveToMeshUV."""

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


@tree("VG Auto Smooth")
def vg_auto_smooth(geometry: Geometry, angle: Float = 0.0):
    shallow_enough = compare(
        operation=Compare.Operation.LESS_EQUAL,
        data_type=Compare.DataType.FLOAT,
        mode=Compare.Mode.ELEMENT,
        a=edge_angle().unsigned_angle,
        b=angle,
    )
    preserve_smooth_face = boolean_math(
        operation=BooleanMath.Operation.AND,
        boolean=(shallow_enough, is_face_smooth()),
    )
    edge_pass = set_shade_smooth(
        domain=SetShadeSmooth.Domain.EDGE,
        mesh=geometry,
        selection=is_edge_smooth(),
        shade_smooth=preserve_smooth_face,
    )
    face_pass = set_shade_smooth(
        domain=SetShadeSmooth.Domain.FACE,
        mesh=edge_pass,
        selection=True,
        shade_smooth=True,
    )
    return {"Geometry": face_pass}


@tree("VG Curve To Mesh UV")
def vg_curve_to_mesh_uv(
    curve: Geometry,
    profile_curve: Geometry,
    fill_caps: Bool = False,
    lock_caps_uv_scaling: Bool = False,
    hole_tolerant: Bool = False,
    smooth_angle: Float = 3.1415927410125732,
    free_u_space: Bool = False,
    lock_u_scaling: Bool = False,
    free_v_space: Bool = False,
    lock_v_scaling: Bool = False,
    sides_uv_scale: Vector = (1.0, 1.0, 0.0),
    sides_uv_offset: Vector = (0.0, 0.0, 0.0),
    sides_uv_z_rotation: Float = 0.0,
    caps_uv_scale: Vector = (1.0, 1.0, 0.0),
    caps_uv_offset: Vector = (0.0, 0.0, 0.0),
    caps_uv_z_rotation: Float = 0.0,
    store_attributes: Bool = False,
):
    del lock_caps_uv_scaling
    del hole_tolerant
    del smooth_angle
    del free_u_space
    del lock_u_scaling
    del free_v_space
    del lock_v_scaling
    del sides_uv_scale
    del sides_uv_offset
    del sides_uv_z_rotation
    del caps_uv_scale
    del caps_uv_offset
    del caps_uv_z_rotation
    del store_attributes

    resampled_curve = resample_curve(
        curve=curve,
        mode="Evaluated",
        keep_last_segment=False,
    )
    cyclic_start = boolean_math(
        operation=BooleanMath.Operation.AND,
        boolean=(endpoint_selection(start_size=1, end_size=0), is_spline_cyclic()),
    )
    curve_parameter = spline_parameter()
    curve_length = spline_length()
    curve_point_index = switch(
        input_type=Switch.InputType.INT,
        switch=cyclic_start,
        false=curve_parameter.index,
        true=curve_length.point_count,
    )
    curve_point_triplet = combine_xyz(x=curve_point_index, y=curve_parameter.index, z=curve_length.point_count)
    curve_points = _capture_attribute_item("VECTOR", "POINT", resampled_curve, curve_point_triplet, "curve point triplet")
    curve_indices = _capture_attribute_item("INT", "CURVE", curve_points.geometry, index(), "curve index")

    resampled_profile = resample_curve(
        curve=profile_curve,
        mode="Evaluated",
        keep_last_segment=False,
    )
    profile_points = _capture_attribute_item("VECTOR", "POINT", resampled_profile, curve_point_triplet, "profile point triplet")
    profile_curve_indices = _capture_attribute_item("INT", "CURVE", profile_points.geometry, index(), "profile curve index")
    profile_point_indices = _capture_attribute_item("INT", "POINT", profile_curve_indices.geometry, index(), "profile point index")

    radius_attribute = named_attribute(data_type=NamedAttribute.DataType.FLOAT, name="radius")
    radius_scale = switch(input_type=Switch.InputType.FLOAT, switch=radius_attribute.exists, false=1.0, true=radius_attribute.attribute)
    mesh = curve_to_mesh(
        curve=curve_indices.geometry,
        profile_curve=profile_point_indices.geometry,
        scale=radius_scale,
        fill_caps=fill_caps,
    )

    profile_curve_count = domain_size(component="CURVE", geometry=profile_curve_indices.geometry)
    corner_group = math(
        operation=Math.Operation.ADD,
        value=(
            math(operation=Math.Operation.MULTIPLY, value=(curve_indices.curve_index, profile_curve_count.spline_count)),
            profile_curve_indices.profile_curve_index,
        ),
    )
    corner_counter = accumulate_field(
        data_type=AccumulateField.DataType.INT,
        domain=AccumulateField.Domain.CORNER,
        value=1,
        group_id=corner_group,
    ).trailing

    curve_cyclic = sample_index(
        data_type=SampleIndex.DataType.BOOLEAN,
        domain=SampleIndex.Domain.CURVE,
        clamp=True,
        geometry=curve_indices.geometry,
        value=is_spline_cyclic(),
        index=curve_indices.curve_index,
    )
    source_curve_length = spline_length()
    source_curve_point_count = switch(
        input_type=Switch.InputType.INT,
        switch=curve_cyclic,
        false=math(operation=Math.Operation.SUBTRACT, value=(source_curve_length.point_count, 1.0)),
        true=source_curve_length.point_count,
    )
    source_curve_points = sample_index(
        data_type=SampleIndex.DataType.INT,
        domain=SampleIndex.Domain.CURVE,
        clamp=True,
        geometry=curve_indices.geometry,
        value=source_curve_point_count,
        index=curve_indices.curve_index,
    )

    profile_cyclic = sample_index(
        data_type=SampleIndex.DataType.BOOLEAN,
        domain=SampleIndex.Domain.CURVE,
        clamp=True,
        geometry=profile_curve_indices.geometry,
        value=is_spline_cyclic(),
        index=profile_curve_indices.profile_curve_index,
    )
    source_profile_length = spline_length()
    source_profile_point_count = switch(
        input_type=Switch.InputType.INT,
        switch=profile_cyclic,
        false=math(operation=Math.Operation.SUBTRACT, value=(source_profile_length.point_count, 1.0)),
        true=source_profile_length.point_count,
    )
    source_profile_points = sample_index(
        data_type=SampleIndex.DataType.INT,
        domain=SampleIndex.Domain.CURVE,
        clamp=True,
        geometry=profile_curve_indices.geometry,
        value=source_profile_point_count,
        index=profile_curve_indices.profile_curve_index,
    )
    cap_start = math(
        operation=Math.Operation.MULTIPLY,
        value=(source_curve_points, math(operation=Math.Operation.MULTIPLY, value=(source_profile_points, 4.0))),
    )
    caps_mask = compare(
        operation=Compare.Operation.GREATER_EQUAL,
        data_type=Compare.DataType.FLOAT,
        mode=Compare.Mode.ELEMENT,
        a=corner_counter,
        b=cap_start,
    )

    corner_mod = math(operation=Math.Operation.MODULO, value=(index(), 4.0))
    use_curve_y = compare(
        operation=Compare.Operation.LESS_EQUAL,
        data_type=Compare.DataType.INT,
        mode=Compare.Mode.ELEMENT,
        a=corner_mod,
        b=1,
    )
    curve_triplet = separate_xyz(vector=curve_points.curve_point_triplet)
    side_u = switch(input_type=Switch.InputType.FLOAT, switch=use_curve_y, false=curve_triplet.x, true=curve_triplet.y)

    profile_mod = math(operation=Math.Operation.MODULO, value=(index(), 4.0))
    use_profile_y = compare(
        operation=Compare.Operation.NOT_EQUAL,
        data_type=Compare.DataType.FLOAT,
        mode=Compare.Mode.ELEMENT,
        a=profile_mod,
        b=1.5,
        epsilon=0.5,
    )
    profile_triplet = separate_xyz(vector=profile_points.profile_point_triplet)
    side_v = switch(input_type=Switch.InputType.FLOAT, switch=use_profile_y, false=profile_triplet.x, true=profile_triplet.y)
    side_uv = combine_xyz(x=side_u, y=side_v, z=0.0)

    source_position = sample_index(
        data_type=SampleIndex.DataType.FLOAT_VECTOR,
        domain=SampleIndex.Domain.POINT,
        clamp=False,
        geometry=profile_point_indices.geometry,
        value=position(),
        index=profile_point_indices.profile_point_index,
    )
    profile_bounds = bounding_box(geometry=profile_point_indices.geometry, use_radius=True)
    cap_uv = map_range(
        clamp=False,
        interpolation_type="LINEAR",
        data_type="FLOAT_VECTOR",
        vector=source_position,
        from_min=profile_bounds.min,
        from_max=profile_bounds.max,
        to_min=(0.0, 0.0, 0.0),
        to_max=(1.0, 1.0, 1.0),
    )
    uv_map = switch(input_type=Switch.InputType.VECTOR, switch=caps_mask, false=side_uv, true=switch(input_type=Switch.InputType.VECTOR, switch=fill_caps, false=(0.0, 0.0, 0.0), true=cap_uv))
    return {"Mesh": mesh, "UV Map": uv_map, "Caps Mask": caps_mask}


@tree("VG Curve To Mesh UV Demo")
def vg_curve_to_mesh_uv_demo():
    curve = transform_geometry(
        geometry=curve_circle(mode=CurveCircle.Mode.RADIUS, resolution=32, radius=1.899999976158142),
        translation=(0.0, 0.0, 0.0),
    )
    profile = curve_circle(mode=CurveCircle.Mode.RADIUS, resolution=16, radius=0.6269999742507935)
    mesh, uv_map, caps_mask = vg_curve_to_mesh_uv(
        curve=curve,
        profile_curve=profile,
        fill_caps=False,
        lock_caps_uv_scaling=True,
        hole_tolerant=True,
        smooth_angle=3.1415927410125732,
        free_u_space=True,
        lock_u_scaling=True,
        free_v_space=True,
        lock_v_scaling=True,
        sides_uv_scale=(1.0, 1.0, 0.0),
        sides_uv_offset=(0.0, 0.0, 0.0),
        sides_uv_z_rotation=0.0,
        caps_uv_scale=(1.0, 1.0, 0.0),
        caps_uv_offset=(0.0, 0.0, 0.0),
        caps_uv_z_rotation=0.0,
        store_attributes=True,
    )
    transformed = transform_geometry(
        geometry=mesh,
        translation=(2.4099998474121094, 0.0, 3.3399999141693115),
        rotation=(0.9615018963813782, 0.0, -0.5942845940589905),
    ).set_material(material=None)
    return {"Geometry": transformed, "UV Map": uv_map, "Caps Mask": caps_mask}


@tree("VG Curve To Mesh UV Title")
def vg_curve_to_mesh_uv_title():
    title = string_to_curves(
        string=string(string="Curve to Mesh UV"),
        size=0.6000000238418579,
        align_x="Center",
        align_y="Top",
        pivot_point="Midpoint",
    ).curve_instances
    subtitle_text = join_strings(
        delimiter=special_characters().line_break,
        strings=[
            string(string="v1.7.02.230210"),
            string(string="for Blender 3.4+"),
            string(string="[ Free|Github Edition]"),
        ],
    )
    subtitle = transform_geometry(
        geometry=string_to_curves(
            string=subtitle_text,
            size=0.4000000059604645,
            align_x="Center",
            align_y="Top",
            pivot_point="Bottom Left",
        ).curve_instances,
        translation=(0.0, -0.699999988079071, 0.0),
    )
    text = transform_geometry(
        geometry=join_geometry(geometry=[title, subtitle]),
        translation=(0.0, 0.0, -1.6699999570846558),
        rotation=(1.5707963705062866, 0.0, 0.0),
    )
    text_face = fill_curve(curve=text, mode="N-gons", fill_rule="Even-Odd").set_material(material=None)

    plinth = cube(size=(4.400000095367432, 0.20000000298023224, 10.0), vertices_x=2, vertices_y=2, vertices_z=2)
    plinth_uv = store_named_attribute(
        data_type=StoreNamedAttribute.DataType.FLOAT_VECTOR,
        domain=StoreNamedAttribute.Domain.CORNER,
        geometry=plinth.mesh,
        name="uv_map",
        value=plinth.uv_map,
    )
    plinth_geo = transform_geometry(geometry=plinth_uv, translation=(0.0, 0.17000000178813934, 0.0)).set_material(material=None)

    backdrop = grid(size_x=2.0, size_y=2.0, vertices_x=2, vertices_y=2)
    backdrop_uv = store_named_attribute(
        data_type=StoreNamedAttribute.DataType.FLOAT_VECTOR,
        domain=StoreNamedAttribute.Domain.CORNER,
        geometry=backdrop.mesh,
        name="uv_map",
        value=backdrop.uv_map,
    )
    backdrop_plane = transform_geometry(
        geometry=backdrop_uv,
        translation=(0.0, -0.019999999552965164, 0.0),
        rotation=(-1.5707963705062866, 0.0, 0.0),
    )
    bounds = bounding_box(geometry=backdrop_plane, use_radius=True)
    uv = map_range(
        clamp=False,
        interpolation_type="LINEAR",
        data_type="FLOAT_VECTOR",
        vector=position(),
        from_min=bounds.min,
        from_max=bounds.max,
        to_min=(-1.0, -1.0, -1.0),
        to_max=(1.0, 1.0, 1.0),
    )
    backdrop_geo = store_named_attribute(
        data_type=StoreNamedAttribute.DataType.FLOAT_VECTOR,
        domain=StoreNamedAttribute.Domain.CORNER,
        geometry=backdrop_plane,
        name="UV",
        value=uv,
    ).set_material(material=None)
    return {"Geometry": join_geometry(geometry=[text_face, plinth_geo, flip_faces(mesh=backdrop_geo)])}


def _finalize_groups():
    import bpy

    groups = []
    for name in (
        "VG Auto Smooth",
        "VG Curve To Mesh UV",
        "VG Curve To Mesh UV Demo",
        "VG Curve To Mesh UV Title",
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
            "VG_CURVE_TO_MESH_UV_GROUP",
            group.name,
            len(group.nodes),
            len(group.links),
            sorted(set(node.bl_idname for node in group.nodes)),
        )

"""Geometry Script recreation of a scalar helper from Shriinivas/fieldvalue.blend."""

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

    key = name.lower().replace(" ", "_")
    return OutputsList({"geometry": Type(node.outputs[0]), key: Type(node.outputs[1])})


def _int_equal(value, target: int):
    return compare(
        operation=Compare.Operation.EQUAL,
        data_type=Compare.DataType.INT,
        mode=Compare.Mode.ELEMENT,
        a=value,
        b=target,
    )


def _float_equal(value, target: float):
    return compare(
        operation=Compare.Operation.EQUAL,
        data_type=Compare.DataType.FLOAT,
        mode=Compare.Mode.ELEMENT,
        a=value,
        b=target,
    )


@tree("VG Create Decimal")
def vg_create_decimal(vertical_segment_size: Float = 2.0, radius: Float = 0.0):
    dot = mesh_circle(fill_type=MeshCircle.FillType.NGON, vertices=32, radius=radius)
    offset = combine_xyz(
        x=0.0,
        y=math(operation=Math.Operation.MULTIPLY, value=(-1.0, vertical_segment_size)),
        z=0.0,
    )
    return {"Dot": dot.set_position(offset=offset)}


@tree("VG Digit At")
def vg_digit_at(number: Float = 0.0, position: Int = 0):
    shifted_position = math(operation=Math.Operation.ADD, value=(position, 1.0))
    upper_scale = math(operation=Math.Operation.POWER, value=(10.0, shifted_position))
    shifted_number = math(operation=Math.Operation.DIVIDE, value=(number, upper_scale))
    fractional_window = math(operation=Math.Operation.FRACT, value=shifted_number)
    digit_window = math(operation=Math.Operation.MULTIPLY, value=(10.0, fractional_window))

    position_scale = math(operation=Math.Operation.POWER, value=(10.0, position))
    rounded_scaled_window = math(
        operation=Math.Operation.ROUND,
        value=math(operation=Math.Operation.MULTIPLY, value=(digit_window, position_scale)),
    )
    digit_value = math(operation=Math.Operation.DIVIDE, value=(rounded_scaled_window, position_scale))

    is_ones_position = compare(
        operation=Compare.Operation.EQUAL,
        data_type=Compare.DataType.INT,
        mode=Compare.Mode.ELEMENT,
        a=position,
        b=0,
    )
    return switch(
        input_type=Switch.InputType.INT,
        switch=is_ones_position,
        false=math(operation=Math.Operation.FLOOR, value=digit_value),
        true=math(operation=Math.Operation.ROUND, value=digit_value),
    )


@tree("VG Next Digit")
def vg_next_digit(
    whole_part: Float = 0.0,
    fraction_part: Float = 0.0,
    max_precision: Int = 0,
    position: Int = 0,
):
    whole_position = math(operation=Math.Operation.SUBTRACT, value=(position, max_precision))
    use_fraction = math(operation=Math.Operation.LESS_THAN, value=(position, max_precision))
    whole_digit = vg_digit_at(number=whole_part, position=whole_position)
    fraction_digit = vg_digit_at(number=fraction_part, position=position)
    return switch(
        input_type=Switch.InputType.INT,
        switch=use_fraction,
        false=whole_digit,
        true=fraction_digit,
    )


@tree("VG Create Segment")
def vg_create_segment(
    x_major: Bool = False,
    segment_length_along_x: Float = 0.0,
    segment_length_along_y: Float = 0.0,
    secondary_axis_segment_thickness: Float = 0.0,
    sharpness: Float = 0.0,
    offset: Vector = (0.0, 0.0, 0.0),
):
    position_parts = separate_xyz(vector=position())
    major_axis = switch(input_type=Switch.InputType.FLOAT, switch=x_major, false=position_parts.y, true=position_parts.x)
    secondary_axis = switch(
        input_type=Switch.InputType.FLOAT,
        switch=x_major,
        false=position_parts.x,
        true=position_parts.y,
    )

    not_x_major = math(operation=Math.Operation.SUBTRACT, value=(1.0, x_major))
    vertices_x = math(operation=Math.Operation.ADD, value=(2.0, not_x_major))
    vertices_y = math(operation=Math.Operation.ADD, value=(2.0, x_major))

    tip_amount = math(
        operation=Math.Operation.MULTIPLY,
        value=(
            math(operation=Math.Operation.MULTIPLY, value=(0.5, sharpness)),
            secondary_axis_segment_thickness,
        ),
    )
    tip_vector = combine_xyz(
        x=math(operation=Math.Operation.MULTIPLY, value=(x_major, tip_amount)),
        y=math(operation=Math.Operation.MULTIPLY, value=(not_x_major, tip_amount)),
        z=0.0,
    )

    has_secondary_axis = compare(
        operation=Compare.Operation.NOT_EQUAL,
        data_type=Compare.DataType.FLOAT,
        mode=Compare.Mode.ELEMENT,
        a=secondary_axis,
        b=0.0,
    )
    negative_tip_gate = math(
        operation=Math.Operation.MULTIPLY,
        value=(math(operation=Math.Operation.LESS_THAN, value=(major_axis, 0.0)), has_secondary_axis),
    )
    positive_tip_gate = math(
        operation=Math.Operation.MULTIPLY,
        value=(math(operation=Math.Operation.GREATER_THAN, value=(major_axis, 0.0)), has_secondary_axis),
    )
    negative_tip = vector_math(operation=VectorMath.Operation.MULTIPLY, vector=(-1.0, tip_vector))
    positive_gate_vector = combine_xyz(x=positive_tip_gate, y=positive_tip_gate, z=positive_tip_gate)
    negative_gate_vector = combine_xyz(x=negative_tip_gate, y=negative_tip_gate, z=negative_tip_gate)
    positive_end_offset = vector_math(operation=VectorMath.Operation.MULTIPLY, vector=(negative_tip, positive_gate_vector))
    negative_end_offset = vector_math(operation=VectorMath.Operation.MULTIPLY, vector=(tip_vector, negative_gate_vector))
    total_offset = vector_math(
        operation=VectorMath.Operation.ADD,
        vector=(
            vector_math(operation=VectorMath.Operation.ADD, vector=(offset, positive_end_offset)),
            negative_end_offset,
        ),
    )

    segment = grid(
        size_x=segment_length_along_x,
        size_y=segment_length_along_y,
        vertices_x=vertices_x,
        vertices_y=vertices_y,
    ).mesh
    return {"Segment": segment.set_position(offset=total_offset)}


@tree("VG Seven Segments")
def vg_seven_segments(
    horizontal_segment_size: Float = 2.0,
    horizontal_segment_thickness: Float = 0.5,
    vertical_segment_size: Float = 2.0,
    vertical_segment_thickness: Float = 0.5,
    x_separation: Float = 0.1,
    y_seperation: Float = 0.1,
    tip_sharpness: Float = 1.0,
):
    half_horizontal = math(operation=Math.Operation.DIVIDE, value=(horizontal_segment_size, 2.0))
    half_vertical = math(operation=Math.Operation.DIVIDE, value=(vertical_segment_size, 2.0))
    negative_half_horizontal = math(operation=Math.Operation.MULTIPLY, value=(-1.0, half_horizontal))
    negative_half_vertical = math(operation=Math.Operation.MULTIPLY, value=(-1.0, half_vertical))

    vertical_bar_length = math(operation=Math.Operation.SUBTRACT, value=(vertical_segment_size, y_seperation))
    horizontal_bar_length = math(operation=Math.Operation.SUBTRACT, value=(horizontal_segment_size, x_separation))

    lower_left = vg_create_segment(
        x_major=False,
        segment_length_along_x=vertical_segment_thickness,
        segment_length_along_y=vertical_bar_length,
        secondary_axis_segment_thickness=horizontal_segment_thickness,
        sharpness=tip_sharpness,
        offset=combine_xyz(x=negative_half_horizontal, y=negative_half_vertical, z=0.0),
    )
    upper_left = vg_create_segment(
        x_major=False,
        segment_length_along_x=vertical_segment_thickness,
        segment_length_along_y=vertical_bar_length,
        secondary_axis_segment_thickness=horizontal_segment_thickness,
        sharpness=tip_sharpness,
        offset=combine_xyz(x=negative_half_horizontal, y=half_vertical, z=0.0),
    )
    lower_right = vg_create_segment(
        x_major=False,
        segment_length_along_x=vertical_segment_thickness,
        segment_length_along_y=vertical_bar_length,
        secondary_axis_segment_thickness=horizontal_segment_thickness,
        sharpness=tip_sharpness,
        offset=combine_xyz(x=half_horizontal, y=negative_half_vertical, z=0.0),
    )
    upper_right = vg_create_segment(
        x_major=False,
        segment_length_along_x=vertical_segment_thickness,
        segment_length_along_y=vertical_bar_length,
        secondary_axis_segment_thickness=horizontal_segment_thickness,
        sharpness=tip_sharpness,
        offset=combine_xyz(x=half_horizontal, y=half_vertical, z=0.0),
    )

    bottom = vg_create_segment(
        x_major=True,
        segment_length_along_x=horizontal_bar_length,
        segment_length_along_y=horizontal_segment_thickness,
        secondary_axis_segment_thickness=vertical_segment_thickness,
        sharpness=tip_sharpness,
        offset=combine_xyz(x=0.0, y=math(operation=Math.Operation.MULTIPLY, value=(-1.0, vertical_segment_size)), z=0.0),
    )
    middle = vg_create_segment(
        x_major=True,
        segment_length_along_x=horizontal_bar_length,
        segment_length_along_y=horizontal_segment_thickness,
        secondary_axis_segment_thickness=vertical_segment_thickness,
        sharpness=tip_sharpness,
        offset=(0.0, 0.0, 0.0),
    )
    top = vg_create_segment(
        x_major=True,
        segment_length_along_x=horizontal_bar_length,
        segment_length_along_y=horizontal_segment_thickness,
        secondary_axis_segment_thickness=vertical_segment_thickness,
        sharpness=tip_sharpness,
        offset=combine_xyz(x=0.0, y=vertical_segment_size, z=0.0),
    )
    dot = vg_create_decimal(
        vertical_segment_size=vertical_segment_size,
        radius=math(operation=Math.Operation.DIVIDE, value=(horizontal_segment_thickness, 2.0)),
    )

    return {
        "bars": join_geometry(
            geometry=[
                dot,
                top,
                middle,
                bottom,
                upper_right,
                lower_right,
                upper_left,
                lower_left,
            ]
        )
    }


@tree("VG Delete Segments")
def vg_delete_segments(digit: Int = 0, segment_position: Int = 0):
    digit_minus_one = math(operation=Math.Operation.SUBTRACT, value=(digit, 1.0))

    p01 = _int_equal(segment_position, 0) | _int_equal(segment_position, 1)
    p23 = _int_equal(segment_position, 2) | _int_equal(segment_position, 3)
    p45 = _int_equal(segment_position, 4) | _int_equal(segment_position, 5)
    p67 = _int_equal(segment_position, 6) | _int_equal(segment_position, 7)
    p89 = _int_equal(segment_position, 8) | _int_equal(segment_position, 9)
    p1011 = _int_equal(segment_position, 10) | _int_equal(segment_position, 11)
    p1213 = _int_equal(segment_position, 12) | _int_equal(segment_position, 13)
    p14 = _int_equal(segment_position, 14)

    d_minus_one = _float_equal(digit_minus_one, -1.0)
    d0 = _float_equal(digit_minus_one, 0.0)
    d1 = _float_equal(digit_minus_one, 1.0)
    d2 = _float_equal(digit_minus_one, 2.0)
    d3 = _float_equal(digit_minus_one, 3.0)
    d4 = _float_equal(digit_minus_one, 4.0)
    d5 = _float_equal(digit_minus_one, 5.0)
    d6 = _float_equal(digit_minus_one, 6.0)
    d7 = _float_equal(digit_minus_one, 7.0)
    d9 = _float_equal(digit_minus_one, 9.0)
    d10 = _float_equal(digit_minus_one, 10.0)
    d11 = _float_equal(digit_minus_one, 11.0)

    delete_for_minus_one = d_minus_one
    delete_for_zero = d0 & p1011
    delete_for_one = d1 & ~(p45 | p67)
    delete_for_two = d2 & (p23 | p45 | p14)
    delete_for_three = d3 & (p01 | p23 | p14)
    delete_for_four = d4 & (p89 | p1213 | p01 | p14)
    delete_for_five = d5 & (p01 | p67 | p14)
    delete_for_six = d6 & (p67 | p14)
    delete_for_seven = d7 & ~(p1213 | p45 | p67)
    delete_for_nine = d9 & (p01 | p14)
    delete_for_ten = d10 & ~p1011
    delete_for_eleven = d11 & ~p14
    delete_for_decimal = p14 & ~d11

    return (
        delete_for_eleven
        | delete_for_ten
        | delete_for_minus_one
        | delete_for_zero
        | delete_for_one
        | delete_for_two
        | delete_for_three
        | delete_for_four
        | delete_for_five
        | delete_for_six
        | delete_for_seven
        | delete_for_decimal
        | delete_for_nine
    )


@tree("VG Field Value")
def vg_field_value(
    geometry: Geometry,
    input_type: Menu = "Float",
    float_value: Float = 0.0,
    vector_value: Vector = (0.0, 0.0, 0.0),
    digits_before_decimal: Int = 4,
    precision: Int = 2,
    domain: Menu = "Point",
    alignment: Menu = "Center",
    align_to_global: Bool = True,
    scale: Float = 0.019999999552965164,
    digit_separation: Float = 0.30000001192092896,
    element_separation: Float = 1.0,
    x_offset: Float = 0.0,
    y_offset: Float = 0.0,
    z_offset: Float = 0.0010000000474974513,
    rotation: Int = 0,
    segment_width_factor: Float = 0.5,
    segment_separation_factor: Float = 0.10000000149011612,
    tip_sharpness: Float = 1.0,
    leading_zeros: Bool = False,
    material: Material = None,
):
    domain_name = menu_switch(
        active_index=2,
        data_type="STRING",
        menu=domain,
        point="Point",
        face="Face",
        edge="Edge",
    )
    use_face_domain = compare(
        operation=Compare.Operation.EQUAL,
        data_type=Compare.DataType.STRING,
        mode=Compare.Mode.ELEMENT,
        a=domain_name.output,
        b="Face",
    )
    use_edge_domain = compare(
        operation=Compare.Operation.EQUAL,
        data_type=Compare.DataType.STRING,
        mode=Compare.Mode.ELEMENT,
        a=domain_name.output,
        b="Edge",
    )
    value_kind = menu_switch(
        active_index=1,
        data_type="STRING",
        menu=input_type,
        float="Float",
        vector="Vector",
    )
    use_vector_value = compare(
        operation=Compare.Operation.EQUAL,
        data_type=Compare.DataType.STRING,
        mode=Compare.Mode.ELEMENT,
        a=value_kind.output,
        b="Vector",
    )

    point_float = _capture_attribute_item("FLOAT", "POINT", geometry, float_value, "float field")
    edge_float = _capture_attribute_item("FLOAT", "EDGE", geometry, float_value, "float field")
    face_float = _capture_attribute_item("FLOAT", "FACE", geometry, float_value, "float field")
    point_vector = _capture_attribute_item("VECTOR", "POINT", geometry, vector_value, "vector field")
    edge_vector = _capture_attribute_item("VECTOR", "EDGE", geometry, vector_value, "vector field")
    face_vector = _capture_attribute_item("VECTOR", "FACE", geometry, vector_value, "vector field")

    captured_float_geometry = switch(
        input_type=Switch.InputType.GEOMETRY,
        switch=use_face_domain,
        false=switch(
            input_type=Switch.InputType.GEOMETRY,
            switch=use_edge_domain,
            false=point_float.geometry,
            true=edge_float.geometry,
        ),
        true=face_float.geometry,
    )
    captured_vector_geometry = switch(
        input_type=Switch.InputType.GEOMETRY,
        switch=use_face_domain,
        false=switch(
            input_type=Switch.InputType.GEOMETRY,
            switch=use_edge_domain,
            false=point_vector.geometry,
            true=edge_vector.geometry,
        ),
        true=face_vector.geometry,
    )
    sampled_source = switch(
        input_type=Switch.InputType.GEOMETRY,
        switch=use_vector_value,
        false=captured_float_geometry,
        true=captured_vector_geometry,
    )
    source_points = switch(
        input_type=Switch.InputType.GEOMETRY,
        switch=use_face_domain,
        false=switch(
            input_type=Switch.InputType.GEOMETRY,
            switch=use_edge_domain,
            false=sampled_source,
            true=mesh_to_points(mode="EDGES", mesh=sampled_source, radius=0.05000000074505806),
        ),
        true=mesh_to_points(mode="FACES", mesh=sampled_source, radius=0.05000000074505806),
    )

    component_count = switch(input_type=Switch.InputType.INT, switch=use_vector_value, false=1, true=3)

    segment_glyph = vg_seven_segments(
        horizontal_segment_size=2.0,
        horizontal_segment_thickness=segment_width_factor,
        vertical_segment_size=2.0,
        vertical_segment_thickness=segment_width_factor,
        x_separation=segment_separation_factor,
        y_seperation=segment_separation_factor,
        tip_sharpness=tip_sharpness,
    )
    glyph_faces = _capture_attribute_item("INT", "FACE", segment_glyph, index(), "int field")
    glyph_position = separate_xyz(vector=position())
    glyph_y_stats = attribute_statistic(
        data_type=AttributeStatistic.DataType.FLOAT,
        domain=AttributeStatistic.Domain.POINT,
        geometry=glyph_faces.geometry,
        attribute=glyph_position.y,
    )
    glyph_height = math(operation=Math.Operation.SUBTRACT, value=(glyph_y_stats.max, glyph_y_stats.min))
    component_spacing = math(operation=Math.Operation.ADD, value=(glyph_height, element_separation))
    vector_component_step = switch(input_type=Switch.InputType.FLOAT, switch=use_vector_value, false=0.0, true=component_spacing)
    component_points = mesh_line(
        mode=MeshLine.Mode.OFFSET,
        count_mode=MeshLine.CountMode.TOTAL,
        count=component_count,
        start_location=combine_xyz(x=0.0, y=vector_component_step, z=0.0),
        offset=combine_xyz(
            x=0.0,
            y=math(operation=Math.Operation.MULTIPLY, value=(-1.0, vector_component_step)),
            z=0.0,
        ),
    )

    digit_count_without_decimal = math(operation=Math.Operation.ADD, value=(digits_before_decimal, precision))
    digit_count_with_decimal = math(operation=Math.Operation.ADD, value=(digit_count_without_decimal, 1.0))
    has_precision = math(operation=Math.Operation.GREATER_THAN, value=(precision, 0.0))
    display_digit_slots = math(operation=Math.Operation.ADD, value=(digit_count_with_decimal, has_precision))

    glyph_x_stats = attribute_statistic(
        data_type=AttributeStatistic.DataType.FLOAT,
        domain=AttributeStatistic.Domain.POINT,
        geometry=glyph_faces.geometry,
        attribute=glyph_position.x,
    )
    glyph_width = math(operation=Math.Operation.SUBTRACT, value=(glyph_x_stats.max, glyph_x_stats.min))
    digit_pitch = math(
        operation=Math.Operation.MULTIPLY,
        value=(math(operation=Math.Operation.ADD, value=(1.0, digit_separation)), glyph_width),
    )
    negative_digit_pitch = math(operation=Math.Operation.MULTIPLY, value=(-1.0, digit_pitch))
    digit_step = combine_xyz(x=negative_digit_pitch, y=0.0, z=0.0)
    digit_points = mesh_line(
        mode=MeshLine.Mode.OFFSET,
        count_mode=MeshLine.CountMode.TOTAL,
        count=display_digit_slots,
        start_location=vector_math(operation=VectorMath.Operation.DIVIDE, vector=(digit_step, (2.0, 0.0, 0.0))),
        offset=digit_step,
    )
    digit_instances = instance_on_points(
        points=digit_points,
        instance=glyph_faces.geometry,
        pick_instance=False,
        rotation=(0.0, 0.0, 0.0),
        scale=(1.0, 1.0, 1.0),
    )
    decimal_slot = math(
        operation=Math.Operation.SUBTRACT,
        value=(math(operation=Math.Operation.SUBTRACT, value=(display_digit_slots, precision)), 0.5),
    )
    decimal_offset = math(operation=Math.Operation.MULTIPLY, value=(decimal_slot, digit_pitch))
    final_digit_index = math(operation=Math.Operation.SUBTRACT, value=(display_digit_slots, 1.0))
    is_final_digit_slot = compare(
        operation=Compare.Operation.EQUAL,
        data_type=Compare.DataType.FLOAT,
        mode=Compare.Mode.ELEMENT,
        a=index(),
        b=final_digit_index,
        epsilon=0.0010000000474974513,
    )
    decimal_shifted_digits = set_position(
        geometry=digit_instances,
        offset=combine_xyz(
            x=math(operation=Math.Operation.MULTIPLY, value=(decimal_offset, is_final_digit_slot)),
            y=0.0,
            z=math(operation=Math.Operation.MULTIPLY, value=(-0.0010000000474974513, is_final_digit_slot)),
        ),
    )
    digit_indexed = _capture_attribute_item("INT", "INSTANCE", decimal_shifted_digits, index(), "int field")
    component_instances = instance_on_points(
        points=component_points,
        instance=digit_indexed.geometry,
        pick_instance=False,
        rotation=(0.0, 0.0, 0.0),
        scale=(1.0, 1.0, 1.0),
    )
    component_indexed = _capture_attribute_item("INT", "INSTANCE", component_instances, index(), "int field")
    value_instances = instance_on_points(
        points=source_points,
        instance=component_indexed.geometry,
        pick_instance=False,
        rotation=(0.0, 0.0, 0.0),
        scale=(1.0, 1.0, 1.0),
    )

    point_position = sample_index(
        data_type=SampleIndex.DataType.FLOAT_VECTOR,
        domain=SampleIndex.Domain.POINT,
        clamp=False,
        geometry=sampled_source,
        value=position(),
        index=index(),
    )
    edge_position = sample_index(
        data_type=SampleIndex.DataType.FLOAT_VECTOR,
        domain=SampleIndex.Domain.EDGE,
        clamp=False,
        geometry=sampled_source,
        value=position(),
        index=index(),
    )
    face_position = sample_index(
        data_type=SampleIndex.DataType.FLOAT_VECTOR,
        domain=SampleIndex.Domain.FACE,
        clamp=False,
        geometry=sampled_source,
        value=position(),
        index=index(),
    )
    source_position = switch(
        input_type=Switch.InputType.VECTOR,
        switch=use_face_domain,
        false=switch(input_type=Switch.InputType.VECTOR, switch=use_edge_domain, false=point_position, true=edge_position),
        true=face_position,
    )

    alignment_name = menu_switch(
        active_index=2,
        data_type="STRING",
        menu=alignment,
        center="Center",
        right="Right",
        left="Left",
    )
    align_left = compare(
        operation=Compare.Operation.EQUAL,
        data_type=Compare.DataType.STRING,
        mode=Compare.Mode.ELEMENT,
        a=alignment_name.output,
        b="Left",
    )
    align_right = compare(
        operation=Compare.Operation.EQUAL,
        data_type=Compare.DataType.STRING,
        mode=Compare.Mode.ELEMENT,
        a=alignment_name.output,
        b="Right",
    )
    scaled_digit_pitch = math(operation=Math.Operation.MULTIPLY, value=(scale, digit_pitch))

    captured_float = switch(
        input_type=Switch.InputType.FLOAT,
        switch=use_face_domain,
        false=switch(
            input_type=Switch.InputType.FLOAT,
            switch=use_edge_domain,
            false=point_float.float_field,
            true=edge_float.float_field,
        ),
        true=face_float.float_field,
    )
    captured_vector = switch(
        input_type=Switch.InputType.VECTOR,
        switch=use_face_domain,
        false=switch(
            input_type=Switch.InputType.VECTOR,
            switch=use_edge_domain,
            false=point_vector.vector_field,
            true=edge_vector.vector_field,
        ),
        true=face_vector.vector_field,
    )
    vector_parts = separate_xyz(vector=captured_vector)
    component_value = index_switch(
        data_type=IndexSwitch.DataType.FLOAT,
        index=component_indexed.int_field,
        _0=vector_parts.x,
        _1=vector_parts.y,
        _2=vector_parts.z,
    )
    displayed_value = switch(input_type=Switch.InputType.FLOAT, switch=use_vector_value, false=captured_float, true=component_value)
    absolute_value = math(operation=Math.Operation.ABSOLUTE, value=displayed_value)
    whole_part = math(operation=Math.Operation.TRUNC, value=absolute_value)
    whole_part_digits = math(
        operation=Math.Operation.MAXIMUM,
        value=(
            math(
                operation=Math.Operation.FLOOR,
                value=math(
                    operation=Math.Operation.LOGARITHM,
                    value=(math(operation=Math.Operation.MULTIPLY, value=(whole_part, 10.0)), 10.0),
                ),
            ),
            1.0,
        ),
    )
    natural_digit_count = math(operation=Math.Operation.ADD, value=(whole_part_digits, precision))
    is_negative = math(operation=Math.Operation.LESS_THAN, value=(displayed_value, 0.0))
    natural_slot_count = math(operation=Math.Operation.ADD, value=(natural_digit_count, is_negative))
    half_text_width = math(
        operation=Math.Operation.DIVIDE,
        value=(math(operation=Math.Operation.MULTIPLY, value=(scaled_digit_pitch, natural_slot_count)), 2.0),
    )
    alignment_offset = switch(
        input_type=Switch.InputType.FLOAT,
        switch=align_left,
        false=switch(input_type=Switch.InputType.FLOAT, switch=align_right, false=half_text_width, true=0),
        true=math(operation=Math.Operation.MULTIPLY, value=(half_text_width, 2.0)),
    )
    placed_position = vector_math(
        operation=VectorMath.Operation.ADD,
        vector=(source_position, combine_xyz(x=math(operation=Math.Operation.ADD, value=(x_offset, alignment_offset)), y=y_offset, z=z_offset)),
    )

    point_normal = sample_index(
        data_type=SampleIndex.DataType.FLOAT_VECTOR,
        domain=SampleIndex.Domain.POINT,
        clamp=False,
        geometry=sampled_source,
        value=normal(legacy_corner_normals=True).normal,
        index=index(),
    )
    edge_normal = sample_index(
        data_type=SampleIndex.DataType.FLOAT_VECTOR,
        domain=SampleIndex.Domain.EDGE,
        clamp=False,
        geometry=sampled_source,
        value=normal(legacy_corner_normals=True).normal,
        index=index(),
    )
    face_normal = sample_index(
        data_type=SampleIndex.DataType.FLOAT_VECTOR,
        domain=SampleIndex.Domain.FACE,
        clamp=False,
        geometry=sampled_source,
        value=normal(legacy_corner_normals=True).normal,
        index=index(),
    )
    source_normal = switch(
        input_type=Switch.InputType.VECTOR,
        switch=use_face_domain,
        false=switch(input_type=Switch.InputType.VECTOR, switch=use_edge_domain, false=point_normal, true=edge_normal),
        true=face_normal,
    )
    normal_aligned_rotation = align_rotation_to_vector(axis="Z", pivot_axis="AUTO", factor=1.0, vector=source_normal)
    normal_parts = separate_xyz(vector=source_normal)
    global_reference_nudge = switch(
        input_type=Switch.InputType.VECTOR,
        switch=math(operation=Math.Operation.GREATER_THAN, value=(normal_parts.y, 0.5)),
        false=(0.0, 0.0, 0.0),
        true=(9.999999747378752e-06, 0.0, 0.0),
    )
    global_reference = combine_xyz(x=global_reference_nudge, y=0.0, z=-1.0)
    self_info = object_info(transform_space="ORIGINAL", object=self_object(), as_instance=False)
    object_space_reference = transform_point(vector=global_reference, transform=invert_matrix(matrix=self_info.transform).matrix)
    reference_vector = switch(input_type=Switch.InputType.VECTOR, switch=align_to_global, false=global_reference, true=object_space_reference)
    tangent_vector = vector_math(operation=VectorMath.Operation.CROSS_PRODUCT, vector=(source_normal, reference_vector))
    tangent_aligned_rotation = align_rotation_to_vector(
        axis="X",
        pivot_axis="AUTO",
        rotation=normal_aligned_rotation,
        factor=1.0,
        vector=tangent_vector,
    )
    local_spin = combine_xyz(x=0.0, y=0.0, z=math(operation=Math.Operation.RADIANS, value=rotation))
    instance_rotation = rotate_rotation(rotation_space="LOCAL", rotation=tangent_aligned_rotation, rotate_by=local_spin)
    rotated_position = vector_rotate(
        rotation_type="EULER_XYZ",
        invert=False,
        vector=placed_position,
        center=source_position,
        rotation=instance_rotation,
    )
    transformed_instances = set_instance_transform(
        instances=value_instances,
        transform=combine_transform(
            translation=rotated_position,
            rotation=instance_rotation,
            scale=combine_xyz(x=scale, y=scale, z=scale),
        ),
    )
    realized_digits = realize_instances(realize_to_point_domain=True, geometry=transformed_instances, realize_all=True, depth=0)

    last_display_slot = math(operation=Math.Operation.SUBTRACT, value=(display_digit_slots, 1.0))
    is_decimal_slot = boolean_math(
        operation=BooleanMath.Operation.AND,
        boolean=(
            compare(
                operation=Compare.Operation.EQUAL,
                data_type=Compare.DataType.FLOAT,
                mode=Compare.Mode.ELEMENT,
                a=digit_indexed.int_field,
                b=last_display_slot,
                epsilon=0.0010000000474974513,
            ),
            math(operation=Math.Operation.GREATER_THAN, value=(precision, 0.0)),
        ),
    )
    is_negative_slot = boolean_math(
        operation=BooleanMath.Operation.AND,
        boolean=(
            is_negative,
            compare(
                operation=Compare.Operation.EQUAL,
                data_type=Compare.DataType.FLOAT,
                mode=Compare.Mode.ELEMENT,
                a=digit_indexed.int_field,
                b=natural_digit_count,
                epsilon=0.0010000000474974513,
            ),
        ),
    )
    forced_visible_digit = boolean_math(
        operation=BooleanMath.Operation.OR,
        boolean=(
            boolean_math(
                operation=BooleanMath.Operation.OR,
                boolean=(
                    math(operation=Math.Operation.LESS_THAN, value=(digit_indexed.int_field, precision)),
                    math(
                        operation=Math.Operation.GREATER_THAN,
                        value=(
                            whole_part,
                            math(
                                operation=Math.Operation.SUBTRACT,
                                value=(
                                    math(
                                        operation=Math.Operation.POWER,
                                        value=(10.0, math(operation=Math.Operation.SUBTRACT, value=(digit_indexed.int_field, precision))),
                                    ),
                                    1.0,
                                ),
                            ),
                        ),
                    ),
                ),
            ),
            boolean_math(
                operation=BooleanMath.Operation.AND,
                boolean=(
                    compare(
                        operation=Compare.Operation.EQUAL,
                        data_type=Compare.DataType.FLOAT,
                        mode=Compare.Mode.ELEMENT,
                        a=whole_part,
                        b=0.0,
                        epsilon=0.0010000000474974513,
                    ),
                    compare(
                        operation=Compare.Operation.EQUAL,
                        data_type=Compare.DataType.INT,
                        mode=Compare.Mode.ELEMENT,
                        a=digit_indexed.int_field,
                        b=precision,
                    ),
                ),
            ),
        ),
    )
    leading_zero_slot = boolean_math(
        operation=BooleanMath.Operation.AND,
        boolean=(
            boolean_math(
                operation=BooleanMath.Operation.AND,
                boolean=(boolean_math(operation=BooleanMath.Operation.NOT, boolean=is_negative), leading_zeros),
            ),
            math(
                operation=Math.Operation.LESS_THAN,
                value=(math(operation=Math.Operation.SUBTRACT, value=(digit_indexed.int_field, precision)), digits_before_decimal),
            ),
        ),
    )
    digit_visible = boolean_math(operation=BooleanMath.Operation.OR, boolean=(forced_visible_digit, leading_zero_slot))
    display_capacity_exceeded = math(
        operation=Math.Operation.GREATER_THAN,
        value=(natural_digit_count, math(operation=Math.Operation.ADD, value=(digits_before_decimal, precision))),
    )
    fraction_part = math(
        operation=Math.Operation.ROUND,
        value=(
            math(
                operation=Math.Operation.MULTIPLY,
                value=(
                    math(operation=Math.Operation.FRACT, value=absolute_value),
                    math(operation=Math.Operation.POWER, value=(10.0, precision)),
                ),
            )
        ),
    )
    next_digit = vg_next_digit(
        whole_part=whole_part,
        fraction_part=fraction_part,
        max_precision=precision,
        position=digit_indexed.int_field,
    )
    digit_code = switch(input_type=Switch.InputType.FLOAT, switch=display_capacity_exceeded, false=next_digit, true=10.0)
    visible_digit_code = switch(
        input_type=Switch.InputType.INT,
        switch=digit_visible,
        false=0,
        true=math(operation=Math.Operation.ADD, value=(digit_code, 1.0)),
    )
    negative_digit_code = switch(input_type=Switch.InputType.INT, switch=is_negative_slot, false=visible_digit_code, true=11)
    final_digit_code = switch(input_type=Switch.InputType.INT, switch=is_decimal_slot, false=negative_digit_code, true=12)
    hidden_segments = vg_delete_segments(digit=final_digit_code, segment_position=glyph_faces.int_field)
    visible_segments = delete_geometry(mode=DeleteGeometry.Mode.ALL, domain=DeleteGeometry.Domain.FACE, geometry=realized_digits, selection=hidden_segments)
    return {"Value": set_material(geometry=visible_segments, material=material)}


def _finalize_groups():
    import bpy

    groups = []
    for name in (
        "VG Create Decimal",
        "VG Digit At",
        "VG Next Digit",
        "VG Create Segment",
        "VG Seven Segments",
        "VG Delete Segments",
        "VG Field Value",
    ):
        group = bpy.data.node_groups.get(name)
        if not group:
            continue
        group.use_fake_user = True
        if hasattr(group, "interface"):
            for item in group.interface.items_tree:
                if item.item_type == "SOCKET" and item.in_out == "INPUT" and item.name == "X Major":
                    item.name = "X Major"
                if item.item_type == "SOCKET" and item.in_out == "INPUT" and item.name in {"Radius", "Offset"}:
                    item.name = item.name.lower()
                if item.item_type == "SOCKET" and item.in_out == "OUTPUT" and item.name == "Bars":
                    item.name = "bars"
                if (
                    name == "VG Delete Segments"
                    and item.item_type == "SOCKET"
                    and item.in_out == "OUTPUT"
                    and item.name == "Result"
                ):
                    item.name = "result"
        groups.append(group)
    return groups


_finalize_groups()


if __name__ == "__main__":
    for group in _finalize_groups():
        print(
            "VG_FIELDVALUE_GROUP",
            group.name,
            len(group.nodes),
            len(group.links),
            sorted(set(node.bl_idname for node in group.nodes)),
        )

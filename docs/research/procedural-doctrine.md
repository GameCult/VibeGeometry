# Procedural Geometry Doctrine

This note is a spatial reasoning playbook for turning geometric ideas into
Geometry Script graphs. The metaphors are not decorative labels. They are meant
to make the right tool feel salient when a form is still only a mental picture:
a rail, a stencil, a chassis, a switchboard, a relay.

Each pattern should answer four questions:

- What visual problem makes this tool relevant?
- What mental move turns that problem into graph structure?
- What does the Geometry Script shape look like?
- What evidence proves the translation kept its behavior?

Code snippets are excerpts from the verified translation scripts unless noted.
They may omit surrounding setup or sibling branches, but they should keep the
same explicit Geometry Script call style that passed Blender verification.

## Start With A Pipeline

Reach for this when the form feels like it has stages: a seed shape, a sampling
strategy, a spatial rule, and a final visible body.

Mental move:

```text
visual target -> seed -> domain -> field rule -> deformation -> realization
```

For a function plot, do not start by imagining mesh coordinates. Imagine a rail
with evenly spaced stations, then a weather field that tells each station where
to move.

```python
end = combine_xyz(x=length, y=0.0, z=0.0)
curve = curve_line(mode=CurveLine.Mode.POINTS, start=(0.0, 0.0, 0.0), end=end)
parts = separate_xyz(vector=position())
y = math(
    operation=Math.Operation.ADD,
    value=(math(operation=Math.Operation.MULTIPLY, value=(parts.x, m)), value),
)
vector = combine_xyz(x=parts.x, y=y, z=parts.z)
positioned = curve.set_position(position=vector)
profile = curve_circle(mode=CurveCircle.Mode.RADIUS, resolution=32, radius=thickness)
mesh = positioned.curve_to_mesh(profile_curve=profile)
```

Verification cue: evaluate the output geometry and compare vertices against the
source or expected curve. A script that creates similar node names has not
proved it has kept the shape.

## Curves Are Rails

Reach for curves when the target reads as a stroke, tube, arc, path, cable,
branch, contour, function trace, or anything whose main identity is a route
through space.

Mental move: draw the centerline first. Thickness, surface, bevel, and material
are later decisions. This keeps you from hand-authoring a mesh when the form is
really a path wearing a body.

```python
rail = curve_line(mode=CurveLine.Mode.POINTS, start=start, end=end)
sampled = rail.resample_curve(count=sample_count)
profile = curve_circle(mode=CurveCircle.Mode.RADIUS, resolution=32, radius=thickness)
solid = sampled.curve_to_mesh(profile_curve=profile)
```

Metaphor in use: a curve is the rail the shape rides on. If the idea in your
head moves like a train route, script a rail before you script a surface.

Verification cue: compare the sampled path or the realized mesh. If downstream
topology order matters, direct vertex order matters; otherwise sorted vertex
comparison may be enough to prove the same visible path.

## Fields Are Weather

Reach for fields when the shape should respond to position, index, normal,
random value, attribute, or any other per-element condition.

Mental move: stop asking "what are the coordinates?" and ask "what does every
point feel here?" The graph is not storing a list. It is defining weather that
Blender evaluates over the current geometry.

```python
parts = separate_xyz(vector=position())
x_squared = math(operation=Math.Operation.POWER, value=(parts.x, 2.0))
y = math(operation=Math.Operation.MULTIPLY, value=(x_squared, amplitude))
target_position = combine_xyz(x=parts.x, y=y, z=parts.z)
geometry = sampled_curve.set_position(position=target_position)
```

Metaphor in use: a point enters the weather, asks for local X, gets back a Y
rule, and moves. This is how equations, ripples, tapers, masks, and gradients
become geometry without precomputing coordinates in Python.

Verification cue: test more than one parameter value. Field graphs often look
right at one value and reveal swapped axes or stale constants when controls
move.

## Set Position Is The Hinge

Reach for `set_position` when your graph has built an invisible spatial rule
and needs to make it real.

Mental move: preserve the coordinates that should remain stable, replace only
the coordinate or offset that carries the design change, then let `Set Position`
be the hinge between math and form.

```python
parts = separate_xyz(vector=position())
y = math(
    operation=Math.Operation.ADD,
    value=(math(operation=Math.Operation.MULTIPLY, value=(parts.x, m)), value),
)
vector = combine_xyz(x=parts.x, y=y, z=parts.z)
positioned = curve.set_position(position=vector)
```

For local nudges, use `offset` instead of an absolute `position`:

```python
offset = combine_xyz(
    x=0.0,
    y=math(operation=Math.Operation.MULTIPLY, value=(-1.0, vertical_segment_size)),
    z=0.0,
)
dot = mesh_circle(fill_type=MeshCircle.FillType.NGON, vertices=32, radius=radius)
positioned_dot = dot.set_position(offset=offset)
```

Metaphor in use: before `Set Position`, the graph is making promises. After it,
the object has moved. If you cannot name what is preserved and what changes,
the hinge is probably attached to the wrong door.

Verification cue: compare evaluated vertices before and after parameter changes
that should move only one axis.

## Profiles Give Rails A Body

Reach for profiles when a path exists but the renderable or inspectable object
should have thickness.

Mental move: separate route from cross-section. The curve says where the object
goes; the profile says what gets dragged along it.

```python
profile = curve_circle(mode=CurveCircle.Mode.RADIUS, resolution=32, radius=thickness)
mesh = path_curve.curve_to_mesh(profile_curve=profile)
```

When upstream geometry may carry variable thickness, look for an attribute
handle:

```python
radius = named_attribute(data_type=NamedAttribute.DataType.FLOAT, name="radius")
scale = switch(input_type=Switch.InputType.FLOAT, switch=radius.exists, false=1.0, true=radius.attribute)
mesh = path_curve.curve_to_mesh(profile_curve=profile, scale=scale)
```

Metaphor in use: `Curve to Mesh` is a drill bit dragged down a rail. A `radius`
attribute lets some stations use a wider bit without changing the rail.

Verification cue: inspect mesh vertex counts and bounding dimensions, not just
the existence of a `Curve to Mesh` node.

## Field Masks Are Chisels

Reach for field masks when a regular seed mesh should become a shaped part by
moving only selected vertices, edges, faces, or instances.

Mental move: start with a boring mesh, describe the local conditions that mark
the parts allowed to move, multiply the movement by those masks, then set
position. This is how `Create Segment` turns a grid into a pointed display bar.

```python
parts = separate_xyz(vector=position())
major = switch(input_type=Switch.InputType.FLOAT, switch=x_major, false=parts.y, true=parts.x)
secondary = switch(input_type=Switch.InputType.FLOAT, switch=x_major, false=parts.x, true=parts.y)

not_x_major = math(operation=Math.Operation.SUBTRACT, value=(1.0, x_major))
tip_amount = math(
    operation=Math.Operation.MULTIPLY,
    value=(math(operation=Math.Operation.MULTIPLY, value=(0.5, sharpness)), secondary_axis_segment_thickness),
)
tip_vector = combine_xyz(
    x=math(operation=Math.Operation.MULTIPLY, value=(x_major, tip_amount)),
    y=math(operation=Math.Operation.MULTIPLY, value=(not_x_major, tip_amount)),
    z=0.0,
)

on_side = compare(
    operation=Compare.Operation.NOT_EQUAL,
    data_type=Compare.DataType.FLOAT,
    mode=Compare.Mode.ELEMENT,
    a=secondary,
    b=0.0,
)
positive_end = math(
    operation=Math.Operation.MULTIPLY,
    value=(math(operation=Math.Operation.GREATER_THAN, value=(major, 0.0)), on_side),
)
negative_end = math(
    operation=Math.Operation.MULTIPLY,
    value=(math(operation=Math.Operation.LESS_THAN, value=(major, 0.0)), on_side),
)
```

Metaphor in use: the mask is the stencil; `Set Position` is the chisel strike.
Do not hard-code every vertex if the part can be described as "these local
conditions get this movement."

Verification cue: test both orientations. The horizontal and vertical segment
cases caught whether major and secondary axes were wired correctly.

## Glyphs Are Parts

Reach for named glyph parts when a larger form is built from small repeated
tokens: bars, dots, strokes, caps, labels, ticks, beads, rivets.

Mental move: isolate the small thing by intent, even if its geometry is simple.
The point is not abstraction theater; it is making future composition read like
the visual idea.

```python
@tree("VG Create Decimal")
def vg_create_decimal(vertical_segment_size: Float = 2.0, radius: Float = 0.0):
    dot = mesh_circle(fill_type=MeshCircle.FillType.NGON, vertices=32, radius=radius)
    offset = combine_xyz(
        x=0.0,
        y=math(operation=Math.Operation.MULTIPLY, value=(-1.0, vertical_segment_size)),
        z=0.0,
    )
    return {"Dot": dot.set_position(offset=offset)}
```

Metaphor in use: a decimal point is punctuation geometry. Naming it keeps the
display script from devolving into anonymous circles with suspicious offsets.

Verification cue: compare the part alone before composing it into the larger
system.

## Chassis Groups Compose Parts

Reach for chassis groups when tested parts need to be arranged into a reusable
frame: digits, panels, facades, mechanical assemblies, tiled motifs, creature
limbs, modular buildings.

Mental move: do not reopen the primitive geometry. Compute placements, call the
part group repeatedly, and join the result. `Seven Segments` uses the tested
bar and dot groups to build a digit scaffold.

```python
horizontal_bar_length = math(operation=Math.Operation.SUBTRACT, value=(horizontal_segment_size, x_separation))

top = vg_create_segment(
    x_major=True,
    segment_length_along_x=horizontal_bar_length,
    segment_length_along_y=horizontal_segment_thickness,
    secondary_axis_segment_thickness=vertical_segment_thickness,
    sharpness=tip_sharpness,
    offset=combine_xyz(x=0.0, y=vertical_segment_size, z=0.0),
)

return {"bars": join_geometry(geometry=[top, middle, bottom, upper_left, lower_left, upper_right, lower_right, dot])}
```

Metaphor in use: the lower group machines the bolt. The chassis group decides
where the bolts go. Keep those jobs separate so later visibility or material
logic can act on the assembly.

Verification cue: compare the whole chassis geometry and preserve part names in
script even when the output is one joined stream.

## Groups Can Pass Batons

Reach for baton outputs when part N+1 depends on state produced by part N:
angles, offsets, bounds, accumulated length, counts, or any other running value.

Mental move: return visible geometry plus the state the next group needs. The
pie segment returns its wedge and the angle where the next wedge should begin.

```python
@tree("VG Pie Segment")
def vg_pie_segment(start: Float = TAU, value: Float = 0.5, total: Float = 0.5):
    fraction = math(operation=Math.Operation.DIVIDE, value=(value, total))
    sweep = math(operation=Math.Operation.MULTIPLY, value=(fraction, TAU))
    end = math(operation=Math.Operation.ADD, value=(start, sweep))
    arc_curve = arc(
        mode=Arc.Mode.RADIUS,
        resolution=64,
        radius=1.0,
        start_angle=start,
        sweep_angle=sweep,
        connect_center=True,
    )
    return {"Curve": arc_curve.fill_curve(), "End": end}

a_geometry, a_end = vg_pie_segment(start=0.0, value=a, total=total)
b_geometry, b_end = vg_pie_segment(start=a_end, value=b, total=total)
```

Metaphor in use: each group runs its stretch and passes the baton. This is the
pattern for charts, stairs, chains, segmented shells, ribs, tracks, and
anything cumulative.

Verification cue: test the composed graph, not only the segment. A baton can be
correct locally but passed to the wrong next socket.

## Branch Helpers Are Switchboards

Reach for branch helpers when the same output contract can be fed by multiple
candidate value paths.

Mental move: compute both candidates, compute the condition, switch. `Next
Digit` chooses whether the current display position reads from the fractional
part or the whole part.

```python
whole_position = math(operation=Math.Operation.SUBTRACT, value=(position, max_precision))
use_fraction = math(operation=Math.Operation.LESS_THAN, value=(position, max_precision))
whole_digit = vg_digit_at(number=whole_part, position=whole_position)
fraction_digit = vg_digit_at(number=fraction_part, position=position)

return switch(input_type=Switch.InputType.INT, switch=use_fraction, false=whole_digit, true=fraction_digit)
```

Metaphor in use: a switchboard does not make the signal interesting. It routes
the right signal at the right moment. Verify both sides or it has merely sat
there looking employed.

Verification cue: choose cases on both sides of the branch boundary.

## Boolean Thickets Are Often Tables

Reach for table translation when a dense boolean region is mostly comparisons
against constants and OR/AND wiring.

Mental move: name the masks and clauses. Preserve behavior, not the ceremony of
every source `OR` node. `Delete Segments` is a truth table for which segment
positions should disappear for a digit.

```python
p01 = _int_equal(segment_position, 0) | _int_equal(segment_position, 1)
p45 = _int_equal(segment_position, 4) | _int_equal(segment_position, 5)
p67 = _int_equal(segment_position, 6) | _int_equal(segment_position, 7)

d1 = _float_equal(digit_minus_one, 1.0)
delete_for_one = d1 & ~(p45 | p67)

return delete_for_zero | delete_for_one | delete_for_two | delete_for_decimal
```

Metaphor in use: this is a stencil card, not a sculptor. Given a digit and slot,
it punches out the pieces that should go dark.

Verification cue: full-grid verification beats reverent node copying. The
translated delete mask was checked across 195 digit/segment-position cases.

## Values Need Megaphones

Reach for harnesses when the graph returns an invisible scalar, boolean, vector,
rotation, or string and you need behavioral evidence.

Mental move: convert the value into small observable geometry. For integer
digits, drive `Mesh Line.Count`; for booleans, switch between count 0 and 1.

```python
digit = nodes.new("GeometryNodeGroup")
digit.node_tree = bpy.data.node_groups["VG Digit At"]

line = nodes.new("GeometryNodeMeshLine")
line.count_mode = "TOTAL"
links.new(digit.outputs["Result"], line.inputs["Count"])
```

Metaphor in use: if a graph only whispers a number, build a little megaphone.
The harness does not need to be beautiful. It needs to make the output hard to
lie about.

Verification cue: record the harness because it defines what behavior was made
observable.

## Stack Abstractions Deliberately

Reach for Python helpers when repeating a tiny authoring idiom. Reach for
nested node groups when a motif has a stable visual or semantic contract that
future graphs should grab by name.

Mental move:

```text
one-off repeated node idiom -> Python helper
reusable graph part with sockets -> @tree node group
larger assembly -> nested @tree calls
```

```python
def _int_equal(value, target: int):
    return compare(
        operation=Compare.Operation.EQUAL,
        data_type=Compare.DataType.INT,
        mode=Compare.Mode.ELEMENT,
        a=value,
        b=target,
    )

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
    horizontal_bar_length = math(operation=Math.Operation.SUBTRACT, value=(horizontal_segment_size, x_separation))
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
    return {"bars": join_geometry(geometry=[top, dot])}
```

Metaphor in use: a Python helper is a stencil; a node group is a machine part
with bolt holes. Stencils keep authoring clean. Machine parts keep graphs
inspectable.

Verification cue: nested groups require both generation checks and behavior
checks. The local Geometry Script fork exists because nested `@tree` calls had
to be patched for Blender 5.1.

## Verify Shape, Contract, And Intent

Reach for verification before accepting any translation, especially when the
script feels obvious. Obvious code is where quiet swaps and axis mistakes go to
breed paperwork.

Mental move: choose the evidence that matches the promise.

- Interface sockets prove the control contract.
- Node vocabulary catches broad translation mistakes.
- Evaluated vertices prove visible shape.
- Sorted vertices prove identical shape when join order differs.
- Direct vertex order proves topology/order-sensitive behavior.
- Scalar harnesses prove invisible values.
- Full-grid tests prove table behavior.

```python
max_delta = max(
    (math.dist(a, b) for a, b in zip(sorted(source_vertices), sorted(translated_vertices))),
    default=0.0,
)
ok = len(source_vertices) == len(translated_vertices) and max_delta <= 1e-6
```

Metaphor in use: verification is not a trophy ceremony. It is a pressure test
on the exact promise the graph is making.

## Control Names Are Handles

Reach for socket cleanup when Geometry Script's generated names drift away from
the source or intended user-facing contract.

Mental move: treat names as the handles an artist, agent, or future graph grabs
later. Do not let generated title casing silently change the control surface.

```python
for item in group.interface.items_tree:
    if item.item_type == "SOCKET" and item.in_out == "OUTPUT" and item.name == "Bars":
        item.name = "bars"
    if item.item_type == "SOCKET" and item.in_out == "INPUT" and item.name in {"Radius", "Offset"}:
        item.name = item.name.lower()
```

Metaphor in use: bad handles make good machinery feel broken. The graph can be
mathematically correct and still hostile if the controls are named wrong.

Verification cue: inspect interface sockets after generation, not just Python
function signatures.

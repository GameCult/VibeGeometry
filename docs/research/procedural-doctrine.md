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

`nodes_to_script` output is evidence, not style guidance. Use generated drafts
to recover wiring, defaults, socket order, and hidden graph structure. Do not
copy their naming, ordering, or mechanical transcript shape into accepted
Geometry Script. A useful draft can still be ugly enough to need supervision.

## Python Is The Authoring Layer

Do not treat Geometry Script as the whole toolchain. It is the graph-emission
surface: the part that turns intent into inspectable Geometry Nodes groups.
Python is where intent can be structured before it becomes nodes.

Reach for ordinary Python when the design has repetition, tables, named parts,
variants, cleanup rules, validation, generated docs, render orchestration, or
scene setup. The goal is not to hide geometry in imperative mesh code. The goal
is to use Python to organize the graph authoring problem so the emitted node
groups stay legible.

Useful split:

```text
Python data/functions -> Geometry Script node groups -> bpy scene orchestration -> Blender evaluation/render
```

Example: a seven-segment display is clearer as a Python table of named bar
placements feeding repeated `vg_create_segment(...)` calls than as hand-copied
node sprawl.

```python
SEGMENT_PLACEMENTS = [
    ("top", True, (0.0, "vertical_segment_size")),
    ("middle", True, (0.0, 0.0)),
    ("bottom", True, (0.0, "negative_vertical_segment_size")),
]

for name, x_major, offset_terms in SEGMENT_PLACEMENTS:
    # In accepted scripts, expand symbolic terms into Geometry Script values
    # before calling the node group.
    segment = vg_create_segment(x_major=x_major, offset=offset_vector)
```

Metaphor in use: Python is the drafting table. Geometry Script is the machine
shop. `bpy` is the crane, paint booth, camera rig, and inspection station. Do
not ask the machine shop to be the whole factory.

Verification cue: if Python generates graph structure, verify the emitted node
groups and evaluated behavior, not the Python loop by itself.

## Ground The Coordinate Frame First

Reach for this before adding visual detail to lore-bound or reference-bound
spaces. Ornament in the wrong frame is not detail. It is a confident lie with
nice bevels.

Mental move:

```text
source vocabulary -> basis axes -> meaning of up/down -> attachment surfaces -> detail
```

For the Bloom, axial, radial, spinward, and counterspinward are not synonyms
for ordinary room directions. On a hubward endcap, "up" means inward toward the
Spire and weaker gravity, so terrace slums become annular shelves, ladders,
nets, handlines, and tilted rooms around the docking hub. They do not climb the
cylinder wall unless the lore says that wall is the relevant surface.

Code shape from the Bloom pass:

```python
def add_hubward_endcap_terraced_slums(prefix, x, mats):
    # Bloom lore frame: on an endcap, "up" is inward toward the axial Spire.
    rings = [0.95, 1.28, 1.62, 1.98, 2.36, 2.76, 3.18, 3.62, 4.08, 4.55, 4.95]
    for tier, radius in enumerate(rings[:-1]):
        inner_r = radius
        outer_r = rings[tier + 1]
        append_endcap_ring_band(shelf_verts, shelf_faces, face_x, inner_r, outer_r)
```

Metaphor in use: the coordinate frame is the local weather. Build with it and
forms lean naturally. Ignore it and every later detail needs apology machinery.

Verification cue: name representative objects after the frame they prove, then
render from a view that can reveal the attachment surface. `hubward_endcap_*`
objects prove something different from `surface_*` objects.

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

## Spines Carry Architecture

Reach for spine curves when a larger architectural feature needs a route before
it needs walls, treads, beams, rails, or trim: spiral stairs, winding roads,
bridges, ribs, towers, vines, banners, cables, and roof seams.

Mental move: author the centerline as a parameterized scaffold first. Attach
parts later. In the IRCSS French Houses file, `MakeSpiral` gives the staircase
system a screw-thread path before stair geometry is hung from it.

```python
rail = curve_line(mode=CurveLine.Mode.POINTS, start=(0.0, 0.0, 0.0), end=(0.0, 0.0, 1.0))
samples = resample_curve(keep_last_segment=True, curve=rail, mode="Count", count=200)
point_count = domain_size(component="CURVE", geometry=samples).point_count
t = math(operation=Math.Operation.DIVIDE, value=(index(), point_count))
theta = math(operation=Math.Operation.MULTIPLY, value=(t, frequency))
expanding_radius = math(
    operation=Math.Operation.ADD,
    value=(radius, math(operation=Math.Operation.MULTIPLY, value=(t, height_radius_gain))),
)
positioned = set_position(
    geometry=samples,
    position=combine_xyz(
        x=math(operation=Math.Operation.MULTIPLY, value=(math(operation=Math.Operation.SINE, value=theta), expanding_radius)),
        y=math(operation=Math.Operation.MULTIPLY, value=(math(operation=Math.Operation.COSINE, value=theta), expanding_radius)),
        z=math(operation=Math.Operation.MULTIPLY, value=(t, height)),
    ),
)
```

Metaphor in use: the spine is the chalk line on the floor before the carpentry
starts. If the chalk line is wrong, every beautiful tread and railing becomes
obedient nonsense.

Verification cue: compare ordered curve points. A spine is order-sensitive;
sorted vertices can hide a route that doubles back through the right positions
in the wrong sequence.

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

## Parameters Are Conveyors

Reach for `Accumulate Field` when a curve or repeated structure needs a steady
parameter ramp: `t`, `theta`, distance, age, row number, phase, growth amount.

Mental move: make a boring sequence of stations first, compute the step between
stations, then let the graph stamp each station with the accumulated parameter.
The equation or deformation reads that parameter downstream.

```python
step = math(
    operation=Math.Operation.DIVIDE,
    value=(max_value, math(operation=Math.Operation.SUBTRACT, value=(resolution, 1.0))),
)
theta = accumulate_field(
    data_type=AccumulateField.DataType.FLOAT,
    domain=AccumulateField.Domain.POINT,
    value=step,
).trailing

mesh = mesh_line(
    mode=MeshLine.Mode.OFFSET,
    count_mode=MeshLine.CountMode.TOTAL,
    count=resolution,
    offset=(0.0, 0.0, 1.0),
)
geometry = mesh.set_position(position=combine_xyz(x=x_from_theta, y=y_from_theta, z=0.0))
```

Metaphor in use: the mesh line is a conveyor belt. `Accumulate Field` stamps
each station with a larger number, and the curve equation tells that station
where to stand.

Verification cue: compare evaluated vertices at a non-default resolution and
range. Off-by-one errors hide at endpoints.

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

## Surface Passes Are Polish Gates

Reach for surface-state utilities when geometry already exists but needs
controlled smoothing, normals, material assignment, UVs, or attributes before
it is usable downstream.

Mental move: keep shape generation separate from finishing state. In `VG Auto
Smooth`, the mesh enters unchanged, edge angle and existing smooth flags decide
edge smoothing, then the face domain is stamped smooth.

```python
shallow_enough = compare(
    operation=Compare.Operation.LESS_EQUAL,
    data_type=Compare.DataType.FLOAT,
    mode=Compare.Mode.ELEMENT,
    a=edge_angle().unsigned_angle,
    b=angle,
)
edge_pass = set_shade_smooth(
    domain=SetShadeSmooth.Domain.EDGE,
    mesh=geometry,
    selection=is_edge_smooth(),
    shade_smooth=shallow_enough & is_face_smooth(),
)
geometry = set_shade_smooth(
    domain=SetShadeSmooth.Domain.FACE,
    mesh=edge_pass,
    selection=True,
    shade_smooth=True,
)
```

Metaphor in use: this is a polishing gate, not a forge. The form passes
through; the gate decides which surface state is allowed to survive.

Verification cue: compare surface flags as well as vertices. A finishing graph
can preserve shape perfectly while changing the thing it was built to control.

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

## Capture Before The Crowd

Reach for `Capture Attribute` when a value or index must survive a domain
change, instancing layer, or later deletion pass.

Mental move: before geometry enters a crowd of instances, pin a name and domain
to the value that later stages still need. In `VG Field Value`, the source
value, glyph face index, digit-slot index, and vector-component index each have
to ride through different instancing layers.

```python
glyph_faces = _capture_attribute_item("INT", "FACE", segment_glyph, index(), "int field")
digit_indexed = _capture_attribute_item("INT", "INSTANCE", digit_instances, index(), "int field")

hidden_segments = vg_delete_segments(
    digit=final_digit_code,
    segment_position=glyph_faces.int_field,
)
visible = delete_geometry(
    mode=DeleteGeometry.Mode.ALL,
    domain=DeleteGeometry.Domain.FACE,
    geometry=realized_digits,
    selection=hidden_segments,
)
```

Metaphor in use: capture is a luggage tag. Once geometry moves through airports
of instances and domains, untagged values are gone in the baggage system.

Verification cue: test the full composed graph after realization or deletion,
not just the captured helper. The point of capture is later survival.

## Scatter In Layers

Reach for scatter layering when the target is grass, fur, candies, rivets,
pebbles, bubbles, leaves, scales, debris, or any repeated body distributed over
a surface.

Mental move: separate the nursery from the bodies. First make the surface that
decides where points may live. Then make the point field that controls density,
spacing, randomness, scale, and seed. Then instance a separately named body and
only realize it when later deformation needs real vertices.

```python
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
    mesh=scattered_surface,
    distance_min=math(
        operation=Math.Operation.DIVIDE,
        value=(math(operation=Math.Operation.MULTIPLY, value=(thickness, 2.0)), density),
    ),
    density_max=math(operation=Math.Operation.MULTIPLY, value=(density, 5000.0)),
    density_factor=radial_falloff,
    seed=seed,
)
instances = instance_on_points(points=points.points, instance=tapered_blade)
scaled = scale_instances(instances=instances, scale=radial_falloff)
roots = _capture_attribute_item("VECTOR", "INSTANCE", scaled, position(), "Value")
realized = realize_instances(geometry=roots.geometry, realize_all=True, depth=0)
```

Metaphor in use: the scatter surface is a nursery tray. Points are planting
holes. Instances are seedlings. Realization is when the seedlings stop being
copies and become individual geometry you can bend, cut, or shade.

Verification cue: test more than one seed/control set. Scatter graphs can match
counts at one setting while density, scale, or captured-root behavior is wrong.

## Ornament Grows On Structure

Reach for this when a form has a big readable architectural body plus smaller
detail that should cling to that body: gothic caps, roof ribs, crenellations,
trim, bolts, vines, scales, and surface greebles.

Mental move: build the host silhouette first, capture the host features that
detail needs, then sample or convert those features into stations for the
ornament. Do not scatter decorative pieces in empty space and hope they look
attached.

```python
point_positions = _capture_attribute_item("VECTOR", "POINT", geometry, position(), "source position")
cone_seed = cylinder(fill_type="NGON", vertices=6, side_segments=1, fill_segments=1, radius=1.0, depth=1.0)
tapered_cone = scale_elements(
    domain="FACE",
    geometry=set_position(geometry=cone_seed.mesh, offset=(0.0, 0.0, 0.5)),
    selection=cone_seed.top,
    scale=0.10000002384185791,
    scale_mode="Uniform",
)
edge_flags = _capture_attribute_item("BOOLEAN", "EDGE", tapered_cone, cap_or_body_edge, "edge trim")
cone_instances = instance_on_points(points=point_positions.geometry, instance=cone_with_skirt.mesh, scale=cone_scale)
realized_cones = realize_instances(geometry=cone_instances, realize_all=True, depth=0)

detail_edges = delete_geometry(mode="ALL", domain="EDGE", geometry=realized_cones, selection=edge_flags.edge_trim)
detail_points = resample_curve(
    keep_last_segment=True,
    curve=mesh_to_curve(mode="EDGES", mesh=detail_edges),
    mode="Length",
    length=gothic_detail_density,
)
details = instance_on_points(points=detail_points, instance=stretched_detail, rotation=detail_rotation, scale=detail_scale)
```

Metaphor in use: the big form is scaffolding, and ornament is ivy on that
scaffolding. If the scaffold is not built first, the ivy floats there looking
confident and wrong.

Verification cue: test the plain host and the ornamented host separately. The
IRCSS `PointyGothicCone` translation verifies both `SpawnDetails=False` and
`SpawnDetails=True` against evaluated source geometry.

## Constraint Helpers Are Bumpers

Reach for constraint helpers when a procedural system has a small physical rule
that should be true after each update: stay inside a boundary, avoid another
point, cap velocity, project out of a collider, or keep motion planar.

Mental move: express the rule as condition, projection, and `Set Position`.
The condition says when the rule applies. The projection computes the nearest
allowed state. `Set Position` makes the point obey.

```python
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
    vector=(
        vector_math(
            operation=VectorMath.Operation.SCALE,
            vector=vector_math(operation=VectorMath.Operation.NORMALIZE, vector=from_center),
            scale=b,
        ),
        (1.0, 1.0, 0.0),
    ),
)
geometry = set_position(geometry=geometry, selection=outside, position=clamped_xy)
```

For point collisions, make the neighbor visible as a sampled field:

```python
neighbor = index_of_nearest(position=position())
neighbor_position = evaluate_at_index(
    domain="POINT",
    data_type="FLOAT_VECTOR",
    value=position(),
    index=neighbor.index,
)
from_neighbor = vector_math(operation=VectorMath.Operation.SUBTRACT, vector=(position(), neighbor_position))
push = vector_math(operation=VectorMath.Operation.SCALE, vector=from_neighbor, scale=push_strength)
geometry = set_position(geometry=geometry, offset=push)
```

Metaphor in use: these are bumpers on the table. They do not make the whole
simulation smart; they keep one kind of stupidity from persisting into the next
tick.

Verification cue: point clouds may evaluate to empty mesh summaries. When the
promise is point position, convert points to vertices in the harness before
comparing geometry.

## Paths Are Topology First

Reach for path nodes when the visual idea depends on connectivity: mazes,
routes, veins, circuit traces, cracks, growth paths, street maps, or solution
reveals.

Mental move: solve the graph before drawing the tube. First mark the root or
target vertices, compute path selection on mesh topology, capture the path
state that later deletion or conversion will destroy, then convert the accepted
path into visible curves.

```python
start_vertex = compare(
    operation=Compare.Operation.EQUAL,
    data_type=Compare.DataType.INT,
    mode=Compare.Mode.ELEMENT,
    a=index(),
    b=0,
)
paths = shortest_edge_paths(end_vertex=start_vertex, edge_cost=edge_cost)
path_selection = edge_paths_to_selection(next_vertex_index=paths.next_vertex_index)
captured_path = _capture_attribute_item("BOOLEAN", "EDGE", base_geometry, path_selection, "Path")
subdivided = subdivide_mesh(mesh=captured_path.geometry, level=1)
walkable = delete_geometry(
    mode=DeleteGeometry.Mode.ALL,
    domain=DeleteGeometry.Domain.POINT,
    geometry=subdivided,
    selection=captured_path.path,
)
solution = edge_paths_to_curves(mesh=walkable, start_vertices=far_x_vertices, next_vertex_index=paths.next_vertex_index)
```

Metaphor in use: topology is the street map. Curves are the painted route.
Paint after the route exists, or you are decorating roads that may be closed in
the next operation.

Verification cue: compare solved and unsolved control states. A path graph can
preserve topology while putting visible tubes at the wrong scale if anonymous
value nodes are misread.

## Rays Are Breadcrumbs

Reach for raycast helpers when a path should bounce, aim, probe, measure
distance, or react to a target object.

Mental move: keep the ray step explicit. Store the breadcrumb line, sample the
previous point, cast from there, write the next point, then pass the reflected
direction and next index forward.

```python
previous_position = sample_index(
    data_type=SampleIndex.DataType.FLOAT_VECTOR,
    domain=SampleIndex.Domain.POINT,
    clamp=True,
    geometry=line,
    value=position(),
    index=math(operation=Math.Operation.SUBTRACT, value=(hit_index, integer(integer=1))),
)
hit = raycast(
    data_type="FLOAT_VECTOR",
    target_geometry=target_info.geometry,
    interpolation="Nearest",
    source_position=previous_position,
    ray_direction=ray_direction,
    ray_length=20.0,
)
updated_line = set_position(geometry=line, selection=active_point, position=hit.hit_position)
reflected = vector_math(operation=VectorMath.Operation.REFLECT, vector=(ray_direction, hit.hit_normal))
```

Metaphor in use: every hit drops a crumb and turns the flashlight. The next
step reads the crumb, not the whole trail.

Verification cue: curve breadcrumbs need a curve-to-points or curve-to-mesh
harness before evaluated mesh comparison can see them.

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

## Clone Families Want Tables

Reach for Python tables when a source file contains numbered near-clones:
`getPie.002`, `getPie.003`, `getPie.004`, and so on.

Mental move: identify the stable contract once, then express each clone as a
row of values feeding the same group. Do not preserve source duplication as
though repetition itself were insight.

```python
values = [value_1, value_2, value_3, value_4]
labels = [label_1, label_2, label_3, label_4]
start_angle = 0.0
segments = []

for index, (segment_value, label) in enumerate(zip(values, labels), start=1):
    end_angle, geometry = vg_extended_pie_segment(
        value=segment_value,
        total=total,
        start_angle=start_angle,
        text=label,
    )
    segments.append(geometry)
    start_angle = end_angle
```

Metaphor in use: clone families are form letters. Python fills the blanks;
Geometry Script emits the one reusable machine.

Verification cue: verify at least one member alone and the composed family.
The contract can be correct while baton order in the compositor is wrong.

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

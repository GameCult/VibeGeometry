# Procedural Geometry Doctrine

This note distills what the translation corpus teaches about turning geometric
ideas into Geometry Script graphs.

## Think In Pipelines

Most useful procedural graphs are not magic knots. They are pipelines:

```text
seed geometry -> sampled domain -> field math -> deformation -> realization
```

For the Cartesian examples:

```text
line curve -> resampled curve points -> y=f(x) -> set position -> curve to mesh
```

The graph becomes legible when each stage has one job. If a stage cannot be
named in plain language, it is probably hiding either cleverness or confusion.
Both invoice later.

## Curves Are Rails

A curve is the rail the shape rides on. It can be a crude two-point line at
first. Detail comes later from resampling, profile thickness, and fields.

Geometry Script calls:

- `curve_line(...)` creates the rail.
- `resample_curve(count=...)` places regular stations along it.
- `curve_to_mesh(profile_curve=...)` gives it physical thickness.

Use curves when the intended form is a path, stroke, vine, tube, branch, cable,
arc, contour, or function plot.

## Fields Are Weather

A field is not a stored list until Blender evaluates it. It is weather over the
geometry: every point can ask, "what is the value here?"

In the Cartesian graphs:

- `position()` asks each point where it currently is.
- `separate_xyz(position())` extracts the local X address.
- math nodes compute the new Y value at that address.
- `combine_xyz(...)` builds the target position field.

Use fields when the graph should react to location, index, normal, random value,
attributes, or any other per-element condition.

## Set Position Is The Hinge

`Set Position` is where an invisible idea becomes shape. Before it, math is just
a promise. After it, the geometry has moved.

The reliable pattern is:

```text
source geometry
+ target position field
-> set_position(position=target)
```

For function curves, preserve X and Z from `Position`, then replace Y with the
formula output. This keeps the rail's sampling and bends only the dimension you
intend to control.

## Profiles Make Curves Inspectable

Curves can be visually thin or renderer-dependent. A circular profile turns a
curve into an inspectable mesh:

```text
curve_circle(radius=thickness) -> curve_to_mesh(profile_curve=profile)
```

Think of `Curve to Mesh` as dragging a drill bit along a path. The path gives
direction; the profile gives body.

## Attributes Are Optional Handles

The Cartesian source graphs use:

```text
named_attribute("radius").exists
  ? named_attribute("radius").attribute
  : 1.0
```

This is a good control pattern. A graph can expose a broad global control like
`Thickness`, while also accepting a per-point or per-curve override when a
`radius` attribute exists.

Use this when a graph should work plainly by default but become more expressive
when upstream geometry brings richer attributes.

## Groups Can Pass Batons

Reusable node groups do not have to output geometry alone. They can output
state: an angle, count, bound, accumulated offset, or any other value the next
group needs.

The pie chart segment returns:

```text
Curve: visible wedge geometry
End: the angle where the next wedge should begin
```

That makes the chart group a relay. Each segment runs its stretch, then passes
the end angle forward. This is the pattern for cumulative structures: charts,
stairs, chains, segmented shells, stacked floors, ribs, vertebrae, and anything
where part N+1 depends on where part N stopped.

## Stack Abstractions Carefully

There are two abstraction layers available:

- Python authoring abstractions: helper functions that emit repeated node
  patterns.
- Blender graph abstractions: reusable node groups nested inside other node
  groups.

The repo-local Geometry Script clone needed a Blender 5.1 patch before nested
`@tree` group references worked. After that patch, nested groups are the
preferred form for stable motifs with a named contract. Python helper functions
remain useful for tiny repeated node idioms or for sketching before a motif
deserves a public socket surface.

Metaphor: a Python helper is a stencil. It draws the same shape again wherever
you place it. A node group is a machine part bolted into another machine. Both
are useful, but they fail differently.

## Verify Shape, Not Just Vocabulary

Matching node types is weak evidence. Matching evaluated output is strong
evidence.

Use multiple checks:

- Node vocabulary and link shape: catches obvious translation mistakes.
- Interface sockets: catches broken control contracts.
- Evaluated vertex comparison: catches semantic drift.
- Sorted vertex comparison: useful when generated geometry is identical but
  join/order differs.
- Direct vertex comparison: needed when downstream topology order matters.

The circle translation proves the distinction: the geometry matched exactly as
a set of vertices, but direct vertex order differed even after restoring nested
group reuse. Matching shape and matching topology order are related but not the
same promise.

## Control Names Are Contracts

Geometry Script may title-case parameter names. For user-facing groups,
post-generation cleanup can be needed to preserve source-compatible controls
such as `r`, `m`, `a`, `b`, and `c`.

Do not treat socket names as cosmetic. They are the handles an agent or artist
will grab later. Bad handles make good machinery feel broken.

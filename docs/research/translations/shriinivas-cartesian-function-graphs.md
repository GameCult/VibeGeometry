# Translation: Shriinivas Cartesian Function Graphs

## Source

- Repository: https://github.com/Shriinivas/geometrynodes
- Source file: `cartesian.blend`
- Source groups:
  - `Geometry Nodes Line`
  - `Geometry Nodes Parabola`
  - `Geometry Nodes Circle`
- Geometry Script recreation:
  `examples/geometry_script/shriinivas_cartesian_helper.py`

## Graph Family

These groups are three versions of the same procedural sentence:

```text
make a simple path
read each point's position
compute a new Y value from X
move the path into that shape
give the curve physical thickness
```

The source file uses this sentence to draw Cartesian function curves. The line
uses `y = m*x + value`. The parabola uses `y = a*x^2 + b*x + c`. The circle
uses the helper graph twice:

```text
y = sqrt(r^2 - x^2)
y = -sqrt(r^2 - x^2)
```

then joins the upper and lower arcs before giving them thickness.

## Translation Summary

### Line

Source group: `Geometry Nodes Line`

Geometry Script group: `VG Cartesian Line`

Mechanism:

- Build a two-point `Curve Line` from origin to `(Length, 0, 0)`.
- Read the current field `Position`.
- Split position into X/Y/Z.
- Compute `y = m*x + Value`.
- Recombine `(x, y, z)`.
- Feed the vector into `Set Position`.
- Convert the resulting curve to mesh using a circular profile.

Metaphor: the curve is a straight rail, and the position field is a set of
chalk marks along it. The math node chain tells each chalk mark how high to
stand. `Set Position` is the hand lifting those marks into place.

### Parabola

Source group: `Geometry Nodes Parabola`

Geometry Script group: `VG Cartesian Parabola`

Mechanism:

- Build a line from `(Start, 0, 0)` to `(End, 0, 0)`.
- Resample it to `Sample Resolution` points.
- Read each point's X coordinate.
- Compute `y = a*x^2 + b*x + c`.
- Move the resampled curve with `Set Position`.
- Tube the curve with `Curve to Mesh`.

Metaphor: resampling makes evenly spaced beads on a string. The parabola
formula is the jig that bends each bead upward or downward based on its X
address.

The source group has two input sockets named `Resolution`; only the later one
drives `Resample Curve.Count`. The translation keeps the unused compatibility
input as `Resolution` and names the active control `Sample Resolution`. This is
one place where perfect socket-name mimicry would make the generated graph less
legible.

### Circle

Source group: `Geometry Nodes Circle`

Geometry Script group: `VG Cartesian Circle`

Mechanism:

- Compute left and right X endpoints from `-r` and `r`.
- Build an upper arc with `sqrt(r^2 - x^2)`.
- Build a lower arc with the same helper and `Value = -1`.
- Move both arcs with `Set Position`.
- Join the two curves.
- Tube the joined curve with `Curve to Mesh`.

Metaphor: the helper graph is a compass arm. Run it once above the axis and
once below the axis, then clamp the two strokes together into a full circle.

The source graph reuses `NodeGroup.001` as nested group nodes. The installed
Geometry Script code initially failed in this path under Blender 5.1 because
its `@tree` returned function called a missing `geometrynodegroup(...)` symbol.
We patched the repo-local Geometry Script clone so nested `@tree` calls create
`GeometryNodeGroup` nodes directly, wire inputs, and expose typed outputs.

The translation now calls `vg_cartesian_helper(...)` twice inside
`VG Cartesian Circle`, preserving the repeated motif as nested graph organs
instead of expanding it inline.

## Control Surfaces

These graphs expose the useful joints:

- `Length`: extent of the line along X.
- `m`: line slope.
- `Value`: line Y offset, and helper polarity/amplitude.
- `Start` / `End`: sampled X range for the parabola.
- `a`, `b`, `c`: parabola coefficients.
- `r`: circle radius.
- `Thickness`: curve profile radius.
- `Sample Resolution`: number of samples before bending a curve.

The important pattern is that controls should match geometric intent, not node
incidental detail. A user wants radius, slope, coefficient, and thickness; they
do not want to manage the third socket of a math node like a cursed vending
machine.

## Verification

Run:

```powershell
& 'C:\Program Files (x86)\Steam\steamapps\common\Blender\blender.exe' --background '.\experiments\source-blends\shriinivas-cartesian.blend' --python '.\tools\verify_cartesian_translations.py'
```

Verification wraps each source and translated group in the same evaluator,
evaluates the resulting mesh, and compares vertices.

Results from Blender 5.1.1:

| Case | Vertices | Direct max delta | Sorted max delta | Status |
| --- | ---: | ---: | ---: | --- |
| Helper | 200 | 0.0 | 0.0 | accepted |
| Line | 64 | 0.0 | 0.0 | accepted |
| Parabola | 992 | 0.0 | 0.0 | accepted |
| Circle | 2368 | 1.2999999523162842 | 0.0 | accepted |

Circle has identical geometry but different vertex order. For rendered geometry
and shape behavior, sorted vertex equality is the relevant check. For
simulations or downstream topology-sensitive processing, direct order would
matter and should be preserved deliberately.

## Lessons

- A field is weather over geometry: it has a value at every point, not one
  value globally. `Position` is the weather station every point carries.
- `Set Position` is the hinge where an abstract formula becomes visible
  geometry.
- `Curve to Mesh` is a lathe/extruder: it turns a weightless path into a tube by
  dragging a profile along it.
- `Named Attribute` plus `Switch` is a graceful override hook: if a `radius`
  attribute exists, use it; otherwise fall back to scale `1.0`.
- Nested Geometry Script `@tree` calls are now viable after the patch branch in
  `external/geometry-script`. Use them when a repeated motif deserves to remain
  a named, inspectable organ in the generated Blender graph.
- Python helper functions are still useful for repeated authoring idioms that do
  not need to survive as named node groups.
- Socket names are part of the control contract. Geometry Script title-cases
  one-letter parameter names, so finalization currently renames `R`, `M`, `A`,
  `B`, and `C` back to `r`, `m`, `a`, `b`, and `c`.

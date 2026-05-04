# Translation: Shriinivas Parametric And Polar Equations

## Source

- Repository: https://github.com/Shriinivas/geometrynodes
- Source file: `paramnpolareq.blend`
- Source groups:
  - `NodeGroup`
  - `NodeGroup.001`
  - `NodeGroup.002`
  - `NodeGroup.003`
  - `Archimedes Spiral`
  - `Epicycloid`
  - `Geometry Nodes Group.002`
- Geometry Script recreation:
  `examples/geometry_script/shriinivas_paramnpolareq.py`

## Why This Graph

This sample teaches parametric curve construction without hiding behind final
rendering polish. The source graphs make a line of points, accumulate a
parameter over that line, turn the parameter into `x/y` fields, and then move
the points into curve shapes.

## Equation Helpers

`VG Param Epicycloid X` and `VG Param Epicycloid Y` recreate the source
epicycloid scalar helpers:

```text
x = (a + b) * cos(t) - b * cos((a / b + 1) * t)
y = (a + b) * sin(t) - b * sin((a / b + 1) * t)
```

`VG Polar Spiral X` and `VG Polar Spiral Y` recreate the polar helper pair:

```text
r = a + b * theta
x = cos(theta) * r
y = sin(theta) * r
```

Metaphor: these helpers are plotter pens without paper. They answer "where
should the point be for this parameter?" but they do not decide how many points
exist or how the curve is sampled.

## Parameter Conveyor

`VG Archimedes Spiral`, `VG Epicycloid`, and `VG Mirrored Root Spiral` share a
sampling spine:

- Create a `Mesh Line` with `Resolution` points.
- Compute `step = max_value / (Resolution - 1)`.
- Feed `step` into `Accumulate Field`.
- Use the trailing accumulated value as `theta` or `t`.
- Compute `x/y`, combine them into a position, and move the mesh line with
  `Set Position`.

Metaphor: the mesh line is a conveyor belt. `Accumulate Field` stamps each
station with a progressively larger parameter, and the equation helper tells
that station where to stand.

## Mirrored Root Spiral

Source group `Geometry Nodes Group.002` is a two-arm spiral:

```text
theta = accumulated(2 * pi * Round Count)
r = a * sqrt(theta)
x = r * cos(theta)
y = r * sin(theta)
```

The source builds a forward point stream and a mirrored stream at `(-x, -y)`,
then joins them.

Metaphor: the first arm is a chalk line unwinding from the center; the second
arm is the same chalk line reflected through the origin.

## Verification

Run:

```powershell
& 'C:\Program Files (x86)\Steam\steamapps\common\Blender\blender.exe' --background '.\experiments\source-blends\shriinivas-paramnpolareq.blend' --python '.\tools\verify_paramnpolareq_translations.py'
```

Results from Blender 5.1.1:

| Case | Source | Translated | Delta | Status |
| --- | ---: | ---: | ---: | --- |
| Epicycloid X scalar vertex | 1 vertex | 1 vertex | 0.0 | accepted |
| Epicycloid Y scalar vertex | 1 vertex | 1 vertex | 0.0 | accepted |
| Polar X scalar vertex | 1 vertex | 1 vertex | 0.0 | accepted |
| Polar Y scalar vertex | 1 vertex | 1 vertex | 0.0 | accepted |
| Archimedes Spiral vertices | 64 | 64 | 4.47e-8 | accepted |
| Epicycloid vertices | 80 | 80 | 0.0 | accepted |
| Mirrored Root Spiral vertices | 192 | 192 | 0.0 | accepted |

The scalar helpers are verified by putting the scalar into a single vertex's X
position. The curve groups are verified by sorted evaluated vertex comparison.

## Lessons

- `Accumulate Field` is the natural way to build a parameter ramp inside a
  node graph. Python should describe the ramp; the graph should evaluate it.
- Equation helpers are worth naming when several curve generators need the same
  scalar law.
- Verifiers should normalize socket names when comparing source groups to
  generated groups. `maxT` and `Max T` are the same control for behavior even
  when the UI spelling drifts.
- A scalar harness should preserve numeric value, not just count geometry.
  Driving a vertex coordinate is often cleaner than driving `Mesh Line.Count`.

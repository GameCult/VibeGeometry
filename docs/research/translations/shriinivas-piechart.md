# Translation: Shriinivas Pie Chart

## Source

- Repository: https://github.com/Shriinivas/geometrynodes
- Source file: `piechart.blend`
- Source groups:
  - `NodeGroup`
  - `Pie Chart`
- Geometry Script recreation:
  `examples/geometry_script/shriinivas_piechart.py`

## Graph Family

The small pie chart is a nested state-passing graph. Each segment receives:

```text
start angle
value
total
shift distance
materials
```

It outputs:

```text
segment geometry
end angle
```

The chart group chains three segment calls:

```text
A starts at 0
B starts at A.end
C starts at B.end
```

This is the new abstraction lesson: a node group can return geometry and a
control value. The geometry is the visible slice; the control value is the baton
passed to the next runner.

## Segment Map

Source group: `NodeGroup`

Geometry Script group: `VG Pie Segment`

Mechanism:

- Compute `fraction = Value / Total`.
- Compute `sweep = fraction * tau`.
- Compute `End = Start + sweep`.
- Build a connected-center `Arc` from `Start` through `sweep`.
- Fill the arc into a mesh face.
- Extrude the face downward for pie thickness.
- Convert `fraction * 100` to a string and append `%`.
- Convert that string to curves, fill it, and extrude it lightly into text.
- Use `Attribute Statistic` over the slice face's `Position` to find a center
  offset for the text.
- Compute a shift vector at the segment midpoint:

```text
mid = Start + sweep / 2
offset = (cos(mid) * Shift, sin(mid) * Shift, 0)
```

- Join text, extruded slice, and cap face.
- Offset the joined geometry by the shift vector.
- Return geometry plus `End`.

Metaphor: the segment group is a pastry cutter with a receipt printer attached.
It cuts one wedge, stamps the percentage label near its middle, nudges the whole
wedge outward if requested, and hands the next cutter the angle where it stopped.

## Chart Map

Source group: `Pie Chart`

Geometry Script group: `VG Pie Chart`

Mechanism:

- Compute `Total = A + B + C`.
- Call `VG Pie Segment` for A with `Start = 0`.
- Call `VG Pie Segment` for B with `Start = A.End`.
- Call `VG Pie Segment` for C with `Start = B.End`.
- Join the three segment geometries.

Metaphor: the chart group is not a shape maker. It is an accountant-conductor:
it totals the values, cues each segment in order, and makes sure every slice
starts where the previous one ended.

## Verification

Run:

```powershell
& 'C:\Program Files (x86)\Steam\steamapps\common\Blender\blender.exe' --background '.\experiments\source-blends\shriinivas-piechart.blend' --python '.\tools\verify_piechart_translations.py'
```

Results from Blender 5.1.1:

| Case | Vertices | Sorted max delta | Status |
| --- | ---: | ---: | --- |
| Segment | 319 | 0.0 | accepted |
| Chart | 957 | 0.0 | accepted |

Generated groups saved and reinspected:

- `VG Pie Segment`: 30 nodes, 48 links.
- `VG Pie Chart`: 8 nodes, 25 links.

## Lessons

- A reusable node group can output both visible geometry and invisible state.
  That state can drive later graph calls.
- `Arc` with `connect_center=True` is a wedge skeleton. `Fill Curve` gives it a
  face; `Extrude Mesh` gives it thickness.
- `Attribute Statistic` can summarize geometry to produce placement handles.
  Here, the mean position of the wedge face becomes a label anchor.
- Text is geometry too: string operations feed `String to Curves`, then the same
  fill/extrude/material pipeline applies.
- Charts and other sequential structures often need cumulative scalar flow.
  In Geometry Script, nested `@tree` calls make that flow readable as ordinary
  Python variable passing.

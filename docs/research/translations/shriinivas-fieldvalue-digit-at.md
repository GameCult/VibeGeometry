# Translation: Shriinivas Field Value Helpers

## Source

- Repository: https://github.com/Shriinivas/geometrynodes
- Source file: `fieldvalue.blend`
- Source groups:
  - `Create Decimal`
  - `Create Segment`
  - `Digit At`
- Geometry Script recreation:
  `examples/geometry_script/shriinivas_fieldvalue.py`

## Why This Graph

`fieldvalue.blend` contains a large seven-segment field display system. The full
`Field Value` graph has 176 nodes, so the first honest targets are small
helpers: `Create Decimal` and `Digit At`.

Together they show the first display-system layers: tiny glyph geometry,
field-sculpted segment geometry, and value-only digit extraction.

## Create Decimal Map

Source group: `Create Decimal`

Geometry Script group: `VG Create Decimal`

Mechanism:

- Create a filled 32-vertex `Mesh Circle`.
- Use `radius` as the circle radius.
- Offset it downward by `Vertical Segment Size * -1`.
- Return the dot geometry.

Metaphor: the decimal is a loose bead placed under the seven-segment digit
frame. It is not a digit; it is punctuation geometry with one placement rule.

## Digit At Map

Inputs:

- `Number`
- `Position`

Output:

- `Result`

Mechanism:

- Shift `Position` by one.
- Divide `Number` by `10^(Position + 1)`.
- Take the fractional part.
- Multiply by 10 to isolate the digit window.
- Scale by `10^Position`, round, then divide back down.
- If `Position == 0`, round the result.
- Otherwise, floor the result.

Metaphor: the group is a little inspection window sliding over a number. It
moves to the requested decimal place, crops the surrounding digits away, then
decides whether to round or floor the exposed digit.

## Create Segment Map

Source group: `Create Segment`

Geometry Script group: `VG Create Segment`

Mechanism:

- Build a `Grid` with either `2x3` or `3x2` vertices depending on `X Major`.
- Read each vertex `Position`.
- Split the position into major-axis and secondary-axis coordinates.
- Build a tip vector along the major axis:

```text
tip = 0.5 * Sharpness * Secondary Axis Segment Thickness
```

- Detect vertices on the secondary axis and at the positive/negative segment
  ends.
- Push only those gated vertices inward/outward to make pointed segment tips.
- Add the user `offset`.
- Move the grid vertices with `Set Position`.

Metaphor: the segment starts as a plain rectangular tile. The position field is
a stencil laid over its vertices. The end-corner vertices get pinched into tips,
while the middle vertices stay put. It is a chisel, not a sculpting spree.

## Verification

Run:

```powershell
& 'C:\Program Files (x86)\Steam\steamapps\common\Blender\blender.exe' --background '.\experiments\source-blends\shriinivas-fieldvalue.blend' --python '.\tools\verify_fieldvalue_translations.py'
```

The verifier wraps both source and translated `Digit At` groups in a mesh-line
graph where the digit output drives vertex count. This turns a scalar output
into geometry Blender can evaluate and compare.

Results from Blender 5.1.1:

| Case | Source | Translated | Delta | Status |
| --- | ---: | ---: | ---: | --- |
| Create Decimal vertices | 32 | 32 | 0.0 | accepted |
| Create Segment horizontal vertices | 6 | 6 | 0.0 | accepted |
| Create Segment vertical vertices | 6 | 6 | 0.0 | accepted |
| Digit At `1234.0`, position `0` | 4 | 4 | 0 | accepted |
| Digit At `1234.0`, position `1` | 3 | 3 | 0 | accepted |
| Digit At `98765.0`, position `2` | 7 | 7 | 0 | accepted |
| Digit At `120305.0`, position `3` | 0 | 0 | 0 | accepted |

## Lessons

- Not every useful node group emits final geometry. Some are value transducers.
- Value-only graph behavior can still be verified in Blender by embedding the
  value output inside a small geometry-producing harness.
- Digit extraction is windowing: scale, crop with fraction/floor/round, then
  normalize.
- Large procedural display systems should be built from tiny tested scalar
  helpers before composing visible glyph geometry.
- Tiny glyph marks are still worth isolating as named groups. A decimal point is
  just a dot, but a named dot with scale and placement controls is a reusable
  punctuation part.
- Field masks can act as chisels. In `Create Segment`, comparisons over
  position decide which vertices are allowed to move, creating pointed tips
  without hand-authoring mesh coordinates.

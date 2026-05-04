# Translation: Shriinivas Field Value Digit At

## Source

- Repository: https://github.com/Shriinivas/geometrynodes
- Source file: `fieldvalue.blend`
- Source group: `Digit At`
- Geometry Script recreation:
  `examples/geometry_script/shriinivas_fieldvalue.py`

## Why This Graph

`fieldvalue.blend` contains a large seven-segment field display system. The full
`Field Value` graph has 176 nodes, so the first honest target is a scalar helper:
`Digit At`.

This group does not make visible geometry. It extracts a digit from a number at
a requested decimal position. That makes it useful for learning how value-only
node groups support larger procedural systems.

## Graph Map

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

## Verification

Run:

```powershell
& 'C:\Program Files (x86)\Steam\steamapps\common\Blender\blender.exe' --background '.\experiments\source-blends\shriinivas-fieldvalue.blend' --python '.\tools\verify_fieldvalue_translations.py'
```

The verifier wraps both source and translated `Digit At` groups in a mesh-line
graph where the digit output drives vertex count. This turns a scalar output
into geometry Blender can evaluate and compare.

Results from Blender 5.1.1:

| Number | Position | Source Count | Translated Count | Status |
| ---: | ---: | ---: | ---: | --- |
| 1234.0 | 0 | 4 | 4 | accepted |
| 1234.0 | 1 | 3 | 3 | accepted |
| 98765.0 | 2 | 7 | 7 | accepted |
| 120305.0 | 3 | 0 | 0 | accepted |

## Lessons

- Not every useful node group emits final geometry. Some are value transducers.
- Value-only graph behavior can still be verified in Blender by embedding the
  value output inside a small geometry-producing harness.
- Digit extraction is windowing: scale, crop with fraction/floor/round, then
  normalize.
- Large procedural display systems should be built from tiny tested scalar
  helpers before composing visible glyph geometry.

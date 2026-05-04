# Translation: Shriinivas Field Value Helpers

## Source

- Repository: https://github.com/Shriinivas/geometrynodes
- Source file: `fieldvalue.blend`
- Source groups:
  - `Create Decimal`
  - `Create Segment`
  - `Seven Segments`
  - `Delete Segments`
  - `Next Digit`
  - `Digit At`
  - `Field Value`
- Geometry Script recreation:
  `examples/geometry_script/shriinivas_fieldvalue.py`

## Why This Graph

`fieldvalue.blend` contains a large seven-segment field display system. The full
`Field Value` graph has 176 nodes, so the first honest targets are helpers that
build the digit chassis before the full display logic is attempted.

Together they show the first display-system layers: tiny glyph geometry,
field-sculpted segment geometry, segment composition, segment visibility masks,
and value-only digit extraction.

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

## Seven Segments Map

Source group: `Seven Segments`

Geometry Script group: `VG Seven Segments`

Mechanism:

- Divide horizontal and vertical segment sizes by two to get left/right and
  upper/lower placement extents.
- Subtract `X Separation` from horizontal length and `Y Seperation` from
  vertical length so the bars leave small gaps.
- Create four vertical bars with `X Major = False`:
  lower left, upper left, lower right, and upper right.
- Create three horizontal bars with `X Major = True`:
  bottom, middle, and top.
- Create the decimal dot with radius `Horizontal Segment Thickness / 2`.
- Join dot plus seven bars into one `bars` output.

Metaphor: `Create Segment` is a single machined stroke; `Seven Segments` is the
digit chassis. It bolts seven strokes and one punctuation bead onto a shared
frame so later graph layers can decide which pieces stay visible.

## Delete Segments Map

Source group: `Delete Segments`

Geometry Script group: `VG Delete Segments`

Inputs:

- `Digit`
- `Segment Position`

Output:

- `result`

Mechanism:

- Shift `Digit` down by one.
- Group `Segment Position` into repeated pair masks:
  `0/1`, `2/3`, `4/5`, `6/7`, `8/9`, `10/11`, `12/13`, plus singleton `14`.
- Compare the shifted digit against the source's digit cases.
- For each digit case, return true when that segment-position mask should be
  deleted.
- OR all digit-specific delete clauses into the final `result`.

Metaphor: `Delete Segments` is not a sculptor. It is a stencil card. Given a
digit and a slot on the chassis, it punches out the slots that should go dark.

## Next Digit Map

Source group: `Next Digit`

Geometry Script group: `VG Next Digit`

Inputs:

- `Whole Part`
- `Fraction Part`
- `Max Precision`
- `Position`

Output:

- `Result`

Mechanism:

- Compute `Position - Max Precision` for whole-part indexing.
- Compare `Position < Max Precision`.
- If true, read from `Fraction Part` at `Position`.
- If false, read from `Whole Part` at `Position - Max Precision`.

Metaphor: `Next Digit` is the read head for the display tape. Before the decimal
boundary it reads the fractional reel; after that boundary it reads the whole
number reel.

## Field Value Map

Source group: `Field Value`

Geometry Script group: `VG Field Value`

Mechanism:

- Use menu switches to route three control choices:
  input type (`Float` or `Vector`), source domain (`Point`, `Edge`, or `Face`),
  and text alignment (`Center`, `Right`, or `Left`).
- Capture the requested float or vector field on point, edge, and face domains,
  then choose the captured geometry and captured value stream for the active
  domain.
- Convert edge or face domains to points so the display can instance one value
  readout per source element.
- Build one seven-segment glyph, capture each glyph face index, then instance
  that glyph across digit slots, vector component slots, and source elements.
- Sample source position and normal by domain index so each readout can be
  placed and oriented back onto the element that produced it.
- Compute the active scalar value for the current component, split it into
  whole/fractional parts, decide visible slots, negative sign, decimal point,
  overflow, and leading-zero behavior.
- Call `VG Next Digit` for digit extraction and `VG Delete Segments` to delete
  the dark faces from each glyph.
- Realize instances and assign the requested material.

Metaphor: the full graph is a label printer mounted on the mesh. It reads a
value from each element, assembles a small digit rack, swings the rack onto the
element normal, then punches out the unlit segments.

Implementation note: Blender 5 capture items and menu sockets exposed two
Geometry Script drift points. `VG Field Value` uses a local
`_capture_attribute_item(...)` helper to create typed capture items explicitly,
and the VibeGeometry Geometry Script fork tolerates menu socket defaults whose
enum items do not exist at group-interface construction time.

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
| Seven Segments vertices | 74 | 74 | 0.0 | accepted |
| Digit At `1234.0`, position `0` | 4 | 4 | 0 | accepted |
| Digit At `1234.0`, position `1` | 3 | 3 | 0 | accepted |
| Digit At `98765.0`, position `2` | 7 | 7 | 0 | accepted |
| Digit At `120305.0`, position `3` | 0 | 0 | 0 | accepted |
| Field Value default-route vertices | 256 | 256 | 0.0 | accepted |
| Next Digit branch cases | 4 cases | 4 cases | 0 mismatches | accepted |
| Delete Segments grid | 195 cases | 195 cases | 0 mismatches | accepted |

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
- Composition groups should preserve part boundaries in the script even when
  the output is one joined geometry stream. The source `Seven Segments` graph is
  easier to reason about as four vertical bars, three horizontal bars, and one
  dot than as a pile of joined anonymous geometry.
- Dense boolean graphs often hide lookup tables. Translate them into named
  clauses and verify over the full input grid instead of preserving every source
  `OR` node as ceremony.
- A branch helper deserves tests on both sides of the branch. `Next Digit`
  verifies positions before and after `Max Precision`, because the interesting
  behavior is not digit extraction itself but choosing which number part feeds
  extraction.
- Capture attributes are a loading dock for fields. Once a graph crosses into
  instancing, capture the values and indices that later stages must still know.
- Full display graphs are stacked assemblies: source element points carry
  value racks; value racks carry component stacks; component stacks carry digit
  slots; digit slots carry segment faces. Preserve each layer's index baton.

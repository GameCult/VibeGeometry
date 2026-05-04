# Translation: Shriinivas Cartesian Helper

## Source

- Repository: https://github.com/Shriinivas/geometrynodes
- Source file: `cartesian.blend`
- Local ignored copy:
  `experiments/source-blends/shriinivas-cartesian.blend`
- Source node group: `NodeGroup.001`
- License: MIT, per source repository.

## Why This Graph

This was the smallest geometry node group in `cartesian.blend` after inspection.
It is a useful first translation because it combines:

- group inputs and multiple outputs
- a generated curve primitive
- curve resampling
- field-driven position reads
- scalar math
- vector recomposition

It does not include materials, object modifiers, or final scene polish. That is
good. First learn the tendon before drawing the whole hand.

## Source Inspection

Inspected with:

```powershell
& 'C:\Program Files (x86)\Steam\steamapps\common\Blender\blender.exe' --background '.\experiments\source-blends\shriinivas-cartesian.blend' --python '.\tools\inspect_blend_node_groups.py' -- --json '.\experiments\inspection\shriinivas-cartesian-node-groups.json'
```

Source group summary:

- Node group: `NodeGroup.001`
- Nodes: 15
- Links: 20
- Inputs: `Count`, `Start`, `End`, `r`, `Value`
- Outputs: `Curve`, `Vector`
- Node types:
  - `GeometryNodeCurvePrimitiveLine`
  - `GeometryNodeInputPosition`
  - `GeometryNodeResampleCurve`
  - `NodeGroupInput`
  - `NodeGroupOutput`
  - `NodeReroute`
  - `ShaderNodeCombineXYZ`
  - `ShaderNodeMath`
  - `ShaderNodeSeparateXYZ`

## Plain-Language Graph Map

The group builds a straight curve from `Start` to `End`, then resamples it to
`Count` points. That output is the `Curve`.

Separately, it reads the current `Position` field and splits it into X, Y, and
Z. It keeps X and Z as-is. For Y, it computes:

```text
sqrt(r^2 - x^2) * Value
```

Then it combines:

```text
(x, sqrt(r^2 - x^2) * Value, z)
```

That output is the `Vector`.

The group is a helper for bending or lifting a Cartesian curve into a circular
arc-like profile. It does not move geometry by itself; it emits the curve and
the vector field that another graph can feed into `Set Position`.

## Geometry Script Translation

Script:

```text
examples/geometry_script/shriinivas_cartesian_helper.py
```

The translation intentionally omits source reroute nodes. Reroutes clarify the
visual editor layout but do not change graph semantics.

One small compatibility adjustment is made after generation: the auto-created
Geometry Script input socket `R` is renamed to `r` to match the source group.

## Verification

Smoke-tested with Blender 5.1.1:

```powershell
& 'C:\Program Files (x86)\Steam\steamapps\common\Blender\blender.exe' --background --python '.\examples\geometry_script\shriinivas_cartesian_helper.py'
```

Result:

```text
VG_CARTESIAN_HELPER True 12 19
```

Generated node types:

- `GeometryNodeCurvePrimitiveLine`
- `GeometryNodeInputPosition`
- `GeometryNodeResampleCurve`
- `NodeGroupInput`
- `NodeGroupOutput`
- `ShaderNodeCombineXYZ`
- `ShaderNodeMath`
- `ShaderNodeSeparateXYZ`

Saved-and-reinspected generated `.blend`:

```text
VG Cartesian Helper: nodes=12 links=19
```

The generated group has fewer nodes than the source because it omits three
`NodeReroute` layout nodes and one reroute link. The computational nodes match
the source mechanism.

Behavior verification:

```powershell
& 'C:\Program Files (x86)\Steam\steamapps\common\Blender\blender.exe' --background '.\experiments\source-blends\shriinivas-cartesian.blend' --python '.\tools\verify_cartesian_helper_behavior.py'
```

The verification harness wraps both the source helper and the Geometry Script
helper in the same graph:

```text
helper Curve + helper Vector -> Set Position -> Curve to Mesh
```

It evaluates both generated meshes with:

```text
Count = 25
Start = (-0.45, 0.0, 0.0)
End = (0.45, 0.0, 0.0)
r = 0.6
Value = 1.25
```

Result:

```text
source_vertex_count = 200
translated_vertex_count = 200
max_vertex_delta = 0.0
mean_vertex_delta = 0.0
```

This verifies that the translated helper retained the source helper's evaluated
behavior for the tested parameter set, not merely its rough node vocabulary.

## Lessons

- The local generated Geometry Script docs should be checked before writing each
  node call. Function signatures and result-object shapes matter.
- Geometry Script is good at semantic graph construction, but it will not
  preserve visual-editor layout details such as reroutes unless we explicitly
  add them.
- Generated node groups need `use_fake_user = True` or a real modifier/object
  user before saving, or Blender will discard them as orphan data.

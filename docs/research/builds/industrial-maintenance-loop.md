# Industrial Maintenance Loop

Grounded fixture generated from the maintenance-loop reference prompt and image.

Run:

```powershell
cargo run -p vg_csg --example industrial_maintenance_loop
```

Outputs:

- `experiments/generated/industrial_maintenance_loop/industrial_maintenance_loop.obj`
- `experiments/generated/industrial_maintenance_loop/industrial_maintenance_loop.mtl`
- `experiments/generated/industrial_maintenance_loop/industrial_maintenance_loop_preview.svg`
- `experiments/generated/industrial_maintenance_loop/industrial_maintenance_loop_preview.png`

Current build stats:

- brushes: 266
- convex fragments: 266
- vertices: 11,448
- triangles: 4,128
- candidate pairs: 0
- rejected pairs: 0
- CSG warnings: 0

## Composition

The scene is a single-level industrial maintenance loop built into a curved
habitat shell. It includes:

- annular scuffed deck, curved outer shell wall, inner island shroud, and
  continuous ceiling previewed as x-ray shell material
- one floor-to-ceiling central machinery island that blocks the far loop
- inner manifold faces with gasket panel proxies, access hatches, amber
  diagnostic strips, and cable bundles
- outer staging zone with anchor rail, sliding rail blocks, lockers, carts,
  clipped rescue lines, and hazard markings
- one raised supervisor gallery segment behind glass with a visible stair
- service artery mouths and pipe-tunnel throats entering the machinery island
- dry-operation mobility gear rack with folded harness loops, cartridges,
  oxygenation tube proxies, and charging/detail blocks

## DSL Lesson

This fixture is mostly about coordinate systems. The example introduces a local
`LoopFrame` helper:

```rust
let frame = LoopFrame::at(angle, OUTER_LOOP_RADIUS - 1.15);
loop_box(level, "bolted outer anchor rail", frame, LoopBox {
    tangent: 0.0,
    radial: 0.0,
    z: 0.55,
    size_tangent: 1.25,
    size_radial: 0.18,
    size_z: 0.18,
    material: HAZARD,
});
```

The move is simple and important: author each surface in its own domain. The
outer staging zone thinks in tangent/radial/up. The inner manifold face uses
the same axes at a different radius. The gallery owns one angular segment. The
shell is generated as annular and vertical arc bands. The world-space brush
placement becomes a compilation step instead of the authoring language.

That is the shape the DSL should grow toward: named local coordinate contracts,
small repeated detail organs, and late mapping into CSG brushes or direct mesh
panels depending on whether the surface needs boolean behavior.

## Caveat

The SVG preview is an inspection cutaway, not a physical render. The model
contains a continuous ceiling and shell, but the preview makes shell materials
transparent so the internal fixture can be judged without a renderer. A Bevy or
Blender pass should turn this into a lit interior view with proper occlusion,
glass, emissive panels, and worn materials.

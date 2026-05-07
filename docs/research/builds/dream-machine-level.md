# Dream Machine Level Slice

This is the first visible Rust-side showpiece for the CSG assembler.

Run:

```powershell
cargo run -p vg_csg --example dream_machine_level
```

Outputs:

- `experiments/generated/dream_machine_level/dream_machine_level.obj`
- `experiments/generated/dream_machine_level/dream_machine_level.mtl`
- `experiments/generated/dream_machine_level/dream_machine_level_preview.svg`

Current build stats:

- brushes: 207
- convex fragments: 375
- vertices: 17,552
- triangles: 6,448
- candidate pairs: 384
- rejected pairs: 1,343
- CSG warnings: 0

## Composition

The level is a machine-cathedral switchyard built directly through
`LevelDsl`. It combines:

- a cut foundation nave with long retaining walls and diagonal vent voids
- a central reactor plinth, cylinder throat, and glass dome cap
- concentric anchor-city towers fading into lower blocks and park patches
- radial plaza strips proving shared polar coordinate intent
- alternating solar and radiator ray florets extending far past the city disk
- looping cargo arteries and outer piers for large-scale structure language

The point is not visual finality. The point is a durable artifact that proves
the Rust CSG organ can already author a named, inspectable, multi-part spatial
idea and emit a portable mesh without waiting for the Bevy renderer loop.

## Doctrine

Use `LevelDsl` as the fast blockout brush, not as a secret final art pipe.
When the idea needs proof now, the DSL can hold the spatial claim in explicit
named primitives, export mesh evidence, and keep the pressure on the CSG kernel.

Additive habitat primitives are useful as scale-language anchors. Dome caps and
florets make the scene read as infrastructure instead of only boxes. The CSG
cuts still carry the machine grammar: trenches, vents, arcades, and service
voids are how solid mass becomes a level instead of a pile.

The preview SVG is deliberately dumb. It is a quick inspection surface for
shape, density, material partitioning, and catastrophic export failures. It is
not a substitute for Blender or Bevy render review.

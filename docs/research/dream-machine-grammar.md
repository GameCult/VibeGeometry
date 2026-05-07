# Dream Machine Grammar

The grammar layer is the authoring mind above CSG.

```text
brief / lore / level intent
-> procedural grammar rules
-> semantic solid and void claims
-> CSG tree classification
-> visible polygon set
-> Bevy mesh cache
-> inspection loop
```

`crates/vg_grammar` starts this layer. It deliberately emits claims before
geometry:

- `Solid` claims say matter exists.
- `Void` claims say space must stay empty.
- tags preserve why the claim exists: `room`, `corridor`, `door`, `wall`,
  `floor`, `ceiling`.

The first rules are small on purpose:

- `RoomSpec`
- `CorridorSpec`
- `DoorSpec`
- `GalleryChainSpec`

They prove the shape of the pipeline: grammar emits semantic claims, claims
compile into `vg_csg` brushes, and the CSG assembler produces the mesh verdict.

The first expansion adds local `Frame`s, deterministic seeded variation, and
`RuleSet`/`GalleryChainSpec` composition. This is the rule: every richer grammar
feature must sharpen spatial intent before it increases mesh complexity.

The rule is simple: future procedural generators should feed CSG with authored
space claims instead of bypassing the tree with final triangles. Cities,
habitats, corridors, and districts can grow from fields and grammars, but hard
architectural legality belongs in the CSG tree.

Where a grammar feature compiles to a CSG behavior that overlaps public
RealtimeCSG semantics, tests should preserve exact parity at that seam: claim
counts, brush counts, category vocabulary, split counts, and mesh invariants.
Novel grammar can sing. Shared API behavior must stay in tune.

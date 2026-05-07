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

The second expansion adds generated CSG tree intent. `ClaimTree` can still
compile to the flat assembler stream for the current backend, but it can also
emit a `CsgTreeArena` where solids are grouped under addition, voids are grouped
under addition, and the result is represented as `solids - voids`. This is the
bridge from grammar-as-list to grammar-as-boolean-program.

Current example output:

```text
claims=42 solids=36 voids=6 brushes=42 tree_nodes=45
```

The rule is simple: future procedural generators should feed CSG with authored
space claims instead of bypassing the tree with final triangles. Cities,
habitats, corridors, and districts can grow from fields and grammars, but hard
architectural legality belongs in the CSG tree.

Where a grammar feature compiles to a CSG behavior that overlaps public
RealtimeCSG semantics, tests should preserve exact parity at that seam: claim
counts, brush counts, category vocabulary, split counts, and mesh invariants.
Novel grammar can sing. Shared API behavior must stay in tune.

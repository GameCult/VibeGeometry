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

They prove the shape of the pipeline: grammar emits semantic claims, claims
compile into `vg_csg` brushes, and the CSG assembler produces the mesh verdict.

The rule is simple: future procedural generators should feed CSG with authored
space claims instead of bypassing the tree with final triangles. Cities,
habitats, corridors, and districts can grow from fields and grammars, but hard
architectural legality belongs in the CSG tree.

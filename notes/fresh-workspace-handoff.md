# Fresh Workspace Handoff

## Immediate Re-entry Instruction

Read `state/map.yaml`, this file, `notes/vibegeometry-current-system-map.md`,
and `notes/vibegeometry-implementation-plan.md`, then run:

```powershell
npm run state:status
```

Restate the persisted next action before editing.

Do not continue implementation automatically from a rehydrate-only request.

Do not trust this file for the exact live HEAD. Use git for volatile truth:

```powershell
git status --short --branch
git log --oneline -5
```

## Current State

VibeGeometry now has three live implementation organs:

- `vibegeometry/`: Python helpers for Blender coordinate frames, deterministic
  fields, batching, object/material/camera setup, and verifier checks.
- `crates/vg_csg`: Rust/Bevy-math CSG brush assembler.
- `crates/vg_grammar`: Dream Machine grammar layer emitting semantic solid/void
  claims into `vg_csg`.

Corpus maps, story-bound builds, translation notes, RealtimeCSG doctrine, and
procedural doctrine live under `docs/research/`; this handoff is not the ledger.
Artifact schemas are still pending.

Current authoring prior: use the full Python stack. Python structures intent,
tables, loops, variants, cleanup, validation, docs, and scene/render
orchestration; Geometry Script emits inspectable Geometry Nodes groups; `bpy`
handles Blender scene machinery and evaluated evidence.

`crates/vg_csg` is the first Rust/Bevy-side interactive geometry organ.
RealtimeCSG's public Unity repo exposes a useful brush/tree/operation/generation
model and public P/Invoke declarations for the optimized native C++ plugin.
The standalone direct-DLL bridge under `tools/realtimecsg_native_bridge` mirrors
that managed wrapper surface and intentionally fails closed if the plugin emits
zero mesh descriptions. Current bridge status: the DLL loads, exported calls
create brush meshes, brushes, and trees, the health probe verifies bounds,
outlines, raycasts, and mesh-description extraction, and the combined perf
fixture appends native C++ timing records. The key construction lesson: build
brush nodes before the tree, create the tree, insert children through the public
Foundation range-insert path, and avoid eagerly setting default brush operation
or flag state.
Do not use those zero outputs as timings. Sander van Rossen's older public
`LogicalError/Realtime-CSG-demo` and blog series remain the preferred clean
research inputs. Current `vg_csg`: public CSG operation/branch/tree/brush handle
surface, child and operation mutation, ordered assembler backend, exact AABB
and oriented-box subtraction and intersection via convex plane splitting,
crossing polygon classification into inside/outside/aligned/reverse-aligned
buckets, polygon category/visibility/reversal metadata, primitive/solid/tree
bounds, additive `CylinderZ`, `DomeCapZ`, and `FloretArm` primitives,
axis-aligned box fast path, compiled brush geometry cache, owned convex
splitting, convex containment shortcuts, stable-generation output cache, stable
and dirty release perf fixture modes, Bevy-math mesh buffers, tests, clippy,
and examples.
Research note: `docs/research/realtime-csg-bevy-assembler.md`.
Where `vg_csg` overlaps public RealtimeCSG/demo behavior, add exact observable
parity fixtures instead of approximate plausibility tests.

`crates/vg_grammar` is the Dream Machine grammar layer above CSG. Rules emit
semantic solid/void claims with tags, then compile those claims into `vg_csg`
brushes. Current features: local `Frame`s, oriented claims, seeded variation,
`RuleSet` composition, `RoomSpec`, `CorridorSpec`, `DoorSpec`, and
`GalleryChainSpec`.
Example: `cargo run -p vg_grammar --example dream_room`. Research note:
`docs/research/dream-machine-grammar.md`.

Repo-local Geometry Script clone notes live in
`docs/research/geometry-script-fork-notes.md`. Run
`.\tools\setup_geometry_script_clone.ps1` if `external/geometry-script` is
missing.

The current next action is to use the new demand-frontier counters to replace
the ordered `vg_csg` dense rotated subtraction path with a category-router
kernel. Keep cached-vs-dirty output parity tests green, compare against the C++
timing oracle, and only add BVH/grid storage after frontier batching proves it
needs one.

Spatial-query correction from EpiphanyAquarium memory: GigaVoxels, froxels, and
Dreams all point away from static "better tree" thinking. Let the consumer
shape the query frontier first: dirty brush, branch bounds, requested output
tile/view, or visible surface set. BVHs, grids, sweep-and-prune, and pair caches
are candidate layouts only after that frontier exists and timing evidence says
they help.

First implementation slice: `vg_csg` exports `DemandFrontier`/`DemandPair`, and
`BuildReport` plus the JSONL perf fixture now expose `candidate_pairs` and
`rejected_pairs`. These counters are currently observational and follow existing
bounds gates; they are not yet a replacement router.

Second implementation slice: `Assembler::rebuild_routed_surfaces()` now exposes
an experimental surface-router path for exactly one convex source and one
candidate subtractive convex cutter. It emits surviving source boundary polygons
plus reversed cutter cap polygons, so the centered cut drops from 72 closed
fragment-carver triangles to 48 boundary triangles. The perf fixture only emits
`mode:"routed"` for supported cases. Dense repeated cutters must stay on the
ordered kernel until the router has compact frontier batching and scratch
storage; naive surface-list routing exploded polygon counts.

Latest dense-kernel guardrail: `PolygonRouteScratch` now reuses routing scratch
vectors for polygon classification. An attempted in-place fragment frontier
changed `rotated_cut_stack_64` output shape, so it was reverted. A regression
now pins that fixture at 280 fragments, 3404 triangles, 804 candidate pairs, and
9417 rejected pairs. Future speed passes must either preserve that ordered
output exactly or make an explicit, reviewed output-contract transition.

Current realtime-editing seam: `Assembler` can mutate brush primitives and
operations by `BrushId`, invalidating cached output and incrementing generation.
`DirtyDemandFrontier` computes the conservative ordered suffix after the first
dirty brush. The prefix before that index is the future cache boundary; the
suffix is live because ordered CSG decisions propagate forward. Box-only ordered
CSG and the general convex builder now have prefix checkpoint caches, and
`build_incremental()` resumes from the checkpoint before the first dirty brush.
Output parity is tested against full rebuilds. Checkpoint validity is tracked as
a prefix boundary to avoid deep-copying stale history after tail edits. Mesh
emission is still whole-output; the category-router path is still separate.

## Important Invariants

- Target Blender 5.0+ unless the task says otherwise.
- Geometry nodes are the primary procedural geometry surface.
- Python is the authoring/orchestration layer, not a fallback after Geometry
  Script runs out of rope.
- Python constructs and orchestrates graphs; it should not bury the design in
  opaque imperative mesh generation.
- Visual target evidence must remain attached to scene briefs and render
  review.
- A graph is not accepted just because it runs. Render evidence decides.
- Node groups, exposed sockets, and attributes need names clear enough for
  future agents to inspect and modify.
- Add evidence only when it changes future belief.

## Open Questions

- What exact JSON shape should the scene brief use for references,
  instructions, target traits, and acceptance criteria?
- What should the first node graph manifest schema require versus merely allow?
- What node-group inspection JSON shape is most useful for translating public
  `.blend` examples into Geometry Script?
- Which Blender 5.0+ APIs and node construction helpers should become the
  first stable builder layer?
- What is the smallest useful render-review artifact?

## Compaction Notes

For imminent compaction, write hot memory first to
`state/scratch-compaction-<guid>.md`, then run:

```powershell
npm run state:prepare-compaction
```

Fold only durable lessons into canonical state and delete the temporary
scratch-compaction file after it has served its purpose.

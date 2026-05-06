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

VibeGeometry is an incubation scaffold with persistence, graph-translation
corpus notes, repo-local Geometry Script tooling, verifiers, doctrine, a Python
helper library, and now a first Rust CSG assembler. Artifact schemas are still
pending.

Corpus inventory, graph maps, verification notes, and doctrine live in
`docs/research/`; this handoff is not the ledger. Accepted corpus families
include local Shriinivas samples, Quellenform `CurveToMeshUV`, official Blender
demos, and IRCSS French Houses footholds. IRCSS blockers remain repeat-zone
feedback, repeat `Top` outputs, foreach zones, gizmo nodes, and the rejected
empty-output `WindowBeams` harness.

From-scratch story-bound builds live in `examples/geometry_script/`:

- `aetheria_bloom_habitat.py`: whole Bloom study with explicit lore coordinate
  frames, cylindrical/endcap attachment, golden-angle transfer curves,
  deterministic settlement noise, batched dense detail, and inspection cameras.
- `lucent_tether_habitat.py`: Ghostlight/Lucent tether habitat with orthogonal
  spin-gravity city plane, flat-cut dome base, street-field city, shader work,
  tether attachment, and exterior Citadel-scale solar/radiator florets.

Build notes and verifiers:

- `docs/research/builds/aetheria-bloom-habitat.md`
- `docs/research/builds/lucent-tether-habitat.md`
- `tools/verify_aetheria_bloom_habitat.py`
- `tools/verify_lucent_tether_habitat.py`

Current authoring prior: use the full Python stack. Python structures intent,
tables, loops, variants, cleanup, validation, docs, and scene/render
orchestration; Geometry Script emits inspectable Geometry Nodes groups; `bpy`
handles Blender scene machinery and evaluated evidence.

`vibegeometry/` is the first reusable helper library. It currently holds
coordinate-frame helpers, deterministic field/noise helpers, mesh batching,
thin Blender object/material/camera helpers, and verifier helpers. The Bloom
script imports these primitives directly, so the library is not just a shrine.

`crates/vg_csg` is the first Rust/Bevy-side interactive geometry organ.
RealtimeCSG's public Unity repo exposes a useful brush/tree/operation/generation
model, but not the optimized native C++ kernel or a supported runtime editing
API. Sander van Rossen's older public `LogicalError/Realtime-CSG-demo` and blog
series are now the preferred clean research inputs. Current `vg_csg`: ordered
brushes, exact AABB and oriented-box subtraction via convex plane splitting,
additive `CylinderZ`, `DomeCapZ`, and `FloretArm` primitives, Bevy-math mesh
buffers, `LevelDsl`, tests, clippy, and an example room. Research note:
`docs/research/realtime-csg-bevy-assembler.md`.

The repo-local Geometry Script clone has Blender 5.1 work for nested `@tree`
group reuse, a ported `nodes_to_script` converter, and menu-socket default
tolerance. See `docs/research/geometry-script-fork-notes.md`. Run
`.\tools\setup_geometry_script_clone.ps1` if `external/geometry-script` is
missing in a fresh workspace.

The local toolchain branch is `vibegeometry/blender-5-nodes-to-script`.
The upstream PR branch is `vibegeometry/blender-5-nested-tree-groups`, and PR
#69 is intentionally limited to the nested-group fix:
https://github.com/carson-katri/geometry-script/pull/69.
The GameCult fork is intentionally pruned to `main` plus VibeGeometry-owned
tooling branches. Do not copy upstream branch soup forward unless a future patch
actually needs it.

The current next action is to move `vg_csg` toward the public RealtimeCSG demo's
faster model: add explicit polygon categories, classify brush polygons through
boolean tree operations, preserve source/cutter surfaces and material intent,
then add spatial rejection/indexing and Bevy `Mesh`/ECS plugin boundaries for
the interactive loop.

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

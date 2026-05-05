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

VibeGeometry is still an incubation scaffold: persistence, graph-translation
corpus, repo-local Geometry Script tooling, verifiers, and doctrine exist; the
builder library and artifact schemas do not.

Corpus inventory, graph maps, verification notes, and spatial doctrine live in
`docs/research/`. Keep this handoff as a re-entry surface, not a second corpus
ledger.

Accepted corpus families so far:

- Local math/display/utility graphs from Shriinivas samples: Cartesian helper
  and function graphs, pie chart, field-value digit display, parametric/polar
  equations.
- Quellenform `CurveToMeshUV` utility sample.
- Official Blender demo tranche: instance attributes, index-of-nearest,
  shortest-path labyrinth, and raycast minigame helpers.
- IRCSS French Houses footholds: `MakeSpiral -> VG Make Spiral` and
  `PointyGothicCone -> VG Pointy Gothic Cone`, verified against source
  evaluated geometry with max delta `0.0`.

Current frontier: IRCSS French Houses city-scale graph work. The accepted
footholds are `MakeSpiral` and `PointyGothicCone`. Mapped blockers are
repeat-zone feedback state, repeat `Top` boolean outputs, foreach zones, gizmo
nodes, and a rejected empty-output harness for `WindowBeams`. The previous
`nodes_to_script` duplicate-key failure around axes-to-rotation is fixed in the
Geometry Script fork, so `GenerateArc` and `MakeStairs` now have compiling
converter drafts. The file-level dependency map lives at
`docs/research/translations/ircss-french-houses-system-map.md`; the all-node
structural atlas lives at
`docs/research/translations/ircss-french-houses-node-atlas.md`; the node-level
mechanism study lives at
`docs/research/translations/ircss-french-houses-node-mechanisms.md`.

First from-scratch build test: `examples/geometry_script/aetheria_bloom_habitat.py`
generates an Aetheria Bloom whole-habitat study using Bloom lore plus Eric
Bruneton's Rama making-of as a cylindrical-world reference. It now emphasizes
whole-cylinder mapped spaces and frame interfaces: full shell layers, despun
hub cap and docking core, spun spire sheath, shared x/angle/radius coordinate
helpers, golden-angle spoke/transfer loops, layered endcaps, mapped civic
bands, roads, rivers, cloud patches, and service seams. The hubward terrace
slums are on the endcap: annular shelves around the docking hub office complex
step inward toward the Spire as "up" and grow outward to the surface. Plazas
and towns have nested buildings, kiosks, feeder walks, and lane networks. Kappa
is only a small service marker. Build notes live at
`docs/research/builds/aetheria-bloom-habitat.md`; verification lives at
`tools/verify_aetheria_bloom_habitat.py`.

Current authoring prior: use the full Python stack. Python structures intent,
tables, loops, variants, cleanup, validation, docs, and scene/render
orchestration; Geometry Script emits inspectable Geometry Nodes groups; `bpy`
handles Blender scene machinery and evaluated evidence.

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

The current next action is to continue the Aetheria Bloom build by moving the
shared cylindrical coordinate helpers plus spiral spoke/transfer-artery network
into reusable Geometry Script groups, then improving atmospheric/light
readability from render evidence.

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

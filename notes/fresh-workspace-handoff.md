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

Corpus inventory, graph maps, verification notes, and doctrine live in
`docs/research/`. This handoff is not the ledger.

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

Current IRCSS frontier: `MakeSpiral` and `PointyGothicCone` are accepted
footholds. Blockers are repeat-zone feedback, repeat `Top` outputs, foreach
zones, gizmo nodes, and rejected empty-output `WindowBeams` harness. IRCSS maps
live in `docs/research/translations/ircss-french-houses-*.md`.

First from-scratch build test: `examples/geometry_script/aetheria_bloom_habitat.py`
generates an Aetheria Bloom whole-habitat study. It now carries the key spatial
lessons: define the lore coordinate frame before ornament, use cylindrical and
endcap helpers for attachment, use golden-angle curves for transfer networks,
use deterministic noise for organic settlement pressure, batch dense detail by
material/class, and render inspection cameras that face the domain being judged.
The hubward terrace slums are noise-driven endcap shelves around the docking hub
office complex, stepping inward toward the Spire as "up" and outward into a
classier high-gravity urban crown. Build notes live at
`docs/research/builds/aetheria-bloom-habitat.md`; verification lives at
`tools/verify_aetheria_bloom_habitat.py`.

Current authoring prior: use the full Python stack. Python structures intent,
tables, loops, variants, cleanup, validation, docs, and scene/render
orchestration; Geometry Script emits inspectable Geometry Nodes groups; `bpy`
handles Blender scene machinery and evaluated evidence.

`vibegeometry/` is the first reusable helper library. It currently holds
coordinate-frame helpers, deterministic field/noise helpers, mesh batching,
thin Blender object/material/camera helpers, and verifier helpers. The Bloom
script imports these primitives directly, so the library is not just a shrine.

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

The current next action is to grow `vibegeometry/` from helper primitives into a
small reusable builder seam, starting with either endcap terrace slums or spiral
transfer arteries, then bind that seam to scene-brief, manifest,
inspection-render, and verifier contract drafts.

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

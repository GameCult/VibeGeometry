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

VibeGeometry is an initial scaffold. It has persistence machinery, project
orientation docs, helper tools, and the first Geometry Nodes translation corpus
entry, but no Blender builder library or artifact schemas yet.

The first completed translation is
`docs/research/translations/shriinivas-cartesian-helper.md`, backed by
`examples/geometry_script/shriinivas_cartesian_helper.py`.

The completed Cartesian function translation is
`docs/research/translations/shriinivas-cartesian-function-graphs.md`. It covers
`Geometry Nodes Line`, `Geometry Nodes Parabola`, and `Geometry Nodes Circle`
from `cartesian.blend`.

The completed pie chart translation is
`docs/research/translations/shriinivas-piechart.md`. It covers `NodeGroup` and
`Pie Chart`, plus the numbered `getPie.*` family and `Extended Pie Chart` from
`piechart.blend`.

The completed field-value translation is
`docs/research/translations/shriinivas-fieldvalue-digit-at.md`. It covers
`Create Decimal`, `Create Segment`, `Seven Segments`, `Delete Segments`,
`Next Digit`, `Digit At`, and the full `Field Value` display graph from
`fieldvalue.blend`. The full graph is verified on a default-route float-value
case with matching evaluated geometry.

The completed parametric/polar translation is
`docs/research/translations/shriinivas-paramnpolareq.md`. It covers scalar
equation helpers, chooser groups, `getxy.001`, `Archimedes Spiral`,
`Epicycloid`, the main wrapper, and a mirrored root spiral from
`paramnpolareq.blend`.

The completed CurveToMeshUV utility sample is
`docs/research/translations/quellenform-curve-to-mesh-uv.md`. It covers
`Auto Smooth`, `Curve to Mesh UV`, `_258246`, and `_Title`.

The completed official Blender demo tranche now includes:

- `docs/research/translations/blender-instance-attributes.md`, covering
  `Grass Tuft Generator`.
- `docs/research/translations/blender-index-of-nearest.md`, covering
  `boundary_step`, `update_velocity`, `collision_step`, and `collider_step`.
- `docs/research/translations/blender-labyrinth-shortest-path.md`, covering
  `Solvable Labyrinth Generator`.
- `docs/research/translations/blender-raycast-minigame.md`, covering
  `Initial Direction`, `Line to be Casted`, and `Cast Rays`.

Official demo files inspected but deferred are listed in
`docs/research/geonodes-translation-corpus.md`: hexgrid, wavy wall, pebble
scattering, gizmo array, jiggly pudding, and repeat-zone flower. They are not
empty; they need legacy-node migration, gizmo-node, simulation-zone, or
repeat-zone support before they are good doctrine targets.

`docs/research/procedural-doctrine.md` now stores the current spatial reasoning
playbook for mapping geometric ideas to Geometry Script. Doctrine entries should
explain when a tool becomes salient for a visual form, the mental move that
turns the form into graph structure, a small code sketch, and the verification
cue.

Current authoring prior: use the full Python stack. Python structures intent,
tables, loops, variants, cleanup, validation, docs, and scene/render
orchestration; Geometry Script emits inspectable Geometry Nodes groups; `bpy`
handles Blender scene machinery and evaluated evidence.

The repo-local Geometry Script clone has a Blender 5.1 patch for nested `@tree`
group reuse, a ported `nodes_to_script` converter, and a menu-socket default
tolerance patch needed by Blender 5 menu inputs. See
`docs/research/geometry-script-fork-notes.md`.
Run `.\tools\setup_geometry_script_clone.ps1` if `external/geometry-script` is
missing in a fresh workspace.
The local toolchain branch is `vibegeometry/blender-5-nodes-to-script`.
The upstream PR branch is `vibegeometry/blender-5-nested-tree-groups`, and PR
#69 is intentionally limited to the nested-group fix:
https://github.com/carson-katri/geometry-script/pull/69.
The GameCult fork is intentionally pruned to `main` plus VibeGeometry-owned
tooling branches. Upstream branch clutter should not be copied forward unless a
future patch actually needs it.

The current next action is to move from translation-corpus chewing into the
next architecture organ: define the scene brief and node graph manifest
contracts using the verified idioms and deferred-zone blockers as pressure
cases. Keep `docs/research/procedural-doctrine.md` compact; put
sample-specific graph maps and verification details in
`docs/research/translations/`.

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
- Should the Geometry Script nested-group patch be upstreamed, or should
  VibeGeometry maintain a fork as its toolchain?
- Which Blender 5.0+ APIs and node construction helpers should become the
  first stable builder layer?
- What is the smallest useful render-review artifact?

## Compaction Notes

When preparing for imminent compaction, write hot memory first to
`state/scratch-compaction-<guid>.md`, then run:

```powershell
npm run state:prepare-compaction
```

Fold only durable lessons into canonical state and delete the temporary
scratch-compaction file after it has served its purpose.

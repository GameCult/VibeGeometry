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
`Pie Chart` from `piechart.blend`.

The completed field-value helper translation is
`docs/research/translations/shriinivas-fieldvalue-digit-at.md`. It covers
`Create Decimal`, `Create Segment`, `Seven Segments`, `Delete Segments`, and
`Next Digit`, and `Digit At` from `fieldvalue.blend`.

`docs/research/procedural-doctrine.md` now stores the current intuitive model
for mapping geometric ideas to Geometry Script: curves as rails, fields as
weather, `Set Position` as the hinge, profiles as body, attributes as optional
handles, and Python helpers as authoring stencils.

The repo-local Geometry Script clone has a Blender 5.1 patch for nested `@tree`
group reuse. See `docs/research/geometry-script-fork-notes.md`.
Run `.\tools\setup_geometry_script_clone.ps1` if `external/geometry-script` is
missing in a fresh workspace.
The patch branch is pushed to `GameCult/geometry-script`, and the upstream PR is
https://github.com/carson-katri/geometry-script/pull/69.
The GameCult fork is intentionally pruned to `main` plus the active
`vibegeometry/blender-5-nested-tree-groups` branch. Upstream branch clutter
should not be copied forward unless a future patch actually needs it.

The current next action is to test or port upstream Geometry Script's
`nodes_to_script` prototype before attempting the full 176-node `Field Value`
translation. `Geometry Nodes Group.002` is a wrapper around the full `Field
Value` group rather than an independent helper.

## Important Invariants

- Target Blender 5.0+ unless the task says otherwise.
- Geometry nodes are the primary procedural geometry surface.
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

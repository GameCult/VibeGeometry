# VibeGeometry Current System Map

VibeGeometry does not have a Blender runtime yet. The live system is a
persistence scaffold plus a planned artifact pipeline for agent-authored
geometry-node scenes.

## Control Flow

1. Rehydrate from `state/map.yaml`, `notes/fresh-workspace-handoff.md`, this
   file, and `notes/vibegeometry-implementation-plan.md`.
2. Run `npm run state:status`.
3. Work one bounded pipeline organ.
4. Validate the seam that matters.
5. Persist only belief-changing evidence.
6. Commit completed work.

## Core Surfaces

- `state/map.yaml`: canonical mission, boundaries, live architecture, next action.
- `state/evidence.jsonl`: distilled belief-changing evidence only.
- `state/branches.json`: active and closed research or implementation branches.
- `notes/fresh-workspace-handoff.md`: compact re-entry packet.
- `notes/vibegeometry-implementation-plan.md`: near-term implementation sequence.
- `docs/architecture/`: detailed contracts and rationale.

## Planned Artifact Pipeline

```text
reference images + user instructions
  -> scene brief
  -> target visual trait extraction
  -> geometry strategy
  -> node graph manifest
  -> Blender Python builder script
  -> generated .blend scene
  -> render output
  -> render review and graph audit
  -> accepted example or revised hypothesis
```

## Missing Or Incomplete Organs

- Scene brief schema
- Node graph manifest schema
- Render review schema
- Blender Python builder helpers
- Geometry-node idiom library
- Headless Blender runner
- Reference-image storage and provenance rules
- Render comparison and review workflow
- Example scene fixtures

## Current North Star

Build the smallest reliable loop where an agent can describe a target, plan
procedural geometry, generate a legible Blender node graph through Python,
render it, and use review evidence to improve the next iteration. The loop
should reward coherent geometry flow, not just scripts that successfully make
Blender emit pixels.

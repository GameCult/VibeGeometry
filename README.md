# VibeGeometry

VibeGeometry is a research and implementation home for agent-authored Blender
scene generation.

The project exists to build a pipeline where Codex, or any other sufficiently
useful local agent, can take reference images and visual instructions, plan a
procedural geometry strategy, generate Blender Python scripts, construct
complex geometry-node graphs, render the result, and revise from evidence
instead of shrugging confidently at a pile of decorative node spaghetti.

The target is Blender 5.0 and later. The repo treats geometry nodes as the
main modeling surface, Python as the graph construction and orchestration
language, and rendered output as the evidence loop.

## Core Idea

VibeGeometry separates five things that are easy to smear together:

1. **Visual target**
   What the result should look like, grounded in reference images and explicit
   instructions.

2. **Geometry strategy**
   The procedural plan: primitives, fields, instances, curves, surfaces,
   simulation zones, attributes, materials, and camera composition.

3. **Node graph contract**
   The legible graph structure that should exist in Blender, including named
   groups, exposed parameters, attribute flow, and reusable node idioms.

4. **Python builder**
   The script that creates the scene, builds node groups, links sockets,
   assigns materials, places cameras and lights, and saves or renders the
   `.blend` result.

5. **Render review**
   What the actual output proves: visual match, graph sanity, missing geometry,
   material errors, performance pain, and rejected approaches.

The script is not the design. The render is not the truth. The node graph is
the machine, and the repo exists to make that machine inspectable.

## Current Status

This is an initial scaffold.

Currently present:

- persistence surfaces for re-entry, evidence, planning, and compaction hygiene
- starter architecture notes for the Blender scene-generation pipeline
- a small `vibegeometry/` helper library for coordinate frames, deterministic
  fields, batching, Blender object/material/camera helpers, and verifier checks
- experimental Rust crates: `vg_csg` for Bevy-math brush assembly and
  `vg_grammar` for semantic procedural claims feeding the CSG tree
- a repo structure for schemas, prompts, examples, experiments, scripts, tools,
  notes, and durable state
- small state inspection and pre-compaction helpers

Not present yet:

- scene brief schema
- node graph manifest schema
- render review schema
- reference-image ingestion helpers
- automated Blender render runner
- visual comparison or reviewer loop

## Repo Tour

- `AGENTS.md`: operating discipline for humans and agents
- `state/map.yaml`: canonical project map and current next action
- `state/scratch.md`: disposable working memory for one bounded subgoal
- `state/evidence.jsonl`: distilled belief-changing evidence
- `state/branches.json`: active or closed investigation branches
- `notes/fresh-workspace-handoff.md`: compact re-entry packet
- `notes/vibegeometry-current-system-map.md`: current repo machinery
- `notes/vibegeometry-implementation-plan.md`: implementation sequence
- `vibegeometry/`: reusable procedural-scene helper library
- `notes/architecture-rationale.md`: why the persistence surfaces exist
- `docs/architecture/`: pipeline contracts and design notes
- `docs/research/`: Blender geometry-node research notes
- `schemas/`: future JSON schema contracts
- `examples/`: future scene briefs, generated scripts, and review artifacts
- `experiments/`: disposable render attempts and captures
- `prompts/`: reusable agent prompts for scene planning and review
- `scripts/`: utility scripts that are not core persistence machinery
- `tools/vibegeometry_state.py`: state inspection and evidence helper
- `tools/vibegeometry_prepare_compaction.py`: pre-compaction audit helper

## Useful Commands

```powershell
npm run state:status
npm run state:prepare-compaction
```

To add distilled evidence:

```powershell
& 'C:\Users\Meta\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' '.\tools\vibegeometry_state.py' add-evidence --type design --status accepted --note '...'
```

## Best Starting Points

- `AGENTS.md`
- `state/map.yaml`
- `notes/vibegeometry-current-system-map.md`
- `notes/vibegeometry-implementation-plan.md`
- `docs/architecture/pipeline-overview.md`

For Codex-driven work, read `AGENTS.md` before changing the repo. It contains
the rules that keep the project from turning into a confident procedural hairball.

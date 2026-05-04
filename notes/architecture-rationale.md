# Architecture Rationale

This note explains why VibeGeometry uses explicit state surfaces. It is not the
current implementation map and not the roadmap. For those, read:

- `state/map.yaml`
- `notes/fresh-workspace-handoff.md`
- `notes/vibegeometry-implementation-plan.md`
- `notes/vibegeometry-current-system-map.md`

## Core Failure

The central failure mode is local plausibility without global coherence.

An agent can write plausible Blender Python, create a large node graph, and
still lose the visual machine. Geometry-node work is especially good at this:
the script runs, the graph exists, the render has objects in it, and somehow
the target has been replaced by decorative procedural fog with a confident
variable name.

The answer is explicit structure:

- slow-changing map
- disposable scratch
- distilled evidence
- compact handoff
- implementation plan that is not pretending to be a second map
- ruthless deletion when code, graph, or memory stops serving the target

## State Split

VibeGeometry treats different kinds of cognition as different artifacts:

- `map`: canonical system model, invariants, accepted design, rejected paths
- `scratch`: temporary local reasoning for one bounded subgoal
- `evidence`: distilled proof, decisions, rejected paths, and scars that change future belief
- `system map`: source-grounded explanation of the live repo machinery
- `handoff`: compact re-entry packet
- `plan`: distilled forward implementation direction
- `output`: user-visible replies, code edits, commits, renders, and verification artifacts

The split matters because Blender scene generation has many seductive proxies:
valid Python, non-empty renders, high node counts, pretty materials, and
parameter sliders. None of those prove that the graph still serves the visual
target.

## Pipeline Principle

The working loop should be:

```text
reference images and instructions
-> scene brief
-> visual trait extraction
-> geometry strategy
-> node graph manifest
-> Blender Python builder
-> render evidence
-> review against target
-> revise one hypothesis
```

The graph is allowed to be complex. The intent is not. If the agent cannot
describe what geometry flows through each stage and why that stage belongs,
the next move is explanation or simplification, not another compensating node
group with a tragic little name.

## Compact-Rehydrate-Reorient

Compaction is a real state transition, not a cosmetic cleanup.

Before compaction, VibeGeometry should preserve:

- current objective and active subgoal
- latest stable map
- distilled evidence or rejected paths that change future belief
- open questions, blockers, and next action

After rehydrating, VibeGeometry should:

- reread canonical state instead of trusting prompt residue
- restate the next action from persisted state
- continue only when instructed or when the task explicitly calls for it
- avoid broad implementation until the current pipeline organ is understood

The aim is simple: the next waking thing should find coals instead of ash.

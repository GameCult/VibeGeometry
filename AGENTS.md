# VibeGeometry Instructions

## Project Purpose

VibeGeometry is a research and implementation home for agent-authored Blender
scene generation.

The core problem is not "make a Python script that creates something shiny."
The core problem is building a pipeline where an agent can understand a visual
target, choose a procedural geometry strategy, construct inspectable Blender
5.0+ geometry-node graphs through Python, render the result, and revise from
evidence without accumulating clever junk.

## Canonical State

- Treat `state/map.yaml` as the canonical project map.
- Treat `state/scratch.md` as disposable working memory for one bounded
  subgoal.
- Treat `state/evidence.jsonl` as the distilled durable ledger of what was
  learned, verified, rejected, or accepted.
- Treat `notes/vibegeometry-implementation-plan.md` as the current
  implementation plan.
- Update `state/map.yaml` when project understanding changes.
- Add evidence after meaningful research, implementation, verification, or
  rejected paths, but keep it distilled. Routine proof belongs in git history,
  renders, smoke artifacts, or targeted logs unless it changes what the next
  session should believe.
- Do not turn notes, map, handoff, and evidence into four copies of the same
  brain. Distinct jobs or bust.

## Important Paths

- Project root: `E:\Projects\VibeGeometry`
- Canonical map: `E:\Projects\VibeGeometry\state\map.yaml`
- Scratch surface: `E:\Projects\VibeGeometry\state\scratch.md`
- Distilled evidence ledger: `E:\Projects\VibeGeometry\state\evidence.jsonl`
- Branch ledger: `E:\Projects\VibeGeometry\state\branches.json`
- Handoff summary: `E:\Projects\VibeGeometry\notes\fresh-workspace-handoff.md`
- System map: `E:\Projects\VibeGeometry\notes\vibegeometry-current-system-map.md`
- Implementation plan: `E:\Projects\VibeGeometry\notes\vibegeometry-implementation-plan.md`
- Architecture rationale: `E:\Projects\VibeGeometry\notes\architecture-rationale.md`
- State CLI: `E:\Projects\VibeGeometry\tools\vibegeometry_state.py`
- Pre-compaction helper: `E:\Projects\VibeGeometry\tools\vibegeometry_prepare_compaction.py`

## Useful Commands

Use the bundled Python runtime if `python` is not on PATH:

```powershell
npm run state:status
npm run state:prepare-compaction
& 'C:\Users\Meta\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' '.\tools\vibegeometry_state.py' add-evidence --type research --status ok --note '...'
& 'C:\Users\Meta\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' '.\tools\vibegeometry_state.py' add-branch --id branch-id --hypothesis '...'
```

## Session Bootstrap And Re-entry Protocol

On fresh session load, do this before implementation:

1. read:
   - `state/map.yaml`
   - `notes/fresh-workspace-handoff.md`
   - `notes/vibegeometry-current-system-map.md`
   - `notes/vibegeometry-implementation-plan.md`
2. run:
   - `npm run state:status`
3. restate the current next action from the persisted state before starting
   edits
4. if the user only asked to rehydrate or reorient, stop after orientation and
   wait for an explicit continue instruction

After compaction, resume, or suspicious continuity loss:

1. rerun `npm run state:status`
2. reread `state/map.yaml` and `notes/fresh-workspace-handoff.md`
3. treat the persisted next action as authoritative unless fresh repo evidence
   contradicts it

When context pressure is clearly rising:

1. stop broad exploration
2. narrow the active move to one bounded pipeline organ
3. persist map or handoff updates, plus distilled evidence only when the lesson
   changes future belief, before the blackout lands

When the user says to prepare for imminent compaction:

1. immediately write hot live context from memory into a new
   `state/scratch-compaction-<guid>.md` file before reading files, running
   status checks, or doing tidy persistence work
2. run `tools/vibegeometry_prepare_compaction.py` before editing persistence
   surfaces
3. use its warnings as the checklist for map, handoff, scratch, evidence, and
   git hygiene
4. update only the state that actually needs to change
5. after hot context has been folded into canonical persisted state, delete the
   `state/scratch-compaction-<guid>.md` file so stale emergency memory does not
   linger
6. run `tools/vibegeometry_prepare_compaction.py` again after edits and scratch
   cleanup
7. fix errors, address warnings, and commit the completed persistence pass
   unless the work is deliberately mid-surgery

## Operating Discipline

- Before substantial edits, restate the current mechanism and intended change.
- Prefer one clear hypothesis per iteration.
- Verify with checks that reflect the visual and procedural goal, not just
  proxy success.
- Revert or discard changes that do not clearly improve the target.
- If the diff grows while understanding shrinks, stop implementation and switch
  to diagnosis.
- Keep maps and prose together; do not replace useful maps with prose-only
  explanations.
- Commit completed work before it rots in the worktree unless the task is
  deliberately mid-surgery or the user asked to leave changes uncommitted.
- Push after major completed passes when a remote exists, unless the user asked
  not to or there is a concrete reason to keep the commit local for a moment.
- Before handoff, compaction, or phase boundaries, sync `state/map.yaml`, add
  distilled evidence when the lesson changes future belief, refresh
  `notes/fresh-workspace-handoff.md`, and make the next action explicit.

## Blender And Geometry-Node Doctrine

- Target Blender 5.0+ unless a task explicitly chooses another version.
- Prefer geometry nodes for procedural geometry and Python for construction,
  orchestration, parameterization, render setup, and validation.
- Keep generated node groups named, inspectable, and reusable. A script that
  creates an opaque graph is just a new kind of mess with sockets.
- Preserve attribute flow explicitly. Name important attributes, document where
  they are created, transformed, consumed, and exposed.
- Prefer proven Blender node idioms and current API guidance over invented
  graph tricks.
- Treat reference images as evidence-bearing inputs. Record what visual traits
  are being targeted: silhouette, repetition, surface breakup, scale language,
  material response, lighting, camera, and color.
- Render review is mandatory for visual claims. A script that runs is not a
  scene that works.
- When a generated graph misses the target, revise one hypothesis at a time:
  geometry structure, distribution logic, material, lighting, camera, or scale.
- Keep failed render attempts only when they teach a durable lesson. Otherwise
  archive lightly or delete them; the repo is not a museum of almost.
- Do not bury visual intent inside Python constants. Scene briefs, graph
  manifests, and review artifacts should expose what the agent meant to build.

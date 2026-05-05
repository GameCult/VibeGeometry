# VibeGeometry Implementation Plan

## Current Phase

Turn the verified translation corpus into a small set of durable contracts and
builder seams for agent-authored Blender geometry-node scenes.

The goal is still not a procedural art factory. The goal is a clean artifact
loop where agents can state a visual target, choose a geometry strategy, emit
inspectable node graphs, render evidence, and revise one hypothesis at a time
without piling clever junk into the machine.

Planning belongs in this file and the handoff/map state surfaces. Architecture
docs should describe durable contracts, boundaries, and data shapes; they should
not carry live next-action clutter.

## Corpus Lessons

- Python is the planning and orchestration layer: loops, tables, variants,
  validation, cleanup, documentation, and Blender scene/render control.
- Geometry Script is strongest as an inspectable graph emitter, especially when
  the script keeps names, sockets, attribute flow, and reusable group boundaries
  legible.
- `bpy` remains necessary for Blender objects, modifiers, materials, cameras,
  lights, files, renders, and evaluated-geometry comparison.
- `nodes_to_script` is useful as a converter draft and source-graph probe. Its
  output should inform the translation, not define good house style.
- Accepted graph translations need behavioral verification, not just successful
  script execution.
- City-scale graphs expose the next toolchain pressure: repeat zones, foreach
  zones, gizmo nodes, repeat `Top` outputs, and converter edge cases.
- Source-bound scenes need a written coordinate contract before ornament.
  Define basis axes, up/down, attachment surfaces, and frame transitions in the
  script and verifier before adding detail.
- Organic distribution needs a field, not tidy placement. Use deterministic
  noise to drive density, offsets, sizes, heights, material/class bands, and
  gaps when the visual target is accretion, poverty, erosion, cloud, vegetation,
  or informal growth.
- Dense procedural detail must be batched by material/class and line family.
  Thousands of standalone Blender objects are the dumb kind of expensive.
- Render evidence must include cameras that face the domain being judged. A
  beauty camera can hide the exact spatial mistake that matters.

## Near-Term Sequence

1. Promote the Bloom coordinate/noise lessons into reusable builder seams.
   - Extract shared cylindrical/endcap coordinate helpers into a clear module or
     Geometry Script-oriented builder layer.
   - Preserve the split between coordinate contract, density field, batched
     realization, domain camera, and verifier checks.
   - Keep the first extraction small: endcap terrace slums or spiral transfer
     arteries, not the whole Bloom at once.

2. Define the scene brief contract.
   - Capture references, text instructions, target visual traits, constraints,
     camera/composition requirements, acceptance criteria, and known unknowns.
   - Preserve source paths or URLs for every reference image.
   - Require a source-coordinate section for lore/reference-bound builds:
     basis axes, local up/down, attachment surfaces, and known frame changes.

3. Define the node graph manifest contract.
   - Describe node groups, sockets, exposed controls, modifiers, attribute
     names, field flow, materials, dependencies, and verification expectations.
   - Require enough naming and rationale for future agents to inspect the graph.
   - Keep graph contracts Blender 5.0+ oriented.

4. Build a minimal Python builder seam.
   - Start with one tiny scene that proves graph construction, material setup,
     camera, lighting, save, and render orchestration.
   - Prefer small composable helpers for node group creation and socket linking.
   - Avoid a giant builder abstraction until repeated graph idioms demand it.

5. Build render review artifacts.
   - Store render path, scene brief id, manifest id, script path, Blender
     version, review status, visual misses, graph issues, and next hypothesis.
   - Treat rendered output as the acceptance surface for visual claims.
   - Require at least one domain-facing inspection render for every major
     spatial claim, not just a composed overview.

6. Promote doctrine only after it survives use.
   - Keep examples small enough to inspect.
   - Put sample-specific graph maps in `docs/research/translations/`.
   - Keep `docs/research/procedural-doctrine.md` tight enough to fit in working
     context when building a new scene from scratch. Nobody needs a sacred
     haystack.

7. Generalize after the loop works.
   - Add reference-image ingestion helpers.
   - Add headless batch rendering.
   - Add visual comparison or reviewer prompts.
   - Add richer examples only after the contracts stop sliding.

8. Return to IRCSS graph blockers after the scene loop has these contracts.
   - Either fix one repeat-zone/foreach/gizmo blocker in the Geometry Script
     fork or select a non-zone architectural helper with a non-empty behavioral
     harness.
   - Keep the chosen target small enough to verify against evaluated geometry.
   - Record rejected paths only when they change future decisions.

## Deferred

- Large procedural asset library
- Automated visual scoring beyond basic review artifacts
- Fine-tuned graph-generation models
- Blender add-on packaging
- Complex simulation-node workflows before the basic graph loop is stable

## Discipline

- Work one bounded organ at a time.
- Explain target-to-graph data flow before broad refactors.
- Prefer explicit manifests and render evidence over implicit agent memory.
- If the diff grows while understanding shrinks, stop and simplify.
- Keep history in git; keep persisted state focused on what future sessions
  need to believe.

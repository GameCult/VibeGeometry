# VibeGeometry Implementation Plan

## Current Phase

Build the first reliable scaffold for agent-authored Blender geometry-node
scenes. The immediate target is not a full procedural art factory. It is a
clean artifact loop with enough structure that agents can generate, inspect,
render, and revise graphs without losing the visual target.

Planning belongs in this file and the handoff/map state surfaces. Architecture
docs should describe durable contracts, boundaries, and data shapes; they
should not carry live next-action clutter.

## Near-Term Sequence

1. Build the first Geometry Nodes translation corpus entry.
   - Start from a small public `.blend` with inspectable node groups.
   - Use Blender to summarize group sockets, node types, links, modifiers, and
     graph shape before translating.
   - Write a plain-language map of one source graph before scripting.
   - Recreate the graph with Geometry Script using the local Blender 5.1
     generated Geometry Script docs for signatures.
   - Smoke-test the generated node group in Blender before rendering.

2. Define the scene brief contract.
   - Capture references, text instructions, target visual traits, constraints,
     camera/composition requirements, acceptance criteria, and known unknowns.
   - Preserve source paths or URLs for every reference image.
   - Separate visual target description from implementation strategy.

3. Define the node graph manifest contract.
   - Describe node groups, sockets, exposed controls, modifiers, attribute
     names, field flow, materials, and dependencies.
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

6. Add geometry-node idiom notes and examples.
   - Document established patterns for distribution, instancing, curve/surface
     generation, attributes, material variation, simulation zones, and exposed
     parameters.
   - Keep examples small enough to inspect.
   - Promote only graph patterns that survive review.

7. Generalize after the loop works.
   - Add reference-image ingestion helpers.
   - Add headless batch rendering.
   - Add visual comparison or reviewer prompts.
   - Add richer examples only after the contracts stop sliding.

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

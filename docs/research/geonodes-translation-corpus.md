# Geometry Nodes Translation Corpus

This note tracks public Geometry Nodes examples that are useful for learning how
to translate visual node graphs into Geometry Script. The goal is not to collect
cool files. The goal is to build a graded ladder from known node networks to
scripts we can generate, inspect, render, and revise.

## Source Selection Rules

- Prefer `.blend` files or repositories with real node groups over screenshot
  and video-only tutorials.
- Prefer examples with clear visual outcomes and bounded mechanisms.
- Use Blender itself to inspect node groups before recreating anything.
- Translate one graph idiom at a time into Geometry Script.
- Verify each translation by generating a node group in Blender, inspecting its
  node/link shape, and rendering when the visual result matters.
- Keep video-only sources as secondary explanation, not primary truth.

## Complexity Ladder

### Tier 1: Primitive Construction And Simple Fields

Use these to learn Geometry Script signatures, result objects, chain syntax,
modifier sockets, and basic graph inspection.

- `Shriinivas/geometrynodes`
  - Source: https://github.com/Shriinivas/geometrynodes
  - Candidate files: `cartesian.blend`, `paramnpolareq.blend`,
    `piechart.blend`, `fieldvalue.blend`
  - Why it matters: small mathematical graphs with clear output shapes.
  - Translation value: curve generation, mesh primitives, math nodes, exposed
    parameters, and field/value flow.

### Tier 2: Scattering, Instancing, And Attribute Flow

Use these after the primitive layer can be recreated without guessing.

- Blender Guru beginner Geometry Nodes candy tutorial
  - Source: https://www.blenderguru.com/tutorials/2025/9/10/blender-tutorial-geometry-nodes-for-beginners
  - Candidate artifact: downloadable final `.blend`
  - Why it matters: canonical beginner scatter workflow.
  - Translation value: distribute points, instance on points, random rotation,
    random scale, join geometry, and exposed controls.

- Samuel Sullins demo file via BlenderNation
  - Source: https://www.blendernation.com/2023/04/20/learn-geometry-nodes-with-this-demo-file/
  - Candidate artifact: free demo `.blend` with node comments and simple
    scattering setups.
  - Why it matters: likely built for learning and rebuilding.
  - Translation value: comments may make node intent easier to map into prose
    and Geometry Script.

### Tier 3: Reusable Utility Node Groups

Use these to learn how artists package node networks into inspectable tools.

- `quellenform/blender-CurveToMeshUV`
  - Source: https://github.com/quellenform/blender-CurveToMeshUV
  - Candidate file: `Curve to Mesh UV v1.7.02.230213-FREE - Blender 3.4+.blend`
  - Why it matters: a focused utility group with a clear contract.
  - Translation value: curve-to-mesh workflows, UV attributes, face-corner
    domain discipline, output attribute handling.

- `Tams3d/T3D-GN-Presets`
  - Source: https://github.com/Tams3d/T3D-GN-Presets
  - Candidate file: `t3d_nodes.blend`
  - Why it matters: a large preset library for Blender 4.4+ with many utility
    node groups.
  - Translation value: reusable group organization, socket naming, matrix and
    deformation utilities. This is not a first target; it is a quarry.

### Tier 4: Procedural Systems

Use these only after the smaller idioms are reliable.

- Blender Studio Geometry Nodes from Scratch files
  - Source: https://studio.blender.org/training/geometry-nodes-from-scratch/chapter/files/
  - Candidate files: rock scattering, tree generator, grass tuft generator,
    spaceship generator, geometry components demo.
  - Why it matters: production-adjacent learning files with a broad concept
    range.
  - Translation value: progressive systems that combine distribution,
    attributes, generated geometry, materials, and exposed controls.

- `IRCSS/Trees-With-Geometry-Nodes-Blender`
  - Source: https://github.com/IRCSS/Trees-With-Geometry-Nodes-Blender
  - Candidate artifact: tree-generation node groups.
  - Why it matters: procedural tree generation based on curves and instancing.
  - Translation value: recursive-looking branch systems, curve distortion,
    instance orientation, scale variation, and material variation.

## First Translation Target

Start with `Shriinivas/geometrynodes` because it is public, GitHub-hosted, MIT
licensed, and contains several bounded `.blend` examples. The first useful
translation is a tiny graph from `cartesian.blend` or `piechart.blend`, chosen
after node group inspection.

## Extraction Workflow

1. Download one source `.blend` into an ignored experiment folder.
2. Run Blender headlessly to list geometry node groups, group interface sockets,
   node types, link counts, and exposed modifiers.
3. Pick one small node group and write a plain-language graph map:
   inputs, generated geometry, fields/attributes, materials, outputs, and why
   each stage belongs.
4. Recreate that group with Geometry Script using local generated 5.1 docs for
   signatures.
5. Smoke-test generation in Blender and compare node types/link shape against
   the source.
6. Render only after the graph structure is close enough to make visual review
   meaningful.

## Known Tooling Need

We need a small Blender inspection script that can summarize node groups from a
`.blend` file into JSON. Without that, every example becomes manual archaeology
with better branding.

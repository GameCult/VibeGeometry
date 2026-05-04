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

- Blender public Geometry Nodes demo: instance attributes grass tuft
  - Source:
    https://download.blender.org/demo/geometry-nodes/instance_attribtues.blend
  - Completed entry:
    `docs/research/translations/blender-instance-attributes.md`
  - Why it matters: compact scatter graph that captures instance root position
    before realization and uses it to curl each realized blade.
  - Translation value: distribute points, instance on points, scale instances,
    capture attributes on instance domain, realize instances, tangent-axis
    deformation, and profile-scaled curve-to-mesh output.

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

- Blender public Geometry Nodes demo: Index Of Nearest
  - Source: https://download.blender.org/demo/geometry-nodes/index_of_nearest.blend
  - Completed entry:
    `docs/research/translations/blender-index-of-nearest.md`
  - Why it matters: compact helper groups around a simulation-zone point
    system.
  - Translation value: nearest-neighbor lookup, evaluate-at-index sampling,
    point-radius collision, velocity-field harnessing, and boundary/collider
    constraint helpers.

- Blender public Geometry Nodes demo: shortest-path labyrinth
  - Source:
    https://download.blender.org/demo/geometry-nodes/labyrinth-shortest_path-simon_thommes.blend
  - Completed entry:
    `docs/research/translations/blender-labyrinth-shortest-path.md`
  - Why it matters: compact pathfinding system built around shortest edge
    paths and path-to-curve conversion.
  - Translation value: topology-first graph structure, edge path selection,
    path capture before deletion, filleted curve output, and solution reveal
    control.

- Blender public Geometry Nodes demo: raycast minigame
  - Source: https://download.blender.org/demo/geometry-nodes/raycast-minigame.blend
  - Completed entry:
    `docs/research/translations/blender-raycast-minigame.md`
  - Why it matters: small ray-step helper groups inside a larger game-like
    procedural setup.
  - Translation value: initial direction vectors, sampled ray lines, raycast
    hit updates, reflected direction, and curve-output harnessing.

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

- `IRCSS/Blender-Geometry-Node-French-Houses`
  - Source: https://github.com/IRCSS/Blender-Geometry-Node-French-Houses
  - Completed foothold:
    `docs/research/translations/ircss-french-houses.md`
  - Why it matters: city-scale architectural kit with houses, gates, towers,
    walls, bridges, church parts, stalls, terrain, roads, vegetation, banners,
    windows, doors, and roofs.
  - Translation value: hierarchical procedural city systems, façade organs,
    topology generators, repeat/foreach/gizmo blockers, and reusable spines.

## First Translation Target

Start with `Shriinivas/geometrynodes` because it is public, GitHub-hosted, MIT
licensed, and contains several bounded `.blend` examples. The first useful
translation is a tiny graph from `cartesian.blend` or `piechart.blend`, chosen
after node group inspection.

First completed translation entry:

- `docs/research/translations/shriinivas-cartesian-helper.md`
- Source group: `NodeGroup.001` from `cartesian.blend`
- Geometry Script recreation:
  `examples/geometry_script/shriinivas_cartesian_helper.py`

Completed Cartesian function graph entry:

- `docs/research/translations/shriinivas-cartesian-function-graphs.md`
- Source groups: `Geometry Nodes Line`, `Geometry Nodes Parabola`,
  `Geometry Nodes Circle`
- Verification: all translated graphs match evaluated source geometry in
  Blender 5.1.1. Circle matches as a sorted vertex set because node expansion
  changes vertex order while preserving shape.
- Toolchain note: `external/geometry-script` is patched so nested `@tree` calls
  create `GeometryNodeGroup` nodes under Blender 5.1.

Completed pie chart entry:

- `docs/research/translations/shriinivas-piechart.md`
- Source groups: `NodeGroup`, `Pie Chart`, `getPie.002` through
  `getPie.012`, `Extended Pie Chart`
- Verification: translated segment and three-slice chart match evaluated source
  geometry with sorted max vertex delta `0.0` in Blender 5.1.1; extended
  segment and extended ten-slice chart also match source geometry with sorted
  max vertex delta `0.0`.

Completed field value helper entry:

- `docs/research/translations/shriinivas-fieldvalue-digit-at.md`
- Source groups: `Create Decimal`, `Create Segment`, `Seven Segments`,
  `Delete Segments`, `Next Digit`, `Digit At`
- Verification: decimal glyph geometry matches source with sorted max vertex
  delta `0.0`; segment geometry matches horizontal and vertical source cases
  with sorted max vertex delta `0.0`; seven-segment chassis geometry matches
  source with 74 vertices and sorted max vertex delta `0.0`; digit scalar
  helper matches source behavior across four number/position cases by driving
  `Mesh Line.Count` with the result; next-digit branch helper matches source
  across four cases spanning both sides of `Max Precision`; delete-mask scalar
  helper matches source across 195 digit/segment-position cases with zero
  mismatches; full `Field Value` default-route geometry matches source with
  256 vertices and sorted max vertex delta `0.0`.
- Toolchain note: full `Field Value` required explicit Blender 5 capture-item
  creation and a Geometry Script fork fix for menu socket defaults.

Completed parametric/polar equation entry:

- `docs/research/translations/shriinivas-paramnpolareq.md`
- Source groups: `chooseFloatVal`, `chooseFloatVal.001`, `chooseStrVal`,
  `chooseStrVal.001`, `NodeGroup`, `NodeGroup.001`, `NodeGroup.002`,
  `NodeGroup.003`, `getxy.001`, `Archimedes Spiral`, `Epicycloid`,
  `Geometry Nodes Group`, `Geometry Nodes Group.002`
- Verification: scalar equation helpers match by placing outputs into a single
  vertex position; Archimedes, epicycloid, and mirrored root spiral evaluated
  vertices match source geometry with max sorted deltas at or near `0.0`.
- Translation value: accumulated parameter ramps, parametric equations, polar
  conversion, mirrored curve streams, and scalar-harness design.

Completed CurveToMeshUV utility entry:

- `docs/research/translations/quellenform-curve-to-mesh-uv.md`
- Source groups: `Auto Smooth`, `Curve to Mesh UV`, `_258246`, `_Title`
- Verification: source and translated `Auto Smooth` preserve cube geometry and
  match smooth-face flags in Blender 5.1.1; main utility mesh, UV-field
  harness, caps-mask harness, demo geometry, and title geometry all match
  source evaluated geometry.

Completed Blender instance attributes entry:

- `docs/research/translations/blender-instance-attributes.md`
- Source group: `Grass Tuft Generator`
- Verification: default and wider/curlier/seeded control cases match source
  evaluated geometry with sorted max vertex delta `0.0`; edge counts, polygon
  counts, and smooth-face flags also match.
- Translation value: scatter nurseries, reused radial falloff, instance-domain
  capture before realization, and per-blade curl driven by remembered root
  position.

Completed Blender index-of-nearest helper entry:

- `docs/research/translations/blender-index-of-nearest.md`
- Source groups: `boundary_step`, `update_velocity`, `collision_step`,
  `collider_step`
- Verification: helper harnesses match source evaluated geometry with sorted
  max vertex delta `0.0`.
- Translation value: constraint projection, velocity capping, nearest-neighbor
  collision, and point-output verification harnesses.

Completed Blender shortest-path labyrinth entry:

- `docs/research/translations/blender-labyrinth-shortest-path.md`
- Source group: `Solvable Labyrinth Generator`
- Verification: small unsolved and solved cases match source evaluated
  geometry with sorted max vertex delta `0.0`; edge and polygon counts also
  match.
- Translation value: shortest edge paths, path capture, topology carving,
  path-to-curve conversion, and solution reveal.

Completed Blender raycast minigame foothold:

- `docs/research/translations/blender-raycast-minigame.md`
- Source groups: `Initial Direction`, `Line to be Casted`, `Cast Rays`
- Verification: direction, line, and raycast-step harnesses match source
  evaluated geometry with sorted max vertex delta `0.0`.
- Translation value: direction vectors, curve breadcrumbs, raycast hit updates,
  reflected vectors, and object-target controls.

Completed IRCSS French Houses foothold:

- `docs/research/translations/ircss-french-houses.md`
- Source groups: `MakeSpiral`, `PointyGothicCone`
- Verification: spiral output curve converted to points matches source with
  ordered max vertex delta `0.0`; plain and ornamented gothic cone cases match
  source evaluated mesh vertices with sorted max vertex delta `0.0`.
- Translation value: procedural-city corpus triage, spiral architectural
  spines, roof-cap ornament grown from structural ribs, captured source points
  through instancing, and explicit blockers for repeat-zone feedback, repeat
  `Top` outputs, foreach zones, gizmo nodes, and converter duplicate-key
  failures.

Inspected but deferred official demo files:

- `hexgrid_blender_geometry_nodes_demo.blend`: mostly legacy undefined nodes
  in Blender 5.1, plus a duplicate `Auto Smooth` helper already covered.
- `wavy_procedural_wall.blend`: several legacy/undefined attribute-toolkit
  groups; useful later as migration quarry, not current doctrine.
- `pebble_scattering.blend`: legacy undefined nodes dominate the single group.
- `gizmo_array.blend`: focused on Blender 4.3+ geometry-node gizmo nodes.
  Needs a dedicated gizmo-authoring pass.
- `jiggly_pudding.blend`: simulation-zone graph. Needs dedicated simulation
  zone support and verification discipline.
- `repeat_zone_flower_by_MiRA.blend`: repeat-zone flower system. Needs a
  repeat-zone pass before translation.

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

`tools/inspect_blend_node_groups.py` can summarize geometry node groups from an
opened `.blend` file into JSON. It records group interfaces, nodes, simple node
properties, sockets, links, and modifier users.

`tools/verify_cartesian_translations.py` verifies the translated Cartesian
helper, line, parabola, and circle groups against their source groups by
wrapping each graph in the same evaluator graph and comparing evaluated mesh
vertices.

Generated node groups must be referenced by an object/modifier or marked with
`use_fake_user = True` before saving a `.blend`; otherwise Blender discards the
orphaned group on save. Very normal behavior, if your filing cabinet hates you.

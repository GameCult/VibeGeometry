# IRCSS French Houses System Map

## Scope

Source file:
`experiments/source-blends/ircss-french-houses.blend`

Inspection cache:
`experiments/inspection/ircss-french-houses-node-groups.json`

Generated with Blender 5.1.1 after extending
`tools/inspect_blend_node_groups.py` to record nested `GeometryNodeGroup`
`node_tree` references.

## High-Level Shape

This `.blend` is a procedural town kit, not one scene graph. The file contains:

- 108 geometry node groups, 107 unique names.
- One duplicate group name: `Is Edge Manifold`.
- 63 distinct modifier root groups used by scene objects.
- 62 groups that call at least one nested group.
- 163 distinct group dependency edges.

The useful mental split:

- **Composers** create recognizable buildings and scene pieces: houses, towers,
  church fronts, gates, walls, windmills, bridges, stalls, terrain, and roads.
- **Organs** make reusable architectural parts: arcs, windows, doors, roof caps,
  stairs, beams, rails, columns, banners, terraces, and covers.
- **Utilities** carry field logic, edge tests, ranges, auto-smoothing, wrapping,
  curve facts, random seeding, and geometry selection.

Metaphor in use: the town is not poured from one mold. It is an assembly yard.
Composers bolt together organs; organs lean on utilities; utilities are the
measuring jigs and clamps.

## Modifier Entrypoints

Most reused scene roots:

| Modifier root | Scene users | Dependency closure |
| --- | ---: | ---: |
| `GenerateHouse` | 5 | 9 |
| `Generate Cliff Type 2` | 3 | 2 |
| `MakeStallCover` | 3 | 0 |
| `GenerateDoorsWithAlcove` | 2 | 2 |
| `Tree On Geo Points` | 2 | 5 |
| `GenerateCover` | 2 | 1 |
| `GenerateStairCase` | 2 | 9 |
| `Generate Tower` | 2 | 10 |
| `GenerateAlcoveWindows` | 2 | 6 |

Large single-root systems:

| Modifier root | Dependency closure | Role |
| --- | ---: | --- |
| `Geometry Nodes.002` | 28 | cathedral root |
| `GenerateChurchBuildingB` | 22 | church side/body composer |
| `ChurchA-Front` | 20 | church front facade composer |
| `CreateGate` | 18 | gate composer |
| `HousesOnCurves` | 13 | curve-distributed houses |
| `DomaTower` | 12 | domed tower composer |
| `ChurchFrontTowers` | 11 | church tower front system |
| `Generate Tower` | 10 | tower composer |
| `TownWall` | 10 | wall composer |
| `WindMill` | 10 | windmill composer |

## Major Composer Wiring

`GenerateHouse` depends on:

- `GetPositionBasedSeed`
- `Switch On Roof Type`
- `Generate Windows`
- `Curve Info`
- `CreateDiagonalBeams`
- `WindowBeams`
- `Is Edge Manifold`

Interpretation: houses are facade assemblers. They choose roof type, place
windows, derive local curve facts, add diagonal beams, and use edge-manifold
tests as selection guards.

`GenerateStairCase` depends on:

- `MakeSpiral`
- `MakeStairs`
- `GenerateTerrace`

Interpretation: this is the cleanest staircase chain. `MakeSpiral` provides the
spine, `MakeStairs` hangs tread geometry on the spine, and `GenerateTerrace`
builds the surrounding rail/ground system.

`DomaTower` depends on:

- `PointWindowsFromEdges`
- `PointyGothicCone`
- `WindowWalls`
- `Generate Gothic Square Tower`

Interpretation: domed towers are edge/window systems with gothic cone ornament.
The accepted `PointyGothicCone` translation is not isolated trivia; it is a
reused ornament organ in this tower family.

`GenerateChurchBuildingB` depends on:

- `Switch On Roof Type`
- `DistancingType`
- `ResampleEdgesAndSpawnWindowedWalld`
- `Is Edge Manifold`
- `Gothic SupportColumn From EDge`
- `GenerateWindowsFromEdges`
- `ChurchA-Front`
- `WindowWalls`

Interpretation: church bodies are facade/edge pipelines. They resample edges,
spawn windowed walls, add gothic supports, and reuse the church front.

`CreateGate` depends on:

- `DoorTileFromArc`
- `Is Edge Manifold`
- `Spawn Normals on faces`
- `GenerateUpperWindowWithAlcove`
- `GetSteppeddirectionFrom position`
- `StonesOnSurface`
- `GenerateMedialAxisRectangleTopology`

Interpretation: gates are topology-first structures. A medial-axis rectangle
topology lays out the plan; arcs and upper windows turn that skeleton into
visible architecture; stones finish surfaces.

## Dependency Hubs

Most reused groups:

| Group | Callers | Role |
| --- | ---: | --- |
| `Is Edge Manifold` | 9 | edge-validity guard |
| `Switch On Roof Type` | 9 | roof/menu router |
| `Curve Info` | 7 | curve endpoint/root/tip facts |
| `Gothic SupportColumn From EDge` | 6 | gothic column organ |
| `Select Original Geometry After Edge Extrude` | 6 | post-extrude selection utility |
| `SetAutoSmooth` | 6 | surface finishing utility |
| `StonesOnSurface` | 6 | stone scatter/finish organ |
| `Generate Windows` | 5 | reusable window generator |
| `Curve Tip` | 4 | curve endpoint helper |
| `GenerateUpperWindowWithAlcove` | 4 | upper window organ |
| `GetPositionBasedSeed` | 4 | deterministic spatial seed helper |
| `RailsFromEdge` | 4 | rail organ |
| `Random Rotation` | 4 | randomized orientation helper |
| `WindowWalls` | 4 | window-wall organ |

These hubs define the file's real language. Translating one thousand-node
composer before these hubs are mapped would be pure ceremony.

## Feature Pressure

Node-feature counts across groups:

| Feature | Groups | Translation meaning |
| --- | ---: | --- |
| repeat zones | 35 | major blocker for accumulators and iterative topology |
| geometry-node gizmos | 31 | authoring/UI blocker, often mixed into large systems |
| foreach zones | 9 | blocker for element-wise geometry workflows |
| closures | 7 | Blender 5 closure/menu workflows need careful converter handling |
| menu switches | 17 | control-surface and socket-default pressure |
| capture attributes | 66 | attribute survival is central |
| store named attributes | 61 | named field/attribute contracts are central |

Captures and stored attributes are not blockers; they are the bloodstream of the
file. Repeat, foreach, gizmo, and closure nodes are the hard toolchain pressure.

## Materials And Assets

The file has:

- 502 objects.
- 56 materials.
- 23 collections.
- 16 `Collection Info` nodes.
- 45 `Object Info` nodes.
- 14 material interface sockets.
- 81 color interface sockets.
- 257 material assignment or material-selection nodes.

Material usage is concentrated around a small palette:

| Material | Node references | Role |
| --- | ---: | --- |
| `GroundFloorWalls` | 86 | dominant wall/base material |
| `Roof` | 42 | roof surfaces |
| `Beam` | 30 | timber and rail pieces |
| `UpperFloorsPaint` | 13 | painted alcove/window systems |
| `Greenery` | 9 | vegetation |
| `RoundWindwos` | 7 | round/gothic windows |
| `Copper` | 6 | domes and metal roof accents |
| `FakeRoof` | 6 | alternate roof material |
| `WindowGlass` | 4 | glass |
| `Rock` | 4 | stones/terrain |

Important material sockets:

- `DomaTower.DomeMaterial -> Copper`
- `Geometry Nodes.002.DomeMaterial -> FakeRoof`
- `GenerateAlcoveWindows.AlcoveMaterial -> UpperFloorsPaint`
- `GenerateDoorsWithAlcove.AlcoveMaterial -> UpperFloorsPaint`
- `GenerateUpperWindowWithAlcove.AlcoveMaterial -> UpperFloorsPaint`
- `Wooden Bridge.Material -> Beam`
- `Fence Type A.Material -> Beam`
- `Generate Cliff Type 2.Walls Material -> Cliff2Walls`
- `Generate Cliff Type 2.Top Ground Materials -> Cliff2Top`

Collection dependencies:

| Collection | Used by | Meaning |
| --- | --- | --- |
| `Bricks` | `MakeStairs`, `StonesOnSurface` | instanced brick/stone assets |
| `BouldersSet` | `Geometry Nodes.001` | landscape scatter assets |
| `Paths` | `Geometry Nodes.001` | landscape/path interaction |
| `Plants` | `Generate Cliff Type 2` | cliff vegetation scatter |
| `RiverBank` | `Make River` | riverbank geometry |

Most `Object Info` nodes have no default object set. The one explicit object
reference observed is `DoorTileFromArc`, used by an object-info node as an
asset handle.

Interpretation: material and collection state is part of the procedural
contract. A translation that matches vertices while dropping materials,
collections, or color sockets may preserve shape but not the authored city kit.

## Accepted Footholds

`MakeSpiral -> VG Make Spiral`

- Role: architectural spine.
- Verified with 200 ordered curve points at max delta `0.0`.
- Used by `GenerateStairCase`.

`PointyGothicCone -> VG Pointy Gothic Cone`

- Role: roof/gothic ornament grown from an input point host.
- Verified with plain and detailed cases at sorted max delta `0.0`.
- Used by `DomaTower`, `Gothic SupportColumn From EDge`, and
  `PointWindowsFromEdges`.

## Current Toolchain State

The Geometry Script fork now emits compiling `nodes_to_script` drafts for these
IRCSS targets:

- `MakeSpiral`
- `PointyGothicCone`
- `GenerateArc`
- `MakeStairs`
- `GenerateStairCase`
- `GenerateBricks`
- `GenerateMedialAxisRectangleTopology`
- `GenerateWindowsFromEdges`
- `Pole`
- `Round Bottom`
- `WindowBeams`

This only proves the converter can produce syntactically valid drafts. It does
not prove runtime graph construction or behavioral equivalence. The drafts are
source probes, not house style.

## Translation Strategy

The next useful city-organ translations should come from dependency hubs or
clean chains, not top-level composers.

Best next candidates:

| Candidate | Why it matters | Risk |
| --- | --- | --- |
| `GenerateArc` | core arch primitive for gates, doors, and gothic systems | large but non-zone |
| `MakeStairs` | direct child of `GenerateStairCase`; now has compiling draft | closures and collection asset dependency |
| `GenerateStairCase` | clean chain proving spine -> treads -> terrace | depends on `MakeStairs` and `GenerateTerrace` |
| `Switch On Roof Type` | tiny, heavily reused roof router | menu contract must be preserved |
| `Is Edge Manifold` | tiny, heavily reused guard | duplicate source names need disambiguation |
| `GenerateUpperWindowWithAlcove` | reused by towers, gates, alcove windows | 128 nodes, nested dependencies |
| `Generate Windows` | reused facade organ | 188 nodes but no zone blocker |

Avoid as first next targets:

- `CreateGate`, `GenerateHouse`, `GenerateChurchBuildingB`, `Generate Tower`,
  `Generate Square Tower`, `ChurchFrontTowers`, `WindMill`: too much composer
  surface before their organs are mapped.
- Repeat/foreach/gizmo-heavy systems unless the explicit goal is toolchain
  support.
- Empty-output harnesses such as the rejected `WindowBeams` case.

## What Is Still Not Understood

- Exact visual appearance of every modifier root under render lighting.
- Runtime behavior of all converter drafts; compile success is only the first
  gate.
- Repeat-zone state semantics for topology accumulators.
- Foreach-zone semantics for edge/window/wall systems.
- Geometry-node gizmo behavior as editable authoring controls.
- How unset object/collection inputs are meant to be supplied by modifier users
  in every root object.

This is enough understanding to choose translation targets intelligently. It is
not enough to claim the whole town can be regenerated from script.

# IRCSS French Houses Node Mechanism Study

This is the pass below the atlas. The atlas answers "which groups exist?" This note answers "what moves do the nodes use?" It is generated from the Blender 5.1.1 inspection cache and then kept as procedural doctrine for city-scale translation work.

## Coverage

- Geometry node groups studied: 108.
- Total inspected nodes: 16889.
- Unique node types: 138.
- Node frames carrying artist intent: 844.
- Nested group nodes: 273; distinct dependency edges: 163.

## What The Town Kit Is Made Of

- Coordinate math is the dominant substrate. `Math`, `Vector Math`, `Combine XYZ`, `Separate XYZ`, comparisons, rotations, and map ranges turn edge facts into heights, offsets, roof slopes, beam directions, and random variation.
- Topology mutation is the architectural engine. Extrude, delete, flip, merge, scale, mesh-to-curve, and curve-to-mesh nodes repeatedly turn boring rectangles and edges into walls, arches, crenellations, rails, and roofs.
- Attribute memory is the load-bearing glue. Captures, stored named attributes, field-on-domain, sample-index, and named attributes preserve edge identity, ordering, side masks, curve facts, and scatter state across domain changes.
- Instancing is used as a fabrication step, not just decoration. Stones, crops, plants, roof spikes, banners, windows, trees, pebbles, and facade details are usually made as small bodies and attached to points or sampled ribs.
- Repeat, foreach, closure, menu, and gizmo nodes are authoring grammar. They encode growth loops, per-element facade passes, reusable calculations, user-selectable variants, and direct viewport controls.

## Family Counts

- `authoring_controls`: 5224
- `coordinate_math`: 5107
- `position_fields`: 1757
- `topology_mutation`: 1064
- `attribute_memory`: 928
- `instances_scatter`: 529
- `control_flow`: 504
- `curve_rails`: 478
- `material_finish`: 372
- `random_inputs`: 271
- `rotation_matrix_math`: 240
- `input_constants`: 148
- `mesh_seeds`: 135
- `topology_query`: 125
- `color_material`: 7

Role counts: `composer: prop/resource` 32, `utility: field/topology` 26, `composer: architecture` 21, `organ: architectural part` 15, `composer: terrain/scatter` 10, `organ: terrain/scatter` 4.

## Frame Intent

The source file has 844 frame nodes with artist labels across 61 groups. Treat
them as field notes, not polished docs. The spelling is rough, but the intent
is often exact enough to preserve stage boundaries in a translation.

Frame-label pressure clusters:

- Roofs, floors, bases, beams, windows, doors, walls, edges, arcs, and supports
  dominate the architecture vocabulary.
- The largest framed systems are `GenerateHouse` (131 frames), `CreateGate`
  (71), `Generate Tower` (70), `Generate Square Tower` (68), `DoorTileFromArc`
  (25), `GenerateChurchBuildingB` (24), `TownWall` (24), `Geometry Nodes`
  (23), `PCAGetLongAndShortAxis` (22), and `TownWall_Climbing` (21).
- Frame labels repeatedly separate calculation from fabrication: calculate
  widths and directions, save edge IDs or random values, filter top/front/side
  selections, then extrude, tile, spawn, or finish geometry.
- The labels confirm the translation ladder: topology utilities first, then
  organ stages, then full composers. A thousand-node group is usually a stack
  of named frame stages, not one indivisible spell.

## Translation Doctrine From This File

### Start With Edges, Not Buildings

Most architecture graphs read an input rectangle, curve, edge strip, or generated topology and then ask edge questions: which side, which corner, which loop, which face belongs to the original extrusion, which edge can host a window. In script, the first useful abstraction is usually a named edge-selection helper, not a complete house.

Planning sketch, not accepted Geometry Script:

```text
base edges -> named side/corner selections -> extruded wall band -> sampled window sites
```

### Treat Curves As Attachment Rails

Many visible details are built by converting mesh edges to curves, resampling them, and instancing parts along the result. This is how roof ribs, stair spines, trim, and detail spikes become controllable instead of hand-placed.

Verified excerpt from `examples/geometry_script/ircss_french_houses.py`:

```python
cone_ribs = delete_geometry(mode="ALL", domain="EDGE", geometry=cone_for_detail_edges, selection=cone_edge_flags.edge_trim)
rib_curve = mesh_to_curve(mode="EDGES", mesh=cone_ribs)
detail_points = resample_curve(
    keep_last_segment=True,
    curve=rib_curve,
    mode="Length",
    count=5,
    length=gothic_detail_density,
)
```

### Capture Before You Change Domains

If a graph instances, realizes, extrudes, deletes, or converts between mesh and curve, values needed later must be captured first. The source does this constantly; skipping it is how a plausible script loses the side or edge it meant to dress.

Verified excerpt from `examples/geometry_script/ircss_french_houses.py`:

```python
point_positions = _capture_attribute_item("VECTOR", "POINT", geometry, position(), "source position")
cone_edge_flags = _capture_attribute_item("BOOLEAN", "EDGE", tapered_cone, cap_or_body_edge, "edge trim")
```

### Use Python For Tables And Orchestration

The file has repeated facade passes, roof variants, banner/crop families, and many near-clone composers. Python should own those tables and call compact Geometry Script groups. The emitted graph should still expose the resulting controls.

Planning sketch, not accepted Geometry Script:

```text
Python rows/variants -> repeated compact group calls -> one inspectable composer graph
```

### Translate Toolchain Grammar Deliberately

Repeat and foreach zones are not inconvenient decorations. They are how this file grows rows, walks geometry elements, and accumulates topology. If Geometry Script cannot emit them cleanly yet, the right response is either toolchain support or an explicit Python-side orchestration model with equivalent evaluated behavior.

## Mechanism Table For Every Group

| Group | Role | Main mechanisms | Features | Nodes | Calls | Called by |
| --- | --- | --- | --- | ---: | ---: | ---: |
| `ArcsFromEdges` | organ: architectural part | route/rail shaping, mesh surgery, edge/face queries, attribute memory, instancing/scatter | `repeat`, `gizmo`, `capture`, `store` | 209 | 1 | 3 |
| `Banner` | composer: prop/resource | mesh surgery, attribute memory, instancing/scatter, surface finish, primitive seeds | `gizmo`, `capture`, `store`, `asset`, `material` | 51 | 2 | 0 |
| `BannerTypeFour` | composer: prop/resource | mesh surgery, attribute memory, instancing/scatter, surface finish, primitive seeds | `capture`, `store`, `asset`, `material` | 70 | 2 | 0 |
| `BannerTypeThree` | composer: prop/resource | mesh surgery, attribute memory, instancing/scatter, surface finish, primitive seeds | `capture`, `store`, `asset`, `material` | 58 | 2 | 0 |
| `ChurchA-Front` | composer: architecture | route/rail shaping, mesh surgery, edge/face queries, attribute memory, instancing/scatter | `repeat`, `foreach`, `gizmo`, `menu`, `capture`, `store`, `material` | 475 | 8 | 1 |
| `ChurchFrontTowers` | composer: architecture | route/rail shaping, mesh surgery, edge/face queries, attribute memory, instancing/scatter | `repeat`, `foreach`, `gizmo`, `closure`, `menu`, `capture`, `store`, `material` | 792 | 8 | 1 |
| `Color in Range` | utility: field/topology | field utility | none | 7 | 0 | 2 |
| `ColumeDecoFromEdges` | composer: prop/resource | route/rail shaping, mesh surgery, edge/face queries, attribute memory, instancing/scatter | `capture`, `store`, `material` | 114 | 0 | 2 |
| `Corn  From Point` | organ: terrain/scatter | route/rail shaping, mesh surgery, attribute memory, instancing/scatter, branching/zones | `capture`, `store`, `material` | 209 | 0 | 1 |
| `CreateDiagonalBeams` | organ: architectural part | route/rail shaping, mesh surgery, attribute memory, instancing/scatter, branching/zones | `capture` | 26 | 0 | 1 |
| `CreateGate` | composer: architecture | route/rail shaping, mesh surgery, edge/face queries, attribute memory, instancing/scatter | `repeat`, `gizmo`, `closure`, `capture`, `store`, `material` | 1081 | 7 | 0 |
| `Curve Info` | utility: field/topology | route/rail shaping, attribute memory | none | 19 | 2 | 7 |
| `Curve Root` | utility: field/topology | route/rail shaping, edge/face queries, attribute memory | none | 10 | 0 | 2 |
| `Curve Tip` | utility: field/topology | route/rail shaping, edge/face queries, attribute memory | none | 10 | 0 | 4 |
| `CurvedDoorFromEdges` | composer: prop/resource | route/rail shaping, mesh surgery, edge/face queries, attribute memory, instancing/scatter | `capture`, `store`, `material` | 182 | 0 | 1 |
| `DistancingType` | utility: field/topology | branching/zones | `menu` | 3 | 0 | 1 |
| `Distribute Corn` | composer: terrain/scatter | attribute memory, instancing/scatter, orientation math | `capture`, `asset` | 18 | 2 | 0 |
| `Distribute Sunflower` | composer: terrain/scatter | attribute memory, instancing/scatter, orientation math | `gizmo`, `capture`, `asset` | 23 | 2 | 0 |
| `Distribute Wheat` | composer: terrain/scatter | attribute memory, instancing/scatter, orientation math | `capture`, `asset` | 19 | 2 | 0 |
| `DomaTower` | composer: architecture | route/rail shaping, mesh surgery, attribute memory, branching/zones, surface finish | `repeat`, `gizmo`, `menu`, `capture`, `store`, `material` | 290 | 4 | 1 |
| `DoorTileFromArc` | composer: prop/resource | mesh surgery, edge/face queries, attribute memory, instancing/scatter, branching/zones | `repeat`, `store` | 313 | 4 | 3 |
| `EdgesToGates` | composer: architecture | route/rail shaping, attribute memory | `store` | 11 | 1 | 0 |
| `Fence Type A` | composer: prop/resource | route/rail shaping, mesh surgery, edge/face queries, attribute memory, instancing/scatter | `repeat`, `foreach`, `capture`, `store`, `material` | 167 | 2 | 1 |
| `Flag` | composer: prop/resource | route/rail shaping, mesh surgery, attribute memory, instancing/scatter, branching/zones | `repeat`, `gizmo`, `capture`, `store`, `material` | 244 | 0 | 3 |
| `Float in Range` | utility: field/topology | field utility | none | 4 | 0 | 2 |
| `float to Rotation` | utility: field/topology | orientation math | none | 13 | 0 | 1 |
| `Generate Cliff Type 2` | composer: terrain/scatter | route/rail shaping, mesh surgery, edge/face queries, attribute memory, instancing/scatter | `repeat`, `gizmo`, `capture`, `store`, `asset`, `material` | 250 | 2 | 0 |
| `Generate Extruded DoorShape` | organ: architectural part | route/rail shaping, mesh surgery, attribute memory, instancing/scatter, branching/zones | `capture`, `store`, `material` | 180 | 1 | 3 |
| `Generate Gothic Square Tower` | organ: architectural part | route/rail shaping, mesh surgery, edge/face queries, attribute memory, instancing/scatter | `foreach`, `capture`, `material` | 238 | 3 | 3 |
| `Generate Square Tower` | composer: architecture | route/rail shaping, mesh surgery, edge/face queries, attribute memory, instancing/scatter | `repeat`, `capture`, `store`, `asset`, `material` | 805 | 6 | 0 |
| `Generate Stones` | composer: terrain/scatter | mesh surgery, instancing/scatter, branching/zones, surface finish, orientation math | `repeat`, `material` | 47 | 0 | 0 |
| `Generate Tower` | composer: architecture | route/rail shaping, mesh surgery, edge/face queries, attribute memory, instancing/scatter | `repeat`, `capture`, `store`, `asset`, `material` | 707 | 7 | 0 |
| `Generate Windows` | organ: architectural part | route/rail shaping, mesh surgery, attribute memory, instancing/scatter, branching/zones | `menu`, `capture`, `store`, `asset`, `material` | 188 | 2 | 5 |
| `GenerateAlcoveWindows` | composer: architecture | mesh surgery, attribute memory, primitive seeds | `store` | 14 | 1 | 0 |
| `GenerateArc` | composer: prop/resource | route/rail shaping, mesh surgery, attribute memory, instancing/scatter, branching/zones | `capture`, `store` | 153 | 0 | 2 |
| `GenerateBricks` | composer: prop/resource | mesh surgery, branching/zones, surface finish, primitive seeds | `repeat`, `material` | 26 | 0 | 0 |
| `GenerateChurchBuildingB` | composer: architecture | route/rail shaping, mesh surgery, edge/face queries, attribute memory, instancing/scatter | `repeat`, `gizmo`, `menu`, `capture`, `store`, `material` | 893 | 8 | 1 |
| `GenerateCover` | composer: prop/resource | route/rail shaping, mesh surgery, edge/face queries, attribute memory, instancing/scatter | `menu`, `capture`, `store`, `material` | 178 | 1 | 0 |
| `GenerateDoorsWithAlcove` | composer: prop/resource | attribute memory | `store` | 10 | 1 | 0 |
| `GenerateHouse` | composer: architecture | route/rail shaping, mesh surgery, edge/face queries, attribute memory, instancing/scatter | `repeat`, `capture`, `store`, `asset`, `material` | 1023 | 7 | 1 |
| `GenerateLightShaftExrudes` | utility: field/topology | mesh surgery, attribute memory, instancing/scatter, branching/zones, surface finish | `capture`, `store`, `material` | 112 | 1 | 2 |
| `GenerateMedialAxisRectangleTopology` | composer: prop/resource | mesh surgery, edge/face queries, attribute memory, branching/zones, primitive seeds | `repeat`, `capture`, `store` | 119 | 0 | 3 |
| `GenerateRockSlow` | composer: prop/resource | mesh surgery, edge/face queries, attribute memory, instancing/scatter, branching/zones | `repeat`, `gizmo`, `menu`, `store`, `material` | 94 | 2 | 1 |
| `GenerateStairCase` | composer: prop/resource | route/rail shaping, mesh surgery, edge/face queries, attribute memory | `capture` | 53 | 3 | 0 |
| `GenerateTerrace` | composer: prop/resource | route/rail shaping, mesh surgery, edge/face queries, attribute memory, instancing/scatter | `menu`, `capture`, `store`, `asset`, `material` | 150 | 3 | 1 |
| `GenerateUpperWindowWithAlcove` | organ: architectural part | mesh surgery, attribute memory, instancing/scatter, branching/zones, surface finish | `menu`, `capture`, `store`, `material` | 128 | 2 | 4 |
| `GenerateWindowsFromEdges` | organ: architectural part | mesh surgery, branching/zones, surface finish | `foreach`, `material` | 29 | 2 | 2 |
| `GeneratorBoulders` | composer: prop/resource | mesh surgery, branching/zones | `repeat` | 16 | 1 | 0 |
| `Geometry Nodes` | composer: prop/resource | route/rail shaping, mesh surgery, attribute memory, instancing/scatter, branching/zones | `repeat`, `gizmo`, `closure`, `capture`, `store`, `material` | 355 | 3 | 0 |
| `Geometry Nodes.001` | composer: prop/resource | route/rail shaping, mesh surgery, attribute memory, instancing/scatter, surface finish | `capture`, `store`, `asset`, `material` | 135 | 1 | 0 |
| `Geometry Nodes.002` | composer: prop/resource | mesh surgery, attribute memory, instancing/scatter, branching/zones | `gizmo`, `store` | 142 | 3 | 0 |
| `GetBoundaryEdgeTangentAndNomral` | utility: field/topology | edge/face queries, attribute memory, branching/zones | `capture` | 45 | 0 | 1 |
| `GetOnlySide Edges after Edge Extrude` | utility: field/topology | attribute memory | none | 7 | 1 | 1 |
| `GetPositionBasedSeed` | utility: field/topology | instancing/scatter | `asset` | 15 | 0 | 4 |
| `GetSteppeddirectionFrom position` | utility: field/topology | field utility | none | 8 | 0 | 1 |
| `Gothic SupportColumn From EDge` | organ: architectural part | mesh surgery, edge/face queries, attribute memory, instancing/scatter, branching/zones | `repeat`, `gizmo`, `menu`, `capture` | 107 | 2 | 6 |
| `GothicSupportBeaconFromEdgeParent` | composer: prop/resource | attribute memory, surface finish | `gizmo`, `store`, `material` | 13 | 1 | 0 |
| `HangingBanners` | composer: prop/resource | route/rail shaping, mesh surgery, edge/face queries, attribute memory, instancing/scatter | `repeat`, `capture`, `store`, `material` | 108 | 0 | 0 |
| `HousesOnCurves` | composer: architecture | route/rail shaping, mesh surgery, edge/face queries, attribute memory, instancing/scatter | `repeat`, `foreach`, `capture`, `store` | 166 | 4 | 0 |
| `Int in Range` | utility: field/topology | field utility | none | 4 | 0 | 1 |
| `Is Edge Manifold [1]` | utility: field/topology | edge/face queries, attribute memory | none | 4 | 0 | 9 |
| `Is Edge Manifold [2]` | utility: field/topology | edge/face queries, attribute memory | none | 4 | 0 | 9 |
| `Make Dirt Road` | composer: prop/resource | route/rail shaping, mesh surgery, attribute memory, instancing/scatter, surface finish | `capture`, `store`, `asset`, `material` | 102 | 0 | 0 |
| `Make Pumpkin From Points` | utility: field/topology | route/rail shaping, mesh surgery, attribute memory, instancing/scatter, branching/zones | `capture`, `store`, `material` | 217 | 1 | 1 |
| `Make River` | composer: terrain/scatter | route/rail shaping, mesh surgery, attribute memory, instancing/scatter, branching/zones | `capture`, `store`, `asset`, `material` | 136 | 0 | 0 |
| `MakeBush` | composer: prop/resource | route/rail shaping, mesh surgery, edge/face queries, attribute memory, instancing/scatter | `repeat`, `gizmo`, `capture`, `store`, `material` | 94 | 1 | 2 |
| `MakeGrass` | composer: prop/resource | mesh surgery, attribute memory, instancing/scatter, branching/zones, surface finish | `repeat`, `store`, `material` | 26 | 0 | 0 |
| `MakeSpiral` | composer: prop/resource | route/rail shaping, edge/face queries | none | 20 | 0 | 1 |
| `MakeStairs` | composer: prop/resource | route/rail shaping, instancing/scatter, branching/zones, surface finish, primitive seeds | `closure`, `menu`, `asset`, `material` | 25 | 0 | 1 |
| `MakeStallCover` | composer: architecture | route/rail shaping, mesh surgery, attribute memory, instancing/scatter, branching/zones | `repeat`, `gizmo`, `menu`, `capture`, `store`, `material` | 282 | 0 | 0 |
| `MakeTree` | composer: terrain/scatter | route/rail shaping, mesh surgery, edge/face queries, attribute memory, instancing/scatter | `gizmo`, `capture`, `store`, `material` | 271 | 1 | 0 |
| `MatrixSubtract` | utility: field/topology | orientation math | none | 23 | 0 | 1 |
| `OctaveBasedSpawnStone` | organ: terrain/scatter | mesh surgery, edge/face queries, instancing/scatter | `asset` | 62 | 1 | 1 |
| `PCAGetLongAndShortAxis` | utility: field/topology | attribute memory, instancing/scatter, branching/zones, orientation math | `repeat` | 155 | 1 | 1 |
| `Points On Surface` | composer: prop/resource | mesh surgery, instancing/scatter | `asset` | 17 | 0 | 0 |
| `PointWindowsFromEdges` | organ: architectural part | route/rail shaping, mesh surgery, edge/face queries, attribute memory, instancing/scatter | `capture`, `material` | 81 | 2 | 1 |
| `PointyGothicCone` | organ: architectural part | route/rail shaping, mesh surgery, attribute memory, instancing/scatter, orientation math | `capture` | 58 | 0 | 3 |
| `Pole` | composer: prop/resource | mesh surgery, attribute memory, branching/zones, surface finish, primitive seeds | `repeat`, `gizmo`, `store`, `material` | 89 | 0 | 3 |
| `ProjectOnCoordinate` | utility: field/topology | field utility | none | 12 | 0 | 1 |
| `Pumpkin` | composer: prop/resource | instancing/scatter, orientation math | `asset` | 15 | 1 | 0 |
| `RailsFromEdge` | organ: architectural part | route/rail shaping, mesh surgery, edge/face queries, attribute memory, instancing/scatter | `gizmo`, `capture`, `material` | 191 | 0 | 4 |
| `Random Rotation` | utility: field/topology | orientation math | none | 25 | 0 | 4 |
| `Reroute` | utility: field/topology | mesh surgery, edge/face queries, attribute memory, instancing/scatter, branching/zones | `repeat`, `gizmo`, `capture`, `store`, `material` | 571 | 3 | 2 |
| `ResampleEdgesAndSpawnWindowedWalld` | organ: architectural part | route/rail shaping, mesh surgery, edge/face queries, attribute memory, branching/zones | `foreach`, `capture` | 56 | 2 | 2 |
| `Round Bottom` | composer: prop/resource | mesh surgery, branching/zones, surface finish, primitive seeds | `repeat`, `gizmo`, `closure` | 56 | 0 | 2 |
| `Select Original Geometry After Edge Extrude` | utility: field/topology | edge/face queries, attribute memory | none | 11 | 0 | 6 |
| `SetAutoSmooth` | utility: field/topology | surface finish | none | 5 | 1 | 6 |
| `ShouldAutoSmooth` | utility: field/topology | edge/face queries, attribute memory | `capture` | 18 | 0 | 3 |
| `Spawn Normals on faces` | utility: field/topology | attribute memory, instancing/scatter, primitive seeds, orientation math | `capture` | 10 | 0 | 1 |
| `Stall` | composer: architecture | route/rail shaping, mesh surgery, attribute memory, instancing/scatter, branching/zones | `gizmo`, `capture`, `store`, `material` | 116 | 2 | 0 |
| `StonesOnSurface` | composer: terrain/scatter | mesh surgery, edge/face queries, attribute memory, instancing/scatter, branching/zones | `closure`, `menu`, `capture`, `store`, `asset`, `material` | 129 | 2 | 6 |
| `Sun Flowers From Points` | utility: field/topology | route/rail shaping, mesh surgery, attribute memory, instancing/scatter, branching/zones | `capture`, `store`, `material` | 229 | 0 | 1 |
| `Switch On Roof Type` | organ: architectural part | branching/zones | `menu` | 3 | 0 | 9 |
| `Tower Gothic Type 2` | composer: architecture | attribute memory | `gizmo`, `store` | 23 | 1 | 0 |
| `TownWall` | composer: architecture | route/rail shaping, mesh surgery, edge/face queries, attribute memory, instancing/scatter | `repeat`, `gizmo`, `closure`, `capture`, `store`, `material` | 342 | 4 | 0 |
| `TownWall_Climbing` | composer: architecture | route/rail shaping, mesh surgery, edge/face queries, attribute memory, instancing/scatter | `repeat`, `gizmo`, `capture`, `store`, `asset`, `material` | 285 | 3 | 0 |
| `Tree On Geo Points` | composer: terrain/scatter | route/rail shaping, mesh surgery, edge/face queries, attribute memory, instancing/scatter | `capture`, `store`, `material` | 282 | 3 | 0 |
| `WallTowerround` | composer: architecture | route/rail shaping, mesh surgery, attribute memory, branching/zones, surface finish | `repeat`, `gizmo`, `capture`, `store`, `material` | 265 | 3 | 0 |
| `Waterfall` | composer: terrain/scatter | route/rail shaping, mesh surgery, attribute memory, instancing/scatter, branching/zones | `gizmo`, `capture`, `store`, `material` | 114 | 0 | 0 |
| `Wheat From Point` | organ: terrain/scatter | route/rail shaping, mesh surgery, edge/face queries, attribute memory, instancing/scatter | `repeat`, `menu`, `capture`, `store`, `material` | 265 | 0 | 1 |
| `Wind On Plants` | organ: terrain/scatter | surface finish | none | 23 | 0 | 3 |
| `WindMill` | composer: architecture | route/rail shaping, mesh surgery, edge/face queries, attribute memory, instancing/scatter | `repeat`, `gizmo`, `capture`, `store`, `material` | 512 | 7 | 0 |
| `WindowBeams` | organ: architectural part | route/rail shaping, mesh surgery, attribute memory, instancing/scatter, branching/zones | `capture`, `store`, `material` | 63 | 1 | 1 |
| `WindowFromEdges` | composer: architecture | route/rail shaping, mesh surgery, edge/face queries, attribute memory, instancing/scatter | `capture`, `store`, `asset`, `material` | 164 | 1 | 1 |
| `WindowInnerPattern` | organ: architectural part | route/rail shaping, mesh surgery, edge/face queries, attribute memory, instancing/scatter | `repeat`, `capture` | 137 | 0 | 1 |
| `WindowWalls` | composer: architecture | route/rail shaping, mesh surgery, edge/face queries, attribute memory, instancing/scatter | `foreach`, `gizmo`, `capture`, `store`, `material` | 141 | 4 | 4 |
| `Wooden Bridge` | composer: architecture | route/rail shaping, mesh surgery, edge/face queries, attribute memory, instancing/scatter | `foreach`, `gizmo`, `capture`, `store`, `material` | 181 | 1 | 0 |
| `WrapGeometryToCurve` | composer: prop/resource | route/rail shaping, instancing/scatter, branching/zones, orientation math | `menu`, `asset` | 43 | 0 | 2 |

## Complete Node-Type Inventory

| Count | Node type | Family |
| ---: | --- | --- |
| 2379 | `NodeReroute` | `authoring_controls` |
| 1869 | `ShaderNodeMath` | `coordinate_math` |
| 1299 | `ShaderNodeVectorMath` | `coordinate_math` |
| 1063 | `NodeGroupInput` | `authoring_controls` |
| 844 | `NodeFrame` | `authoring_controls` |
| 715 | `ShaderNodeCombineXYZ` | `coordinate_math` |
| 667 | `GeometryNodeSetPosition` | `position_fields` |
| 503 | `GeometryNodeInputPosition` | `position_fields` |
| 461 | `FunctionNodeCompare` | `coordinate_math` |
| 431 | `GeometryNodeViewer` | `authoring_controls` |
| 369 | `FunctionNodeBooleanMath` | `coordinate_math` |
| 316 | `GeometryNodeDeleteGeometry` | `topology_mutation` |
| 303 | `GeometryNodeJoinGeometry` | `topology_mutation` |
| 273 | `GeometryNodeGroup` | `authoring_controls` |
| 271 | `FunctionNodeRandomValue` | `random_inputs` |
| 263 | `GeometryNodeStoreNamedAttribute` | `attribute_memory` |
| 262 | `GeometryNodeInputIndex` | `position_fields` |
| 262 | `ShaderNodeSeparateXYZ` | `coordinate_math` |
| 259 | `GeometryNodeCaptureAttribute` | `attribute_memory` |
| 257 | `GeometryNodeExtrudeMesh` | `topology_mutation` |
| 236 | `GeometryNodeSetMaterial` | `material_finish` |
| 154 | `GeometryNodeInstanceOnPoints` | `instances_scatter` |
| 135 | `GeometryNodeSampleIndex` | `attribute_memory` |
| 134 | `GeometryNodeRealizeInstances` | `instances_scatter` |
| 130 | `GeometryNodeFieldOnDomain` | `attribute_memory` |
| 122 | `ShaderNodeValue` | `input_constants` |
| 118 | `GeometryNodeSwitch` | `control_flow` |
| 115 | `GeometryNodeGizmoLinear` | `authoring_controls` |
| 114 | `GeometryNodeInputNormal` | `position_fields` |
| 108 | `NodeGroupOutput` | `authoring_controls` |
| 98 | `GeometryNodeCurveToMesh` | `curve_rails` |
| 92 | `GeometryNodeInputNamedAttribute` | `attribute_memory` |
| 90 | `NodeSeparateBundle` | `control_flow` |
| 85 | `GeometryNodeSetShadeSmooth` | `material_finish` |
| 83 | `GeometryNodeResampleCurve` | `curve_rails` |
| 80 | `GeometryNodeMeshToCurve` | `curve_rails` |
| 78 | `GeometryNodeTransform` | `instances_scatter` |
| 72 | `GeometryNodeProximity` | `position_fields` |
| 68 | `FunctionNodeAxesToRotation` | `rotation_matrix_math` |
| 68 | `GeometryNodeFlipFaces` | `topology_mutation` |
| 66 | `ShaderNodeMapRange` | `coordinate_math` |
| 65 | `GeometryNodeIndexSwitch` | `control_flow` |
| 64 | `GeometryNodeMeshCube` | `mesh_seeds` |
| 60 | `GeometryNodeRepeatInput` | `control_flow` |
| 60 | `GeometryNodeRepeatOutput` | `control_flow` |
| 59 | `GeometryNodeMergeByDistance` | `topology_mutation` |
| 55 | `GeometryNodeInputMeshEdgeVertices` | `topology_query` |
| 53 | `FunctionNodeRotateVector` | `rotation_matrix_math` |
| 50 | `GeometryNodeCurvePrimitiveLine` | `curve_rails` |
| 49 | `ShaderNodeMix` | `coordinate_math` |
| 47 | `GeometryNodeSelfObject` | `position_fields` |
| 47 | `GeometryNodeDistributePointsOnFaces` | `instances_scatter` |
| 46 | `GeometryNodeCurvePrimitiveCircle` | `curve_rails` |
| 45 | `GeometryNodeObjectInfo` | `instances_scatter` |
| 45 | `GeometryNodeInputTangent` | `position_fields` |
| 42 | `GeometryNodeSplineParameter` | `curve_rails` |
| 39 | `FunctionNodeAlignRotationToVector` | `rotation_matrix_math` |
| 35 | `GeometryNodeAttributeDomainSize` | `topology_query` |
| 30 | `GeometryNodeMeshToPoints` | `instances_scatter` |
| 30 | `GeometryNodeBoundBox` | `position_fields` |
| 30 | `GeometryNodeCurveToPoints` | `curve_rails` |
| 28 | `ShaderNodeTexNoise` | `material_finish` |
| 25 | `NodeCombineBundle` | `control_flow` |
| 25 | `GeometryNodeMeshCircle` | `mesh_seeds` |
| 24 | `GeometryNodeMeshGrid` | `mesh_seeds` |
| 22 | `GeometryNodeMeshLine` | `mesh_seeds` |
| 21 | `GeometryNodeMenuSwitch` | `control_flow` |
| 21 | `GeometryNodeMaterialSelection` | `material_finish` |
| 21 | `GeometryNodeAttributeStatistic` | `attribute_memory` |
| 19 | `GeometryNodeRemoveAttribute` | `attribute_memory` |
| 18 | `GeometryNodeScaleElements` | `topology_mutation` |
| 16 | `FunctionNodeRotateRotation` | `rotation_matrix_math` |
| 16 | `GeometryNodeCollectionInfo` | `instances_scatter` |
| 15 | `GeometryNodeCurveLength` | `curve_rails` |
| 14 | `GeometryNodeForeachGeometryElementInput` | `control_flow` |
| 14 | `GeometryNodeForeachGeometryElementOutput` | `control_flow` |
| 13 | `NodeEvaluateClosure` | `control_flow` |
| 13 | `GeometryNodeInputID` | `position_fields` |
| 12 | `NodeClosureInput` | `control_flow` |
| 12 | `NodeClosureOutput` | `control_flow` |
| 12 | `GeometryNodeMeshCylinder` | `topology_mutation` |
| 12 | `ShaderNodeVectorRotate` | `rotation_matrix_math` |
| 11 | `GeometryNodeGizmoDial` | `authoring_controls` |
| 11 | `GeometryNodeSubdivideMesh` | `topology_mutation` |
| 11 | `ShaderNodeClamp` | `coordinate_math` |
| 10 | `FunctionNodeInputInt` | `input_constants` |
| 10 | `FunctionNodeEulerToRotation` | `rotation_matrix_math` |
| 10 | `FunctionNodeAxisAngleToRotation` | `rotation_matrix_math` |
| 10 | `GeometryNodeRaycast` | `instances_scatter` |
| 9 | `GeometryNodeFillCurve` | `curve_rails` |
| 9 | `GeometryNodeFieldAtIndex` | `attribute_memory` |
| 8 | `GeometryNodeMeshUVSphere` | `topology_mutation` |
| 8 | `FunctionNodeInvertRotation` | `rotation_matrix_math` |
| 7 | `GeometryNodeCurveArc` | `curve_rails` |
| 7 | `FunctionNodeInputVector` | `input_constants` |
| 7 | `GeometryNodeSampleNearest` | `instances_scatter` |
| 7 | `GeometryNodeEdgesOfVertex` | `topology_query` |
| 7 | `GeometryNodeInputMeshEdgeAngle` | `topology_query` |
| 6 | `ShaderNodeFloatCurve` | `coordinate_math` |
| 6 | `GeometryNodeInputCollection` | `instances_scatter` |
| 6 | `FunctionNodeSeparateMatrix` | `rotation_matrix_math` |
| 5 | `FunctionNodeCombineTransform` | `rotation_matrix_math` |
| 5 | `GeometryNodePointsOfCurve` | `topology_query` |
| 5 | `GeometryNodeCornersOfEdge` | `topology_query` |
| 5 | `GeometryNodeSampleCurve` | `curve_rails` |
| 4 | `FunctionNodeSeparateColor` | `color_material` |
| 4 | `GeometryNodeReverseCurve` | `curve_rails` |
| 4 | `GeometryNodeCurveEndpointSelection` | `curve_rails` |
| 4 | `FunctionNodeIntegerMath` | `input_constants` |
| 4 | `FunctionNodeCombineMatrix` | `rotation_matrix_math` |
| 3 | `GeometryNodeMeshIcoSphere` | `topology_mutation` |
| 3 | `GeometryNodeSubdivisionSurface` | `topology_mutation` |
| 3 | `FunctionNodeInputRotation` | `input_constants` |
| 3 | `GeometryNodeVertexOfCorner` | `topology_query` |
| 3 | `GeometryNodeFaceOfCorner` | `topology_query` |
| 3 | `FunctionNodeTransformDirection` | `rotation_matrix_math` |
| 2 | `FunctionNodeCombineColor` | `color_material` |
| 2 | `GeometryNodeSampleNearestSurface` | `instances_scatter` |
| 2 | `GeometryNodeConvexHull` | `topology_mutation` |
| 2 | `GeometryNodeMeshBoolean` | `topology_mutation` |
| 2 | `FunctionNodeInvertMatrix` | `rotation_matrix_math` |
| 2 | `GeometryNodeSetMeshNormal` | `topology_mutation` |
| 2 | `GeometryNodeOffsetCornerInFace` | `topology_query` |
| 2 | `GeometryNodeInputMeshIsland` | `topology_query` |
| 2 | `GeometryNodeUVUnwrap` | `material_finish` |
| 2 | `GeometryNodeInputRadius` | `position_fields` |
| 2 | `GeometryNodeSetCurveRadius` | `curve_rails` |
| 2 | `FunctionNodeInputBool` | `input_constants` |
| 2 | `GeometryNodeInputSceneTime` | `position_fields` |
| 1 | `GeometryNodeInputMeshVertexNeighbors` | `topology_query` |
| 1 | `GeometryNodeSplineLength` | `curve_rails` |
| 1 | `ShaderNodeTexVoronoi` | `color_material` |
| 1 | `GeometryNodeSetCurveTilt` | `curve_rails` |
| 1 | `GeometryNodeSetInstanceTransform` | `rotation_matrix_math` |
| 1 | `FunctionNodeTransformPoint` | `rotation_matrix_math` |
| 1 | `GeometryNodeInputSplineCyclic` | `curve_rails` |
| 1 | `FunctionNodeMatrixMultiply` | `rotation_matrix_math` |
| 1 | `FunctionNodeQuaternionToRotation` | `rotation_matrix_math` |

## Reading Order Now That Every Node Is Accounted For

1. Utility leaves: `Is Edge Manifold`, `Select Original Geometry After Edge Extrude`, `ShouldAutoSmooth`, `Curve Root`, `Curve Tip`, `Random Rotation`, `GetPositionBasedSeed`, and roof/menu routers.
2. Organ chains: `GenerateArc`, `DoorTileFromArc`, `WindowInnerPattern`, `Generate Windows`, `GenerateWindowsFromEdges`, `RailsFromEdge`, `Gothic SupportColumn From EDge`, `GenerateTerrace`, `MakeStairs`, `Fence Type A`, `StonesOnSurface`.
3. Composer roots: house, tower, church, gate, wall, bridge, terrain, vegetation, river, and set-dressing groups only after their utilities and organs have behavioral harnesses.
4. Toolchain targets: repeat/foreach/gizmo/closure graphs when the goal is to teach Geometry Script the missing grammar instead of dodging it.

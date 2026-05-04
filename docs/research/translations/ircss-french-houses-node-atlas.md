# IRCSS French Houses Node Atlas

This accounts for every `GeometryNodeTree` in `experiments/source-blends/ircss-french-houses.blend` as inspected by Blender 5.1.1. It is an atlas, not an accepted translation set: each entry says what the graph appears to do, how it participates in the scene, and what kind of translation pressure it applies.

## Coverage

- Node group datablocks: 108 (107 unique names; duplicate names are disambiguated with `[n]`).
- Modifier-root groups: 63. Nested-only helpers: 45.
- Dependency edges: 163 distinct caller-to-callee names, 273 group-node references.
- Feature tags: `repeat`, `foreach`, `gizmo`, and `closure` are toolchain-pressure tags; `capture` and `store_attr` mark explicit attribute flow; `collection_info`, `object_info`, and `material` mark Blender datablock coupling.

## Patterns After Reading All Groups

- The file is a town-kit board, not one master city generator. Modifier roots build houses, church pieces, walls, bridges, terrain, vegetation, river banks, props, and resource examples; Blender object placement composes the final view.
- The architecture stack is layered: selection and curve utilities feed trim organs; trim organs feed facade and roof composers; composers become placed scene objects. Translation should follow that direction instead of trying to swallow a building root whole.
- Attribute flow is not optional bookkeeping here. Captures and stored named attributes carry edge identity, side selection, roof state, window placement, and scatter masks between graph phases.
- The artist uses repeat/foreach/gizmo/closure machinery as shape grammar controls: loops grow rows, enumerate facade pieces, expose handles, and package reusable calculations. Geometry Script needs direct support or deliberate Python-side orchestration for those patterns.
- Collections, Object Info nodes, and material assignments make the scene hybrid. Python should own asset binding, modifier setup, variants, and evidence extraction while Geometry Script owns the inspectable procedural graph body.

## Translation Ladder

Read the atlas from the bottom of the dependency tree upward:

1. Translate tiny utilities first: manifold tests, roof switches, curve facts,
   random seed helpers, smoothing, and projection. These are the measuring
   tools. If they lie, every facade built on them lies with confidence.
2. Translate organs next: arcs, windows, rails, doors, stairs, roof caps,
   columns, banners, stones, fences, and terrain scatter. These are reusable
   shape verbs: bend this edge into an arch, dress this wall, populate this
   surface, grow this cap.
3. Translate composers after their organs are accepted: houses, towers, church
   fronts, gates, walls, bridges, cliffs, river banks, fields, trees, and
   stalls. These should become orchestration graphs plus exposed controls, not
   giant opaque scripture.
4. Leave repeat/foreach/gizmo/closure-heavy graphs as explicit toolchain
   targets unless their behavior can be isolated. Those nodes are not noise;
   they are the authoring grammar of the file.

## Feature Counts

- `capture`: 66
- `store_attr`: 61
- `material`: 58
- `repeat`: 35
- `gizmo`: 31
- `menu`: 17
- `object_info`: 16
- `collection_info`: 13
- `foreach`: 9
- `closure`: 7

## Atlas

### ArcsFromEdges

- Role: architectural organ or trim helper.
- Scale: 209 nodes, 264 links; dominant nodes: NodeReroute x35, Math x21, CombineXYZ x12, Viewer x11.
- Interface: inputs `Geometry`, `TotalHeight`, `ArcProportion`, `ArcPadToEdge`, `DecorRes`, `ArcIndentIn`, `ArcIndentDepth`, `ArcBendExponent`, +3; outputs `Arcs`, `InnerSideOfExtrude`, `JustTheTips`, `tipFirstEdgePosition`, `justInnerBase`, `firstBottomEdgePosition`.
- Scene use: modifier users none; object collections none.
- Graph links: calls `ProjectOnCoordinate`; called by `ChurchFrontTowers`, `GenerateWindowsFromEdges`, `WindowWalls`.
- Signals: `repeat`, `gizmo`, `capture`, `store_attr`; frames `get the top of the arc`, `The extend hegiht`, `the arc hegiht`, `Get edge info`, `Get the middle point`, +5.
- Translation posture: toolchain-pressure candidate: understand structurally first, translate after zone/gizmo/closure support is explicit.

### Banner

- Role: root scene asset generator.
- Scale: 51 nodes, 70 links; dominant nodes: Math x11, NodeReroute x9, NodeGroupInput x5, CombineXYZ x5.
- Interface: inputs `BeamColor`, `IndentationResolution`, `ApplyWind`, `FlagColor`, `DistanceBetweenLoops`, `VerticalPoleHeight`, `FrontOffset`, `TipWidth`, +3; outputs `Geometry`.
- Scene use: modifier users `Banner`; object collections SetDressing x1.
- Evaluated roots: Banner: 131v/102p.
- Graph links: calls `Pole`, `Flag`; called by none.
- Signals: `gizmo`, `capture`, `store_attr`, `object_info`, `material`; frames none.
- Asset bindings: objects `?`; materials `FlatColorWithGeometryInputFlag`; color sockets `BeamColor`, `FlagColor`.
- Translation posture: toolchain-pressure candidate: understand structurally first, translate after zone/gizmo/closure support is explicit.

### BannerTypeFour

- Role: root scene asset generator.
- Scale: 70 nodes, 89 links; dominant nodes: Math x12, NodeReroute x11, NodeGroupInput x9, CombineXYZ x6.
- Interface: inputs `BeamColor`, `IndentationResolution`, `ApplyWind`, `FlagColor`, `DistanceBetweenLoops`, `VerticalPoleHeight`, `FrontOffset`, `TipWidth`, +5; outputs `Geometry`.
- Scene use: modifier users `BannerTypeTwo`; object collections SetDressing x1.
- Evaluated roots: BannerTypeTwo: 251v/214p.
- Graph links: calls `Pole x2`, `Flag`; called by none.
- Signals: `capture`, `store_attr`, `object_info`, `material`; frames none.
- Asset bindings: objects `?`; materials `FlatColorWithGeometryInputFlag`, `Beam`; color sockets `BeamColor`, `FlagColor`.
- Translation posture: composite helper: translate callees before treating this as accepted behavior.

### BannerTypeThree

- Role: root scene asset generator.
- Scale: 58 nodes, 85 links; dominant nodes: Math x11, NodeReroute x7, NodeGroupInput x6, CombineXYZ x6.
- Interface: inputs `BeamColor`, `IndentationResolution`, `ApplyWind`, `FlagColor`, `DistanceBetweenLoops`, `VerticalPoleHeight`, `FrontOffset`, `TipWidth`, +5; outputs `Geometry`.
- Scene use: modifier users `BannerTypeOne`; object collections SetDressing x1.
- Evaluated roots: BannerTypeOne: 244v/191p.
- Graph links: calls `Pole x2`, `Flag x2`; called by none.
- Signals: `capture`, `store_attr`, `object_info`, `material`; frames none.
- Asset bindings: objects `?`; materials `FlatColorWithGeometryInputFlag`; color sockets `BeamColor`, `FlagColor`.
- Translation posture: composite helper: translate callees before treating this as accepted behavior.

### ChurchA-Front

- Role: root architectural composer.
- Scale: 475 nodes, 584 links; dominant nodes: NodeReroute x62, Math x48, NodeGroupInput x37, CombineXYZ x27.
- Interface: inputs `DimensionX`, `DimensionY`, `FirstFloorHeight`, `DoorNormalizedHeight`, `DoorOffset`, `DoorIndentationOffset`, `SideDecorWidth`, `FrontPeakHeight`, +18; outputs `Geometry`.
- Scene use: modifier users `BuildA-Front`; object collections Church x1.
- Evaluated roots: BuildA-Front: 31127v/22010p.
- Graph links: calls `Switch On Roof Type x3`, `Reroute x2`, `Gothic SupportColumn From EDge x2`, `RailsFromEdge x2`, `ResampleEdgesAndSpawnWindowedWalld x2`, `GenerateMedialAxisRectangleTopology`, `Is Edge Manifold`, +1; called by `GenerateChurchBuildingB`.
- Signals: `repeat`, `foreach`, `gizmo`, `menu`, `capture`, `store_attr`, `material`; frames `Get foundation baisic shape`, `save the major corners, front left, right back`, `Get just the front`, `Get middle vertices`, `determine middle arcs lenght`, +12.
- Asset bindings: materials `GroundFloorWalls`, `Roof`; color sockets `RoofColor`, `DoorColor`.
- Translation posture: toolchain-pressure candidate: understand structurally first, translate after zone/gizmo/closure support is explicit.

### ChurchFrontTowers

- Role: root architectural composer.
- Scale: 792 nodes, 990 links; dominant nodes: VectorMath x83, NodeReroute x82, Math x79, CombineXYZ x37.
- Interface: inputs `FoundationX`, `FoundataionY`, `SupportBeamWidthMultiplier`, `BeamPushTendence`, `supportBeamDepth`, `TowerFirstPartHegiht`, `FoundationMultiplier`, `MiddleFloorsHeight`, +12; outputs `Geometry`.
- Scene use: modifier users `Tower-Front`; object collections Church x1.
- Evaluated roots: Tower-Front: 11604v/8126p.
- Graph links: calls `Switch On Roof Type x5`, `ColumeDecoFromEdges x4`, `ArcsFromEdges x3`, `Gothic SupportColumn From EDge`, `Curve Info`, `Curve Tip`, `Curve Root`, +1; called by `Geometry Nodes.002`.
- Signals: `repeat`, `foreach`, `gizmo`, `closure`, `menu`, `capture`, `store_attr`, `material`; frames `Main Support Beams`, `Create Foundation`, `Lower Foundation Section`, `Middle Florrs`, `Upper Part`, +10.
- Asset bindings: materials `GroundFloorWalls`, `RoundWindwos`, `Roof`, `Copper`, `FakeRoof`; color sockets `RoofColor`.
- Translation posture: toolchain-pressure candidate: understand structurally first, translate after zone/gizmo/closure support is explicit.

### Color in Range

- Role: nested helper.
- Scale: 7 nodes, 12 links; dominant nodes: SeparateColor x2, NodeGroupOutput x1, NodeGroupInput x1, RandomValue x1.
- Interface: inputs `Color A`, `Color B`, `ID`, `Seed`; outputs `Result`.
- Scene use: modifier users none; object collections none.
- Graph links: calls none; called by `HousesOnCurves`, `Tree On Geo Points`.
- Signals: none; frames none.
- Asset bindings: color sockets `Result`, `Color A`, `Color B`.
- Translation posture: leaf candidate: suitable for behavioral harness if source output is non-empty.

### ColumeDecoFromEdges

- Role: root scene asset generator.
- Scale: 114 nodes, 139 links; dominant nodes: NodeReroute x17, NodeGroupInput x10, Math x9, VectorMath x9.
- Interface: inputs `Geometry`, `Height`, `FlipEdge`, `BaseOutDendent`, `DecoInIndendt`, `ArcPropotion`, `BaseMultiplier`, `ColumnWidthMultiplier`; outputs `Geometry`, `IsTheInnerExtrudeedFace`.
- Scene use: modifier users `ColumnDecoFromEdges`; object collections Resources x1.
- Evaluated roots: ColumnDecoFromEdges: 35v/28p.
- Graph links: calls none; called by `ChurchFrontTowers`, `Generate Gothic Square Tower`.
- Signals: `capture`, `store_attr`, `material`; frames `ReorderMesh`, `generate arc shape`.
- Asset bindings: materials `GroundFloorWalls`.
- Translation posture: medium helper: inspect frames and attributes before translation.

### Corn  From Point

- Role: nested helper.
- Scale: 209 nodes, 253 links; dominant nodes: NodeReroute x32, Math x25, SetPosition x13, InputPosition x13.
- Interface: inputs `Points`, `Seed`, `Direction`, `Detail Type`; outputs `Instances`.
- Scene use: modifier users none; object collections none.
- Graph links: calls none; called by `Distribute Corn`.
- Signals: `capture`, `store_attr`, `material`; frames none.
- Asset bindings: materials `Greenery`, `Corn`.
- Translation posture: medium helper: inspect frames and attributes before translation.

### CreateDiagonalBeams

- Role: architectural organ or trim helper.
- Scale: 26 nodes, 32 links; dominant nodes: VectorMath x6, NodeReroute x5, InputPosition x2, JoinGeometry x2.
- Interface: inputs `Up`, `Right`, `WindowSupportBase`, `GeneralSekeletonBase`, `Seed`; outputs `Instances`.
- Scene use: modifier users none; object collections none.
- Graph links: calls none; called by `GenerateHouse`.
- Signals: `capture`; frames `Make beams end point`.
- Translation posture: leaf candidate: suitable for behavioral harness if source output is non-empty.

### CreateGate

- Role: root architectural composer.
- Scale: 1081 nodes, 1234 links; dominant nodes: Math x195, NodeReroute x112, NodeFrame x71, CombineXYZ x71.
- Interface: inputs `Geometry`, `FoundationDimension`, `FoundationHeight`, `GateMaxRadius`, `MaxGateHeight`, `BeamColor`, `RoofColor`, `PaintCOlor`, +10; outputs `Geometry`.
- Scene use: modifier users `Gate`; object collections WallsAndBridgets x1.
- Evaluated roots: Gate: 43642v/40323p.
- Graph links: calls `DoorTileFromArc x3`, `Is Edge Manifold x3`, `Spawn Normals on faces x2`, `GenerateUpperWindowWithAlcove x2`, `GetSteppeddirectionFrom position x2`, `StonesOnSurface`, `GenerateMedialAxisRectangleTopology`; called by none.
- Signals: `repeat`, `gizmo`, `closure`, `capture`, `store_attr`, `material`; frames `calculate gate width`, `calculate rest`, `get the outer edges`, `Filter Top part`, `Construct topology for window`, +55.
- Asset bindings: materials `BeamFakeTextureVertical`, `GroundFloorWalls`, `Roof`, `Beam`; color sockets `BeamColor`, `RoofColor`, `PaintCOlor`.
- Translation posture: toolchain-pressure candidate: understand structurally first, translate after zone/gizmo/closure support is explicit.

### Curve Info

- Role: utility, selection, or attribute helper.
- Scale: 19 nodes, 18 links; dominant nodes: Group x4, FieldOnDomain x3, FieldAtIndex x2, VectorMath x2.
- Interface: inputs none; outputs `Curve Index`, `Curve ID`, `Length`, `Direction`, `Random`, `Surface UV`.
- Scene use: modifier users none; object collections none.
- Graph links: calls `Curve Root x3`, `Curve Tip`; called by `ChurchFrontTowers`, `Fence Type A`, `Generate Windows`, `GenerateHouse`, `Make Pumpkin From Points`, `WindMill`, `WindowBeams`.
- Signals: none; frames `ID per Curve`.
- Translation posture: composite helper: translate callees before treating this as accepted behavior.

### Curve Root

- Role: utility, selection, or attribute helper.
- Scale: 10 nodes, 11 links; dominant nodes: FieldOnDomain x3, FieldAtIndex x2, InputPosition x1, InputTangent x1.
- Interface: inputs none; outputs `Root Selection`, `Root Position`, `Root Direction`, `Root Index`.
- Scene use: modifier users none; object collections none.
- Graph links: calls none; called by `ChurchFrontTowers`, `Curve Info`.
- Signals: none; frames none.
- Translation posture: leaf candidate: suitable for behavioral harness if source output is non-empty.

### Curve Tip

- Role: utility, selection, or attribute helper.
- Scale: 10 nodes, 11 links; dominant nodes: FieldOnDomain x3, FieldAtIndex x2, InputPosition x1, InputTangent x1.
- Interface: inputs none; outputs `Tip Selection`, `Tip Position`, `Tip Direction`, `Tip Index`.
- Scene use: modifier users none; object collections none.
- Graph links: calls none; called by `ChurchFrontTowers`, `Curve Info`, `Generate Windows`, `ResampleEdgesAndSpawnWindowedWalld`.
- Signals: none; frames none.
- Translation posture: leaf candidate: suitable for behavioral harness if source output is non-empty.

### CurvedDoorFromEdges

- Role: root scene asset generator.
- Scale: 182 nodes, 242 links; dominant nodes: NodeReroute x32, Math x23, VectorMath x13, CombineXYZ x11.
- Interface: inputs `Geometry`, `Seed`, `Reverse`, `Side Padding Normalized`, `TileHeight`, `FlattenTop`, `DoorDepth`, `DoorHeightNormalized`; outputs `Geometry`.
- Scene use: modifier users `CurveDoorFromEdge`; object collections Resources x1.
- Evaluated roots: CurveDoorFromEdge: 320v/196p.
- Graph links: calls none; called by `WindMill`.
- Signals: `capture`, `store_attr`, `material`; frames `Sort edge orders`.
- Asset bindings: materials `FakeWoodTextureWithUV`, `GroundFloorWalls`.
- Translation posture: composer candidate: translate by organs and assets first, then rebuild orchestration.

### DistancingType

- Role: nested helper.
- Scale: 3 nodes, 6 links; dominant nodes: NodeGroupInput x1, NodeGroupOutput x1, MenuSwitch x1.
- Interface: inputs `Menu`, `EqualDistance`, `Receeding`; outputs `Output`, `EqualDistance`, `Receeding`.
- Scene use: modifier users none; object collections none.
- Graph links: calls none; called by `GenerateChurchBuildingB`.
- Signals: `menu`; frames none.
- Translation posture: leaf candidate: suitable for behavioral harness if source output is non-empty.

### Distribute Corn

- Role: root scene asset generator.
- Scale: 18 nodes, 22 links; dominant nodes: NodeGroupInput x4, Group x2, InputPosition x2, NodeGroupOutput x1.
- Interface: inputs `Geometry`, `Seed`, `DirectionAngle`, `Height`, `Density Factor`, `Snap To Surface`, `Snap To Geometry`; outputs `Geometry`.
- Scene use: modifier users `Wheat.001`; object collections Farms x1.
- Evaluated roots: Wheat.001: 13866v/10930p.
- Graph links: calls `Corn  From Point`, `Wind On Plants`; called by none.
- Signals: `capture`, `object_info`; frames none.
- Asset bindings: objects `?`.
- Translation posture: composite helper: translate callees before treating this as accepted behavior.

### Distribute Sunflower

- Role: root scene asset generator.
- Scale: 23 nodes, 27 links; dominant nodes: NodeGroupInput x5, Group x2, CombineXYZ x2, NodeReroute x2.
- Interface: inputs `Geometry`, `Seed`, `DirectionAngle`, `Height`, `Density Factor`, `Snap To Surface`, `Snap To Geometry`; outputs `Geometry`.
- Scene use: modifier users `SunFlowers`; object collections Farms x1.
- Evaluated roots: SunFlowers: 2412v/2010p.
- Graph links: calls `Sun Flowers From Points`, `Wind On Plants`; called by none.
- Signals: `gizmo`, `capture`, `object_info`; frames none.
- Asset bindings: objects `?`.
- Translation posture: toolchain-pressure candidate: understand structurally first, translate after zone/gizmo/closure support is explicit.

### Distribute Wheat

- Role: root scene asset generator.
- Scale: 19 nodes, 23 links; dominant nodes: NodeGroupInput x5, Group x2, InputPosition x2, NodeGroupOutput x1.
- Interface: inputs `Geometry`, `Seed`, `DirectionAngle`, `Height`, `Density Factor`, `Detail Type`, `Snap To Surface`, `Snap To Geometry`; outputs `Geometry`.
- Scene use: modifier users `Wheat`; object collections Farms x1.
- Evaluated roots: Wheat: 11748v/7746p.
- Graph links: calls `Wheat From Point`, `Wind On Plants`; called by none.
- Signals: `capture`, `object_info`; frames none.
- Asset bindings: objects `?`.
- Translation posture: composite helper: translate callees before treating this as accepted behavior.

### DomaTower

- Role: root architectural composer.
- Scale: 290 nodes, 366 links; dominant nodes: Math x49, NodeReroute x42, NodeGroupInput x25, VectorMath x16.
- Interface: inputs `FoundationX`, `FoundationY`, `LowerPartTiling`, `FirstPartHeight`, `DomeBaseHegiht`, `NumberOfMiddleFloors`, `AdjustHeightEveryNFloors`, `MiddleFoorDistributionRatio`, +9; outputs `Geometry`.
- Scene use: modifier users `Tower-Doma`; object collections Church x1.
- Evaluated roots: Tower-Doma: 59960v/41607p.
- Graph links: calls `PointWindowsFromEdges x2`, `PointyGothicCone x2`, `WindowWalls`, `Generate Gothic Square Tower`; called by `Geometry Nodes.002`.
- Signals: `repeat`, `gizmo`, `menu`, `capture`, `store_attr`, `material`; frames `Middle Floors`, `LastFloor`, `Get The Dome Base`.
- Asset bindings: materials `GroundFloorWalls`, `Copper`, `?`; material sockets `DomeMaterial`; color sockets `RoofColor`.
- Translation posture: toolchain-pressure candidate: understand structurally first, translate after zone/gizmo/closure support is explicit.

### DoorTileFromArc

- Role: root scene asset generator.
- Scale: 313 nodes, 379 links; dominant nodes: NodeReroute x45, Math x39, VectorMath x30, NodeFrame x25.
- Interface: inputs `Scale`, `ArcRadius`, `CenterLift`, `CenterLiftGamma`, `ArcExtendLength`, `DistanceBetweenInnergrid`, `SpawnBaseEdge`, `PadAroundArc`, +9; outputs `Geometry`, `InnerNet`.
- Scene use: modifier users `DoorTileFromArc`; object collections Resources x1.
- Graph links: calls `GetOnlySide Edges after Edge Extrude x2`, `ShouldAutoSmooth x2`, `Select Original Geometry After Edge Extrude x2`, `GenerateArc`; called by `CreateGate`, `Geometry Nodes`, `TownWall`.
- Signals: `repeat`, `store_attr`; frames `Get center`, `Center To Corner`, `Is Flipped?`, `mitered intersection`, `Position of the vertex of the next edge`, +18.
- Translation posture: toolchain-pressure candidate: understand structurally first, translate after zone/gizmo/closure support is explicit.

### EdgesToGates

- Role: root architectural composer.
- Scale: 11 nodes, 9 links; dominant nodes: StoreNamedAttribute x3, NodeGroupInput x1, NodeGroupOutput x1, Group x1.
- Interface: inputs `Geometry`; outputs `Geometry`.
- Scene use: modifier users `DoorsFromEdges`; object collections Resources x1.
- Evaluated roots: DoorsFromEdges: 1145v/1045p.
- Graph links: calls `Reroute`; called by none.
- Signals: `store_attr`; frames `A normal mesh might not have the edges ordered`.
- Translation posture: composite helper: translate callees before treating this as accepted behavior.

### Fence Type A

- Role: root scene asset generator.
- Scale: 167 nodes, 254 links; dominant nodes: Math x26, NodeReroute x21, NodeGroupInput x13, VectorMath x10.
- Interface: inputs `Geometry`, `Seed`, `Support beam density`, `Beam Height`, `Beam Thicknes`, `Number Of Inner Beams`, `Material`, `Color`, +7; outputs `Geometry`.
- Scene use: modifier users `Fence-A`; object collections Farms x1.
- Evaluated roots: Fence-A: 552v/414p.
- Graph links: calls `float to Rotation x2`, `Curve Info`; called by `Wooden Bridge`.
- Signals: `repeat`, `foreach`, `capture`, `store_attr`, `material`; frames none.
- Asset bindings: materials `Beam`; material sockets `Material`; color sockets `Color`.
- Translation posture: toolchain-pressure candidate: understand structurally first, translate after zone/gizmo/closure support is explicit.

### Flag

- Role: root scene asset generator.
- Scale: 244 nodes, 284 links; dominant nodes: Math x37, NodeReroute x30, NodeGroupInput x26, CombineXYZ x21.
- Interface: inputs `FrontOffset`, `TipWidth`, `MiddleLength`, `DistanceBetweenLoops`, `BaseWidthMultiplyer`, `ApplyWind`, `WindSeed`, `FlagColor`, +3; outputs `Geometry`.
- Scene use: modifier users `Flag`; object collections SetDressing x1.
- Evaluated roots: Flag: 49v/24p.
- Graph links: calls none; called by `Banner`, `BannerTypeFour`, `BannerTypeThree`.
- Signals: `repeat`, `gizmo`, `capture`, `store_attr`, `material`; frames `fitler the middle vertex`, `shape the tip pointness`, `determine tip width`, `Figure out the direction to put the vertex`, `case of first iteration`, +4.
- Asset bindings: materials `FlatColorWithGeometryInputFlag`; color sockets `FlagColor`.
- Translation posture: toolchain-pressure candidate: understand structurally first, translate after zone/gizmo/closure support is explicit.

### Float in Range

- Role: nested helper.
- Scale: 4 nodes, 6 links; dominant nodes: NodeGroupOutput x1, NodeGroupInput x1, RandomValue x1, SeparateXYZ x1.
- Interface: inputs `In Range`, `ID`, `Seed`; outputs `Value`.
- Scene use: modifier users none; object collections none.
- Graph links: calls none; called by `HousesOnCurves`, `Tree On Geo Points`.
- Signals: none; frames none.
- Translation posture: leaf candidate: suitable for behavioral harness if source output is non-empty.

### float to Rotation

- Role: nested helper.
- Scale: 13 nodes, 16 links; dominant nodes: Math x7, NodeGroupInput x2, NodeGroupOutput x1, EulerToRotation x1.
- Interface: inputs `factor-X`, `period`, `amplitude`, `Rotation Z Axis Modifier`; outputs `Rotation`.
- Scene use: modifier users none; object collections none.
- Graph links: calls none; called by `Fence Type A`.
- Signals: none; frames none.
- Translation posture: leaf candidate: suitable for behavioral harness if source output is non-empty.

### Generate Cliff Type 2

- Role: root terrain or dressing composer.
- Scale: 250 nodes, 294 links; dominant nodes: NodeGroupInput x37, VectorMath x34, Math x30, NodeReroute x21.
- Interface: inputs `Geometry`, `Base Height`, `Seed`, `Aditional Spawn`, `Scale`, `Spawn Density`, `Clustered Distribution`, `Collection to Spawn From`, +24; outputs `Geometry`.
- Scene use: modifier users `Cliff Type 2`, `Cliff Type 2.001`, `Cliff Type 2.002`; object collections RiverBank x2, Cliffs x1.
- Evaluated roots: Cliff Type 2: 13404v/7877p; Cliff Type 2.001: 5514v/3823p; Cliff Type 2.002: 4258v/3159p.
- Graph links: calls `Is Edge Manifold`, `Random Rotation`; called by none.
- Signals: `repeat`, `gizmo`, `capture`, `store_attr`, `collection_info`, `material`; frames `order vertecies`.
- Asset bindings: collections `Plants`; materials `Cliff2Top`, `Cliff2Walls`, `Cliff2Grass`; material sockets `Walls Material`, `Top Ground Materials`; color sockets `Wall Color One`, `Wall Color Two`, `Grass Color`.
- Translation posture: toolchain-pressure candidate: understand structurally first, translate after zone/gizmo/closure support is explicit.

### Generate Extruded DoorShape

- Role: architectural organ or trim helper.
- Scale: 180 nodes, 205 links; dominant nodes: NodeReroute x17, NodeFrame x16, RandomValue x15, SetPosition x13.
- Interface: inputs `Seed`, `DoorWidth`, `DoorHeight`, `Roof Geometry Type`; outputs `Geometry`.
- Scene use: modifier users none; object collections none.
- Graph links: calls `Switch On Roof Type x2`; called by `Generate Square Tower`, `Generate Tower`, `GenerateDoorsWithAlcove`.
- Signals: `capture`, `store_attr`, `material`; frames `Offset abit along normal to create iregularities`, `Save some per tile randomness for shading`, `Randomize Size`, `Get Baisic SHape`, `Extrude to the door shape`, +11.
- Asset bindings: materials `Beam`, `GroundFloorWalls`, `Roof`.
- Translation posture: composite helper: translate callees before treating this as accepted behavior.

### Generate Gothic Square Tower

- Role: architectural organ or trim helper.
- Scale: 238 nodes, 305 links; dominant nodes: NodeReroute x38, Math x24, VectorMath x19, Viewer x15.
- Interface: inputs `Foundation X`, `Foundation Y`, `Lower Part Tiling`, `Height`, `Make Only Half the Tower`; outputs `Geometry`.
- Scene use: modifier users none; object collections none.
- Graph links: calls `ColumeDecoFromEdges`, `RailsFromEdge`, `Gothic SupportColumn From EDge`; called by `ChurchA-Front`, `DomaTower`, `Tower Gothic Type 2`.
- Signals: `foreach`, `capture`, `material`; frames `Create Foundation`, `Base`.
- Asset bindings: materials `GroundFloorWalls`.
- Translation posture: toolchain-pressure candidate: understand structurally first, translate after zone/gizmo/closure support is explicit.

### Generate Square Tower

- Role: root architectural composer.
- Scale: 805 nodes, 877 links; dominant nodes: NodeReroute x112, NodeFrame x68, VectorMath x65, Math x48.
- Interface: inputs `Number Of Floors`, `Seed`, `BaseDepth`, `BaseWidth`, `RoofHeight`, `FirstFloorHeight`, `RoofColor`, `PaintColor`, +6; outputs `Mesh`.
- Scene use: modifier users `TowerOne.002`; object collections Towers x1.
- Evaluated roots: TowerOne.002: 13930v/16433p.
- Graph links: calls `Switch On Roof Type x9`, `GetPositionBasedSeed x3`, `GenerateUpperWindowWithAlcove x2`, `Generate Windows`, `Generate Extruded DoorShape`, `GenerateLightShaftExrudes`; called by none.
- Signals: `repeat`, `capture`, `store_attr`, `collection_info`, `object_info`, `material`; frames `Base Shape`, `Generate Ground Floor`, `Frame.002`, `Get location based random for ground floor Distortion`, `Spawn Ground Floor`, +53.
- Asset bindings: collections `?`; objects `?`; materials `GroundFloorWalls`, `UpperFloorsPaint`, `Beam`, `Roof`, `Copper`, +2; color sockets `RoofColor`, `PaintColor`, `BeamColor`.
- Translation posture: toolchain-pressure candidate: understand structurally first, translate after zone/gizmo/closure support is explicit.

### Generate Stones

- Role: root terrain or dressing composer.
- Scale: 47 nodes, 53 links; dominant nodes: NodeReroute x9, Math x6, CombineXYZ x4, VectorMath x3.
- Interface: inputs `Geometry`; outputs `Geometry`.
- Scene use: modifier users `Stone.001`; object collections Generator x1.
- Graph links: calls none; called by none.
- Signals: `repeat`, `material`; frames `Get a direction`, `Get how much to cut`.
- Asset bindings: materials `Stone`.
- Translation posture: toolchain-pressure candidate: understand structurally first, translate after zone/gizmo/closure support is explicit.

### Generate Tower

- Role: root architectural composer.
- Scale: 707 nodes, 754 links; dominant nodes: NodeReroute x72, VectorMath x70, NodeFrame x70, Math x59.
- Interface: inputs `Number Of Floors`, `Seed`, `BaseRadius`, `RoofHeight`, `FirstFloorHeight`, `RoofColor`, `PaintColor`, `BeamColor`, +9; outputs `Mesh`.
- Scene use: modifier users `TowerOne`, `TowerOne.001`; object collections Towers x2.
- Evaluated roots: TowerOne: 8344v/8346p; TowerOne.001: 10781v/10362p.
- Graph links: calls `Switch On Roof Type x5`, `GetPositionBasedSeed x3`, `GenerateUpperWindowWithAlcove x2`, `Generate Windows`, `Generate Extruded DoorShape`, `GenerateLightShaftExrudes`, `Round Bottom`; called by none.
- Signals: `repeat`, `capture`, `store_attr`, `collection_info`, `object_info`, `material`; frames `Base Shape`, `Generate Ground Floor`, `Frame.002`, `Get location based random for ground floor Distortion`, `Spawn Ground Floor`, +58.
- Asset bindings: collections `?`; objects `?`; materials `GroundFloorWalls`, `UpperFloorsPaint`, `Beam`, `Roof`, `Copper`, +2; color sockets `RoofColor`, `PaintColor`, `BeamColor`.
- Translation posture: toolchain-pressure candidate: understand structurally first, translate after zone/gizmo/closure support is explicit.

### Generate Windows

- Role: architectural organ or trim helper.
- Scale: 188 nodes, 205 links; dominant nodes: NodeFrame x19, Math x18, NodeReroute x16, NodeGroupInput x15.
- Interface: inputs `Points`, `Normal`, `Seed`, `Scale`, `RandomnessFactor`, `WidthCalculationType`, `WidthHardcodedValue`, `NoFlowerProbability`, +1; outputs `Instances`, `WindowBase`.
- Scene use: modifier users none; object collections none.
- Graph links: calls `Curve Tip`, `Curve Info`; called by `Generate Square Tower`, `Generate Tower`, `GenerateHouse`, `GenerateLightShaftExrudes`, `GenerateUpperWindowWithAlcove`.
- Signals: `menu`, `capture`, `store_attr`, `collection_info`, `material`; frames `Randomize the position abit`, `Deterimne Window Width`, `Determine Windows height`, `Construct right up coordinate system`, `Create windwo glass and save the edge ID for each side`, +14.
- Asset bindings: collections `?`; materials `WindowGlass`, `Beam`.
- Translation posture: composite helper: translate callees before treating this as accepted behavior.

### GenerateAlcoveWindows

- Role: root architectural composer.
- Scale: 14 nodes, 22 links; dominant nodes: StoreNamedAttribute x5, NodeGroupOutput x1, Group x1, SetPosition x1.
- Interface: inputs `Seed`, `RoofColor`, `PaintColor`, `BeamColor`, `AlcoveMaterial`, `WifthType`, `HardcodedWidth`, `Dpeth`, +2; outputs `Geometry`.
- Scene use: modifier users `WindowExample`, `WindowExample2`; object collections SetDressing x2.
- Evaluated roots: WindowExample: 280v/210p; WindowExample2: 96v/72p.
- Graph links: calls `GenerateUpperWindowWithAlcove`; called by none.
- Signals: `store_attr`; frames none.
- Asset bindings: material sockets `AlcoveMaterial`; color sockets `RoofColor`, `PaintColor`, `BeamColor`.
- Translation posture: composite helper: translate callees before treating this as accepted behavior.

### GenerateArc

- Role: root scene asset generator.
- Scale: 153 nodes, 174 links; dominant nodes: NodeReroute x28, VectorMath x17, NodeFrame x17, Math x16.
- Interface: inputs `Forward`, `Scale`, `Resolution`, `ArcRadius`, `CenterLift`, `CenterLiftGamma`, `ArcExtendLength`, `DistanceBetweenInnergrid`, +3; outputs `Geometry`, `InnerNet`.
- Scene use: modifier users `CreateArc`; object collections Resources x1.
- Evaluated roots: CreateArc: 19v/0p.
- Graph links: calls none; called by `DoorTileFromArc`, `Reroute`.
- Signals: `capture`, `store_attr`; frames `Construct coordinate system`, `Map gradient to center of the arc`, `visualize points indices`, `Move up so the pivot is on the ground`, `LeftEdge`, +12.
- Translation posture: medium helper: inspect frames and attributes before translation.

### GenerateBricks

- Role: root scene asset generator.
- Scale: 26 nodes, 28 links; dominant nodes: NodeReroute x6, Math x5, SetPosition x2, VectorMath x2.
- Interface: inputs `Geometry`; outputs `Geometry`.
- Scene use: modifier users `Bricks`; object collections Generator x1.
- Graph links: calls none; called by none.
- Signals: `repeat`, `material`; frames none.
- Asset bindings: materials `Stone`.
- Translation posture: toolchain-pressure candidate: understand structurally first, translate after zone/gizmo/closure support is explicit.

### GenerateChurchBuildingB

- Role: root architectural composer.
- Scale: 893 nodes, 1124 links; dominant nodes: NodeReroute x126, Math x90, NodeGroupInput x54, SetPosition x52.
- Interface: inputs `MiddleSectionDimension`, `FirstFloorHeight`, `Middle Section Building Type`, `Front Section Building Type`, `BackBuildingType`, `Number Of Upper Floors`, `UpperFloorIntrudeAmount`, `UpperFloorIndentType`, +15; outputs `Geometry`.
- Scene use: modifier users `BuildingB-sides`; object collections Church x1.
- Evaluated roots: BuildingB-sides: 36136v/26336p.
- Graph links: calls `Switch On Roof Type x9`, `DistancingType x4`, `ResampleEdgesAndSpawnWindowedWalld x3`, `Is Edge Manifold x3`, `Gothic SupportColumn From EDge x2`, `GenerateWindowsFromEdges x2`, `ChurchA-Front`, +1; called by `Geometry Nodes.002`.
- Signals: `repeat`, `gizmo`, `menu`, `capture`, `store_attr`, `material`; frames `Middle Section`, `Back`, `Front Section`, `Upper Floor Support Beam`, `Walls`, +12.
- Asset bindings: materials `Roof`, `GroundFloorWalls`, `RoundWindwos`; color sockets `RoofColor`.
- Translation posture: toolchain-pressure candidate: understand structurally first, translate after zone/gizmo/closure support is explicit.

### GenerateCover

- Role: root scene asset generator.
- Scale: 178 nodes, 194 links; dominant nodes: NodeReroute x26, VectorMath x17, NodeFrame x17, NodeGroupInput x12.
- Interface: inputs `Geometry`, `BaseHeight`, `RoofHeight`, `AmountToExrudeRoofIn`, `RoofColor`, `PaintColor`, `BeamColor`, `BeamType`, +2; outputs `Geometry`.
- Scene use: modifier users `RoofPavalion`, `RoofPavalion2`; object collections SetDressing x2.
- Evaluated roots: RoofPavalion: 2819v/2131p; RoofPavalion2: 2573v/1957p.
- Graph links: calls `GetBoundaryEdgeTangentAndNomral`; called by none.
- Signals: `menu`, `capture`, `store_attr`, `material`; frames `Deterimne Height`, `Move in to make base`, `Make top beam`, `Bringe the roof back to the outer edge`, `Make Top beam`, +12.
- Asset bindings: materials `Beam`, `Roof`, `BeamFakeTexture`, `?`; color sockets `RoofColor`, `PaintColor`, `BeamColor`.
- Translation posture: composite helper: translate callees before treating this as accepted behavior.

### GenerateDoorsWithAlcove

- Role: root scene asset generator.
- Scale: 10 nodes, 14 links; dominant nodes: StoreNamedAttribute x5, NodeGroupOutput x1, InputPosition x1, InputNormal x1.
- Interface: inputs `Seed`, `RoofColor`, `PaintColor`, `BeamColor`, `AlcoveMaterial`, `DoorWidth`, `DoorHeight`; outputs `Geometry`.
- Scene use: modifier users `DoorExample`, `DoorExample2`; object collections SetDressing x2.
- Evaluated roots: DoorExample: 276v/212p; DoorExample2: 340v/260p.
- Graph links: calls `Generate Extruded DoorShape`; called by none.
- Signals: `store_attr`; frames none.
- Asset bindings: material sockets `AlcoveMaterial`; color sockets `RoofColor`, `PaintColor`, `BeamColor`.
- Translation posture: composite helper: translate callees before treating this as accepted behavior.

### GenerateHouse

- Role: root architectural composer.
- Scale: 1023 nodes, 1075 links; dominant nodes: NodeReroute x144, NodeFrame x131, Math x88, VectorMath x55.
- Interface: inputs `Input`, `Object`, `Seed`, `NumberFloor`, `RoofCurvature`, `RoofColor`, `PaintColor`, `BeamCollor`, +5; outputs `Geometry`.
- Scene use: modifier users `examplePlane.004`, `HouseFour`, `HouseOne`, `HouseThree`, `HouseTWo`; object collections Houses x4.
- Evaluated roots: HouseFour: 61312v/44326p; HouseOne: 27919v/20003p; HouseThree: 52567v/38223p; HouseTWo: 25326v/18253p.
- Graph links: calls `GetPositionBasedSeed x7`, `Switch On Roof Type x5`, `Generate Windows x4`, `Curve Info x2`, `CreateDiagonalBeams x2`, `WindowBeams`, `Is Edge Manifold`; called by `HousesOnCurves`.
- Signals: `repeat`, `capture`, `store_attr`, `collection_info`, `object_info`, `material`; frames `extrude out first floor`, `Extude the base out wards so that we can pull up second floor`, `Deterime how much the first floor is extuded out`, `Extude out inbetween floors`, `Get just the base of the roof`, +116.
- Asset bindings: collections `?`; objects `?`; materials `Beam`, `GroundFloorWalls`, `UpperFloorsPaint`, `Roof`, `Greenery`, +1; color sockets `RoofColor`, `PaintColor`, `BeamCollor`.
- Translation posture: toolchain-pressure candidate: understand structurally first, translate after zone/gizmo/closure support is explicit.

### GenerateLightShaftExrudes

- Role: nested helper.
- Scale: 112 nodes, 111 links; dominant nodes: NodeReroute x13, VectorMath x12, NodeFrame x12, NodeGroupInput x9.
- Interface: inputs `Input`, `Seed`, `WindowScale`, `AlcoveMaterial`, `Normal`; outputs `Instances`.
- Scene use: modifier users none; object collections none.
- Graph links: calls `Generate Windows`; called by `Generate Square Tower`, `Generate Tower`.
- Signals: `capture`, `store_attr`, `material`; frames `So that we can work in local space`, `Deterimne Window Width`, `Get the back edge`, `Offset abit along normal to create iregularities`, `Save some per tile randomness for shading`, +4.
- Asset bindings: materials `UpperFloorsPaint`, `Roof`; material sockets `AlcoveMaterial`.
- Translation posture: composite helper: translate callees before treating this as accepted behavior.

### GenerateMedialAxisRectangleTopology

- Role: root scene asset generator.
- Scale: 119 nodes, 140 links; dominant nodes: NodeReroute x25, NodeFrame x15, VectorMath x14, Math x10.
- Interface: inputs `PlaneDimension`, `Resolution`, `MedialAxisWidth`, `X-Distort`, `Y-Distort`, `RidgeScaler`; outputs `Geometry`, `OuterRim`, `RidgeMesh`.
- Scene use: modifier users `MedialAxisRectangle`; object collections Resources x1.
- Graph links: calls none; called by `ChurchA-Front`, `CreateGate`, `Stall`.
- Signals: `repeat`, `capture`, `store_attr`; frames `figure out the longer axis`, `Get Edge Center`, `Get Edge Direction`, `Is it more right/left or front back`, `Check on edge`, +10.
- Translation posture: toolchain-pressure candidate: understand structurally first, translate after zone/gizmo/closure support is explicit.

### GenerateRockSlow

- Role: root scene asset generator.
- Scale: 94 nodes, 112 links; dominant nodes: NodeReroute x12, NodeGroupInput x9, SetPosition x9, StoreNamedAttribute x6.
- Interface: inputs `Geometry`, `Seed`, `Height`, `StoneColor`, `MossColor`, `CutFrom`, `StartingShape`, `RotateTheCuttingCubeRandomly`, +4; outputs `Geometry`.
- Scene use: modifier users `GenerateStoneSlow`; object collections landscape x1.
- Evaluated roots: GenerateStoneSlow: 154v/86p.
- Graph links: calls `Random Rotation`, `PCAGetLongAndShortAxis`; called by `GeneratorBoulders`.
- Signals: `repeat`, `gizmo`, `menu`, `store_attr`, `material`; frames `reset pivot to bottom`.
- Asset bindings: materials `Rock`; color sockets `StoneColor`, `MossColor`, `TopGrassColor`.
- Translation posture: toolchain-pressure candidate: understand structurally first, translate after zone/gizmo/closure support is explicit.

### GenerateStairCase

- Role: root scene asset generator.
- Scale: 53 nodes, 65 links; dominant nodes: VectorMath x6, NodeFrame x6, Compare x4, NodeGroupInput x4.
- Interface: inputs `Frequency`, `StairsWidth`, `Radius`, `Height`, `HeightRadiusGain`, `StairType`, `WallsType`, `GroundType`, +4; outputs `Geometry`.
- Scene use: modifier users `SpiralStairCase`, `SpiralStairCase.001`; object collections SetDressing x2.
- Evaluated roots: SpiralStairCase: 20280v/33250p; SpiralStairCase.001: 6076v/8897p.
- Graph links: calls `MakeStairs`, `GenerateTerrace`, `MakeSpiral`; called by none.
- Signals: `capture`; frames `Generate Spiral`, `Extrude out faces left and right`, `Get curve right alight with up`, `Add depth`, `Generate rails and base`, +1.
- Asset bindings: color sockets `BeamColor`.
- Translation posture: composite helper: translate callees before treating this as accepted behavior.

### GenerateTerrace

- Role: root scene asset generator.
- Scale: 150 nodes, 163 links; dominant nodes: NodeReroute x30, NodeFrame x13, NodeGroupInput x11, DeleteGeometry x8.
- Interface: inputs `Geometry`, `fenceMask`, `Seed`, `Dont Spawn Fence`, `WallsType`, `GroundType`, `RailMaterialType`, `BeamColor`, +3; outputs `Geometry`.
- Scene use: modifier users `Terrace`; object collections SetDressing x1.
- Evaluated roots: Terrace: 12188v/18928p.
- Graph links: calls `StonesOnSurface x2`, `GetPositionBasedSeed`, `Is Edge Manifold`; called by `GenerateStairCase`.
- Signals: `menu`, `capture`, `store_attr`, `collection_info`, `object_info`, `material`; frames `So that all the work we do is in local space`, `Decide what is wall and what is ground`, `Delete The base`, `Keep just the walls`, `Get only edges that have high curveture`, +8.
- Asset bindings: collections `?`; objects `?`; materials `GroundFloorWalls`, `Beam`; color sockets `BeamColor`.
- Translation posture: composite helper: translate callees before treating this as accepted behavior.

### GenerateUpperWindowWithAlcove

- Role: architectural organ or trim helper.
- Scale: 128 nodes, 136 links; dominant nodes: NodeReroute x14, NodeFrame x12, VectorMath x11, NodeGroupInput x10.
- Interface: inputs `Input`, `Seed`, `WindowHeight`, `AlcoveMaterial`, `Normal`, `WifthType`, `Dpeth`, `BackLift`, +3; outputs `Instances`.
- Scene use: modifier users none; object collections none.
- Graph links: calls `Switch On Roof Type x2`, `Generate Windows`; called by `CreateGate`, `Generate Square Tower`, `Generate Tower`, `GenerateAlcoveWindows`.
- Signals: `menu`, `capture`, `store_attr`, `material`; frames `So that we can work in local space`, `Deterimne Window Width`, `Get the back edge`, `Offset abit along normal to create iregularities`, `Save some per tile randomness for shading`, +4.
- Asset bindings: materials `UpperFloorsPaint`, `Roof`; material sockets `AlcoveMaterial`.
- Translation posture: composite helper: translate callees before treating this as accepted behavior.

### GenerateWindowsFromEdges

- Role: architectural organ or trim helper.
- Scale: 29 nodes, 40 links; dominant nodes: NodeReroute x12, SetMaterial x3, NodeGroupInput x2, Group x2.
- Interface: inputs `Geometry`, `TotalWallHeight`, `WindowArcProportion`, `ArcPadToEdge`, `ArcIndentIn`, `ArcIndentDepth`, `ArcBendExponent`, `FlattenTheTop`, +2; outputs `Geometry`.
- Scene use: modifier users none; object collections none.
- Graph links: calls `ArcsFromEdges`, `WindowInnerPattern`; called by `GenerateChurchBuildingB`, `WindowWalls`.
- Signals: `foreach`, `material`; frames `window height`.
- Asset bindings: materials `GroundFloorWalls`, `RoundWindwos`.
- Translation posture: toolchain-pressure candidate: understand structurally first, translate after zone/gizmo/closure support is explicit.

### GeneratorBoulders

- Role: root terrain or dressing composer.
- Scale: 16 nodes, 18 links; dominant nodes: NodeReroute x4, Math x3, MergeByDistance x1, RepeatInput x1.
- Interface: inputs `Geometry`; outputs `Geometry`.
- Scene use: modifier users `BouldersGeneartor`; object collections Generator x1.
- Graph links: calls `GenerateRockSlow`; called by none.
- Signals: `repeat`; frames none.
- Translation posture: toolchain-pressure candidate: understand structurally first, translate after zone/gizmo/closure support is explicit.

### Geometry Nodes

- Role: root scene asset generator.
- Scale: 355 nodes, 420 links; dominant nodes: NodeReroute x52, Math x38, VectorMath x24, NodeGroupInput x23.
- Interface: inputs `Geometry`, `BridgeSupportDensities`, `BridgeWidth`, `BridgeHegiht`, `OutsideColor`, `InsideColor`, `StoneType`, `RailColor`, +15; outputs `Geometry`.
- Scene use: modifier users `Bridge`; object collections WallsAndBridgets x1.
- Evaluated roots: Bridge: 11636v/13857p.
- Graph links: calls `DoorTileFromArc x2`, `WrapGeometryToCurve`, `StonesOnSurface`; called by none.
- Signals: `repeat`, `gizmo`, `closure`, `capture`, `store_attr`, `material`; frames `convert to points`, `Calculate desired number of segments`, `Lenght of the desired tile`, `Force fit the arc`, `Right beams`, +18.
- Asset bindings: materials `BridgeMat`, `Beam`, `GroundFloorWalls`; color sockets `OutsideColor`, `InsideColor`, `RailColor`.
- Translation posture: toolchain-pressure candidate: understand structurally first, translate after zone/gizmo/closure support is explicit.

### Geometry Nodes.001

- Role: root scene asset generator.
- Scale: 135 nodes, 142 links; dominant nodes: NodeReroute x15, NodeGroupInput x13, Math x12, NodeFrame x10.
- Interface: inputs `Geometry`, `StoneColor`, `MossColor`, `TopGrassColor`, `SpawnGrass`, `GrassDensity`, `GrassSize`, `DontSpawnCloseTo`, +6; outputs `Geometry`.
- Scene use: modifier users `Landscape`; object collections Cliffs x1.
- Evaluated roots: Landscape: 11281v/10751p.
- Graph links: calls `Random Rotation`; called by none.
- Signals: `capture`, `store_attr`, `collection_info`, `material`; frames `To smoothen the harder input`, `Spawn Ground detal`, `Spawn Ground Detail`, `Get just the top ground part`, `Cap so that it never geos above the surface of the upper part`, +5.
- Asset bindings: collections `BouldersSet`, `Paths`; materials `Rock`, `GrassClif`; color sockets `StoneColor`, `MossColor`, `TopGrassColor`.
- Translation posture: composite helper: translate callees before treating this as accepted behavior.

### Geometry Nodes.002

- Role: root scene asset generator.
- Scale: 142 nodes, 216 links; dominant nodes: Math x49, NodeReroute x27, NodeGroupInput x17, CombineXYZ x13.
- Interface: inputs `SpawnCross`, `FrontFoundationX`, `FrontFoundationY`, `FrontBalkonyOffset`, `FrontFirstFloorHeight`, `FrontNumber Of Upper Floors`, `FrontUpperFloorIntrudeAmount`, `FrontUpperFloorIndentType`, +28; outputs `Geometry`.
- Scene use: modifier users `Catehdral`; object collections Church x1.
- Evaluated roots: Catehdral: 255516v/183189p.
- Graph links: calls `GenerateChurchBuildingB x3`, `DomaTower`, `ChurchFrontTowers`; called by none.
- Signals: `gizmo`, `store_attr`; frames `Church Corner Position on upper floor`.
- Asset bindings: material sockets `DomeMaterial`; color sockets `RoofColor`, `DomeRoofColor`.
- Translation posture: toolchain-pressure candidate: understand structurally first, translate after zone/gizmo/closure support is explicit.

### GetBoundaryEdgeTangentAndNomral

- Role: utility, selection, or attribute helper.
- Scale: 45 nodes, 51 links; dominant nodes: NodeReroute x11, NodeFrame x7, VectorMath x4, VertexOfCorner x3.
- Interface: inputs `Geometry`; outputs `Geometry`, `EdgeDirection`, `EdgeNormal`, `EdgeIn`.
- Scene use: modifier users none; object collections none.
- Graph links: calls none; called by `GenerateCover`.
- Signals: `capture`; frames `C is V1`, `C`, `N`, `P`, `N is Border Edge`, +2.
- Translation posture: leaf candidate: suitable for behavioral harness if source output is non-empty.

### GetOnlySide Edges after Edge Extrude

- Role: utility, selection, or attribute helper.
- Scale: 7 nodes, 8 links; dominant nodes: BooleanMath x3, NodeGroupOutput x1, NodeGroupInput x1, Group x1.
- Interface: inputs `TopSelection`, `Geometry`; outputs `Value`.
- Scene use: modifier users none; object collections none.
- Graph links: calls `Select Original Geometry After Edge Extrude`; called by `DoorTileFromArc`.
- Signals: none; frames none.
- Translation posture: composite helper: translate callees before treating this as accepted behavior.

### GetPositionBasedSeed

- Role: nested helper.
- Scale: 15 nodes, 16 links; dominant nodes: Math x8, NodeGroupOutput x1, NodeGroupInput x1, ObjectInfo x1.
- Interface: inputs `Object`, `Seed`, `SecondarySeed`; outputs `Seed`.
- Scene use: modifier users none; object collections none.
- Graph links: calls none; called by `Generate Square Tower`, `Generate Tower`, `GenerateHouse`, `GenerateTerrace`.
- Signals: `object_info`; frames none.
- Asset bindings: objects `?`.
- Translation posture: leaf candidate: suitable for behavioral harness if source output is non-empty.

### GetSteppeddirectionFrom position

- Role: nested helper.
- Scale: 8 nodes, 8 links; dominant nodes: VectorMath x2, Math x2, NodeGroupOutput x1, NodeGroupInput x1.
- Interface: inputs `Vector`; outputs `Vector`.
- Scene use: modifier users none; object collections none.
- Graph links: calls none; called by `CreateGate`.
- Signals: none; frames none.
- Translation posture: leaf candidate: suitable for behavioral harness if source output is non-empty.

### Gothic SupportColumn From EDge

- Role: architectural organ or trim helper.
- Scale: 107 nodes, 164 links; dominant nodes: NodeReroute x20, VectorMath x16, Math x13, NodeGroupInput x7.
- Interface: inputs `Geometry`, `HeightWall`, `DensityLength`, `PeakHeight`, `DepthLos`, `BeamPushTendence`, `Depth`, `SupportDepthLosType`, +3; outputs `Geometry`.
- Scene use: modifier users none; object collections none.
- Graph links: calls `Select Original Geometry After Edge Extrude`, `PointyGothicCone`; called by `ChurchA-Front`, `ChurchFrontTowers`, `Generate Gothic Square Tower`, `GenerateChurchBuildingB`, `GothicSupportBeaconFromEdgeParent`, `WindowWalls`.
- Signals: `repeat`, `gizmo`, `menu`, `capture`; frames none.
- Translation posture: toolchain-pressure candidate: understand structurally first, translate after zone/gizmo/closure support is explicit.

### GothicSupportBeaconFromEdgeParent

- Role: root scene asset generator.
- Scale: 13 nodes, 17 links; dominant nodes: StoreNamedAttribute x2, InputPosition x2, NodeGroupInput x1, NodeGroupOutput x1.
- Interface: inputs `Geometry`, `HeightWall`, `PeakHeight`, `DensityLength`; outputs `Geometry`.
- Scene use: modifier users `Column`; object collections Resources x1.
- Evaluated roots: Column: 354v/266p.
- Graph links: calls `Gothic SupportColumn From EDge`; called by none.
- Signals: `gizmo`, `store_attr`, `material`; frames none.
- Asset bindings: materials `GroundFloorWalls`.
- Translation posture: toolchain-pressure candidate: understand structurally first, translate after zone/gizmo/closure support is explicit.

### HangingBanners

- Role: root scene asset generator.
- Scale: 108 nodes, 141 links; dominant nodes: Math x23, NodeReroute x12, VectorMath x11, NodeGroupInput x7.
- Interface: inputs `Geometry`, `BannerLenght`, `FlagLenght`, `0`, `1`, `2`, `3`; outputs `Geometry`.
- Scene use: modifier users `Banners Type Three`; object collections SetDressing x1.
- Evaluated roots: Banners Type Three: 252v/123p.
- Graph links: calls none; called by none.
- Signals: `repeat`, `capture`, `store_attr`, `material`; frames `convert to points`, `Calculate desired number of segments`, `Lenght of the desired tile`.
- Asset bindings: materials `Beam`, `FlatColorWithGeometryInputFlag`; color sockets `0`, `1`, `2`, `3`.
- Translation posture: toolchain-pressure candidate: understand structurally first, translate after zone/gizmo/closure support is explicit.

### HousesOnCurves

- Role: root architectural composer.
- Scale: 166 nodes, 228 links; dominant nodes: NodeReroute x25, NodeGroupInput x18, VectorMath x16, Math x15.
- Interface: inputs `Geometry`, `Seed`, `Flip Direction`, `High Polz Plants`, `RoofGeometryType`, `SpawnIVY`, `DisableRoofExrudeFront`, `DisableRoofExrudeBack`, +13; outputs `Geometry`.
- Scene use: modifier users `HousesOnCurve`; object collections Houses x1.
- Evaluated roots: HousesOnCurve: 385472v/360845p.
- Graph links: calls `Color in Range x3`, `Float in Range x2`, `GenerateHouse`, `Int in Range`; called by none.
- Signals: `repeat`, `foreach`, `capture`, `store_attr`; frames `Number of Units`.
- Asset bindings: color sockets `Wood Color B`, `Wood Color A`, `Paint Color B`, `Paint Color A`, +2.
- Translation posture: toolchain-pressure candidate: understand structurally first, translate after zone/gizmo/closure support is explicit.

### Int in Range

- Role: nested helper.
- Scale: 4 nodes, 6 links; dominant nodes: NodeGroupOutput x1, NodeGroupInput x1, RandomValue x1, SeparateXYZ x1.
- Interface: inputs `In Range`, `ID`, `Seed`; outputs `Value`.
- Scene use: modifier users none; object collections none.
- Graph links: calls none; called by `HousesOnCurves`.
- Signals: none; frames none.
- Translation posture: leaf candidate: suitable for behavioral harness if source output is non-empty.

### Is Edge Manifold [1]

- Role: utility, selection, or attribute helper.
- Scale: 4 nodes, 3 links; dominant nodes: NodeGroupOutput x1, CornersOfEdge x1, Compare x1, FieldOnDomain x1.
- Interface: inputs none; outputs `Is Edge Manifold`.
- Scene use: modifier users none; object collections none.
- Graph links: calls none; called by `ChurchA-Front`, `CreateGate`, `Generate Cliff Type 2`, `GenerateChurchBuildingB`, `GenerateHouse`, `GenerateTerrace`, `OctaveBasedSpawnStone`, +2.
- Signals: none; frames none.
- Translation posture: leaf candidate: suitable for behavioral harness if source output is non-empty.

### Is Edge Manifold [2]

- Role: utility, selection, or attribute helper.
- Scale: 4 nodes, 3 links; dominant nodes: NodeGroupOutput x1, CornersOfEdge x1, Compare x1, FieldOnDomain x1.
- Interface: inputs none; outputs `Is Edge Manifold`.
- Scene use: modifier users none; object collections none.
- Graph links: calls none; called by `ChurchA-Front`, `CreateGate`, `Generate Cliff Type 2`, `GenerateChurchBuildingB`, `GenerateHouse`, `GenerateTerrace`, `OctaveBasedSpawnStone`, +2.
- Signals: none; frames none.
- Translation posture: leaf candidate: suitable for behavioral harness if source output is non-empty.

### Make Dirt Road

- Role: root scene asset generator.
- Scale: 102 nodes, 139 links; dominant nodes: NodeReroute x16, VectorMath x13, NodeGroupInput x8, StoreNamedAttribute x6.
- Interface: inputs `Geometry`, `Ignore Materials 1`, `Ignore Materials 2`, `Snap to`, `Resolution Distance between loops`, `Flip`, `Widht`, `Offset to Ground`, +5; outputs `Geometry`.
- Scene use: modifier users `Road`; object collections Paths x1.
- Evaluated roots: Road: 1258v/940p.
- Graph links: calls none; called by none.
- Signals: `capture`, `store_attr`, `collection_info`, `material`; frames none.
- Asset bindings: collections `?`; materials `?`, `DirtPath`; material sockets `Ignore Materials 1`, `Ignore Materials 2`.
- Translation posture: medium helper: inspect frames and attributes before translation.

### Make Pumpkin From Points

- Role: nested helper.
- Scale: 217 nodes, 268 links; dominant nodes: NodeReroute x35, Math x28, VectorMath x16, SetPosition x12.
- Interface: inputs `Points`, `Seed`; outputs `Instances`.
- Scene use: modifier users none; object collections none.
- Graph links: calls `Curve Info`; called by `Pumpkin`.
- Signals: `capture`, `store_attr`, `material`; frames `generate leaf shape`.
- Asset bindings: materials `Greenery`, `PumpkingLeave`, `Pumpkin`.
- Translation posture: composite helper: translate callees before treating this as accepted behavior.

### Make River

- Role: root terrain or dressing composer.
- Scale: 136 nodes, 188 links; dominant nodes: NodeReroute x31, VectorMath x13, NodeGroupInput x10, StoreNamedAttribute x9.
- Interface: inputs `Geometry`, `Resolution distance Between Loops`, `Water half Width`, `PushIntoShore Amount`, `Shore line Edge Width`; outputs `Geometry`.
- Scene use: modifier users `River`; object collections Collection x1, landscape x1.
- Evaluated roots: River: 530v/420p.
- Graph links: calls none; called by none.
- Signals: `capture`, `store_attr`, `collection_info`, `material`; frames none.
- Asset bindings: collections `RiverBank`; materials `River`.
- Translation posture: medium helper: inspect frames and attributes before translation.

### MakeBush

- Role: root scene asset generator.
- Scale: 94 nodes, 119 links; dominant nodes: NodeReroute x16, VectorMath x10, StoreNamedAttribute x7, NodeGroupInput x6.
- Interface: inputs `Geometry`, `Seed`, `Squarness`, `NoiseScale`, `NoiseStrenght`, `LightDirection`, `SubdividLevel`, `LeafsDensity`, +3; outputs `Geometry`.
- Scene use: modifier users `bush`; object collections landscape x1.
- Evaluated roots: bush: 6446v/3615p.
- Graph links: calls `SetAutoSmooth`; called by `MakeTree`, `Tree On Geo Points`.
- Signals: `repeat`, `gizmo`, `capture`, `store_attr`, `material`; frames none.
- Asset bindings: materials `TreeBase`, `TreeSingleLeafAddons`; color sockets `Leafcolor`.
- Translation posture: toolchain-pressure candidate: understand structurally first, translate after zone/gizmo/closure support is explicit.

### MakeGrass

- Role: root scene asset generator.
- Scale: 26 nodes, 29 links; dominant nodes: Math x5, SetPosition x2, Transform x2, VectorMath x2.
- Interface: inputs `Density`, `Seed`; outputs `Geometry`.
- Scene use: modifier users `MakeGrass`; object collections Resources x1.
- Evaluated roots: MakeGrass: 144v/100p.
- Graph links: calls none; called by none.
- Signals: `repeat`, `store_attr`, `material`; frames none.
- Asset bindings: materials `Grass`.
- Translation posture: toolchain-pressure candidate: understand structurally first, translate after zone/gizmo/closure support is explicit.

### MakeSpiral

- Role: root scene asset generator.
- Scale: 20 nodes, 24 links; dominant nodes: Math x8, NodeGroupInput x4, NodeGroupOutput x1, ResampleCurve x1.
- Interface: inputs `Frequency`, `Radius`, `Height`, `HeightRadiusGain`; outputs `Geometry`.
- Scene use: modifier users `SpiralMaker`; object collections Resources x1.
- Evaluated roots: SpiralMaker: 200v/0p.
- Graph links: calls none; called by `GenerateStairCase`.
- Signals: none; frames none.
- Translation posture: leaf candidate: suitable for behavioral harness if source output is non-empty.

### MakeStairs

- Role: root scene asset generator.
- Scale: 25 nodes, 33 links; dominant nodes: NodeGroupInput x3, NodeClosureInput x2, NodeClosureOutput x2, InstanceOnPoints x2.
- Interface: inputs `Geometry`, `StairType`, `DistanceBetweenStairs`, `StairWidth`, `StairDepth`, `StairsHeight`; outputs `Geometry`.
- Scene use: modifier users `Stairs`; object collections SetDressing x1.
- Evaluated roots: Stairs: 140v/236p.
- Graph links: calls none; called by `GenerateStairCase`.
- Signals: `closure`, `menu`, `collection_info`, `material`; frames none.
- Asset bindings: collections `Bricks`; materials `Stone`.
- Translation posture: toolchain-pressure candidate: understand structurally first, translate after zone/gizmo/closure support is explicit.

### MakeStallCover

- Role: root architectural composer.
- Scale: 282 nodes, 320 links; dominant nodes: NodeReroute x36, Math x24, VectorMath x22, NodeGroupInput x21.
- Interface: inputs `Geometry`, `Height`, `CoverDepth`, `BackLift`, `MiddleLift`, `ExtrusionDirection`, `Resolution`, `BeamColor`, +8; outputs `Geometry`.
- Scene use: modifier users `Cover`, `Cover.001`, `Cover.002`; object collections SetDressing x3.
- Evaluated roots: Cover: 326v/272p; Cover.001: 714v/544p; Cover.002: 880v/746p.
- Graph links: calls none; called by none.
- Signals: `repeat`, `gizmo`, `menu`, `capture`, `store_attr`, `material`; frames `Get curve right`, `Decide on extrusion direction`, `Extrude at equal steps`, `Subdivided Extrusion`, `Middle Lift`, +15.
- Asset bindings: materials `Beam`, `CoverMat`; color sockets `BeamColor`, `PaintColor`, `PaintColor2`.
- Translation posture: toolchain-pressure candidate: understand structurally first, translate after zone/gizmo/closure support is explicit.

### MakeTree

- Role: root terrain or dressing composer.
- Scale: 271 nodes, 305 links; dominant nodes: NodeReroute x63, Math x36, VectorMath x19, NodeGroupInput x18.
- Interface: inputs `TreeHeight`, `Seed`, `TrunkThickness`, `TotalCrownSize`, `IndividualCrown`, `PullUpBranches`, `TrunkColor`, `Leafcolor`, +3; outputs `Geometry`.
- Scene use: modifier users `Tree`; object collections landscape x1.
- Evaluated roots: Tree: 32706v/15081p.
- Graph links: calls `MakeBush`; called by none.
- Signals: `gizmo`, `capture`, `store_attr`, `material`; frames `twist trunk`, `Determine where to spawn`, `Get curve thickness at origin of the branch`, `Get rotation around up axis`, `Tilt up wards`, +10.
- Asset bindings: materials `TreeTrunk`; color sockets `TrunkColor`, `Leafcolor`.
- Translation posture: toolchain-pressure candidate: understand structurally first, translate after zone/gizmo/closure support is explicit.

### MatrixSubtract

- Role: nested helper.
- Scale: 23 nodes, 34 links; dominant nodes: Math x9, SeparateMatrix x6, NodeGroupInput x3, NodeFrame x3.
- Interface: inputs `A`, `B`; outputs `Matrix`.
- Scene use: modifier users none; object collections none.
- Graph links: calls none; called by `PCAGetLongAndShortAxis`.
- Signals: none; frames `Column X`, `Column Y`, `Column Z`.
- Translation posture: leaf candidate: suitable for behavioral harness if source output is non-empty.

### OctaveBasedSpawnStone

- Role: terrain, vegetation, or scatter helper.
- Scale: 62 nodes, 80 links; dominant nodes: NodeReroute x16, Math x11, DeleteGeometry x4, Compare x4.
- Interface: inputs `JustTheWalls`, `DepthIndex`, `Stones`, `WholeBaseMesh`, `Size`, `Seed`, `StoneCollection`, `Density`; outputs `Geometry`.
- Scene use: modifier users none; object collections none.
- Graph links: calls `Is Edge Manifold`; called by `StonesOnSurface`.
- Signals: `collection_info`; frames `Get only edges that have high curveture`, `delete things too close to open edges`.
- Asset bindings: collections `?`.
- Translation posture: composite helper: translate callees before treating this as accepted behavior.

### PCAGetLongAndShortAxis

- Role: nested helper.
- Scale: 155 nodes, 198 links; dominant nodes: NodeReroute x52, VectorMath x23, NodeFrame x22, Math x16.
- Interface: inputs `Geometry`, `NumberOfIteration`; outputs `LongestAxis`, `ShortestAxis`, `MiddleAxis`, `Centriod`, `Covariance`, `Outer`.
- Scene use: modifier users none; object collections none.
- Graph links: calls `MatrixSubtract`; called by `GenerateRockSlow`.
- Signals: `repeat`; frames `Get points to act on`, `Centeriod`, `Covariance Matrix`, `Initial Vector`, `safty gaurd`, +11.
- Translation posture: toolchain-pressure candidate: understand structurally first, translate after zone/gizmo/closure support is explicit.

### Points On Surface

- Role: root scene asset generator.
- Scale: 17 nodes, 25 links; dominant nodes: VectorMath x3, NodeReroute x2, NodeGroupInput x1, NodeGroupOutput x1.
- Interface: inputs `Geometry`, `traget`, `Density Factor`, `Seed`, `Distance Min`, `Density Max`; outputs `Geometry`.
- Scene use: modifier users `Plane`; object collections Houses x1.
- Evaluated roots: Plane: 12410v/6660p.
- Graph links: calls none; called by none.
- Signals: `object_info`; frames none.
- Asset bindings: objects `?`.
- Translation posture: leaf candidate: suitable for behavioral harness if source output is non-empty.

### PointWindowsFromEdges

- Role: architectural organ or trim helper.
- Scale: 81 nodes, 105 links; dominant nodes: NodeReroute x14, VectorMath x11, NodeGroupInput x7, Math x5.
- Interface: inputs `Edges`, `Height`, `FlipEdge`, `PatternTiling`, `ArcPadToEdge`, `FlattenTheTop`, `FlattenBottom`, `PointyPointyRadius`, +7; outputs `Geometry`.
- Scene use: modifier users none; object collections none.
- Graph links: calls `PointyGothicCone x2`, `WindowWalls`; called by `DomaTower`.
- Signals: `capture`, `material`; frames none.
- Asset bindings: materials `GroundFloorWalls`.
- Translation posture: composite helper: translate callees before treating this as accepted behavior.

### PointyGothicCone

- Role: architectural organ or trim helper.
- Scale: 58 nodes, 69 links; dominant nodes: NodeGroupInput x7, SetPosition x4, InputPosition x4, VectorMath x4.
- Interface: inputs `Geometry`, `ColumnRadius`, `PeakHeight`, `GothicDetailDensity`, `DetailScale`, `SpawnDetails`, `Rotation`; outputs `Geometry`.
- Scene use: modifier users none; object collections none.
- Graph links: calls none; called by `DomaTower`, `Gothic SupportColumn From EDge`, `PointWindowsFromEdges`.
- Signals: `capture`; frames `get just side edges`.
- Translation posture: leaf candidate: suitable for behavioral harness if source output is non-empty.

### Pole

- Role: root scene asset generator.
- Scale: 89 nodes, 117 links; dominant nodes: Math x19, NodeGroupInput x14, NodeReroute x11, CombineXYZ x6.
- Interface: inputs `PoleRadius`, `VerticalPoleHeight`, `BeamColor`, `IndentationResolution`, `IndentIn`, `IndentationProportion`; outputs `Geometry`, `PoleMidSectionRadius`.
- Scene use: modifier users `Pole`; object collections SetDressing x1.
- Evaluated roots: Pole: 114v/104p.
- Graph links: calls none; called by `Banner`, `BannerTypeFour`, `BannerTypeThree`.
- Signals: `repeat`, `gizmo`, `store_attr`, `material`; frames `Make Base Shape`, `Gizmos`, `determine base indentation height`, `middle section height`.
- Asset bindings: materials `Beam`; color sockets `BeamColor`.
- Translation posture: toolchain-pressure candidate: understand structurally first, translate after zone/gizmo/closure support is explicit.

### ProjectOnCoordinate

- Role: nested helper.
- Scale: 12 nodes, 17 links; dominant nodes: VectorMath x7, NodeGroupOutput x1, NodeGroupInput x1, NodeReroute x1.
- Interface: inputs `Right`, `Center`, `Forward`; outputs `CoordinatesRaw`.
- Scene use: modifier users none; object collections none.
- Graph links: calls none; called by `ArcsFromEdges`.
- Signals: none; frames none.
- Translation posture: leaf candidate: suitable for behavioral harness if source output is non-empty.

### Pumpkin

- Role: root scene asset generator.
- Scale: 15 nodes, 17 links; dominant nodes: NodeGroupInput x4, NodeGroupOutput x1, Group x1, CombineXYZ x1.
- Interface: inputs `Geometry`, `Seed`, `DirectionAngle`, `Height`, `Density Factor`, `Snap To Surface`, `Snap To Geometry`; outputs `Geometry`.
- Scene use: modifier users `Wheat.002`; object collections Farms x1.
- Evaluated roots: Wheat.002: 4704v/4424p.
- Graph links: calls `Make Pumpkin From Points`; called by none.
- Signals: `object_info`; frames none.
- Asset bindings: objects `?`.
- Translation posture: composite helper: translate callees before treating this as accepted behavior.

### RailsFromEdge

- Role: architectural organ or trim helper.
- Scale: 191 nodes, 250 links; dominant nodes: Math x35, NodeReroute x22, VectorMath x17, SetPosition x11.
- Interface: inputs `Mesh`, `TotalHeight`, `Reverse Curve`; outputs `Curve`.
- Scene use: modifier users none; object collections none.
- Graph links: calls none; called by `ChurchA-Front`, `ChurchFrontTowers`, `Generate Gothic Square Tower`, `WindowWalls`.
- Signals: `gizmo`, `capture`, `material`; frames `force reordering of edges just in case`, `Total Extude So far`, `Generate Star shape`, `get support decor shape`.
- Asset bindings: materials `GroundFloorWalls`.
- Translation posture: toolchain-pressure candidate: understand structurally first, translate after zone/gizmo/closure support is explicit.

### Random Rotation

- Role: utility, selection, or attribute helper.
- Scale: 25 nodes, 33 links; dominant nodes: Math x13, NodeReroute x5, NodeGroupInput x2, NodeGroupOutput x1.
- Interface: inputs `Min Zenith`, `Max Zenith`, `ID`, `Seed`; outputs `Rotation`.
- Scene use: modifier users none; object collections none.
- Graph links: calls none; called by `Generate Cliff Type 2`, `GenerateRockSlow`, `Geometry Nodes.001`, `WindowFromEdges`.
- Signals: none; frames none.
- Translation posture: leaf candidate: suitable for behavioral harness if source output is non-empty.

### Reroute

- Role: nested helper.
- Scale: 571 nodes, 726 links; dominant nodes: NodeReroute x87, VectorMath x82, Math x61, NodeGroupInput x32.
- Interface: inputs `Input`, `DecorGatedensity`, `Height`, `DoorNormalizedHeight`, `DoorOffset`, `IndentationOffset`, `CenterLift`, `WindowMaterial`, +6; outputs `Output`.
- Scene use: modifier users none; object collections none.
- Graph links: calls `Select Original Geometry After Edge Extrude`, `SetAutoSmooth`, `GenerateArc`; called by `ChurchA-Front`, `EdgesToGates`.
- Signals: `repeat`, `gizmo`, `capture`, `store_attr`, `material`; frames `Make Right Side`, `Make LeftSide`, `Dont place on the last`, `Figure out the base of the door`, `get the middle section`, +11.
- Asset bindings: materials `GroundFloorWalls`, `BeamFakeTextureVertical`, `RoundWindwos`; material sockets `WindowMaterial`, `DoorMaterial`.
- Translation posture: toolchain-pressure candidate: understand structurally first, translate after zone/gizmo/closure support is explicit.

### ResampleEdgesAndSpawnWindowedWalld

- Role: architectural organ or trim helper.
- Scale: 56 nodes, 68 links; dominant nodes: VectorMath x7, Compare x5, NodeGroupInput x3, CurveToMesh x3.
- Interface: inputs `TotalWallHeight`, `RailsTotalHeight`, `Geometry`, `WindowWallTiling`, `Irregularity`, `FlipWalls`, `CornersMovedTowardsCenter`, `WallMiddleMultiplyer`, +2; outputs `Geometry`, `SupportBeamEdges`.
- Scene use: modifier users none; object collections none.
- Graph links: calls `WindowWalls`, `Curve Tip`; called by `ChurchA-Front`, `GenerateChurchBuildingB`.
- Signals: `foreach`, `capture`; frames none.
- Translation posture: toolchain-pressure candidate: understand structurally first, translate after zone/gizmo/closure support is explicit.

### Round Bottom

- Role: root scene asset generator.
- Scale: 56 nodes, 67 links; dominant nodes: NodeGroupInput x11, Math x10, NodeReroute x10, CombineXYZ x3.
- Interface: inputs `Radius`, `Resolution Ring`, `Lower Indent Iteration`, `Low Point Offset`, `Cover The Top`; outputs `Geometry`.
- Scene use: modifier users `RoundBottom`; object collections Resources x1.
- Evaluated roots: RoundBottom: 216v/182p.
- Graph links: calls none; called by `Generate Tower`, `WindMill`.
- Signals: `repeat`, `gizmo`, `closure`; frames none.
- Translation posture: toolchain-pressure candidate: understand structurally first, translate after zone/gizmo/closure support is explicit.

### Select Original Geometry After Edge Extrude

- Role: utility, selection, or attribute helper.
- Scale: 11 nodes, 13 links; dominant nodes: FieldOnDomain x2, SampleIndex x2, BooleanMath x2, NodeGroupOutput x1.
- Interface: inputs `TopSelection`, `Geometry`; outputs `Boolean`.
- Scene use: modifier users none; object collections none.
- Graph links: calls none; called by `DoorTileFromArc`, `GetOnlySide Edges after Edge Extrude`, `Gothic SupportColumn From EDge`, `Reroute`, `TownWall_Climbing`, `WallTowerround`.
- Signals: none; frames `Get the original loop we extruded from`.
- Translation posture: leaf candidate: suitable for behavioral harness if source output is non-empty.

### SetAutoSmooth

- Role: utility, selection, or attribute helper.
- Scale: 5 nodes, 6 links; dominant nodes: SetShadeSmooth x2, NodeGroupOutput x1, NodeGroupInput x1, Group x1.
- Interface: inputs `Input`, `AutoSmooth Threshold in Dot Space`; outputs `Mesh`.
- Scene use: modifier users none; object collections none.
- Graph links: calls `ShouldAutoSmooth`; called by `MakeBush`, `Reroute`, `StonesOnSurface`, `TownWall`, `TownWall_Climbing`, `WallTowerround`.
- Signals: none; frames none.
- Translation posture: composite helper: translate callees before treating this as accepted behavior.

### ShouldAutoSmooth

- Role: utility, selection, or attribute helper.
- Scale: 18 nodes, 21 links; dominant nodes: NodeReroute x3, NodeGroupInput x2, CornersOfEdge x2, FaceOfCorner x2.
- Interface: inputs `Input`, `AutoSmooth Threshold in Dot Space`; outputs `Geometry`, `Value`.
- Scene use: modifier users none; object collections none.
- Graph links: calls none; called by `DoorTileFromArc`, `SetAutoSmooth`, `WindMill`.
- Signals: `capture`; frames `Get faces of an edge`.
- Translation posture: leaf candidate: suitable for behavioral harness if source output is non-empty.

### Spawn Normals on faces

- Role: utility, selection, or attribute helper.
- Scale: 10 nodes, 11 links; dominant nodes: NodeGroupOutput x1, NodeGroupInput x1, MeshToPoints x1, CaptureAttribute x1.
- Interface: inputs `Geometry`, `Length`; outputs `Instances`.
- Scene use: modifier users none; object collections none.
- Graph links: calls none; called by `CreateGate`.
- Signals: `capture`; frames none.
- Translation posture: leaf candidate: suitable for behavioral harness if source output is non-empty.

### Stall

- Role: root architectural composer.
- Scale: 116 nodes, 147 links; dominant nodes: Math x22, NodeGroupInput x20, CombineXYZ x17, GizmoLinear x12.
- Interface: inputs `Height`, `ExtendX`, `ExtendY`, `X-Distort`, `Y-Distort`, `MedialAxisWidth`, `RidgeScaler`, `TopLift`, +6; outputs `Geometry`.
- Scene use: modifier users `Stall`; object collections SetDressing x1.
- Evaluated roots: Stall: 32v/29p.
- Graph links: calls `Is Edge Manifold x2`, `GenerateMedialAxisRectangleTopology`; called by none.
- Signals: `gizmo`, `capture`, `store_attr`, `material`; frames none.
- Asset bindings: materials `Beam`, `FlatColorWithGeometryInputFlag`; color sockets `BeamColor`, `CoverColor`.
- Translation posture: toolchain-pressure candidate: understand structurally first, translate after zone/gizmo/closure support is explicit.

### StonesOnSurface

- Role: root terrain or dressing composer.
- Scale: 129 nodes, 144 links; dominant nodes: NodeReroute x27, NodeFrame x13, VectorMath x9, Math x7.
- Interface: inputs `JustTheSurface`, `TheWholeBaseMesh`, `StoneType`, `PebbleSize`, `PebbleDensity`; outputs `Geometry`.
- Scene use: modifier users `SpawnStoneOnSurface`; object collections Resources x1.
- Evaluated roots: SpawnStoneOnSurface: 0v/0p.
- Graph links: calls `OctaveBasedSpawnStone x3`, `SetAutoSmooth`; called by `CreateGate`, `GenerateTerrace`, `Geometry Nodes`, `TownWall`, `TownWall_Climbing`, `WallTowerround`.
- Signals: `closure`, `menu`, `capture`, `store_attr`, `collection_info`, `object_info`, `material`; frames `Get location based random for ground floor Distortion`, `Generate Pebbles`, `Generate Regural stones`, `Get only edges that have high curveture`, `First distribute randomly`, +7.
- Asset bindings: collections `Bricks`; objects `?`; materials `GroundFloorWalls`, `BrickMaterial`.
- Translation posture: toolchain-pressure candidate: understand structurally first, translate after zone/gizmo/closure support is explicit.

### Sun Flowers From Points

- Role: nested helper.
- Scale: 229 nodes, 279 links; dominant nodes: NodeReroute x31, Math x26, InputPosition x16, SetPosition x15.
- Interface: inputs `Points`, `Seed`, `Direction`; outputs `Instances`.
- Scene use: modifier users none; object collections none.
- Graph links: calls none; called by `Distribute Sunflower`.
- Signals: `capture`, `store_attr`, `material`; frames `making a circle with split edge so there are no uv seems`.
- Asset bindings: materials `Greenery`, `SunFlower Seed`, `SunFlowerPetals`.
- Translation posture: medium helper: inspect frames and attributes before translation.

### Switch On Roof Type

- Role: architectural organ or trim helper.
- Scale: 3 nodes, 4 links; dominant nodes: NodeGroupInput x1, NodeGroupOutput x1, MenuSwitch x1.
- Interface: inputs `Menu`; outputs `Output`, `Real Geometry `, `Faked Texture`.
- Scene use: modifier users none; object collections none.
- Graph links: calls none; called by `ChurchA-Front`, `ChurchFrontTowers`, `Generate Extruded DoorShape`, `Generate Square Tower`, `Generate Tower`, `GenerateChurchBuildingB`, `GenerateHouse`, +2.
- Signals: `menu`; frames none.
- Translation posture: leaf candidate: suitable for behavioral harness if source output is non-empty.

### Tower Gothic Type 2

- Role: root architectural composer.
- Scale: 23 nodes, 26 links; dominant nodes: NodeGroupInput x4, Math x4, GizmoLinear x3, CombineXYZ x3.
- Interface: inputs `Foundation X`, `Foundation Y`, `Lower Part Tiling`, `Height`, `Make Only Half the Tower`; outputs `Geometry`.
- Scene use: modifier users `Tower-Foundation`; object collections Church x1.
- Evaluated roots: Tower-Foundation: 11156v/7211p.
- Graph links: calls `Generate Gothic Square Tower`; called by none.
- Signals: `gizmo`, `store_attr`; frames none.
- Translation posture: toolchain-pressure candidate: understand structurally first, translate after zone/gizmo/closure support is explicit.

### TownWall

- Role: root architectural composer.
- Scale: 342 nodes, 389 links; dominant nodes: NodeReroute x58, VectorMath x52, Math x32, NodeFrame x24.
- Interface: inputs `Geometry`, `merlonLength`, `Offset Scale`, `WallHeight`, `StoneType`, `MerlonsOutExtrude`, `MerlonHeight`; outputs `Geometry`.
- Scene use: modifier users `Walls`; object collections WallsAndBridgets x1.
- Evaluated roots: Walls: 8779v/11598p.
- Graph links: calls `SetAutoSmooth`, `StonesOnSurface`, `WrapGeometryToCurve`, `DoorTileFromArc`; called by none.
- Signals: `repeat`, `gizmo`, `closure`, `capture`, `store_attr`, `material`; frames `convert to points`, `Calculate desired number of segments`, `Lenght of the desired tile`, `WallWidth`, `extrude out the base inwards`, +16.
- Asset bindings: materials `GroundFloorWalls`.
- Translation posture: toolchain-pressure candidate: understand structurally first, translate after zone/gizmo/closure support is explicit.

### TownWall_Climbing

- Role: root architectural composer.
- Scale: 285 nodes, 332 links; dominant nodes: NodeReroute x51, VectorMath x42, Math x24, NodeFrame x21.
- Interface: inputs `Geometry`, `merlonLength`, `Offset Scale`, `WallHeight`, `StoneType`, `MerlonsOutExtrude`, `MerlonHeight`, `SnapToGround`; outputs `Geometry`.
- Scene use: modifier users `Walls.001`; object collections WallsAndBridgets x1.
- Evaluated roots: Walls.001: 8897v/13878p.
- Graph links: calls `SetAutoSmooth x2`, `StonesOnSurface`, `Select Original Geometry After Edge Extrude`; called by none.
- Signals: `repeat`, `gizmo`, `capture`, `store_attr`, `object_info`, `material`; frames `WallWidth`, `extrude out the base inwards`, `extrude up the first part`, `Get the front facing part`, `Wall Height`, +16.
- Asset bindings: objects `?`; materials `GroundFloorWalls`.
- Translation posture: toolchain-pressure candidate: understand structurally first, translate after zone/gizmo/closure support is explicit.

### Tree On Geo Points

- Role: root terrain or dressing composer.
- Scale: 282 nodes, 348 links; dominant nodes: NodeReroute x72, Math x34, VectorMath x17, NodeFrame x15.
- Interface: inputs `Geometry`, `Seed`, `LeafsDensity`, `LeafExtrudeAmount`, `Spawn Transparent Leafs`, `Tree Height Variance`, `Trunk thickness Variance`, `Total Crown Size Variance`, +6; outputs `Geometry`.
- Scene use: modifier users `Plane`, `Tree.001`; object collections Houses x1, landscape x1.
- Evaluated roots: Plane: 12410v/6660p; Tree.001: 5742v/5952p.
- Graph links: calls `Float in Range x5`, `Color in Range x2`, `MakeBush`; called by none.
- Signals: `capture`, `store_attr`, `material`; frames `twist trunk`, `Determine where to spawn`, `Get curve thickness at origin of the branch`, `Get rotation around up axis`, `Tilt up wards`, +9.
- Asset bindings: materials `TreeTrunk`; color sockets `Leaf Color A`, `Leaf Color B`, `Trunk Color A`, `Trunk Color B`.
- Translation posture: composer candidate: translate by organs and assets first, then rebuild orchestration.

### WallTowerround

- Role: root architectural composer.
- Scale: 265 nodes, 346 links; dominant nodes: Math x54, NodeReroute x32, CombineXYZ x21, NodeGroupInput x20.
- Interface: inputs `BaseRadius`, `TowerHeight`, `LowerDecorDensity`, `UpperExtend`, `LowerDecorMoveIN`, `DesiredMerloneDensityLenght`, `UpperDeckGaurdheight`, `StoneType`, +2; outputs `Mesh`.
- Scene use: modifier users `WallTower`; object collections WallsAndBridgets x1.
- Evaluated roots: WallTower: 13849v/21814p.
- Graph links: calls `Select Original Geometry After Edge Extrude x2`, `StonesOnSurface`, `SetAutoSmooth`; called by none.
- Signals: `repeat`, `gizmo`, `capture`, `store_attr`, `material`; frames `construct base`, `deterime how tall is the base`, `space for decor`, `tower middle height`, `final upper deck radius`.
- Asset bindings: materials `GroundFloorWalls`, `BeamFakeTexture`; color sockets `WoodTint`.
- Translation posture: toolchain-pressure candidate: understand structurally first, translate after zone/gizmo/closure support is explicit.

### Waterfall

- Role: root scene asset generator.
- Scale: 114 nodes, 136 links; dominant nodes: Math x25, NodeReroute x19, NodeGroupInput x12, CombineXYZ x9.
- Interface: inputs `Initial Speed`, `Outward Angle`, `Ground Height`, `Resolution distance between points`, `Waterfall Width`, `Solidify`, `SplashHeight`; outputs `Geometry`.
- Scene use: modifier users `WatterFall`; object collections landscape x1.
- Evaluated roots: WatterFall: 30v/11p.
- Graph links: calls none; called by none.
- Signals: `gizmo`, `capture`, `store_attr`, `material`; frames `Calculate hit time`, `Time per point`, `Velocty Y and Z`, `Y`, `Z`.
- Asset bindings: materials `WaterFall`, `WaterFallSpalsh`.
- Translation posture: toolchain-pressure candidate: understand structurally first, translate after zone/gizmo/closure support is explicit.

### Wheat From Point

- Role: nested helper.
- Scale: 265 nodes, 320 links; dominant nodes: NodeReroute x36, Math x30, SetPosition x16, Compare x15.
- Interface: inputs `Points`, `Seed`, `Direction`, `Detail Type`; outputs `Instances`.
- Scene use: modifier users none; object collections none.
- Graph links: calls none; called by `Distribute Wheat`.
- Signals: `repeat`, `menu`, `capture`, `store_attr`, `material`; frames none.
- Asset bindings: materials `Wheat`, `WeatLowPoly`.
- Translation posture: toolchain-pressure candidate: understand structurally first, translate after zone/gizmo/closure support is explicit.

### Wind On Plants

- Role: terrain, vegetation, or scatter helper.
- Scale: 23 nodes, 26 links; dominant nodes: VectorMath x8, NodeGroupInput x2, InputPosition x2, SeparateXYZ x2.
- Interface: inputs `Geometry`, `Root Position`, `WindDirection`, `WindSpeed`, `WindDisplacementStrenght`; outputs `Geometry`.
- Scene use: modifier users none; object collections none.
- Graph links: calls none; called by `Distribute Corn`, `Distribute Sunflower`, `Distribute Wheat`.
- Signals: none; frames none.
- Translation posture: leaf candidate: suitable for behavioral harness if source output is non-empty.

### WindMill

- Role: root architectural composer.
- Scale: 512 nodes, 634 links; dominant nodes: NodeReroute x77, Math x43, NodeGroupInput x41, VectorMath x39.
- Interface: inputs `Seed`, `Roof Color`, `Roof geo type`, `Roof thickness`, `Over hang size`, `Roof Height`, `Mill`, `Mill Wood Color`, +21; outputs `Geometry`.
- Scene use: modifier users `WindMillTower`; object collections Farms x1.
- Evaluated roots: WindMillTower: 14571v/10735p.
- Graph links: calls `Switch On Roof Type x6`, `Is Edge Manifold x2`, `CurvedDoorFromEdges`, `WindowFromEdges`, `ShouldAutoSmooth`, `Curve Info`, `Round Bottom`; called by none.
- Signals: `repeat`, `gizmo`, `capture`, `store_attr`, `material`; frames `Roof tip`, `Offset abit along normal to create iregularities`, `Save some per tile randomness for shading`, `Ground floor`, `Middle Floors`, +2.
- Asset bindings: materials `GroundFloorWalls`, `?`, `Roof`, `Copper`, `Beam`, +1; color sockets `Roof Color`, `Mill Wood Color`, `Wood Color`.
- Translation posture: toolchain-pressure candidate: understand structurally first, translate after zone/gizmo/closure support is explicit.

### WindowBeams

- Role: architectural organ or trim helper.
- Scale: 63 nodes, 69 links; dominant nodes: NodeReroute x9, VectorMath x8, Math x5, NodeFrame x5.
- Interface: inputs `WindlowLowerEdge`, `FloorBaseEdge`, `WindowCenterHeight`; outputs `Geometry`, `WindowBeamsBaseAsPoints`.
- Scene use: modifier users none; object collections none.
- Graph links: calls `Curve Info`; called by `GenerateHouse`.
- Signals: `capture`, `store_attr`, `material`; frames `This is to somewhat deal with tilted surfaces and houses on slo`, `find the poin in the base to set as beam end`, `Each edge has only 2 entry. So we can sample the other edge eas`, `do what we did below but now crossed`, `Window beams base as points`.
- Asset bindings: materials `Beam`.
- Translation posture: composite helper: translate callees before treating this as accepted behavior.

### WindowFromEdges

- Role: root architectural composer.
- Scale: 164 nodes, 225 links; dominant nodes: NodeReroute x34, Math x19, VectorMath x11, NodeGroupInput x10.
- Interface: inputs `Geometry`, `Reverse`, `Seed`, `RandomnessAmount`, `WallHeight`, `SpawnFlowers`, `High Poly Plants`, `VerticalPosition`, +3; outputs `Geometry`.
- Scene use: modifier users `WindowFromEDges`; object collections Resources x1.
- Evaluated roots: WindowFromEDges: 192v/120p.
- Graph links: calls `Random Rotation`; called by `WindMill`.
- Signals: `capture`, `store_attr`, `collection_info`, `material`; frames `Sort edge orders`, `random scale`.
- Asset bindings: collections `?`; materials `GroundFloorWalls`, `FakeWoodTextureWithUV`, `Beam`.
- Translation posture: composite helper: translate callees before treating this as accepted behavior.

### WindowInnerPattern

- Role: architectural organ or trim helper.
- Scale: 137 nodes, 161 links; dominant nodes: Math x25, NodeReroute x17, InputIndex x10, Compare x8.
- Interface: inputs `Value`, `Geometry`, `Exponent`, `Radius`, `PatternTiling`; outputs `Geometry`.
- Scene use: modifier users none; object collections none.
- Graph links: calls none; called by `GenerateWindowsFromEdges`.
- Signals: `repeat`, `capture`; frames `get the top of the arc`, `The extend hegiht`, `the arc hegiht`, `DONT CHANGE`, `Get edge info`.
- Translation posture: toolchain-pressure candidate: understand structurally first, translate after zone/gizmo/closure support is explicit.

### WindowWalls

- Role: root architectural composer.
- Scale: 141 nodes, 177 links; dominant nodes: NodeReroute x22, Math x15, NodeGroupInput x13, CombineXYZ x8.
- Interface: inputs `Geometry`, `TotalWallHeight`, `BaseOutExtrude`, `WallMiddleMultiplyer`, `PatternTiling`, `RailsTotalHeight`, `CornersMovedTowardsCenter`, `FlipEdge`, +9; outputs `Geometry`, `SupportBeamEdges`.
- Scene use: modifier users `WindowWalls`; object collections Resources x1.
- Evaluated roots: WindowWalls: 21942v/15416p.
- Graph links: calls `ArcsFromEdges`, `Gothic SupportColumn From EDge`, `RailsFromEdge`, `GenerateWindowsFromEdges`; called by `DomaTower`, `GenerateChurchBuildingB`, `PointWindowsFromEdges`, `ResampleEdgesAndSpawnWindowedWalld`.
- Signals: `foreach`, `gizmo`, `capture`, `store_attr`, `material`; frames `Get the base height`, `Force re order vertices`, `Get edge info`, `Make base indent`, `Make it have a tilted shape`, +2.
- Asset bindings: materials `GroundFloorWalls`.
- Translation posture: toolchain-pressure candidate: understand structurally first, translate after zone/gizmo/closure support is explicit.

### Wooden Bridge

- Role: root architectural composer.
- Scale: 181 nodes, 240 links; dominant nodes: NodeGroupInput x28, VectorMath x23, NodeReroute x22, Math x17.
- Interface: inputs `Geometry`, `Foundation Height`, `Foundation Distance Between Beams`, `Foundation Distance irregularity`, `Bridge Width`, `Material`, `Color`, `Seed`, +13; outputs `Geometry`.
- Scene use: modifier users `Wooden Bridge`; object collections Farms x1.
- Evaluated roots: Wooden Bridge: 1152v/864p.
- Graph links: calls `Fence Type A x2`; called by none.
- Signals: `foreach`, `gizmo`, `capture`, `store_attr`, `material`; frames none.
- Asset bindings: materials `?`; material sockets `Material`; color sockets `Color`.
- Translation posture: toolchain-pressure candidate: understand structurally first, translate after zone/gizmo/closure support is explicit.

### WrapGeometryToCurve

- Role: root scene asset generator.
- Scale: 43 nodes, 44 links; dominant nodes: VectorMath x11, NodeFrame x7, SeparateXYZ x4, SetPosition x3.
- Interface: inputs `Curve`, `Geometry`, `WrapAxis`; outputs `Geometry`.
- Scene use: modifier users `WrapItemAroundBezierCurve`; object collections Resources x1.
- Graph links: calls none; called by `Geometry Nodes`, `TownWall`.
- Signals: `menu`, `object_info`; frames `Get right coordinate system`, `world to loccal`, `Align x min with zerop`, `Get how far vertex is along x axis`, `tangent`, +2.
- Asset bindings: objects `DoorTileFromArc`.
- Translation posture: leaf candidate: suitable for behavioral harness if source output is non-empty.

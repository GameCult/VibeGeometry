# Translation: IRCSS French Houses Footholds

## Source

- Repository: https://github.com/IRCSS/Blender-Geometry-Node-French-Houses
- Source file:
  `GeometryNodesFrenchHous.blend`
- Source groups translated so far:
  - `MakeSpiral`
  - `PointyGothicCone`
- Geometry Script recreation:
  `examples/geometry_script/ircss_french_houses.py`

## Why This File

This is the first genuinely city-scale corpus target. The inspected `.blend`
contains 108 geometry node groups, including thousand-node architectural
systems:

- `CreateGate`: 1081 nodes / 1234 links
- `GenerateHouse`: 1023 nodes / 1075 links
- `GenerateChurchBuildingB`: 893 nodes / 1124 links
- `Generate Square Tower`: 805 nodes / 877 links
- `ChurchFrontTowers`: 792 nodes / 990 links
- `Generate Tower`: 707 nodes / 754 links

The file is a town-building kit: houses, gates, towers, walls, bridges, church
parts, stalls, cliffs, roads, rivers, vegetation, banners, windows, doors, and
roof systems. This is the right quarry for procedural-city doctrine, but the
first accepted bite has to be small enough to verify.

## Accepted Graph: MakeSpiral

Source group: `MakeSpiral`

Geometry Script group: `VG Make Spiral`

Mechanism:

- Create a vertical curve line from `(0, 0, 0)` to `(0, 0, 1)`.
- Resample it to 200 points.
- Use `Index / Point Count` as a normalized parameter `t`.
- Compute angle as `t * Frequency`.
- Compute radius as `Radius + t * HeightRadiusGain`.
- Place each point at:
  - `x = sin(angle) * radius`
  - `y = cos(angle) * radius`
  - `z = t * Height`

Metaphor: the spiral is a screw-thread spine. Stairs, rails, walls, and
decorative ribs can hang from it later, but the first job is to prove the spine
lands in the same places as the source.

## Verification

Run:

```powershell
& 'C:\Program Files (x86)\Steam\steamapps\common\Blender\blender.exe' --background '.\experiments\source-blends\ircss-french-houses.blend' --python '.\tools\verify_ircss_french_houses_translations.py'
```

Results from Blender 5.1.1:

| Case | Source vertices | Translated vertices | Delta | Status |
| --- | ---: | ---: | ---: | --- |
| MakeSpiral curve points | 200 | 200 | 0.0 | accepted |
| PointyGothicCone plain | 36 | 36 | 0.0 | accepted |
| PointyGothicCone with details | 138 | 138 | 0.0 | accepted |

## Accepted Graph: PointyGothicCone

Source group: `PointyGothicCone`

Geometry Script group: `VG Pointy Gothic Cone`

Mechanism:

- Capture each input point position before instancing starts.
- Build a tapered six-sided cone seed from a cylinder.
- Capture an edge-domain trim mask that marks cone cap/body edges.
- Instance one scaled cone at each input point.
- When `SpawnDetails` is enabled, delete the marked cone edges, convert the
  remaining ribs to curves, resample them into detail stations, and instance
  small tapered five-sided spikes along those ribs.
- Orient each detail spike toward the horizontal direction from the source
  point to the current rib point.

Metaphor: the input points are roof pegs. The main cone is the roof cap hung on
each peg; the optional details grow from the cap ribs after the cap is already
real enough to have edges. Build the big readable silhouette first, then let
ornament use that structure.

The spiral case converts the output curve to evaluated points and compares
ordered vertex positions. Cone cases feed identical synthetic point meshes into
the source and translation, then compare sorted evaluated vertices.

## Blockers Exposed

- `GenerateMedialAxisRectangleTopology` is a strong next target, but it uses a
  repeat-zone feedback loop and exposes the repeat `Top` boolean as a group
  output. The current Geometry Script path does not provide a clean linkable
  socket for that output.
- `GenerateBricks` also uses repeat-zone geometry accumulation. Blender's
  source graph can leave the repeat geometry seed implicit; the current DSL
  path exposed the previous-geometry state as `None`.
- `GenerateWindowsFromEdges` uses `For Each Geometry Element` zones.
- `Pole` uses repeat zones and geometry-node gizmos.
- `GenerateArc` and `MakeStairs` exposed a `nodes_to_script` converter bug:
  duplicated keyword arguments for `primary_axis`.
- `WindowBeams` depends on specific upstream edge/curve inputs. A synthetic
  harness could verify its secondary base-point output, but the main beam mesh
  stayed empty for both source and translation. That was rejected as an
  acceptance target.

## Lessons

- City-scale graphs are hierarchies of organs. Start with reusable spines,
  tiles, rails, façade parts, and topology generators before translating a
  thousand-node composer.
- Ornament often needs a structural host. `PointyGothicCone` first creates the
  readable cap silhouette, then derives detail placement from the cap's own
  realized ribs.
- Captures are not optional bookkeeping when instancing starts. The original
  point position and cone edge mask both have to survive later domain changes.
- Converter drafts are still useful for triage: they quickly separate clean
  helpers, repeat-zone blockers, foreach-zone blockers, gizmo-specific groups,
  and false symbol names.
- Verification harnesses must reject empty success. If both source and
  translation output zero visible vertices for the main contract, the harness
  is not proving the graph.

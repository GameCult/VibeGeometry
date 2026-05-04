# Translation: IRCSS French Houses Foothold

## Source

- Repository: https://github.com/IRCSS/Blender-Geometry-Node-French-Houses
- Source file:
  `GeometryNodesFrenchHous.blend`
- Source group translated in this pass:
  - `MakeSpiral`
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

## First Accepted Graph

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

The verifier converts the output curve to evaluated points and compares ordered
vertex positions.

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
- Converter drafts are still useful for triage: they quickly separate clean
  helpers, repeat-zone blockers, foreach-zone blockers, gizmo-specific groups,
  and false symbol names.
- Verification harnesses must reject empty success. If both source and
  translation output zero visible vertices for the main contract, the harness
  is not proving the graph.

# Translation: Blender Shortest-Path Labyrinth

## Source

- Source file:
  https://download.blender.org/demo/geometry-nodes/labyrinth-shortest_path-simon_thommes.blend
- Source group: `Solvable Labyrinth Generator`
- Geometry Script recreation:
  `examples/geometry_script/blender_labyrinth_shortest_path.py`

## Why This Graph

This graph is the first accepted pathfinding translation. It uses grid topology,
randomized edge costs, shortest-edge paths, path selection, path-to-curve
conversion, stored UV attributes, curve radius, and endpoint markers.

## Graph Map

- Build a square grid and store its UV map on the corner domain.
- Mark vertex `0` as the path root.
- Use edge-neighbor count and random booleans to create edge costs.
- Run `Shortest Edge Paths`, convert the result to an edge selection, and
  capture that boolean on the edge domain.
- Subdivide the mesh and delete selected points to carve the walkable graph.
- Run shortest paths again on the carved graph, find the farthest X point on
  the path, and convert the edge path into curves.
- Instance endpoint marker spheres on the path endpoints and capture their
  instance indices as `Start/End`.
- Trim the solution curve by the exposed `Solve` value and capture a `Path`
  boolean on the curve domain.
- Convert maze walls and solution curves into filleted radius curves, then
  convert them to mesh with a circular profile.
- Join endpoint markers, path/wall geometry, and the base grid.

Metaphor: the grid is a street map, random edge costs close some roads, shortest
path draws the route home, and the captured booleans are colored tape left on
the roads so later carving and tube-building know what survived.

## Verification

Run:

```powershell
& 'C:\Program Files (x86)\Steam\steamapps\common\Blender\blender.exe' --background '.\experiments\source-blends\blender-labyrinth-shortest-path.blend' --python '.\tools\verify_labyrinth_translations.py'
```

Results from Blender 5.1.1:

| Case | Source vertices | Translated vertices | Delta | Status |
| --- | ---: | ---: | ---: | --- |
| small unsolved | 22730 | 22730 | 0.0 | accepted |
| small solved | 25484 | 25484 | 0.0 | accepted |

Edge and polygon counts also match for both cases.

## Lessons

- Shortest-path graphs can be translated as topology passes first, visual
  passes second.
- Capture path booleans before subdivision/deletion. Once the graph is carved,
  the original edge selection is no longer obvious.
- Anonymous `Value` nodes are easy for converter output to misassign. The
  source links showed `0.1 / Size` driving radius and `3.0` driving marker
  scale; trusting the generated variable names produced the right topology at
  the wrong size.
- Path outputs are fields. Geometry comparison catches the visible contract;
  scalar/boolean path outputs need a harness only when they become the target.

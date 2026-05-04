# Translation: Blender Raycast Minigame Foothold

## Source

- Source file:
  https://download.blender.org/demo/geometry-nodes/raycast-minigame.blend
- Source groups translated in this pass:
  - `Initial Direction`
  - `Line to be Casted`
  - `Cast Rays`
- Geometry Script recreation:
  `examples/geometry_script/blender_raycast_minigame.py`

## Why This Graph

The full minigame graph is larger, but these helpers isolate the ray pipeline:
make a direction, make a sampled line, cast one ray step, write the hit point
back into the line, and return the reflected direction plus traveled distance.

## Helper Maps

`VG Initial Direction`:

- Start with `(1, 0, 0)` as forward.
- Rotate it by the exposed Euler vector.
- Output the resulting direction vector.

`VG Line To Be Casted`:

- Create a zero-length curve line.
- Move it to `Start Pos`.
- Resample it to `Line Size` points.

`VG Cast Rays`:

- Select the active hit point by `Hit Index`.
- Sample the previous line point.
- Raycast from that previous point into the target geometry along the current
  ray direction.
- Move the active point to the hit position scaled by `0.999`.
- Reflect the ray direction by the hit normal.
- Add hit distance to traveled distance and increment the hit index.

Metaphor: the line is a breadcrumb trail. Each raycast step reads the previous
crumb, throws a beam into the boundary object, places the next crumb just short
of impact, then turns the beam for the next bounce.

## Verification

Run:

```powershell
& 'C:\Program Files (x86)\Steam\steamapps\common\Blender\blender.exe' --background '.\experiments\source-blends\blender-raycast-minigame.blend' --python '.\tools\verify_raycast_translations.py'
```

Results from Blender 5.1.1:

| Case | Source vertices | Translated vertices | Delta | Status |
| --- | ---: | ---: | ---: | --- |
| initial direction harness | 1 | 1 | 0.0 | accepted |
| line to be casted | 5 | 5 | 0.0 | accepted |
| cast rays | 4 | 4 | 0.0 | accepted |

Vector outputs are verified by geometry harnesses: direction drives a single
vertex position, and curve outputs are converted through curve points to
vertices before comparison.

## Lessons

- A ray pipeline is a baton chain: direction, previous point, hit, reflected
  direction, next index.
- Object-dependent groups are better authored with explicit object inputs than
  hard-coded source object names.
- Curve outputs may need curve-to-points harnesses before evaluated mesh
  comparison can see their control points.

# Translation: Blender Index Of Nearest Helpers

## Source

- Source file: https://download.blender.org/demo/geometry-nodes/index_of_nearest.blend
- Source groups translated in this pass:
  - `boundary_step`
  - `update_velocity`
  - `collision_step`
  - `collider_step`
- Geometry Script recreation:
  `examples/geometry_script/blender_index_of_nearest.py`

## Why This Graph

The main `Geometry Nodes` group is a simulation-zone point system. The compact
helper groups are the useful entry point: each one enforces a small physical
rule on point positions or velocity fields.

## Helper Maps

`VG Boundary Step`:

- Compute point position relative to a center vector.
- If distance exceeds boundary radius `B`, normalize the direction and place
  the point on the boundary circle.
- Multiply by `(1, 1, 0)` to keep the constraint planar.

`VG Update Velocity`:

- Estimate movement from current `Position - Last Position`.
- Dampen and flatten the movement vector.
- If it exceeds the velocity cap, normalize to the cap.
- Otherwise blend previous velocity toward the new planar movement.

`VG Collision Step`:

- Find the nearest point with `Index Of Nearest`.
- Evaluate that neighbor's position with `Evaluate at Index`.
- If the current point is closer than its radius, push it away a small planar
  amount.

`VG Collider Step`:

- Read an object's location and scale.
- If a point is inside the object's scaled radius, project it to the collider
  boundary in XY.
- The accepted Geometry Script group exposes the collider as an object input
  instead of hard-coding the source object's name.

Metaphor: these groups are bumpers. They do not decide the whole simulation;
they make one small rule true each tick: stay inside the table, do not move too
fast, stop sitting on another point, stop sitting inside the obstacle.

## Verification

Run:

```powershell
& 'C:\Program Files (x86)\Steam\steamapps\common\Blender\blender.exe' --background '.\experiments\source-blends\blender-index-of-nearest.blend' --python '.\tools\verify_index_of_nearest_translations.py'
```

Results from Blender 5.1.1:

| Case | Source vertices | Translated vertices | Delta | Status |
| --- | ---: | ---: | ---: | --- |
| boundary_step | 6 | 6 | 0.0 | accepted |
| update_velocity harness | 4 | 4 | 0.0 | accepted |
| collision_step point harness | 5 | 5 | 0.0 | accepted |
| collider_step | 6 | 6 | 0.0 | accepted |

The velocity output is verified by driving `Set Position.Position` with the
output vector. The collision output is verified by converting the resulting
points to vertices after the helper group.

## Lessons

- Small simulation helpers are better first translation targets than full
  simulation zones.
- Constraint groups read well when scripted as condition, projection, and
  `Set Position`.
- Invisible vector fields need harnesses. `update_velocity` became observable
  only after using the vector output as point position.
- Point-cloud outputs can evaluate as empty mesh summaries. Convert points to
  vertices in the verifier when point positions are the behavior under test.
- Geometry Script's `mix(...)` helper mapped to the wrong Blender node family
  here. The accepted translation expresses the source vector mix as explicit
  scale-and-add nodes.

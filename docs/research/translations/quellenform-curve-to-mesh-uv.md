# Translation: quellenform Curve To Mesh UV Foothold

## Source

- Repository: https://github.com/quellenform/blender-CurveToMeshUV
- Source file:
  `Curve to Mesh UV v1.7.02.230213-FREE - Blender 3.4+.blend`
- Source group translated in this pass:
  - `Auto Smooth`
- Geometry Script recreation:
  `examples/geometry_script/quellenform_curve_to_mesh_uv.py`

## Why This Graph

The main `Curve to Mesh UV` group is a 126-node utility network with curve
resampling, spline parameters, UV fields, capture attributes, endpoint masks,
domain-size accounting, and named attribute outputs. That is useful quarry, but
not a single-pass snack.

`Auto Smooth` is the small utility attached to that system. It teaches how a
graph can be a surface-finishing gate instead of a shape generator.

## Auto Smooth Map

Source group: `Auto Smooth`

Geometry Script group: `VG Auto Smooth`

Mechanism:

- Read the unsigned mesh edge angle.
- Compare it against the exposed `Angle`.
- AND that threshold result with the existing face smooth state.
- On the edge domain, set shade smooth for already-smooth edges using that
  thresholded condition.
- On the face domain, set shade smooth true for the full mesh.

Metaphor: the group is a polishing gate. It does not build the object. It
decides where the surface may keep a smooth handshake across edges and then
hands the mesh back to the larger utility.

## Verification

Run:

```powershell
& 'C:\Program Files (x86)\Steam\steamapps\common\Blender\blender.exe' --background 'E:\Projects\VibeGeometry\experiments\source-repos\blender-CurveToMeshUV\Curve to Mesh UV v1.7.02.230213-FREE - Blender 3.4+.blend' --python '.\tools\verify_curve_to_mesh_uv_translations.py'
```

Results from Blender 5.1.1:

| Case | Source | Translated | Delta | Status |
| --- | ---: | ---: | ---: | --- |
| Auto Smooth cube vertices | 8 | 8 | 0.0 | accepted |
| Auto Smooth smooth faces | 6 | 6 | exact flags | accepted |

## Lessons

- Not every reusable node group creates form. Some preserve or condition
  surface state for a larger graph.
- Edge-domain and face-domain passes can be stacked deliberately: first decide
  edge continuity, then stamp final face smoothness.
- Utility mega-graphs should be entered through their small helpers first.
  They expose the local contracts the main group relies on.

# Translation: quellenform Curve To Mesh UV Foothold

## Source

- Repository: https://github.com/quellenform/blender-CurveToMeshUV
- Source file:
  `Curve to Mesh UV v1.7.02.230213-FREE - Blender 3.4+.blend`
- Source group translated in this pass:
  - `Auto Smooth`
  - `Curve to Mesh UV`
  - `_258246`
  - `_Title`
- Geometry Script recreation:
  `examples/geometry_script/quellenform_curve_to_mesh_uv.py`

## Why This Graph

The main `Curve to Mesh UV` group is a 126-node utility network with curve
resampling, spline parameters, UV fields, capture attributes, endpoint masks,
domain-size accounting, and named attribute outputs. That is useful quarry, but
not a single-pass snack.

`Auto Smooth` is the small utility attached to that system. The main
`Curve to Mesh UV` group teaches how a utility can output geometry plus fields
that only make sense when sampled on that geometry.

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
| Curve To Mesh UV mesh | 192 | 192 | 0.0 | accepted |
| Curve To Mesh UV UV-field harness | 192 | 192 | 0.0 | accepted |
| Curve To Mesh UV caps-mask harness | 192 | 192 | 0.0 | accepted |
| Demo geometry | 512 | 512 | 0.0 | accepted |
| Title geometry | 12 | 12 | 0.0 | accepted |

## Curve To Mesh UV Map

Source group: `Curve to Mesh UV`

Geometry Script group: `VG Curve To Mesh UV`

Mechanism:

- Resample the source curve and profile curve.
- Capture point triplets and curve indices before converting the curves to a
  mesh.
- Convert the curve/profile pair with `Curve to Mesh`.
- Use corner-domain accumulation to identify cap regions.
- Build side UVs from captured curve/profile point positions.
- Build cap UVs by remapping profile source positions through a bounding box.
- Switch between side UVs and cap UVs with the cap mask.

Metaphor: the curve and profile are two rulers crossing. The mesh is the cloth
stretched across them; the captured indices are the ruler marks that survive
after the cloth exists.

## Demo And Title

`VG Curve To Mesh UV Demo` recreates `_258246` as a simple closed curve/profile
example that calls `VG Curve To Mesh UV`.

`VG Curve To Mesh UV Title` recreates `_Title` as decorative text, plinth, and
backdrop geometry. It is useful mostly because it exercises text curves,
stored UV attributes, face flipping, and map-range UV generation.

## Lessons

- Not every reusable node group creates form. Some preserve or condition
  surface state for a larger graph.
- Edge-domain and face-domain passes can be stacked deliberately: first decide
  edge continuity, then stamp final face smoothness.
- Utility mega-graphs should be entered through their small helpers first.
  They expose the local contracts the main group relies on.
- Field outputs need field-shaped verification. The UV output was checked by
  driving vertex position with the UV vector; the caps mask was checked by
  using it as a deletion selection.
- Utility graphs often return several contracts at once. Verify geometry,
  fields, and masks separately so one passing output does not launder the rest.

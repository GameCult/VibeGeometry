# Translation: Blender Instance Attributes Grass Tuft

## Source

- Source file: https://download.blender.org/demo/geometry-nodes/instance_attribtues.blend
- Source group: `Grass Tuft Generator`
- Geometry Script recreation:
  `examples/geometry_script/blender_instance_attributes.py`

## Why This Graph

This is the first verified scatter/instance/deform sample in the corpus. It is
small enough to translate directly, but it uses the important grown-up trick:
capture instance state before realization, then use that remembered value to
deform the realized geometry.

## Graph Map

Source group: `Grass Tuft Generator`

Geometry Script group: `VG Grass Tuft Generator`

Mechanism:

- Build a triangular-fan disc, subdivide it, and use it as the scatter nursery.
- Compute radial distance from `Position`, remap it through `Map Range`, and
  reuse that falloff for both point density and instance scale.
- Build one blade as a five-point vertical mesh line, convert it to a curve,
  and taper it with `Set Curve Radius` from `1 - Spline Parameter.Factor`.
- Distribute points on the disc with Poisson spacing controlled by thickness
  and density.
- Instance the tapered blade on the points, scale each instance by radial
  falloff, then capture the instance `Position` on the `INSTANCE` domain.
- Realize the instances. The captured root position survives as the center,
  radius sample, and tangent-axis basis for curl.
- Rotate each realized blade position around a tangent axis. Curl grows along
  blade length and is modulated by distance from the tuft center.
- Convert curled curves to mesh with a triangular profile. If a `radius`
  attribute exists, use it as the profile scale.

Metaphor: the disc is a nursery tray, the points are planting holes, each
instance carries a root tag, and realization turns the tray into individual
blades. Curl reads the root tag to bend every blade around its own base instead
of around the world origin.

## Verification

Run:

```powershell
& 'C:\Program Files (x86)\Steam\steamapps\common\Blender\blender.exe' --background '.\experiments\source-blends\blender-instance-attributes.blend' --python '.\tools\verify_instance_attributes_translations.py'
```

Results from Blender 5.1.1:

| Case | Source vertices | Translated vertices | Delta | Status |
| --- | ---: | ---: | ---: | --- |
| default | 45 | 45 | 0.0 | accepted |
| wider curlier seeded | 165 | 165 | 0.0 | accepted |

Both cases also match edge counts, polygon counts, and smooth-face flags.

## Lessons

- Scatter graphs often have three separable layers: seed surface, point field,
  and instance body. Keep them named in script.
- A field can be reused across domains intentionally. Here, radial falloff
  controls both scatter density and final instance scale.
- Captured instance attributes must be explicit under Blender 5.1. Geometry
  Script's generic `capture_attribute(...)` call did not create the required
  capture item here; the verified script uses the explicit
  `_capture_attribute_item(...)` helper.
- `nodes_to_script` recovered the wiring and defaults well enough to debug the
  translation, but its output remains a transcript, not accepted style.

# Lucent Tether Habitat Build

## Source Read

Primary source: `Aetheria/Stories/Lucent Hostage Feed.md` and its interactive
Ghostlight scaffold. Supporting faction read:
`Aetheria/Worldbuilding/Pre-Elysium/Factions/Powers/Major/Lucent Media.md`.
Street-generation priors came from Parish and Muller's SIGGRAPH 2001
`Procedural Modeling of Cities` and Chen, Esch, Wonka, Muller, and Zhang's
SIGGRAPH 2008 `Interactive Procedural Street Modeling`:

- https://people.eecs.berkeley.edu/~sequin/CS285/PAPERS/Parish_Muller01.pdf
- https://peterwonka.net/Publications/pdfs/2008.SG.Chen.InteractiveProceduralStreetModeling.pdf

The story describes a Lucent tether station with a transfer lounge at the
media-eye end of the tether. The lounge has glass walls, an elevator gate, a
waist-high glass rail, a city bubble far below like a sealed aquarium, public
surfaces full of moderation overlays, Mara's private control rail, influencer
side panels, sponsor-risk colors, breach estimates, audience heat, Lucent-gray
security beyond the lounge doors, and a white safe-line two careful steps back
from the elevator-side glass rail.

Lucent's broader faction language matters: its habitats are partially staged
media ecologies. Permissiveness sits over a classification engine. The build
therefore treats surfaces as active controls, not passive decoration.

## Coordinate Contract

- `X`: tether axis, from the city-bubble side to the media-eye lounge.
- `YZ`: spinning city ground plane, orthogonal to the tether.
- `+X`: outward from the city ground toward the dome/headquarters anchor side;
  building height runs along this axis.
- `Y`: lounge width and city ground-plane axis.
- The media-eye lounge is at positive `X`.
- The dome city is at negative `X`, boolean-cut flat at the ground plane, and
  attached to the tether through a prestige anchor plaza.
- Crisis geometry lives inside the lounge: elevator gate and glass rail at the
  threshold, safe-line arc behind it, security beyond the doors.

This is deliberately room-scale plus habitat-scale in one frame. The tether
axis gives the habitat its body; the lounge threshold gives it teeth.

## Implementation

Script:
`examples/geometry_script/lucent_tether_habitat.py`

Generated artifacts:

- `experiments/generated/lucent_tether_habitat/lucent_tether_habitat.blend`
- `experiments/generated/lucent_tether_habitat/lucent_tether_overview.png`
- `experiments/generated/lucent_tether_habitat/lucent_media_eye_lounge.png`
- `experiments/generated/lucent_tether_habitat/lucent_city_bubble_aquarium.png`

Verifier:
`tools/verify_lucent_tether_habitat.py`

Geometry Script group:
`VG Lucent Feed Ribbon`

The group creates a procedural ribbon of moderation/feed geometry orbiting the
media-eye lounge. Python owns the lore table, deterministic city detail,
materials, camera setup, render output, and verification. Geometry Script owns
the inspectable node graph for the feed ribbon so the scene keeps a live
procedural editing surface instead of becoming only a pile of mesh facts.

The accepted revision uses Cycles, not EEVEE. Shader graph work is part of the
build contract: glass gets procedural noise/bump and transmission tuning, metal
and floor materials get micro-surface bump, and Lucent overlay materials use
noise plus color ramps to read as active feed surfaces rather than flat colored
cards.

## Translation Patterns

**Habitat First, Room Second**

The tether and city bubble establish that the lounge is part of a larger
orbital media habitat. Without that, the crisis room becomes a generic glass
office with neon rectangles, which is how worldbuilding goes to die wearing a
lanyard.

```python
add_cylinder_between("lucent_tether_main_cable", TETHER_START, TETHER_END, 0.075, mats["tether"])
add_uv_sphere("city_bubble_sealed_aquarium", CITY_BUBBLE_CENTER, CITY_BUBBLE_SCALE, mats["glass"])
add_yz_disk("city_bubble_flat_ground_surface_disk", CITY_GROUND_X + 0.004, 1.54, mats["park"], segments=128)
```

**Crisis Geometry As Spatial Contract**

The white arc is not decoration. It is a negotiated border between hostage,
glass rail, security, and feed optics. Its object name and verifier check make
that contract explicit.

```python
add_curve_polyline("waist_high_glass_rail", [(5.25, -0.62, -0.08), (5.31, 0.0, -0.035), (5.25, 0.62, -0.08)], 0.027, mats["glass"])
add_curve_polyline("safe_line_white_arc", arc_points((4.82, 0.0, -0.36), 0.68, 208, 332, 36, plane="xy"), 0.015, mats["safe"])
```

**Surfaces Are Interfaces**

Lucent habitat surfaces carry classification pressure: prompts, sponsor risk,
audience heat, delayed influencer panels, and public edit trails. The panels
are separate named objects because future passes may need to animate or route
them independently.

```python
add_panel("feed_ops_prompt_panels", (4.12, -0.88, 0.34), (1.08, 0.028, 0.22), mats["amber"])
add_panel("sponsor_risk_color_stack", (4.74, -0.86, 0.34), (0.15, 0.032, 0.62), mats["risk"])
add_panel("audience_heat_meter", (3.55, -0.84, 0.30), (0.2, 0.032, 0.58), mats["heat"])
```

**Street Fields Beat Grids**

The first city pass used a regular grid. The revised pass uses a small
procedural street field instead: radial avenues grow from the tether anchor,
tangential promenade rings bend around it, and irregular annular parcels fill
between them. This is a compact use of two research lessons: global goals plus
local constraints from L-system city growth, and smoothly varying direction
fields from tensor-field street modeling.

```python
for i in range(16):
    base_angle = TAU * i / 16 + (hash01(i, 4, 11) - 0.5) * 0.12
    line = []
    for step in range(9):
        u = step / 8
        r = 0.12 + 1.42 * smoothstep(u)
        angle = base_angle + 0.08 * pymath.sin(u * TAU + i)
        line.append((ground_x + 0.025, r * pymath.cos(angle), r * pymath.sin(angle)))
    roads.append(line)

for ring_i, radius in enumerate([0.22, 0.42, 0.68, 0.95, 1.2, 1.42]):
    for arc_i in range(3):
        start = TAU * arc_i / 3 + ring_i * 0.21
        end = start + TAU / 3 * (0.72 + 0.12 * hash01(ring_i, arc_i, 23))
        roads.append(arc_points((ground_x + 0.028, 0.0, 0.0), radius, pymath.degrees(start), pymath.degrees(end), 24, plane="yz"))
```

**Land Use Falls Off From The Anchor**

The tether anchor plaza is the prestige attractor. Tallest skyscrapers cluster
around the plug-in point, the middle city steps down into irregular midrise
blocks and parks, and the outer ring fades into green faux-rural cottagecore.
This gives the skyline a social gradient instead of a height-map haircut.

```python
if zone < 0.28:
    verts, faces = prestige_verts, prestige_faces
elif zone < 0.72:
    verts, faces = tower_verts, tower_faces
else:
    verts, faces = cottage_verts, cottage_faces
```

**Sunflower Utility Crest**

The city disk is the disk-floret region. The external crest is the ray-floret
region: alternating solar panels and radiators, Perlin-warped and hinged around
the flat dome base. These are Citadel-scale arms, large enough that a defensive
folded posture can reach toward the far media-eye end of the tether and dwarf
the dome itself.

```python
for petal in range(34):
    center_a = TAU * petal / petals + 0.025 * pymath.sin(petal * 1.7)
    target_verts = solar_verts if petal % 2 == 0 else radiator_verts
    radius = 1.57 + outward_reach * smoothstep(t)
    x = CITY_GROUND_X + arm_length * smoothstep(t)
```

**Shader Graphs Are Geometry Evidence Too**

Flat material defaults can make a procedural scene read like a diagram even
when the object layout is correct. The revised pass spends actual shader nodes
on the surfaces that carry the lore: glass, tether material, and feed panels.

```python
noise = nodes.new("ShaderNodeTexNoise")
bump = nodes.new("ShaderNodeBump")
links.new(noise.outputs["Fac"], bump.inputs["Height"])
links.new(bump.outputs["Normal"], bsdf.inputs["Normal"])
```

## Verification

Command:

```powershell
& 'C:\Program Files (x86)\Steam\steamapps\common\Blender\blender.exe' --background '.\experiments\generated\lucent_tether_habitat\lucent_tether_habitat.blend' --python '.\tools\verify_lucent_tether_habitat.py'
```

Result:

```text
LUCENT_TETHER_VERIFY ok objects=81
```

Render review rejected the first pass because the city bubble read as detached
from the tether and the EEVEE/default-material pass was too shallow. The
accepted revision uses Cycles, explicit bubble-to-tether attachment geometry,
shader-node work, a non-grid city map, the orthogonal spinning city frame,
boolean-cut flat dome base, and an external alternating solar/radiator
sunflower ray-floret crest. The verifier now
checks the attachment objects, Cycles engine, material shader-node types, named
crisis geometry, city coordinate contract, render artifacts, and the `VG Lucent
Feed Ribbon` Geometry Script group.

## Durable Lesson

For Lucent spaces, avoid thinking "set dressing." The set is the power system.
Build public surfaces as rails, rankings, prompt stacks, edits, delayed feeds,
and shader behavior. Then put physical bodies and thresholds where those
abstractions become dangerous. Also: "far below" is not the coordinate system.
For a tether habitat, spin gravity decides the ground plane. Large habitat parts
need visible load paths, or the render becomes a polite lie.

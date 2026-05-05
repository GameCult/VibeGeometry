# Lucent Tether Habitat Build

## Source Read

Primary source: `Aetheria/Stories/Lucent Hostage Feed.md` and its interactive
Ghostlight scaffold. Supporting faction read:
`Aetheria/Worldbuilding/Pre-Elysium/Factions/Powers/Major/Lucent Media.md`.

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
- `Z`: local visual altitude in the scene; the city bubble sits below the
  tether/lounge assembly to preserve the story's "far below" read.
- `Y`: lounge width and panel spread.
- The media-eye lounge is at positive `X`.
- The sealed city bubble is at negative `X`, lower `Z`.
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

## Translation Patterns

**Habitat First, Room Second**

The tether and city bubble establish that the lounge is part of a larger
orbital media habitat. Without that, the crisis room becomes a generic glass
office with neon rectangles, which is how worldbuilding goes to die wearing a
lanyard.

```python
add_cylinder_between("lucent_tether_main_cable", (-6.5, 0.0, 0.0), (6.8, 0.0, 0.0), 0.075, mats["tether"])
add_uv_sphere("city_bubble_sealed_aquarium", (-5.9, 0.0, -3.25), (1.95, 1.95, 1.05), mats["glass"])
add_uv_sphere("media_eye_transfer_lounge_glass_shell", (4.6, 0.0, 0.0), (1.75, 1.05, 0.78), mats["glass"])
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

**The City Bubble Is A Miniature Pressure Field**

The sealed city uses deterministic noise for attention-lit tower variation.
This keeps the aquarium dense without hand-authoring every tower.

```python
n = fbm_2d(ix * 0.27, iy * 0.33, seed=91)
append_box_parts(material_verts, material_faces, (x, y, -3.55 + height * 0.5), axes, size)
```

## Verification

Command:

```powershell
& 'C:\Program Files (x86)\Steam\steamapps\common\Blender\blender.exe' --background '.\experiments\generated\lucent_tether_habitat\lucent_tether_habitat.blend' --python '.\tools\verify_lucent_tether_habitat.py'
```

Result:

```text
LUCENT_TETHER_VERIFY ok objects=59
```

Render review accepted the first-pass composition after label shrinkage. The
overview reads as tether plus city bubble plus media-eye lounge; the lounge
inspection render exposes glass shell, elevator threshold, glass rail,
safe-line, overlay panels, private rail, side panels, and security doors; the
city inspection render reads as an aquarium-bubble miniature city.

## Durable Lesson

For Lucent spaces, avoid thinking "set dressing." The set is the power system.
Build public surfaces as rails, rankings, prompt stacks, edits, and delayed
feeds. Then put physical bodies and thresholds where those abstractions become
dangerous.

# Aetheria Bloom Habitat Build Study

## Source Lore Read

Indexed AetheriaLore sources:

- `Aetheria/Worldbuilding/Pre-Elysium/Technology/Bloom Habitat Anatomy.md`
- `Aetheria/Brainstorming/Technology/Bloom Habitat Engineering Research Notes.md`
- `Aetheria/Brainstorming/Technology/Bloom Habitat Systems Walkthroughs.md`
- `Aetheria/Brainstorming/Technology/Bloom Habitat Open Questions And Red Team.md`

External visual/procedural reference:

- Eric Bruneton, `Modeling and Rendering Rama`, via
  `http://ebruneton.free.fr/rama3/rama.html` and the mirrored text at
  `https://doczz.net/doc/3617854/making-of---rama`

Rama lessons used here:

- sell the cylinder as a whole world, not just a tube
- divide the inner surface into large readable axial/circumferential regions
- generate terrain, roads, rivers, cities, fields, forests, clouds, and lighting
  from layered map logic
- adapt detail to the view instead of pretending a hand-modeled megastructure
  is a sensible authoring target

The build follows the current Bloom model:

- rotating manufactured cylinder, not hollowed asteroid rock
- broad open pressurized commons
- high-radius civic surface with comfortable spin gravity
- despun or partially despun axial hub and light/traffic spire
- despun hub cap and docking port on the center axis
- spun-up spire sheath connected to the rotating spoke frame
- shared cylindrical coordinate helpers so shell districts, spokes, surface
  routes, cloud patches, and endcaps all join in one `x / angle / radius` frame
- expensive spoke interfaces where transit, utilities, cargo, air, and authority
  concentrate
- golden-angle spiral spoke layout with tangential passenger/cargo loops from
  the spun sheath to the civic surface
- frame-transfer arteries between the despun core and spun sheath/spoke frame,
  modeled as curved transfer loops instead of straight shafts
- layered endcaps with pressure faces, terrace rings, slum balconies, and beach
  service structures
- outward stack of utility mat, pressure/structural shell, and aggregate shielding
- layered civic geography: hub-cap terrace slums, hyper-urban favela belts,
  luxury spoke districts, urban mixed belts, suburban/industrial areas,
  industrial/agricultural bands, beach rim, sea band, roads, rivers, cloud
  patches, and service routes
- fractal favela wall detail: batched core shacks, child shacks, patched roofs,
  stilts, diagonal braces, and catwalks climbing the hubward wall
- elaborated spoke plazas and town fields: plaza rings, kiosks, feeder walks,
  nested town houses, and lane networks
- one small Service Ring Kappa marker among many maintenance systems, not the
  compositional focus

## Built Artifact

Script:
`examples/geometry_script/aetheria_bloom_habitat.py`

Generated artifacts:

- `experiments/generated/aetheria_bloom/aetheria_bloom_habitat.blend`
- `experiments/generated/aetheria_bloom/aetheria_bloom_habitat.png`
- `experiments/generated/aetheria_bloom/aetheria_bloom_interior_world.png`

Verification:

```powershell
& 'C:\Program Files (x86)\Steam\steamapps\common\Blender\blender.exe' --background '.\experiments\generated\aetheria_bloom\aetheria_bloom_habitat.blend' --python '.\tools\verify_aetheria_bloom_habitat.py'
```

Result:

```text
AETHERIA_BLOOM_VERIFY ok
AETHERIA_BLOOM_VERIFY group VG Bloom Light Spine 21 31
AETHERIA_BLOOM_VERIFY objects 1102
```

## Procedural Translation Notes

This is intentionally hybrid:

- Python structures the lore-derived coordinate system, layer tables, material
  meanings, mapped civic regions, cameras, labels, and render paths.
- Geometry Script emits `VG Bloom Light Spine`, an inspectable 21-node
  geometry-node group used by a Nodes modifier in the scene.
- bpy builds the full shell surfaces, despun core, hub cap, docking port, spun
  sheath, spiral spoke loops, endcaps, frame-transfer arteries, wrapped region
  patches, city blocks, batched favela/town/plaza detail, roads, rivers, clouds,
  utility lines, service markers, and cameras.

The IRCSS pass paid off in three ways:

- **Edge-first architecture:** the Bloom is built as shell layers, spoke lines,
  transfer arteries, region patches, utility routes, and service markers before
  local dressing.
- **Curves as attachment rails:** roads, rivers, and utility routes are curves
  wrapped onto the inner cylinder or service layers; spiral spokes and
  frame-transfer arteries curve between rotating frames instead of pretending
  the hub/spire interface is a straight elevator.
- **Coordinate space as contract:** `surface_point`, `cyl_point`, radial axes,
  and tangents let each subsystem attach to the same cylindrical frame. That
  makes twisted forms useful instead of decorative: the loop can bend, but its
  endpoints still land on the sheath, shell, cap, or district layer.
- **Golden-angle filling:** spoke placement uses the sunflower trick, stepping
  by the golden angle along the axis so each new spoke avoids the previous
  radial lanes while still reading as one organic exchange network.
- **Batched micro-detail:** rickety visual detail should not mean one Blender
  object per plank. The favela/town pass batches many boxes into shared meshes
  and many brace/catwalk paths into shared curve objects, preserving detail
  without making scene generation stall.
- **Python as orchestration:** the cylinder layers, region maps, city blocks,
  social-gradient bands, roads, rivers, forests, clouds, and spokes come from
  small tables and named helpers rather than copied object placement.

## Current Limits

- The build is a spatial systems study, not final art.
- The civic surface is still a symbolic map-layer world, but the hubward favela
  now has enough nested structure to read as precarious built habitat.
- The current whole-Bloom view is less skeletal, but still a study. It needs
  denser horizon city detail and better art-directed lighting before it earns
  the word cinematic without fraud.
- Only the light spine is emitted through Geometry Script so far. The next pass
  should move the shared coordinate helpers plus spiral spoke/artery network
  into reusable Geometry Script groups.

"""Build the Lucent tether habitat from the Ghostlight hostage-feed scene.

Spatial contract from the story:

- The tether is the long station spine.
- The transfer lounge sits at the media-eye end of the tether.
- The city bubble is far below, readable as a sealed aquarium.
- The lounge threshold carries an elevator gate, waist-high glass rail, and
  a white safe-line arc two careful steps back from the rail.
- Lucent surfaces are never only surfaces: overlays, rails, prompts, status
  edits, influencer side panels, and audience heat are part of the room.
"""

import math as pymath
from pathlib import Path

try:
    from tools.geometry_script_loader import load_repo_geometry_script
except ModuleNotFoundError:
    import sys

    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
    from tools.geometry_script_loader import load_repo_geometry_script

load_repo_geometry_script()

from geometry_script import *  # noqa: F403 - Geometry Script exposes node functions as DSL globals.
from mathutils import Vector
from vibegeometry import (
    add_box,
    add_curve_polyline,
    add_cylinder_between,
    add_material,
    add_mesh_parts,
    add_multi_polyline_curve,
    aim_camera,
    append_box_parts,
    clear_scene,
    fbm_2d,
    hash01,
    smoothstep,
)


TAU = pymath.tau
OUT_DIR = Path("experiments/generated/lucent_tether_habitat")
CITY_GROUND_X = -5.45
CITY_BUBBLE_CENTER = (-4.95, 0.0, 0.0)
CITY_BUBBLE_SCALE = (1.0, 1.95, 1.95)
CITY_TETHER_JUNCTION = (CITY_GROUND_X, 0.0, 0.0)
TETHER_START = CITY_TETHER_JUNCTION
TETHER_END = (6.8, 0.0, 0.0)
MEDIA_EYE_CENTER = (4.6, 0.0, 0.0)


@tree("VG Lucent Feed Ribbon")
def vg_lucent_feed_ribbon(
    length: Float = 11.5,
    radius: Float = 1.25,
    turns: Float = 2.25,
    wave: Float = 0.22,
    thickness: Float = 0.025,
):
    """Procedural moderation/feed rail orbiting the media-eye lounge."""

    rail = curve_line(mode=CurveLine.Mode.POINTS, start=(-5.75, 0.0, 0.0), end=(5.75, 0.0, 0.0))
    samples = resample_curve(keep_last_segment=True, curve=rail, mode="Count", count=360, length=0.1)
    point_count = domain_size(component="CURVE", geometry=samples).point_count
    t = math(operation=Math.Operation.DIVIDE, value=(index(), point_count))
    theta = math(operation=Math.Operation.MULTIPLY, value=(t, math(operation=Math.Operation.MULTIPLY, value=(turns, TAU))))
    x = math(operation=Math.Operation.SUBTRACT, value=(math(operation=Math.Operation.MULTIPLY, value=(t, length)), math(operation=Math.Operation.DIVIDE, value=(length, 2.0))))
    pulse = math(operation=Math.Operation.SINE, value=math(operation=Math.Operation.MULTIPLY, value=(theta, 4.0)))
    animated_radius = math(operation=Math.Operation.ADD, value=(radius, math(operation=Math.Operation.MULTIPLY, value=(pulse, wave))))
    y = math(operation=Math.Operation.MULTIPLY, value=(math(operation=Math.Operation.COSINE, value=theta), animated_radius))
    z = math(operation=Math.Operation.MULTIPLY, value=(math(operation=Math.Operation.SINE, value=theta), animated_radius))
    positioned = set_position(geometry=samples, position=combine_xyz(x=x, y=y, z=z), offset=(0.0, 0.0, 0.0))
    profile = curve_circle(mode=CurveCircle.Mode.RADIUS, resolution=8, radius=thickness)
    return {"Geometry": curve_to_mesh(curve=positioned, profile_curve=profile, fill_caps=True)}


def mat(name, color, emission=False, strength=0.0, alpha=1.0):
    return add_material(name, color, emission=emission, strength=strength, alpha=alpha)


def socket_set(node, socket_name, value):
    if socket_name in node.inputs:
        node.inputs[socket_name].default_value = value


def add_shader_bump(material, scale=38.0, detail=7.0, strength=0.05, distance=0.08):
    nodes = material.node_tree.nodes
    links = material.node_tree.links
    bsdf = nodes.get("Principled BSDF")
    if not bsdf:
        return
    noise = nodes.new("ShaderNodeTexNoise")
    noise.name = f"{material.name} procedural micro-noise"
    noise.inputs["Scale"].default_value = scale
    noise.inputs["Detail"].default_value = detail
    noise.inputs["Roughness"].default_value = 0.58
    bump = nodes.new("ShaderNodeBump")
    bump.name = f"{material.name} shader bump"
    bump.inputs["Strength"].default_value = strength
    bump.inputs["Distance"].default_value = distance
    links.new(noise.outputs["Fac"], bump.inputs["Height"])
    links.new(bump.outputs["Normal"], bsdf.inputs["Normal"])


def add_panel_shader_graph(material, base_color, emission_color, pulse_color):
    nodes = material.node_tree.nodes
    links = material.node_tree.links
    bsdf = nodes.get("Principled BSDF")
    if not bsdf:
        return
    noise = nodes.new("ShaderNodeTexNoise")
    noise.name = f"{material.name} scanline noise"
    noise.inputs["Scale"].default_value = 55.0
    noise.inputs["Detail"].default_value = 10.0
    ramp = nodes.new("ShaderNodeValToRGB")
    ramp.name = f"{material.name} risk-color ramp"
    ramp.color_ramp.elements[0].position = 0.28
    ramp.color_ramp.elements[0].color = base_color
    ramp.color_ramp.elements[1].position = 1.0
    ramp.color_ramp.elements[1].color = pulse_color
    links.new(noise.outputs["Fac"], ramp.inputs["Fac"])
    links.new(ramp.outputs["Color"], bsdf.inputs["Base Color"])
    if "Emission Color" in bsdf.inputs:
        bsdf.inputs["Emission Color"].default_value = emission_color
    if "Emission Strength" in bsdf.inputs:
        bsdf.inputs["Emission Strength"].default_value = 0.65


def make_glass_shader(material, tint=(0.38, 0.72, 1.0, 0.28)):
    material.use_nodes = True
    material.blend_method = "BLEND"
    material.use_screen_refraction = True
    material.show_transparent_back = True
    nodes = material.node_tree.nodes
    bsdf = nodes.get("Principled BSDF")
    if not bsdf:
        return
    socket_set(bsdf, "Base Color", tint)
    socket_set(bsdf, "Alpha", tint[3])
    socket_set(bsdf, "Roughness", 0.05)
    socket_set(bsdf, "Metallic", 0.0)
    socket_set(bsdf, "Transmission Weight", 0.55)
    socket_set(bsdf, "IOR", 1.47)
    add_shader_bump(material, scale=96.0, detail=8.0, strength=0.018, distance=0.045)


def enrich_shader_graphs(mats):
    make_glass_shader(mats["glass"])
    add_shader_bump(mats["tether"], scale=70.0, detail=9.0, strength=0.075, distance=0.035)
    add_shader_bump(mats["lucent_gray"], scale=45.0, detail=6.0, strength=0.045, distance=0.035)
    add_shader_bump(mats["floor"], scale=24.0, detail=7.0, strength=0.035, distance=0.025)
    add_shader_bump(mats["city"], scale=82.0, detail=4.0, strength=0.03, distance=0.02)
    add_shader_bump(mats["prestige"], scale=64.0, detail=7.0, strength=0.025, distance=0.018)
    add_shader_bump(mats["park"], scale=18.0, detail=6.0, strength=0.045, distance=0.028)
    add_shader_bump(mats["cottage"], scale=31.0, detail=5.0, strength=0.055, distance=0.03)
    add_shader_bump(mats["plaza"], scale=36.0, detail=6.0, strength=0.028, distance=0.02)
    add_shader_bump(mats["solar_panel"], scale=42.0, detail=8.0, strength=0.028, distance=0.018)
    add_shader_bump(mats["radiator"], scale=58.0, detail=9.0, strength=0.035, distance=0.02)
    for key, pulse in [
        ("cyan", (0.65, 1.0, 1.0, 1.0)),
        ("amber", (1.0, 0.88, 0.32, 1.0)),
        ("risk", (1.0, 0.45, 0.86, 1.0)),
        ("heat", (1.0, 0.18, 0.08, 1.0)),
        ("overlay_blue", (0.7, 0.86, 1.0, 1.0)),
    ]:
        add_panel_shader_graph(mats[key], mats[key].diffuse_color, mats[key].diffuse_color, pulse)


def add_uv_sphere(name, loc, scale, material, segments=48, rings=24):
    import bpy

    bpy.ops.mesh.primitive_uv_sphere_add(segments=segments, ring_count=rings, radius=1.0, location=loc)
    obj = bpy.context.object
    obj.name = name
    obj.data.name = name + "Mesh"
    obj.scale = scale
    obj.data.materials.append(material)
    obj.show_transparent = True
    return obj


def add_torus(name, loc, major_radius, minor_radius, material, rotation=(0.0, 0.0, 0.0), segments=96):
    import bpy

    bpy.ops.mesh.primitive_torus_add(
        major_segments=segments,
        minor_segments=10,
        major_radius=major_radius,
        minor_radius=minor_radius,
        location=loc,
        rotation=rotation,
    )
    obj = bpy.context.object
    obj.name = name
    obj.data.name = name + "Mesh"
    obj.data.materials.append(material)
    return obj


def add_label(name, text, loc, size, material, rotation=(pymath.radians(65), 0.0, pymath.radians(0))):
    import bpy

    bpy.ops.object.text_add(location=loc, rotation=rotation)
    obj = bpy.context.object
    obj.name = name
    obj.data.body = text
    obj.data.align_x = "CENTER"
    obj.data.align_y = "CENTER"
    obj.data.size = size
    obj.data.materials.append(material)
    return obj


def arc_points(center, radius, start_deg, end_deg, steps, plane="xy", wobble=0.0):
    points = []
    for i in range(steps + 1):
        t = i / steps
        a = pymath.radians(start_deg + (end_deg - start_deg) * t)
        w = wobble * pymath.sin(t * TAU * 2.0)
        r = radius + w
        if plane == "xy":
            points.append((center[0] + r * pymath.cos(a), center[1] + r * pymath.sin(a), center[2]))
        elif plane == "yz":
            points.append((center[0], center[1] + r * pymath.cos(a), center[2] + r * pymath.sin(a)))
        else:
            points.append((center[0] + r * pymath.cos(a), center[1], center[2] + r * pymath.sin(a)))
    return points


def annular_sector_points(center, inner_radius, outer_radius, start_angle, end_angle, plane="xy"):
    if plane == "yz":
        x, y, z = center
        return [
            (x, y + inner_radius * pymath.cos(start_angle), z + inner_radius * pymath.sin(start_angle)),
            (x, y + outer_radius * pymath.cos(start_angle), z + outer_radius * pymath.sin(start_angle)),
            (x, y + outer_radius * pymath.cos(end_angle), z + outer_radius * pymath.sin(end_angle)),
            (x, y + inner_radius * pymath.cos(end_angle), z + inner_radius * pymath.sin(end_angle)),
        ]
    return [
        (center[0] + inner_radius * pymath.cos(start_angle), center[1] + inner_radius * pymath.sin(start_angle), center[2]),
        (center[0] + outer_radius * pymath.cos(start_angle), center[1] + outer_radius * pymath.sin(start_angle), center[2]),
        (center[0] + outer_radius * pymath.cos(end_angle), center[1] + outer_radius * pymath.sin(end_angle), center[2]),
        (center[0] + inner_radius * pymath.cos(end_angle), center[1] + inner_radius * pymath.sin(end_angle), center[2]),
    ]


def add_flat_polygon(name, verts, material):
    return add_mesh_parts(name, verts, [(0, 1, 2, 3)], material)


def add_yz_disk(name, x, radius, material, segments=96):
    verts = [(x, 0.0, 0.0)]
    faces = []
    for i in range(segments):
        a = TAU * i / segments
        verts.append((x, radius * pymath.cos(a), radius * pymath.sin(a)))
    for i in range(segments):
        faces.append((0, i + 1, 1 + ((i + 1) % segments)))
    return add_mesh_parts(name, verts, faces, material)


def add_dome_base_crest(mats):
    solar_verts, solar_faces = [], []
    radiator_verts, radiator_faces = [], []
    petals = 18
    radial_steps = 8
    for petal in range(petals):
        center_a = TAU * petal / petals + 0.025 * pymath.sin(petal * 1.7)
        width = TAU / petals * (0.72 + 0.24 * hash01(petal, 0, 251))
        outward_reach = 0.8 + 0.42 * fbm_2d(pymath.cos(center_a) * 2.1, pymath.sin(center_a) * 2.1, seed=177)
        arm_length = (TETHER_END[0] - CITY_GROUND_X) * (0.88 + 0.08 * hash01(petal, 12, 277))
        twist = 0.18 * (hash01(petal, 4, 271) - 0.5)
        target_verts = solar_verts if petal % 2 == 0 else radiator_verts
        target_faces = solar_faces if petal % 2 == 0 else radiator_faces
        petal_base = len(target_verts)
        for side in (-1.0, 1.0):
            for step in range(radial_steps + 1):
                t = step / radial_steps
                edge = (0.55 + 0.45 * smoothstep(1.0 - abs(t - 0.55) * 2.0))
                noise = fbm_2d(petal * 0.41, step * 0.73 + side, seed=303) - 0.5
                local_width = width * (1.0 - 0.42 * smoothstep(t)) * edge + noise * 0.018
                a = center_a + side * local_width * 0.5 + twist * t
                radius = 1.62 + outward_reach * smoothstep(t) + 0.05 * noise
                # External defensive arms stow by folding along the tether
                # toward the far media-eye end; deployed they read as Citadel
                # scale ray florets rather than petals glued to the dome.
                x = CITY_GROUND_X + arm_length * smoothstep(t)
                y = radius * pymath.cos(a)
                z = radius * pymath.sin(a)
                target_verts.append((x, y, z))
        for step in range(radial_steps):
            target_faces.append((petal_base + step, petal_base + step + 1, petal_base + radial_steps + 2 + step + 1, petal_base + radial_steps + 2 + step))
    solar = add_mesh_parts("city_bubble_solar_panel_ray_florets", solar_verts, solar_faces, mats["solar_panel"])
    radiator = add_mesh_parts("city_bubble_radiator_ray_florets", radiator_verts, radiator_faces, mats["radiator"])
    solar.show_transparent = True
    radiator.show_transparent = True
    return solar, radiator


def add_floor_patch(name, center, width, depth, material, z=0.0):
    return add_box(name, (center[0], center[1], z), ((1, 0, 0), (0, 1, 0), (0, 0, 1)), (width, depth, 0.035), material)


def add_panel(name, loc, size, material, angle=0.0, lean=0.0):
    x_axis = (pymath.cos(angle), pymath.sin(angle), 0)
    y_axis = (-pymath.sin(angle), pymath.cos(angle), lean)
    z_axis = (0, -lean, 1)
    return add_box(name, loc, (x_axis, y_axis, z_axis), size, material)


def add_habitat_cable_bundle(mats):
    add_cylinder_between("lucent_tether_main_cable", TETHER_START, TETHER_END, 0.075, mats["tether"], vertices=24)
    add_cylinder_between("lucent_tether_spin_reference_core", (-6.25, 0.18, 0.16), (6.25, 0.18, 0.16), 0.023, mats["cyan"], vertices=10)
    add_cylinder_between("lucent_tether_service_darkline", (-6.25, -0.16, -0.12), (6.25, -0.16, -0.12), 0.018, mats["dark"], vertices=8)
    for i, x in enumerate([-4.9, -3.2, -1.4, 0.4, 2.1, 3.9, 5.4]):
        add_torus(
            f"slow_rotation_reference_ring_{i:02d}",
            (x, 0.0, 0.0),
            0.42 + 0.04 * (i % 3),
            0.008,
            mats["soft_white"],
            rotation=(0.0, pymath.radians(90), 0.0),
            segments=64,
        )


def add_city_bubble(mats):
    import bpy

    bubble = add_uv_sphere("city_bubble_sealed_aquarium", CITY_BUBBLE_CENTER, CITY_BUBBLE_SCALE, mats["glass"], 64, 32)
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(CITY_GROUND_X - 2.0, 0.0, 0.0))
    cutter = bpy.context.object
    cutter.name = "city_bubble_flattening_boolean_cutter"
    cutter.dimensions = (4.0, 5.0, 5.0)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    boolean = bubble.modifiers.new("boolean cut flat ground base", "BOOLEAN")
    boolean.operation = "DIFFERENCE"
    boolean.object = cutter
    bpy.context.view_layer.objects.active = bubble
    bubble.select_set(True)
    bpy.ops.object.modifier_apply(modifier=boolean.name)
    cutter.hide_viewport = True
    cutter.hide_render = True
    add_torus(
        "city_bubble_pressure_equator",
        (CITY_GROUND_X + 0.02, 0.0, 0.0),
        1.95,
        0.022,
        mats["cyan"],
        rotation=(0.0, pymath.radians(90), 0.0),
        segments=128,
    )
    add_torus(
        "city_bubble_flat_ground_rim",
        (CITY_GROUND_X + 0.01, 0.0, 0.0),
        1.42,
        0.018,
        mats["aquarium"],
        rotation=(0.0, pymath.radians(90), 0.0),
        segments=96,
    )
    add_yz_disk("city_bubble_flat_ground_surface_disk", CITY_GROUND_X + 0.004, 1.54, mats["park"], segments=128)

    ground_x = CITY_GROUND_X + 0.018
    tower_verts, tower_faces = [], []
    prestige_verts, prestige_faces = [], []
    cottage_verts, cottage_faces = [], []
    park_faces = []
    roads = []

    # Street field: major avenues radiate from the tether anchor, then bend
    # toward a tangential promenade field. This borrows the tensor-field idea
    # without pretending this tiny bubble needs a whole GIS stack.
    for i in range(16):
        base_angle = TAU * i / 16 + (hash01(i, 4, 11) - 0.5) * 0.12
        line = []
        for step in range(9):
            u = step / 8
            r = 0.12 + 1.42 * smoothstep(u)
            drift = 0.22 * pymath.sin(u * pymath.pi) * (hash01(i, step, 17) - 0.5)
            angle = base_angle + drift + 0.08 * pymath.sin(u * TAU + i)
            line.append((ground_x + 0.025, r * pymath.cos(angle), r * pymath.sin(angle)))
        roads.append(line)
    for ring_i, radius in enumerate([0.22, 0.42, 0.68, 0.95, 1.2, 1.42]):
        for arc_i in range(3):
            start = TAU * arc_i / 3 + ring_i * 0.21
            end = start + TAU / 3 * (0.72 + 0.12 * hash01(ring_i, arc_i, 23))
            roads.append(arc_points((ground_x + 0.028, 0.0, 0.0), radius, pymath.degrees(start), pymath.degrees(end), 24, plane="yz", wobble=0.018))

    # Anchor plaza: the tether physically lands on the ground surface. The
    # skyline knows where power plugs in.
    add_yz_disk("city_bubble_tether_anchor_plaza_core", ground_x + 0.012, 0.24, mats["plaza"], segments=48)
    add_torus("city_bubble_anchor_plaza_ring", (ground_x + 0.025, 0.0, 0.0), 0.32, 0.011, mats["soft_white"], rotation=(0.0, pymath.radians(90), 0.0), segments=96)
    add_dome_base_crest(mats)

    rings = [0.24, 0.42, 0.62, 0.84, 1.08, 1.31, 1.52]
    for ring in range(len(rings) - 1):
        inner = rings[ring]
        outer = rings[ring + 1]
        zone = ring / (len(rings) - 2)
        cells = int(18 + ring * 7)
        for cell in range(cells):
            u0 = cell / cells
            u1 = (cell + 0.78 + 0.34 * hash01(ring, cell, 33)) / cells
            a0 = TAU * u0 + 0.1 * pymath.sin(ring * 1.7)
            a1 = TAU * u1 + 0.07 * (hash01(cell, ring, 35) - 0.5)
            n = fbm_2d(ring * 0.61, cell * 0.29, seed=91)
            park_bias = fbm_2d(pymath.cos((a0 + a1) * 0.5) * 2.2 + ring, pymath.sin((a0 + a1) * 0.5) * 2.2, seed=121)
            if zone > 0.32 and park_bias > 0.68:
                park_faces.extend(annular_sector_points((ground_x + 0.012, 0.0, 0.0), inner + 0.025, outer - 0.02, a0 + 0.025, a1 - 0.018, plane="yz"))
                continue
            r = inner + (outer - inner) * (0.45 + 0.22 * (n - 0.5))
            angle = (a0 + a1) * 0.5
            radial_axis = (0.0, pymath.cos(angle), pymath.sin(angle))
            tangent_axis = (0.0, -pymath.sin(angle), pymath.cos(angle))
            radial_width = max(0.04, (outer - inner) * (0.36 + 0.28 * n))
            tangential_width = max(0.045, r * (a1 - a0) * (0.55 + 0.3 * hash01(cell, ring, 37)))
            if zone < 0.28:
                height = 0.5 + 0.62 * n
                verts, faces = prestige_verts, prestige_faces
                size = (tangential_width * 0.72, radial_width * 0.8, height)
                loc = (ground_x + height * 0.5, r * pymath.cos(angle), r * pymath.sin(angle))
            elif zone < 0.72:
                height = 0.16 + 0.36 * n * (1.0 - zone * 0.35)
                verts, faces = tower_verts, tower_faces
                size = (tangential_width * 0.82, radial_width * 0.9, height)
                loc = (ground_x + height * 0.5, r * pymath.cos(angle), r * pymath.sin(angle))
            else:
                if n < 0.38:
                    park_faces.extend(annular_sector_points((ground_x + 0.012, 0.0, 0.0), inner + 0.02, outer - 0.02, a0 + 0.02, a1 - 0.02, plane="yz"))
                    continue
                height = 0.045 + 0.07 * n
                verts, faces = cottage_verts, cottage_faces
                size = (tangential_width * 0.55, radial_width * 0.6, height)
                loc = (ground_x + height * 0.5, r * pymath.cos(angle), r * pymath.sin(angle))
            append_box_parts(verts, faces, loc, (tangent_axis, radial_axis, (1, 0, 0)), size)

    if park_faces:
        verts = park_faces
        faces = [(i, i + 1, i + 2, i + 3) for i in range(0, len(verts), 4)]
        add_mesh_parts("city_bubble_interspersed_park_cells", verts, faces, mats["park"])
    add_mesh_parts("city_bubble_prestige_anchor_skyscrapers", prestige_verts, prestige_faces, mats["prestige"])
    add_mesh_parts("city_bubble_midcity_irregular_blocks", tower_verts, tower_faces, mats["city"])
    add_mesh_parts("city_bubble_faux_rural_cottagecore_edge", cottage_verts, cottage_faces, mats["cottage"])
    add_multi_polyline_curve("city_bubble_tensor_field_street_network", roads, 0.006, mats["soft_white"], resolution=3)
    add_multi_polyline_curve(
        "city_bubble_prestige_plaza_spokes",
        [[(ground_x + 0.04, 0.0, 0.0), road[-1]] for road in roads[:16:2]],
        0.012,
        mats["cyan"],
        resolution=3,
    )


def add_city_bubble_tether_attachment(mats):
    x, y, z = CITY_TETHER_JUNCTION
    top = (x, y, z)
    collar = (CITY_GROUND_X + 0.08, 0.0, 0.0)
    plaza = (CITY_GROUND_X + 0.08, 0.0, 0.0)
    keel = (CITY_GROUND_X - 0.12, 0.0, 0.0)
    add_cylinder_between("city_bubble_tether_load_spine", top, plaza, 0.045, mats["tether"], vertices=16)
    add_cylinder_between("city_bubble_elevator_umbilical", (x + 0.14, 0.0, -0.05), (plaza[0] + 0.14, 0.0, -0.05), 0.022, mats["cyan"], vertices=10)
    add_cylinder_between("city_bubble_elevator_drop_to_anchor_plaza", (plaza[0] + 0.14, 0.0, -0.05), (plaza[0] + 0.14, 0.0, 0.18), 0.018, mats["cyan"], vertices=10)
    add_torus(
        "city_bubble_upper_tether_collar",
        collar,
        0.52,
        0.025,
        mats["soft_white"],
        rotation=(0.0, pymath.radians(90), 0.0),
        segments=96,
    )
    add_box("city_bubble_tether_transfer_node", (x + 0.08, 0.0, 0.0), ((1, 0, 0), (0, 1, 0), (0, 0, 1)), (0.42, 0.34, 0.34), mats["lucent_gray"])
    for i, angle in enumerate([0.0, pymath.pi / 2, pymath.pi, pymath.pi * 1.5]):
        y2 = pymath.cos(angle) * 1.35
        z2 = pymath.sin(angle) * 1.35
        x2 = CITY_GROUND_X + 0.18 + 0.22 * pymath.sin(angle * 2.0)
        add_cylinder_between(f"city_bubble_suspension_stay_{i:02d}", top, (x2, y2, z2), 0.012, mats["soft_white"], vertices=6)
        add_curve_polyline(
            f"city_bubble_tension_trace_{i:02d}",
            [top, ((top[0] + x2) * 0.5, y2 * 0.35, z2 * 0.35), (x2, y2, z2)],
            0.004,
            mats["cyan"],
            resolution=3,
        )
    add_cylinder_between("city_bubble_under_keel_counterweight", keel, (keel[0] - 0.75, keel[1], keel[2]), 0.028, mats["dark"], vertices=10)


def add_media_eye_lounge(mats):
    add_uv_sphere("media_eye_transfer_lounge_glass_shell", MEDIA_EYE_CENTER, (1.75, 1.05, 0.78), mats["glass"], 64, 32)
    add_torus(
        "media_eye_lounge_structural_lash_ring",
        (4.6, 0.0, 0.0),
        1.07,
        0.025,
        mats["soft_white"],
        rotation=(0.0, pymath.radians(90), 0.0),
        segments=128,
    )
    add_torus(
        "media_eye_public_camera_eye",
        (5.58, 0.0, 0.08),
        0.42,
        0.022,
        mats["cyan"],
        rotation=(0.0, pymath.radians(90), 0.0),
        segments=96,
    )
    add_floor_patch("transfer_lounge_curved_floor_slab", (4.58, 0.0), 2.55, 1.36, mats["floor"], z=-0.42)
    for i, y in enumerate([-0.56, -0.28, 0.0, 0.28, 0.56]):
        add_curve_polyline(
            f"floor_keeps_remembering_physics_arc_{i:02d}",
            arc_points((4.58, y, -0.385), 0.34 + abs(y) * 0.15, 190, 350, 18, plane="xz"),
            0.004,
            mats["soft_white"],
            resolution=2,
        )

    # The crisis geometry: elevator glass rail at the threshold, and the safe
    # line behind it. This is the room's moral diagram, unfortunately built
    # out of real materials and several departments' bad incentives.
    add_box("elevator_gate_threshold", (5.42, 0.0, -0.12), ((1, 0, 0), (0, 1, 0), (0, 0, 1)), (0.11, 1.36, 0.82), mats["lucent_gray"])
    add_curve_polyline("waist_high_glass_rail", [(5.25, -0.62, -0.08), (5.31, 0.0, -0.035), (5.25, 0.62, -0.08)], 0.027, mats["glass"], resolution=3)
    add_curve_polyline("safe_line_white_arc", arc_points((4.82, 0.0, -0.36), 0.68, 208, 332, 36, plane="xy"), 0.015, mats["safe"], resolution=3)
    add_box("elevator_side_glass_warning_strip", (5.18, 0.0, -0.31), ((1, 0, 0), (0, 1, 0), (0, 0, 1)), (0.025, 1.2, 0.03), mats["amber"])

    add_panel("moderation_overlay_wall_public_status", (4.2, -0.82, 0.12), (1.18, 0.026, 0.46), mats["overlay_blue"], angle=0.0, lean=0.18)
    add_panel("feed_ops_prompt_panels", (4.12, -0.88, 0.34), (1.08, 0.028, 0.22), mats["amber"], angle=0.0, lean=0.18)
    add_panel("sponsor_risk_color_stack", (4.74, -0.86, 0.34), (0.15, 0.032, 0.62), mats["risk"], angle=0.0, lean=0.18)
    add_panel("audience_heat_meter", (3.55, -0.84, 0.30), (0.2, 0.032, 0.58), mats["heat"], angle=0.0, lean=0.18)
    add_panel("pippa_delayed_side_panel", (3.55, 0.87, 0.26), (0.54, 0.03, 0.38), mats["pippa"], angle=0.0, lean=-0.16)
    add_panel("brant_delayed_side_panel", (4.34, 0.9, 0.28), (0.58, 0.03, 0.42), mats["brant"], angle=0.0, lean=-0.16)
    add_panel("public_edit_trail_checksum_panel", (4.92, -0.84, -0.12), (0.6, 0.025, 0.16), mats["cyan"], angle=0.0, lean=0.08)

    add_curve_polyline("mara_private_control_rail", [(3.32, -0.63, -0.22), (4.1, -0.69, -0.12), (5.05, -0.56, -0.2)], 0.018, mats["private"], resolution=3)
    for i in range(9):
        x = 3.42 + i * 0.18
        z = -0.18 + 0.08 * pymath.sin(i * 0.9)
        material = mats["risk"] if i in {2, 5, 8} else mats["cyan"] if i % 2 else mats["amber"]
        add_box(f"mara_private_rail_control_chip_{i:02d}", (x, -0.68, z), ((1, 0, 0), (0, 1, 0), (0, 0, 1)), (0.09, 0.022, 0.045), material)

    add_box("security_lounge_doors", (3.12, 0.0, -0.08), ((1, 0, 0), (0, 1, 0), (0, 0, 1)), (0.11, 1.12, 0.72), mats["lucent_gray"])
    for i, y in enumerate([-0.42, -0.14, 0.14, 0.42]):
        add_box(f"lucent_gray_security_waiting_marker_{i:02d}", (2.83, y, -0.2), ((1, 0, 0), (0, 1, 0), (0, 0, 1)), (0.08, 0.08, 0.36), mats["security"])


def add_overlay_ribbons_and_signage(mats):
    import bpy

    group = bpy.data.node_groups.get("VG Lucent Feed Ribbon")
    mesh = bpy.data.meshes.new("LucentFeedRibbonCarrierMesh")
    carrier = bpy.data.objects.new("GN_Lucent_Feed_Ribbon_Carrier", mesh)
    bpy.context.collection.objects.link(carrier)
    carrier.location = (4.45, 0.0, 0.0)
    carrier.rotation_euler[1] = pymath.radians(90)
    carrier.scale = (0.32, 0.32, 0.32)
    carrier.data.materials.append(mats["cyan"])
    mod = carrier.modifiers.new("VG Lucent Feed Ribbon", "NODES")
    mod.node_group = group

    for i, radius in enumerate([0.92, 1.12, 1.34]):
        points = []
        for j in range(72):
            t = j / 71
            a = TAU * t + i * 0.7
            x = 4.55 + (t - 0.5) * 1.8
            y = radius * pymath.cos(a) * 0.82
            z = 0.12 + radius * pymath.sin(a) * 0.46
            points.append((x, y, z))
        add_curve_polyline(f"manual_status_ribbon_orbit_{i:02d}", points, 0.006 + i * 0.002, mats["overlay_blue"], resolution=4)

    labels = [
        ("label_media_eye", "media-eye transfer lounge", (4.65, -1.52, 0.7), 0.082),
        ("label_safe_line", "safe-line / glass rail", (5.18, 1.2, -0.34), 0.066),
        ("label_city_bubble", "orthogonal dome city / sunflower crest", (-5.38, -1.82, -1.72), 0.095),
        ("label_lucent_surfaces", "surfaces as controls, rankings, edits", (1.6, -0.82, 0.5), 0.082),
    ]
    for name, text, loc, size in labels:
        add_label(name, text, loc, size, mats["label"])


def build_scene():
    import bpy

    clear_scene()
    mats = {
        "tether": mat("Lucent tether graphite", (0.11, 0.12, 0.14), alpha=0.98),
        "dark": mat("dark service cable", (0.035, 0.04, 0.05), alpha=1.0),
        "glass": mat("media-eye blue glass", (0.38, 0.72, 1.0), alpha=0.26),
        "floor": mat("polished lounge floor", (0.47, 0.49, 0.51), alpha=0.9),
        "lucent_gray": mat("Lucent security gray", (0.54, 0.56, 0.58), alpha=0.95),
        "security": mat("Lucent gray security figures", (0.23, 0.25, 0.27), alpha=0.98),
        "soft_white": mat("soft white public line", (0.9, 0.94, 1.0), emission=True, strength=0.35),
        "safe": mat("safe-line hard white", (1.0, 1.0, 0.94), emission=True, strength=0.8),
        "cyan": mat("Lucent cyan feed glow", (0.1, 0.86, 1.0), emission=True, strength=0.65),
        "amber": mat("Feed Ops amber", (1.0, 0.58, 0.08), emission=True, strength=0.45),
        "risk": mat("sponsor risk magenta", (1.0, 0.16, 0.42), emission=True, strength=0.55),
        "heat": mat("audience heat red", (1.0, 0.08, 0.06), emission=True, strength=0.6),
        "pippa": mat("Pippa soft-focus side panel", (0.95, 0.52, 0.78), emission=True, strength=0.35, alpha=0.72),
        "brant": mat("Brant outrage side panel", (1.0, 0.34, 0.08), emission=True, strength=0.38, alpha=0.72),
        "overlay_blue": mat("moderation overlay blue", (0.24, 0.48, 1.0), emission=True, strength=0.2, alpha=0.36),
        "private": mat("Mara private rail green", (0.32, 1.0, 0.62), emission=True, strength=0.38),
        "aquarium": mat("aquarium blue", (0.02, 0.28, 0.55), alpha=0.58),
        "city": mat("sealed miniature city", (0.58, 0.62, 0.66), alpha=0.95),
        "prestige": mat("prestige anchor skyscraper glass", (0.72, 0.82, 0.9), emission=True, strength=0.08, alpha=0.95),
        "park": mat("interspersed park green", (0.12, 0.48, 0.22), alpha=0.92),
        "cottage": mat("verdant faux rural cottagecore", (0.46, 0.64, 0.39), alpha=0.96),
        "plaza": mat("tether anchor plaza stone", (0.68, 0.7, 0.66), alpha=0.96),
        "solar_panel": mat("sunward blue solar ray florets", (0.08, 0.42, 0.88), emission=True, strength=0.08, alpha=0.58),
        "radiator": mat("silver radiator ray florets", (0.78, 0.88, 0.86), emission=True, strength=0.04, alpha=0.52),
        "label": mat("label white", (0.92, 0.95, 1.0), emission=True, strength=0.45),
    }
    enrich_shader_graphs(mats)
    add_habitat_cable_bundle(mats)
    add_city_bubble(mats)
    add_city_bubble_tether_attachment(mats)
    add_media_eye_lounge(mats)
    add_overlay_ribbons_and_signage(mats)

    bpy.ops.object.light_add(type="AREA", location=(3.8, -4.8, 4.2))
    key = bpy.context.object
    key.name = "Lucent soft inspection key"
    key.data.energy = 620
    key.data.size = 5.5
    bpy.ops.object.light_add(type="POINT", location=(4.8, 0.0, 0.25))
    eye = bpy.context.object
    eye.name = "media eye internal glow"
    eye.data.energy = 180
    eye.data.color = (0.45, 0.85, 1.0)

    bpy.context.scene.render.engine = "CYCLES"
    bpy.context.scene.cycles.samples = 36
    bpy.context.scene.cycles.preview_samples = 12
    bpy.context.scene.cycles.use_denoising = True
    bpy.context.scene.render.resolution_x = 1200
    bpy.context.scene.render.resolution_y = 820
    bpy.context.scene.view_settings.view_transform = "Filmic"
    bpy.context.scene.view_settings.look = "Medium High Contrast"

    bpy.ops.object.camera_add(location=(6.6, -7.6, 4.9))
    overview = bpy.context.object
    overview.name = "Camera_Lucent_Tether_Overview"
    aim_camera(overview, (0.15, 0.0, 0.0))
    overview.data.type = "ORTHO"
    overview.data.ortho_scale = 7.6
    bpy.context.scene.camera = overview

    bpy.ops.object.camera_add(location=(5.85, -2.95, 1.15))
    lounge = bpy.context.object
    lounge.name = "Camera_Media_Eye_Lounge"
    aim_camera(lounge, (4.58, 0.02, -0.12))
    lounge.data.type = "ORTHO"
    lounge.data.ortho_scale = 2.5

    bpy.ops.object.camera_add(location=(-2.75, -3.25, 1.75))
    city = bpy.context.object
    city.name = "Camera_City_Bubble_Aquarium"
    aim_camera(city, CITY_BUBBLE_CENTER)
    city.data.type = "ORTHO"
    city.data.ortho_scale = 4.05


def render_camera(camera_name, path):
    import bpy

    bpy.context.scene.camera = bpy.data.objects[camera_name]
    bpy.context.scene.render.filepath = str(path.resolve())
    bpy.ops.render.render(write_still=True)


def main():
    import bpy

    vg_lucent_feed_ribbon()
    build_scene()
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    blend_path = OUT_DIR / "lucent_tether_habitat.blend"
    overview_path = OUT_DIR / "lucent_tether_overview.png"
    lounge_path = OUT_DIR / "lucent_media_eye_lounge.png"
    city_path = OUT_DIR / "lucent_city_bubble_aquarium.png"
    bpy.ops.wm.save_as_mainfile(filepath=str(blend_path.resolve()))
    render_camera("Camera_Lucent_Tether_Overview", overview_path)
    render_camera("Camera_Media_Eye_Lounge", lounge_path)
    render_camera("Camera_City_Bubble_Aquarium", city_path)
    print("LUCENT_TETHER_BLEND", blend_path.resolve())
    print("LUCENT_TETHER_OVERVIEW_RENDER", overview_path.resolve())
    print("LUCENT_TETHER_LOUNGE_RENDER", lounge_path.resolve())
    print("LUCENT_TETHER_CITY_RENDER", city_path.resolve())
    group = bpy.data.node_groups.get("VG Lucent Feed Ribbon")
    if group:
        print("LUCENT_TETHER_GN_GROUP", group.name, len(group.nodes), len(group.links))


if __name__ == "__main__":
    main()

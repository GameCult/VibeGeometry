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


def add_floor_patch(name, center, width, depth, material, z=0.0):
    return add_box(name, (center[0], center[1], z), ((1, 0, 0), (0, 1, 0), (0, 0, 1)), (width, depth, 0.035), material)


def add_panel(name, loc, size, material, angle=0.0, lean=0.0):
    x_axis = (pymath.cos(angle), pymath.sin(angle), 0)
    y_axis = (-pymath.sin(angle), pymath.cos(angle), lean)
    z_axis = (0, -lean, 1)
    return add_box(name, loc, (x_axis, y_axis, z_axis), size, material)


def add_habitat_cable_bundle(mats):
    add_cylinder_between("lucent_tether_main_cable", (-6.5, 0.0, 0.0), (6.8, 0.0, 0.0), 0.075, mats["tether"], vertices=24)
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
    bubble = add_uv_sphere("city_bubble_sealed_aquarium", (-5.9, 0.0, -3.25), (1.95, 1.95, 1.05), mats["glass"], 64, 32)
    bubble.rotation_euler[0] = pymath.radians(8)
    add_torus(
        "city_bubble_pressure_equator",
        (-5.9, 0.0, -3.25),
        1.95,
        0.022,
        mats["cyan"],
        rotation=(0.0, 0.0, 0.0),
        segments=128,
    )
    add_torus(
        "city_bubble_lower_aquarium_rim",
        (-5.9, 0.0, -3.52),
        1.42,
        0.018,
        mats["aquarium"],
        rotation=(0.0, 0.0, 0.0),
        segments=96,
    )

    city_verts, city_faces = [], []
    light_verts, light_faces = [], []
    roads = []
    for ix in range(28):
        x = -7.1 + ix * 0.09
        for iy in range(22):
            y = -1.15 + iy * 0.11
            ell = ((x + 5.9) / 1.42) ** 2 + (y / 1.42) ** 2
            if ell > 1.0:
                continue
            n = fbm_2d(ix * 0.27, iy * 0.33, seed=91)
            if n < 0.33:
                continue
            height = 0.06 + 0.28 * n
            material_verts, material_faces = (light_verts, light_faces) if n > 0.72 else (city_verts, city_faces)
            append_box_parts(
                material_verts,
                material_faces,
                (x, y, -3.55 + height * 0.5),
                ((1, 0, 0), (0, 1, 0), (0, 0, 1)),
                (0.045 + 0.03 * n, 0.055 + 0.025 * hash01(ix, iy, 7), height),
            )
        if ix % 4 == 0:
            roads.append([(x, -1.25, -3.46), (x + 0.15 * pymath.sin(ix), 0.0, -3.44), (x, 1.25, -3.46)])
    for iy in range(-10, 11, 3):
        y = iy * 0.11
        roads.append([(-7.05, y, -3.47), (-5.9, y + 0.08 * pymath.sin(iy), -3.45), (-4.75, y, -3.47)])
    add_mesh_parts("city_bubble_miniature_skyscraper_mesh", city_verts, city_faces, mats["city"])
    add_mesh_parts("city_bubble_attention_lit_tower_mesh", light_verts, light_faces, mats["cyan"])
    add_multi_polyline_curve("city_bubble_aquarium_street_grid", roads, 0.006, mats["soft_white"], resolution=2)


def add_media_eye_lounge(mats):
    add_uv_sphere("media_eye_transfer_lounge_glass_shell", (4.6, 0.0, 0.0), (1.75, 1.05, 0.78), mats["glass"], 64, 32)
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
        ("label_city_bubble", "city bubble below: sealed aquarium", (-5.9, -1.9, -2.42), 0.12),
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
        "label": mat("label white", (0.92, 0.95, 1.0), emission=True, strength=0.45),
    }
    add_habitat_cable_bundle(mats)
    add_city_bubble(mats)
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

    bpy.context.scene.render.engine = "BLENDER_EEVEE"
    if hasattr(bpy.context.scene, "eevee"):
        bpy.context.scene.eevee.taa_render_samples = 24
    bpy.context.scene.render.resolution_x = 1400
    bpy.context.scene.render.resolution_y = 950
    bpy.context.scene.view_settings.view_transform = "Filmic"
    bpy.context.scene.view_settings.look = "Medium High Contrast"

    bpy.ops.object.camera_add(location=(7.8, -8.4, 4.2))
    overview = bpy.context.object
    overview.name = "Camera_Lucent_Tether_Overview"
    aim_camera(overview, (0.0, 0.0, -0.9))
    overview.data.type = "ORTHO"
    overview.data.ortho_scale = 8.4
    bpy.context.scene.camera = overview

    bpy.ops.object.camera_add(location=(5.85, -2.95, 1.15))
    lounge = bpy.context.object
    lounge.name = "Camera_Media_Eye_Lounge"
    aim_camera(lounge, (4.58, 0.02, -0.12))
    lounge.data.type = "ORTHO"
    lounge.data.ortho_scale = 2.5

    bpy.ops.object.camera_add(location=(-4.4, -3.15, -1.75))
    city = bpy.context.object
    city.name = "Camera_City_Bubble_Aquarium"
    aim_camera(city, (-5.92, 0.0, -3.32))
    city.data.type = "ORTHO"
    city.data.ortho_scale = 3.9


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

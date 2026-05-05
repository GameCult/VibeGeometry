"""Build an Aetheria Bloom habitat study scene.

This is a hybrid authoring test:

- Python owns the lore-derived scene brief, tables, materials, labels, camera,
  and Blender object orchestration.
- Geometry Script emits reusable inspectable node groups for procedural rails.
- bpy builds the cutaway habitat mesh and render evidence.
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
from vibegeometry import (
    CylinderFrame,
    add_box,
    add_curve_polyline,
    add_cylinder_between,
    add_material,
    add_mesh_parts,
    add_multi_polyline_curve,
    aim_camera,
    append_box_parts,
    append_cylindrical_ring_band,
    clear_scene,
    fbm_2d,
    smoothstep,
)


TAU = pymath.tau
AXIS_LENGTH = 18.0
CUT_START = pymath.radians(-132.0)
CUT_END = pymath.radians(132.0)
FULL_START = -pymath.pi
FULL_END = pymath.pi
INNER_RADIUS = 5.0
FRAME = CylinderFrame(INNER_RADIUS)
radial = FRAME.radial
tangent = FRAME.tangent
cyl_point = FRAME.cyl_point
surface_point = FRAME.surface_point
mat = add_material


@tree("VG Bloom Light Spine")
def vg_bloom_light_spine(
    length: Float = 18.0,
    helix_radius: Float = 0.18,
    turns: Float = 7.5,
    thickness: Float = 0.035,
):
    """A thin procedural light/distribution rail around the axial spire."""

    rail = curve_line(mode=CurveLine.Mode.POINTS, start=(-9.0, 0.0, 0.0), end=(9.0, 0.0, 0.0))
    samples = resample_curve(keep_last_segment=True, curve=rail, mode="Count", count=420, length=0.1)
    point_count = domain_size(component="CURVE", geometry=samples).point_count
    t = math(operation=Math.Operation.DIVIDE, value=(index(), point_count))
    theta = math(operation=Math.Operation.MULTIPLY, value=(t, math(operation=Math.Operation.MULTIPLY, value=(turns, TAU))))
    x = math(operation=Math.Operation.SUBTRACT, value=(math(operation=Math.Operation.MULTIPLY, value=(t, length)), math(operation=Math.Operation.DIVIDE, value=(length, 2.0))))
    y = math(operation=Math.Operation.MULTIPLY, value=(math(operation=Math.Operation.SINE, value=theta), helix_radius))
    z = math(operation=Math.Operation.MULTIPLY, value=(math(operation=Math.Operation.COSINE, value=theta), helix_radius))
    positioned = set_position(geometry=samples, position=combine_xyz(x=x, y=y, z=z), offset=(0.0, 0.0, 0.0))
    profile = curve_circle(mode=CurveCircle.Mode.RADIUS, resolution=8, radius=thickness)
    return {"Geometry": curve_to_mesh(curve=positioned, profile_curve=profile, fill_caps=True)}


def add_shell_segment(name, radius, half_length, thickness, material, angle_steps=144, x_steps=8, start_angle=FULL_START, end_angle=FULL_END):
    import bpy

    verts = []
    faces = []
    for ix in range(x_steps + 1):
        x = -half_length + (2.0 * half_length * ix / x_steps)
        for ia in range(angle_steps + 1):
            a = start_angle + (end_angle - start_angle) * ia / angle_steps
            verts.append(cyl_point(x, a, radius))
    for ix in range(x_steps):
        for ia in range(angle_steps):
            row = angle_steps + 1
            faces.append((ix * row + ia, (ix + 1) * row + ia, (ix + 1) * row + ia + 1, ix * row + ia + 1))
    mesh = bpy.data.meshes.new(name + "Mesh")
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    obj.data.materials.append(material)
    obj.show_transparent = True
    solid = obj.modifiers.new("visible thickness", "SOLIDIFY")
    solid.thickness = thickness
    solid.offset = 0.0
    return obj


def add_surface_patch(name, x0, x1, a0, a1, radius, material, lift=-0.045, angle_steps=8, x_steps=3):
    import bpy

    verts = []
    faces = []
    for ix in range(x_steps + 1):
        x = x0 + (x1 - x0) * ix / x_steps
        for ia in range(angle_steps + 1):
            a = a0 + (a1 - a0) * ia / angle_steps
            verts.append(surface_point(x, a, radius, lift=lift))
    row = angle_steps + 1
    for ix in range(x_steps):
        for ia in range(angle_steps):
            faces.append((ix * row + ia, (ix + 1) * row + ia, (ix + 1) * row + ia + 1, ix * row + ia + 1))
    mesh = bpy.data.meshes.new(name + "Mesh")
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    obj.data.materials.append(material)
    return obj


def add_surface_curve(name, samples, radius, bevel, material, lift=-0.11):
    points = [surface_point(x, angle, radius, lift=lift) for x, angle in samples]
    return add_curve_polyline(name, points, bevel, material)


def add_surface_box(name, x, angle, material, size=(0.22, 0.12, 0.08), radial_lift=-0.18):
    r = radial(angle)
    t = tangent(angle)
    loc = surface_point(x, angle, INNER_RADIUS, lift=radial_lift)
    return add_box(name, loc, axes=((1, 0, 0), t, r), size=size, material=material)


def add_surface_block_field(name, x_values, angles, material, size, radial_lift=-0.22, jitter=0.0):
    for ix, x in enumerate(x_values):
        for ia, angle in enumerate(angles):
            if jitter:
                x_offset = ((ix * 17 + ia * 7) % 9 - 4) * jitter
                angle_offset = ((ix * 11 + ia * 5) % 7 - 3) * jitter * 0.05
            else:
                x_offset = 0.0
                angle_offset = 0.0
            add_surface_box(
                f"{name}_{ix:02d}_{ia:02d}",
                x + x_offset,
                angle + angle_offset,
                material,
                size=size,
                radial_lift=radial_lift,
            )


def add_surface_stilt(name, x, angle, inner_lift, outer_lift, material, radius=0.009):
    start = surface_point(x, angle, INNER_RADIUS, lift=inner_lift)
    end = surface_point(x, angle, INNER_RADIUS, lift=outer_lift)
    return add_cylinder_between(name, start, end, radius, material, vertices=6)


def add_surface_brace(name, x0, angle0, x1, angle1, lift0, lift1, material, bevel=0.006):
    return add_curve_polyline(
        name,
        [
            surface_point(x0, angle0, INNER_RADIUS, lift=lift0),
            surface_point((x0 + x1) * 0.5, (angle0 + angle1) * 0.5, INNER_RADIUS, lift=(lift0 + lift1) * 0.5 - 0.03),
            surface_point(x1, angle1, INNER_RADIUS, lift=lift1),
        ],
        bevel,
        material,
        resolution=3,
    )


def add_favela_fractal_cluster(prefix, x_values, angles, mats):
    shack_verts, shack_faces = [], []
    roof_verts, roof_faces = [], []
    brace_lines = []
    for ix, x in enumerate(x_values):
        for ia, angle in enumerate(angles):
            lean = ((ix * 5 + ia * 3) % 5 - 2) * 0.018
            root = f"{prefix}_{ix:02d}_{ia:02d}"
            axes = ((1, 0, 0), tangent(angle + lean), radial(angle + lean))
            append_box_parts(shack_verts, shack_faces, surface_point(x, angle + lean, INNER_RADIUS, lift=-0.38), axes, (0.2, 0.12, 0.24))
            for level in range(2):
                lift = -0.55 - level * 0.14
                width = 0.13 - level * 0.015
                for wing in (-1, 1):
                    dx = wing * (0.09 + 0.035 * level)
                    da = wing * (0.018 + 0.012 * level) + lean
                    local_axes = ((1, 0, 0), tangent(angle + da), radial(angle + da))
                    append_box_parts(
                        shack_verts,
                        shack_faces,
                        surface_point(x + dx, angle + da, INNER_RADIUS, lift=lift),
                        local_axes,
                        (width, 0.075, 0.11),
                    )
                    roof_axes = ((1, 0, 0), tangent(angle + da + 0.006 * wing), radial(angle + da + 0.006 * wing))
                    append_box_parts(
                        roof_verts,
                        roof_faces,
                        surface_point(x + dx + 0.012 * wing, angle + da + 0.006 * wing, INNER_RADIUS, lift=lift - 0.07),
                        roof_axes,
                        (width * 1.22, 0.095, 0.018),
                    )
                    brace_lines.append(
                        [
                            surface_point(x + dx - width * 0.25, angle + da - 0.006, INNER_RADIUS, lift=lift + 0.05),
                            surface_point(x + dx - width * 0.25, angle + da - 0.006, INNER_RADIUS, lift=-0.25),
                        ]
                    )
                    brace_lines.append(
                        [
                            surface_point(x + dx - width * 0.42, angle + da - 0.012, INNER_RADIUS, lift=lift + 0.02),
                            surface_point(x + dx, angle + da, INNER_RADIUS, lift=lift - 0.04),
                            surface_point(x + dx + width * 0.42, angle + da + 0.012, INNER_RADIUS, lift=lift - 0.09),
                        ]
                    )
            for step in range(2):
                brace_lines.append(
                    [
                        surface_point(x - 0.18, angle + lean + step * 0.028, INNER_RADIUS, lift=-0.62 - step * 0.08),
                        surface_point(x, angle + lean + 0.035 + step * 0.025, INNER_RADIUS, lift=-0.62 - step * 0.08),
                        surface_point(x + 0.2, angle + lean + step * 0.02, INNER_RADIUS, lift=-0.62 - step * 0.08),
                    ]
                )
    add_mesh_parts(prefix + "_shack_mesh", shack_verts, shack_faces, mats["favela"])
    add_mesh_parts(prefix + "_roof_mesh", roof_verts, roof_faces, mats["shack_roof"])
    add_multi_polyline_curve(prefix + "_brace_and_catwalks", brace_lines, 0.005, mats["brace"], resolution=2)


def add_hubward_endcap_terraced_slums(prefix, x, mats):
    # Bloom lore frame: on an endcap, "up" is inward toward the axial Spire.
    # These terraces are not polar graph paper. Fractal noise makes the shelf
    # edges wobble, the settlement thicken, and the class gradient accrete
    # outward until it meets the high-gravity surface city.
    shelf_verts, shelf_faces = [], []
    poor_verts, poor_faces = [], []
    middle_verts, middle_faces = [], []
    city_verts, city_faces = [], []
    roof_verts, roof_faces = [], []
    ladder_lines = []
    rings = [0.72, 0.98, 1.24, 1.52, 1.82, 2.14, 2.48, 2.84, 3.22, 3.62, 4.04, 4.48, 4.9, 5.18]
    for tier, radius in enumerate(rings[:-1]):
        inner_r = radius
        outer_r = rings[tier + 1]
        tier_t = tier / (len(rings) - 2)
        face_x = x + 0.035 + tier * 0.018
        append_cylindrical_ring_band(shelf_verts, shelf_faces, face_x, inner_r, outer_r, segments=160)
        count = int(30 + tier * 8 + 18 * fbm_2d(tier * 0.71, 4.0, seed=12))
        angular_step = TAU / count
        run = 0
        for i in range(count):
            u = i / count
            n = fbm_2d(u * 8.0 + tier * 0.37, tier * 0.91, seed=31)
            n2 = fbm_2d(u * 15.0, tier * 1.7 + 3.0, seed=53)
            density = 0.58 + tier_t * 0.34 + 0.23 * n
            if n2 > density and run < 4:
                run += 1
                continue
            run = 0
            angle_warp = (n - 0.5) * angular_step * 1.6 + 0.12 * pymath.sin(tier * 1.37 + u * TAU * 2.0)
            a = FULL_START + TAU * u + angle_warp
            radial_t = 0.24 + 0.56 * fbm_2d(u * 5.0, tier * 0.8, seed=74)
            lane_r = inner_r + (outer_r - inner_r) * radial_t + (n - 0.5) * (outer_r - inner_r) * 0.55
            lane_r = max(inner_r + 0.04, min(outer_r - 0.035, lane_r))
            local_x = face_x + 0.035 * ((i + tier) % 3) + 0.08 * (n - 0.5)
            local_axes = (tangent(a), radial(a), (1, 0, 0))
            tangential = max(0.055, TAU * lane_r / count * (0.72 + 0.5 * n))
            radial_depth = max(0.08, (outer_r - inner_r) * (0.58 + 0.45 * n2))
            height = (0.1 + 0.24 * tier_t) * (0.75 + 0.7 * n)
            if tier_t < 0.55:
                mesh_verts, mesh_faces = poor_verts, poor_faces
                material_bias = 0.0
            elif tier_t < 0.82:
                mesh_verts, mesh_faces = middle_verts, middle_faces
                material_bias = 0.12
            else:
                mesh_verts, mesh_faces = city_verts, city_faces
                material_bias = 0.24
            append_box_parts(
                mesh_verts,
                mesh_faces,
                cyl_point(local_x + height * (0.34 + material_bias), a, lane_r),
                local_axes,
                (tangential, radial_depth, height),
            )
            if tier_t < 0.78 or n > 0.62:
                roof_axes = (tangent(a + 0.006), radial(a + 0.006), (1, 0, 0))
                append_box_parts(
                    roof_verts,
                    roof_faces,
                    cyl_point(local_x + height * 0.78, a + 0.004, lane_r - 0.012),
                    roof_axes,
                    (tangential * 1.2, radial_depth * 1.06, 0.018),
                )
            if n > 0.38:
                ladder_lines.append([cyl_point(local_x + 0.12, a, min(outer_r - 0.03, lane_r + radial_depth * 0.45)), cyl_point(local_x + 0.18, a + 0.012, max(inner_r + 0.03, lane_r - radial_depth * 0.48))])
            if n2 > 0.34:
                ladder_lines.append(
                    [
                        cyl_point(local_x + 0.08, a - angular_step * 0.35, lane_r + radial_depth * 0.35),
                        cyl_point(local_x + 0.11, a + (n - 0.5) * angular_step, lane_r),
                        cyl_point(local_x + 0.08, a + angular_step * 0.42, lane_r - radial_depth * 0.38),
                    ]
                )
    add_mesh_parts(prefix + "_annular_shelf_mesh", shelf_verts, shelf_faces, mats["favela"])
    add_mesh_parts(prefix + "_rickety_shack_mesh", poor_verts, poor_faces, mats["favela"])
    add_mesh_parts(prefix + "_midrise_housing_mesh", middle_verts, middle_faces, mats["city"])
    add_mesh_parts(prefix + "_surface_urban_crown_mesh", city_verts, city_faces, mats["luxury"])
    add_mesh_parts(prefix + "_patched_roof_mesh", roof_verts, roof_faces, mats["shack_roof"])
    add_multi_polyline_curve(prefix + "_ladders_nets_handlines", ladder_lines, 0.0055, mats["brace"], resolution=2)


def add_hubward_office_complex(prefix, x, mats):
    office_verts, office_faces = [], []
    for i, radius in enumerate((0.42, 0.68, 0.92)):
        append_cylindrical_ring_band(office_verts, office_faces, x + 0.18 + i * 0.06, radius, radius + 0.16, segments=96)
    add_mesh_parts(prefix + "_ring_office_mesh", office_verts, office_faces, mats["hub"])
    for i, angle in enumerate([pymath.radians(a) for a in range(-150, 181, 30)]):
        add_cylinder_between(
            f"{prefix}_office_spoke_bridge_{i:02d}",
            cyl_point(x + 0.28, angle, 0.9),
            cyl_point(x + 0.18, angle, 1.22),
            0.012,
            mats["pressure_line"],
            vertices=6,
        )


def add_town_detail_cluster(prefix, x_values, angles, material, road_material):
    verts, faces = [], []
    lanes = []
    for ix, x in enumerate(x_values):
        for ia, angle in enumerate(angles):
            root = f"{prefix}_{ix:02d}_{ia:02d}"
            for lane in (-1, 0, 1):
                local_angle = angle + lane * 0.024
                lanes.append(
                    [
                        surface_point(x - 0.32, local_angle - 0.014, INNER_RADIUS, lift=-0.37),
                        surface_point(x, local_angle + 0.008, INNER_RADIUS, lift=-0.37),
                        surface_point(x + 0.32, local_angle - 0.006, INNER_RADIUS, lift=-0.37),
                    ]
                )
                for b in range(3):
                    dx = -0.22 + b * 0.22 + ((ix + ia + b) % 3 - 1) * 0.018
                    da = lane * 0.026 + ((ix * 7 + ia * 5 + b) % 5 - 2) * 0.004
                    height = 0.12 + 0.035 * ((ix + ia + b) % 4)
                    append_box_parts(
                        verts,
                        faces,
                        surface_point(x + dx, angle + da, INNER_RADIUS, lift=-0.3 - height * 0.5),
                        ((1, 0, 0), tangent(angle + da), radial(angle + da)),
                        (0.12, 0.07, height),
                    )
    add_mesh_parts(prefix + "_nested_house_mesh", verts, faces, material)
    add_multi_polyline_curve(prefix + "_lane_network", lanes, 0.006, road_material, resolution=2)


def add_spoke_plaza_detail(prefix, x, angle, mats, seed):
    add_surface_curve(
        f"{prefix}_plaza_ring",
        [(x + 0.34 * pymath.cos(t), angle + 0.065 * pymath.sin(t)) for t in [TAU * i / 28 for i in range(29)]],
        INNER_RADIUS,
        0.01,
        mats["road"],
        lift=-0.42,
    )
    for i in range(10):
        t = TAU * i / 10 + seed * 0.13
        dx = 0.28 * pymath.cos(t)
        da = 0.052 * pymath.sin(t)
        add_surface_box(
            f"{prefix}_kiosk_{i:02d}",
            x + dx,
            angle + da,
            mats["luxury"],
            size=(0.09, 0.055, 0.1 + 0.025 * (i % 3)),
            radial_lift=-0.37,
        )
    for i, spoke_da in enumerate((-0.11, -0.055, 0.055, 0.11)):
        add_surface_curve(
            f"{prefix}_feeder_walk_{i:02d}",
            [(x - 0.45, angle + spoke_da), (x, angle + spoke_da * 0.3), (x + 0.45, angle - spoke_da * 0.6)],
            INNER_RADIUS,
            0.008,
            mats["pressure_line"],
            lift=-0.43,
        )


def add_rotating_spoke(name, x, angle, inner_radius, outer_radius, material, radius=0.045, vertices=10):
    r = radial(angle)
    return add_cylinder_between(
        name,
        (x, r[1] * inner_radius, r[2] * inner_radius),
        (x, r[1] * outer_radius, r[2] * outer_radius),
        radius,
        material,
        vertices=vertices,
    )


def add_frame_transfer_artery(name, x, angle, start_radius, end_radius, material, sweep=0.42, bevel=0.025):
    samples = []
    for i in range(9):
        t = i / 8
        a = angle + (t - 0.5) * sweep
        radius = start_radius + (end_radius - start_radius) * t
        samples.append((x + (t - 0.5) * 0.65, radius * pymath.cos(a), radius * pymath.sin(a)))
    return add_curve_polyline(name, samples, bevel, material)


def add_spiral_spoke_loop(name, x, angle, start_radius, end_radius, material, bevel=0.04, cargo=False):
    """Shared cylinder frame: x is axial, angle is shell azimuth, radius is spin radius."""
    samples = []
    handed = 1.0 if pymath.sin(angle * 2.0 + x * 0.37) >= 0 else -1.0
    tangent_bias = 0.68 if cargo else 0.42
    loop_gain = 0.58 if cargo else 0.34
    for i in range(22):
        u = i / 21
        e = smoothstep(u)
        radius = start_radius + (end_radius - start_radius) * e
        a = angle + handed * (tangent_bias * (1.0 - u) + loop_gain * pymath.sin(u * pymath.pi))
        x2 = x + handed * 0.62 * pymath.sin(u * pymath.pi) + 0.15 * pymath.sin(u * TAU * 2.0)
        samples.append(cyl_point(x2, a, radius))
    return add_curve_polyline(name, samples, bevel, material, resolution=4)


def add_endcap_face(name, x, radius, material, segments=144):
    import bpy

    mesh = bpy.data.meshes.new(name + "Mesh")
    verts = [(x, 0.0, 0.0)]
    verts.extend(cyl_point(x, FULL_START + TAU * i / segments, radius) for i in range(segments))
    faces = [(0, i + 1, 1 + ((i + 1) % segments)) for i in range(segments)]
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    obj.data.materials.append(material)
    return obj


def add_endcap_ring(name, x, radius, material, minor_radius=0.025):
    import bpy

    bpy.ops.mesh.primitive_torus_add(
        major_radius=radius,
        minor_radius=minor_radius,
        major_segments=128,
        minor_segments=8,
        location=(x, 0, 0),
    )
    obj = bpy.context.object
    obj.name = name
    obj.data.name = name + "Mesh"
    obj.rotation_euler[1] = pymath.radians(90)
    obj.data.materials.append(material)
    return obj


def add_endcap_terrace_blocks(prefix, x, radii, angles, material, height=0.18):
    for ir, radius in enumerate(radii):
        for ia, angle in enumerate(angles):
            loc = cyl_point(x, angle, radius)
            add_box(
                f"{prefix}_{ir:02d}_{ia:02d}",
                loc,
                axes=((1, 0, 0), tangent(angle), radial(angle)),
                size=(0.09, 0.16, height),
                material=material,
            )


def add_label(name, text, loc, size, material):
    import bpy

    bpy.ops.object.text_add(location=loc, rotation=(pymath.radians(70), 0.0, pymath.radians(0)))
    obj = bpy.context.object
    obj.name = name
    obj.data.body = text
    obj.data.align_x = "CENTER"
    obj.data.align_y = "CENTER"
    obj.data.size = size
    obj.data.materials.append(material)
    return obj


def add_gn_light_spine(material):
    import bpy

    group = bpy.data.node_groups.get("VG Bloom Light Spine")
    mesh = bpy.data.meshes.new("BloomLightSpineCarrierMesh")
    obj = bpy.data.objects.new("GN_Light_Spine_Modifier_Carrier", mesh)
    bpy.context.collection.objects.link(obj)
    mod = obj.modifiers.new("VG Bloom Light Spine", "NODES")
    mod.node_group = group
    obj.data.materials.append(material)
    return obj


def build_scene():
    import bpy

    clear_scene()

    mats = {
        "inner": mat("civic inner surface - open commons", (0.28, 0.30, 0.32), alpha=0.78),
        "utility": mat("utility mat amber", (0.95, 0.57, 0.18), alpha=0.42),
        "pressure": mat("pressure laminate blue", (0.18, 0.45, 0.86), alpha=0.2),
        "shield": mat("aggregate shielding graphite", (0.08, 0.075, 0.07), alpha=0.38),
        "hub": mat("despun hub white", (0.82, 0.86, 0.88), alpha=0.88),
        "endcap": mat("layered endcap pressure face", (0.62, 0.66, 0.7), alpha=0.62),
        "spire_sheath": mat("spun spire sheath", (0.38, 0.42, 0.46), alpha=0.34),
        "light": mat("light spine gold", (1.0, 0.78, 0.25), emission=True, strength=1.6),
        "farm": mat("TCS Root farms", (0.15, 0.55, 0.24), alpha=0.92),
        "district": mat("surface districts", (0.55, 0.58, 0.62), alpha=0.95),
        "favela": mat("hubcap terrace slums", (0.74, 0.48, 0.26), alpha=0.98),
        "shack_roof": mat("patched favela sheet metal", (0.46, 0.39, 0.32), alpha=0.98),
        "brace": mat("rickety brace dark steel", (0.12, 0.10, 0.085), alpha=0.98),
        "luxury": mat("luxury spoke districts", (0.82, 0.78, 0.62), alpha=0.98),
        "industrial": mat("industrial works", (0.32, 0.34, 0.36), alpha=0.98),
        "suburban": mat("suburban mixed belt", (0.5, 0.64, 0.5), alpha=0.96),
        "beach": mat("beach rim", (0.86, 0.76, 0.48), alpha=0.96),
        "water": mat("cylindrical sea", (0.05, 0.28, 0.55), alpha=0.82),
        "forest": mat("forest canopy", (0.04, 0.32, 0.1), alpha=0.92),
        "road": mat("road graph", (0.72, 0.66, 0.52), alpha=0.96),
        "city": mat("city clusters", (0.62, 0.64, 0.67), alpha=0.98),
        "cloud": mat("interior cloud layer", (0.8, 0.86, 0.9), alpha=0.24),
        "air": mat("air return cyan", (0.1, 0.85, 1.0), emission=True, strength=0.25),
        "coolant": mat("coolant blue", (0.08, 0.25, 1.0), emission=True, strength=0.2),
        "condensate": mat("condensate green", (0.15, 0.95, 0.55), emission=True, strength=0.15),
        "pressure_line": mat("pressure amber", (1.0, 0.65, 0.08), emission=True, strength=0.35),
        "hazard": mat("emergency red", (1.0, 0.12, 0.07), emission=True, strength=0.45),
        "label": mat("label white", (0.92, 0.95, 1.0), emission=True, strength=0.4),
        "glass": mat("operations glass", (0.45, 0.8, 1.0), alpha=0.28),
    }

    add_shell_segment("01_open_civic_inner_surface_full_bloom", 5.0, AXIS_LENGTH / 2, 0.045, mats["inner"])
    add_shell_segment("02_utility_mat_service_interlayer_full_bloom", 5.35, AXIS_LENGTH / 2, 0.075, mats["utility"])
    add_shell_segment("03_pressure_structural_shell_full_bloom", 5.75, AXIS_LENGTH / 2, 0.11, mats["pressure"])
    add_shell_segment("04_outer_aggregate_shielding_full_bloom", 6.35, AXIS_LENGTH / 2, 0.28, mats["shield"])

    add_cylinder_between("despun_center_axis_core", (-10.2, 0, 0), (10.2, 0, 0), 0.28, mats["hub"], vertices=32)
    add_cylinder_between("despun_hub_cap_docking_axis", (-10.85, 0, 0), (-9.25, 0, 0), 0.72, mats["hub"], vertices=48)
    add_cylinder_between("docking_port_on_despun_hub_cap", (-11.55, 0, 0), (-10.75, 0, 0), 0.36, mats["pressure_line"], vertices=32)
    add_cylinder_between("traffic_light_spire_core", (-9.2, 0, 0), (9.2, 0, 0), 0.13, mats["light"], vertices=16)
    add_cylinder_between("spun_spire_sheath_outer_frame", (-8.9, 0, 0), (8.9, 0, 0), 0.82, mats["spire_sheath"], vertices=48)
    add_gn_light_spine(mats["light"])

    # The Bloom lives in one cylindrical coordinate space. Spokes, endcaps,
    # surface districts, roads, clouds, and transfer arteries all speak x/angle/radius.
    for x, prefix in [(-9.05, "hubward"), (9.05, "capward")]:
        add_endcap_face(f"{prefix}_endcap_pressure_face", x, 5.72, mats["endcap"])
        add_endcap_face(f"{prefix}_endcap_inner_face", x + (0.035 if x < 0 else -0.035), INNER_RADIUS, mats["inner"], segments=128)
        for ir, rr in enumerate((0.82, 1.6, 2.45, 3.25, 4.05, 4.75, 5.35)):
            mat_key = "favela" if x < 0 and ir >= 2 else "beach" if x > 0 and ir >= 4 else "pressure_line"
            add_endcap_ring(f"{prefix}_endcap_terrace_ring_{ir:02d}", x, rr, mats[mat_key], minor_radius=0.018 + ir * 0.002)
    add_hubward_office_complex("hubward_docking_hub_office_complex", -9.24, mats)
    add_hubward_endcap_terraced_slums("hubward_endcap_rice_paddy_slums", -9.18, mats)
    add_endcap_terrace_blocks(
        "capward_endcap_beach_service",
        9.12,
        [3.5, 4.1, 4.65],
        [pymath.radians(a) for a in range(-160, 181, 40)],
        mats["beach"],
        height=0.1,
    )

    # Golden-angle spokes fill the cylinder like seeds on a head: each new
    # artery avoids the previous one while staying in the same global frame.
    golden_angle = pymath.pi * (3.0 - pymath.sqrt(5.0))
    spoke_count = 46
    prestige_angles = []
    for i in range(spoke_count):
        t = i / (spoke_count - 1)
        x = -8.25 + 16.5 * t
        a = ((i * golden_angle + 0.48 * pymath.sin(t * TAU * 3.0)) % TAU) - pymath.pi
        cargo = i % 3 == 0
        material = mats["pressure_line"] if cargo else mats["hub"]
        bevel = 0.052 if cargo else 0.036
        name = "spiral_cargo_spoke" if cargo else "spiral_passenger_spoke"
        add_spiral_spoke_loop(f"{name}_{i:02d}", x, a, 0.82, 5.18, material, bevel=bevel, cargo=cargo)
        add_cylinder_between(
            f"spiral_spoke_shell_collar_{i:02d}",
            cyl_point(x - 0.2, a, 5.05),
            cyl_point(x + 0.2, a, 5.05),
            0.12 if cargo else 0.085,
            mats["pressure_line"],
            vertices=18,
        )
        add_frame_transfer_artery(
            f"spun_to_despun_transfer_loop_{i:02d}",
            x,
            a + pymath.pi / 2,
            0.28,
            0.82,
            mats["pressure_line"],
            sweep=0.95 if cargo else 0.62,
            bevel=0.017,
        )
        if i % 5 == 0:
            prestige_angles.append(a)
    for i in range(64):
        t = i / 63
        x = -8.65 + 17.3 * t
        a = ((i * golden_angle * 1.618 + 0.72 * pymath.sin(t * TAU * 2.0)) % TAU) - pymath.pi
        add_spiral_spoke_loop(f"spiral_atmospheric_utility_rib_{i:02d}", x, a, 0.95, 5.55, mats["air"], bevel=0.015, cargo=False)

    # Whole-cylinder civic gradient. Axial bands move from hubward transition
    # through dense and luxury urban districts, mixed suburbs, industrial/farm
    # belts, and finally a beach/sea edge.
    add_surface_patch("hubward_low_g_transition_band", -8.9, -7.35, FULL_START, FULL_END, INNER_RADIUS, mats["favela"], lift=-0.20, angle_steps=72, x_steps=3)
    add_surface_patch("hyperurban_favela_city_belt", -7.35, -5.6, FULL_START, FULL_END, INNER_RADIUS, mats["city"], lift=-0.18, angle_steps=72, x_steps=3)
    add_surface_patch("prestige_urban_luxury_spoke_belt", -5.6, -2.7, FULL_START, FULL_END, INNER_RADIUS, mats["luxury"], lift=-0.17, angle_steps=72, x_steps=4)
    add_surface_patch("urban_mixed_suburban_industrial_belt", -2.7, 0.9, FULL_START, FULL_END, INNER_RADIUS, mats["suburban"], lift=-0.18, angle_steps=72, x_steps=4)
    add_surface_patch("industrial_agricultural_belt", 0.9, 5.8, FULL_START, FULL_END, INNER_RADIUS, mats["farm"], lift=-0.16, angle_steps=72, x_steps=5)
    add_surface_patch("beach_resort_rim", 5.8, 7.05, FULL_START, FULL_END, INNER_RADIUS, mats["beach"], lift=-0.23, angle_steps=72, x_steps=3)
    add_surface_patch("cylindrical_sea_after_beach", 7.05, 8.85, FULL_START, FULL_END, INNER_RADIUS, mats["water"], lift=-0.25, angle_steps=72, x_steps=3)

    dense_angles = [pymath.radians(a) for a in range(-165, 180, 15)]
    add_surface_block_field("hubward_spoke_access_market_stack", [-8.65, -8.25, -7.85, -7.45], dense_angles, mats["favela"], size=(0.16, 0.08, 0.18), radial_lift=-0.29, jitter=0.035)
    add_surface_block_field("hyperurban_microtower", [-7.0, -6.55, -6.1, -5.7], dense_angles[::2], mats["city"], size=(0.2, 0.1, 0.36), radial_lift=-0.42, jitter=0.03)
    add_town_detail_cluster(
        "hyperurban_nested_town",
        [-7.1, -6.65, -6.2, -5.75],
        [pymath.radians(a) for a in range(-150, 181, 45)],
        mats["city"],
        mats["road"],
    )
    for x in [-5.0, -4.2, -3.4]:
        for ia, a in enumerate(prestige_angles[:8]):
            add_surface_box(f"luxury_spoke_plaza_{x:.1f}_{a:.2f}", x, a, mats["luxury"], size=(0.55, 0.34, 0.14), radial_lift=-0.31)
            add_spoke_plaza_detail(f"luxury_spoke_plaza_detail_{x:.1f}_{ia:02d}", x, a, mats, ia)
            for da in (-0.16, 0.16):
                add_surface_box(f"luxury_spoke_tower_{x:.1f}_{a:.2f}_{da:.1f}", x + da, a + da, mats["city"], size=(0.18, 0.1, 0.42), radial_lift=-0.44)
    add_surface_block_field("mixed_suburban_industrial_block", [-2.2, -1.4, -0.6, 0.2], [pymath.radians(a) for a in range(-150, 181, 30)], mats["suburban"], size=(0.42, 0.18, 0.12), radial_lift=-0.27, jitter=0.04)
    add_town_detail_cluster(
        "mixed_belt_nested_town",
        [-2.35, -1.65, -0.95, -0.25, 0.45],
        [pymath.radians(a) for a in range(-150, 181, 60)],
        mats["suburban"],
        mats["road"],
    )
    add_surface_block_field("factory_yard_block", [1.2, 2.0, 2.8, 3.6], [pymath.radians(a) for a in range(-150, 181, 45)], mats["industrial"], size=(0.62, 0.22, 0.16), radial_lift=-0.29, jitter=0.035)
    add_surface_block_field("farm_service_shed", [4.2, 5.0, 5.6], [pymath.radians(a) for a in range(-165, 181, 45)], mats["farm"], size=(0.52, 0.16, 0.08), radial_lift=-0.24, jitter=0.04)
    for i, deg in enumerate(range(-170, 181, 20)):
        a = pymath.radians(deg + (i % 3) * 3)
        add_surface_curve(f"axial_surface_service_lane_{i:02d}", [(-8.7, a), (-5.5, a + 0.08), (-1.4, a - 0.04), (2.9, a + 0.06), (8.6, a - 0.02)], INNER_RADIUS, 0.007, mats["pressure_line"], lift=-0.43)
    for i, x in enumerate([-8.65, -7.25, -5.85, -4.45, -3.05, -1.65, -0.25, 1.15, 2.55, 3.95, 5.35, 6.75, 8.15]):
        add_surface_curve(f"circumferential_market_seam_{i:02d}", [(x, pymath.radians(a)) for a in range(-180, 181, 18)], INNER_RADIUS, 0.006, mats["road"], lift=-0.45)

    road_specs = [
        [(-8.7, -160), (-7.2, -130), (-5.6, -94), (-3.0, -58), (-1.0, -34), (1.6, -14), (4.4, 8), (6.7, 26), (8.4, 44)],
        [(-8.4, 140), (-6.7, 118), (-4.9, 92), (-2.0, 72), (0.8, 62), (3.2, 74), (5.4, 94), (8.1, 122)],
        [(-8.2, -26), (-6.0, -8), (-3.6, 18), (-1.0, 42), (1.8, 50), (4.2, 38), (6.4, 20), (8.4, -2)],
        [(-8.6, 12), (-6.2, 32), (-4.2, 48), (-1.8, 38), (0.4, 12), (2.8, -22), (5.5, -52), (8.2, -84)],
    ]
    for i, spec in enumerate(road_specs):
        add_surface_curve(f"wrapped_road_graph_{i}", [(x, pymath.radians(a)) for x, a in spec], INNER_RADIUS, 0.016, mats["road"], lift=-0.39)
    river_specs = [
        [(-8.6, 82), (-6.5, 68), (-4.6, 42), (-2.2, 22), (0.8, 8), (3.8, -2), (6.1, -12), (8.6, -24)],
        [(-8.2, -112), (-5.6, -92), (-3.0, -72), (-0.2, -58), (2.6, -46), (5.2, -38), (8.4, -34)],
    ]
    for i, spec in enumerate(river_specs):
        add_surface_curve(f"wrapped_river_{i}", [(x, pymath.radians(a)) for x, a in spec], INNER_RADIUS, 0.035, mats["water"], lift=-0.34)
    for i, (x, a, sx) in enumerate([(-6.9, -120, 0.8), (-5.2, 75, 0.7), (-2.4, 15, 0.9), (0.9, -54, 0.8), (3.4, 88, 0.9), (5.8, -12, 1.0)]):
        add_surface_patch(f"airflow_cloud_patch_{i}", x - sx, x + sx, pymath.radians(a - 12), pymath.radians(a + 12), 3.25, mats["cloud"], lift=0.0, angle_steps=10, x_steps=3)

    # Service and heat/air/water flows running below the public surface.
    for deg, material, label in [
        (-112, mats["air"], "inward warm return"),
        (-105, mats["coolant"], "coolant trunk"),
        (-98, mats["condensate"], "condensate recovery"),
        (105, mats["pressure_line"], "pressure reserve"),
        (112, mats["hazard"], "emergency isolation"),
    ]:
        a = pymath.radians(deg)
        r = radial(a)
        add_curve_polyline(
            label.replace(" ", "_"),
            [(-8.6, r[1] * 5.42, r[2] * 5.42), (8.6, r[1] * 5.42, r[2] * 5.42)],
            0.035,
            material,
        )

    # Kappa service ring: kept as one small local maintenance marker, not the point of the scene.
    kappa_x = -2.7
    kappa_angle = pymath.radians(-45)
    kr = radial(kappa_angle)
    kt = tangent(kappa_angle)
    service_center = (kappa_x, kr[1] * 5.22, kr[2] * 5.22)
    add_box("service_ring_kappa_human_gallery", service_center, axes=((1, 0, 0), kt, kr), size=(2.4, 0.34, 0.16), material=mats["utility"])
    add_box(
        "kappa_operations_gallery_badge_route",
        (kappa_x - 0.25, kr[1] * 4.72, kr[2] * 4.72 + 0.28),
        axes=((1, 0, 0), kt, kr),
        size=(1.7, 0.24, 0.18),
        material=mats["glass"],
    )
    add_box(
        "octopoid_support_rig_prep_station",
        (kappa_x + 1.35, kr[1] * 5.05, kr[2] * 5.05 - 0.12),
        axes=((1, 0, 0), kt, kr),
        size=(0.7, 0.32, 0.2),
        material=mats["hazard"],
    )

    # Crawl throats branch outward into the shell. Seal lungs live beyond them.
    for i, offset in enumerate([-0.62, 0.0, 0.62], start=1):
        base = (kappa_x + offset, kr[1] * 5.36, kr[2] * 5.36)
        end = (kappa_x + offset, kr[1] * 6.14, kr[2] * 6.14)
        add_cylinder_between(f"kappa_crawl_throat_{i}", base, end, 0.055, mats["hazard"], vertices=10)
        bpy.ops.mesh.primitive_uv_sphere_add(segments=24, ring_count=12, radius=0.23, location=(kappa_x + offset, kr[1] * 6.0, kr[2] * 6.0))
        lung = bpy.context.object
        lung.name = f"kappa_seal_lung_{i}"
        lung.scale = (0.8, 1.0, 0.45)
        lung.data.materials.append(mats["pressure_line"])

    manifold_base = (kappa_x - 0.05, kr[1] * 5.48, kr[2] * 5.48)
    for dz, material, name in [
        (-0.12, mats["air"], "air_return_to_filters"),
        (0.0, mats["coolant"], "coolant_heat_exchanger"),
        (0.12, mats["condensate"], "condensate_drain"),
    ]:
        add_curve_polyline(
            "kappa_" + name,
            [
                (manifold_base[0] - 1.0, manifold_base[1], manifold_base[2] + dz),
                (manifold_base[0], manifold_base[1] + kt[1] * 0.55, manifold_base[2] + kt[2] * 0.55 + dz),
                (manifold_base[0] + 1.0, manifold_base[1], manifold_base[2] + dz),
            ],
            0.025,
            material,
        )

    bpy.ops.object.light_add(type="AREA", location=(-1.6, 6.7, -2.0))
    kappa_light = bpy.context.object
    kappa_light.name = "Kappa colored service inspection light"
    kappa_light.data.energy = 360
    kappa_light.data.size = 4.0

    # Labels are sparse: only the relationships the lore says a blueprint must show.
    add_label("label_inward", "INWARD: open air / light spine / hub", (5.8, 1.2, 1.0), 0.23, mats["label"])
    add_label("label_outward", "OUTWARD: utility mat -> pressure shell -> shielding", (-6.0, -3.8, -4.1), 0.21, mats["label"])
    add_label("label_regions", "mapped regions: sea, plains, cities, fields, forests, roads, rivers", (-3.4, 3.8, 3.5), 0.16, mats["label"])
    add_label("label_kappa", "one service-ring marker among many", (kappa_x, -4.2, -4.0), 0.14, mats["label"])
    add_label("label_spokes", "spoke interfaces: transit, utilities, authority", (1.8, 2.2, 3.2), 0.18, mats["label"])

    # Lighting and camera.
    bpy.ops.object.light_add(type="AREA", location=(1.5, -6.5, 7.0))
    key = bpy.context.object
    key.name = "large soft inspection light"
    key.data.energy = 650
    key.data.size = 6.5
    bpy.ops.object.camera_add(location=(15.5, -19.0, 12.5))
    bpy.context.scene.camera = bpy.context.object
    bpy.context.object.name = "Camera_Bloom_Cutaway"
    aim_camera(bpy.context.object, (0.0, 0.0, 0.0))
    bpy.context.object.data.type = "ORTHO"
    bpy.context.object.data.ortho_scale = 20.5

    bpy.ops.object.camera_add(location=(-0.8, 9.5, -7.5))
    detail_camera = bpy.context.object
    detail_camera.name = "Camera_Interior_World"
    aim_camera(detail_camera, (0.0, 0.0, 0.0))
    detail_camera.data.type = "ORTHO"
    detail_camera.data.ortho_scale = 9.0

    bpy.ops.object.camera_add(location=(-13.5, 0.45, 0.35))
    cap_camera = bpy.context.object
    cap_camera.name = "Camera_Hubward_Endcap_Terraces"
    aim_camera(cap_camera, (-9.05, 0.0, 0.0))
    cap_camera.data.type = "ORTHO"
    cap_camera.data.ortho_scale = 6.6

    bpy.context.scene.render.engine = "BLENDER_EEVEE"
    if hasattr(bpy.context.scene, "eevee"):
        bpy.context.scene.eevee.taa_render_samples = 24
    bpy.context.scene.render.resolution_x = 1400
    bpy.context.scene.render.resolution_y = 1000
    bpy.context.scene.view_settings.view_transform = "Filmic"
    bpy.context.scene.view_settings.look = "Medium High Contrast"


def main():
    import bpy

    # Force Geometry Script group creation before scene objects reference it.
    vg_bloom_light_spine()
    build_scene()

    out_dir = Path("experiments/generated/aetheria_bloom")
    out_dir.mkdir(parents=True, exist_ok=True)
    blend_path = out_dir / "aetheria_bloom_habitat.blend"
    render_path = out_dir / "aetheria_bloom_habitat.png"
    detail_render_path = out_dir / "aetheria_bloom_interior_world.png"
    cap_render_path = out_dir / "aetheria_bloom_hubward_endcap_terraces.png"
    bpy.ops.wm.save_as_mainfile(filepath=str(blend_path.resolve()))
    bpy.context.scene.camera = bpy.data.objects["Camera_Bloom_Cutaway"]
    bpy.context.scene.render.filepath = str(render_path.resolve())
    bpy.ops.render.render(write_still=True)
    bpy.context.scene.camera = bpy.data.objects["Camera_Interior_World"]
    bpy.context.scene.render.filepath = str(detail_render_path.resolve())
    bpy.ops.render.render(write_still=True)
    bpy.context.scene.camera = bpy.data.objects["Camera_Hubward_Endcap_Terraces"]
    bpy.context.scene.render.filepath = str(cap_render_path.resolve())
    bpy.ops.render.render(write_still=True)
    print("AETHERIA_BLOOM_BLEND", blend_path.resolve())
    print("AETHERIA_BLOOM_RENDER", render_path.resolve())
    print("AETHERIA_BLOOM_INTERIOR_RENDER", detail_render_path.resolve())
    print("AETHERIA_BLOOM_HUBWARD_ENDCAP_RENDER", cap_render_path.resolve())
    group = bpy.data.node_groups.get("VG Bloom Light Spine")
    if group:
        print("AETHERIA_BLOOM_GN_GROUP", group.name, len(group.nodes), len(group.links))


if __name__ == "__main__":
    main()

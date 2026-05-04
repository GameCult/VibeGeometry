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


TAU = pymath.tau
AXIS_LENGTH = 18.0
CUT_START = pymath.radians(-132.0)
CUT_END = pymath.radians(132.0)
INNER_RADIUS = 5.0


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


def mat(name, color, emission=False, strength=0.0, alpha=1.0):
    import bpy

    material = bpy.data.materials.new(name)
    material.diffuse_color = (color[0], color[1], color[2], alpha)
    material.use_nodes = True
    bsdf = material.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        if emission:
            bsdf.inputs["Emission Color"].default_value = (color[0], color[1], color[2], 1.0)
            bsdf.inputs["Emission Strength"].default_value = strength
        bsdf.inputs["Base Color"].default_value = (color[0], color[1], color[2], alpha)
        bsdf.inputs["Roughness"].default_value = 0.62
        bsdf.inputs["Alpha"].default_value = alpha
    if alpha < 1.0:
        material.blend_method = "BLEND"
        material.use_screen_refraction = True
        material.show_transparent_back = True
    return material


def clear_scene():
    import bpy

    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete()


def radial(angle: float):
    return (0.0, pymath.cos(angle), pymath.sin(angle))


def tangent(angle: float):
    return (0.0, -pymath.sin(angle), pymath.cos(angle))


def add_shell_segment(name, radius, half_length, thickness, material, angle_steps=96, x_steps=8):
    import bpy

    verts = []
    faces = []
    for ix in range(x_steps + 1):
        x = -half_length + (2.0 * half_length * ix / x_steps)
        for ia in range(angle_steps + 1):
            a = CUT_START + (CUT_END - CUT_START) * ia / angle_steps
            verts.append((x, radius * pymath.cos(a), radius * pymath.sin(a)))
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


def surface_point(x, angle, radius=INNER_RADIUS, lift=-0.04):
    r = radius + lift
    return (x, r * pymath.cos(angle), r * pymath.sin(angle))


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


def add_cylinder_between(name, start, end, radius, material, vertices=16):
    import bpy
    from mathutils import Vector

    start_v = Vector(start)
    end_v = Vector(end)
    mid = (start_v + end_v) / 2.0
    direction = end_v - start_v
    length = direction.length
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices, radius=radius, depth=length, location=mid)
    obj = bpy.context.object
    obj.name = name
    obj.data.name = name + "Mesh"
    obj.rotation_euler = direction.to_track_quat("Z", "Y").to_euler()
    obj.data.materials.append(material)
    return obj


def add_curve_polyline(name, points, bevel, material, resolution=2):
    import bpy

    curve = bpy.data.curves.new(name + "Curve", "CURVE")
    curve.dimensions = "3D"
    curve.resolution_u = resolution
    curve.bevel_depth = bevel
    curve.bevel_resolution = 4
    spline = curve.splines.new("POLY")
    spline.points.add(len(points) - 1)
    for point, co in zip(spline.points, points):
        point.co = (co[0], co[1], co[2], 1.0)
    obj = bpy.data.objects.new(name, curve)
    bpy.context.collection.objects.link(obj)
    obj.data.materials.append(material)
    return obj


def add_box(name, loc, axes, size, material):
    import bpy
    from mathutils import Matrix, Vector

    bpy.ops.mesh.primitive_cube_add(size=1.0, location=loc)
    obj = bpy.context.object
    obj.name = name
    obj.dimensions = size
    matrix = Matrix.Identity(4)
    matrix.col[0].xyz = Vector(axes[0]).normalized()
    matrix.col[1].xyz = Vector(axes[1]).normalized()
    matrix.col[2].xyz = Vector(axes[2]).normalized()
    obj.rotation_euler = matrix.to_euler()
    obj.data.materials.append(material)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    return obj


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


def aim_camera(obj, target):
    from mathutils import Vector

    direction = Vector(target) - obj.location
    obj.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()


def build_scene():
    import bpy

    clear_scene()

    mats = {
        "inner": mat("civic inner surface - open commons", (0.28, 0.30, 0.32), alpha=0.78),
        "utility": mat("utility mat amber", (0.95, 0.57, 0.18), alpha=0.42),
        "pressure": mat("pressure laminate blue", (0.18, 0.45, 0.86), alpha=0.25),
        "shield": mat("aggregate shielding graphite", (0.08, 0.075, 0.07), alpha=0.86),
        "hub": mat("despun hub white", (0.82, 0.86, 0.88), alpha=0.88),
        "light": mat("light spine gold", (1.0, 0.78, 0.25), emission=True, strength=1.6),
        "farm": mat("TCS Root farms", (0.15, 0.55, 0.24), alpha=0.92),
        "district": mat("surface districts", (0.55, 0.58, 0.62), alpha=0.95),
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

    add_shell_segment("01_open_civic_inner_surface", 5.0, AXIS_LENGTH / 2, 0.05, mats["inner"])
    add_shell_segment("02_utility_mat_service_interlayer", 5.35, AXIS_LENGTH / 2, 0.08, mats["utility"])
    add_shell_segment("03_pressure_structural_shell", 5.75, AXIS_LENGTH / 2, 0.12, mats["pressure"])
    add_shell_segment("04_outer_aggregate_shielding", 6.35, AXIS_LENGTH / 2, 0.32, mats["shield"])

    add_cylinder_between("despun_axial_hub", (-9.8, 0, 0), (9.8, 0, 0), 0.42, mats["hub"], vertices=32)
    add_cylinder_between("traffic_light_spire_core", (-9.2, 0, 0), (9.2, 0, 0), 0.13, mats["light"], vertices=16)
    add_gn_light_spine(mats["light"])

    # Spokes and transfer collars: places where frame changes, and therefore where class power gathers.
    spoke_angles = [pymath.radians(a) for a in (-96, -45, 0, 45, 96)]
    for idx, a in enumerate(spoke_angles, start=1):
        r = radial(a)
        add_cylinder_between(
            f"rotating_spoke_{idx:02d}_transfer_trunk",
            (0.0, r[1] * 0.52, r[2] * 0.52),
            (0.0, r[1] * 5.18, r[2] * 5.18),
            0.08,
            mats["hub"],
            vertices=12,
        )
        add_cylinder_between(
            f"spoke_base_transfer_collar_{idx:02d}",
            (-0.35, r[1] * 5.06, r[2] * 5.06),
            (0.35, r[1] * 5.06, r[2] * 5.06),
            0.22,
            mats["pressure_line"],
            vertices=24,
        )

    # Civic skin: Rama-style map layers wrapped to the rotating inner surface.
    # Blooms do not copy Rama's poles/sea literally, but the procedural lesson is
    # useful: big readable regions first, then roads, rivers, cities, fields,
    # forests, clouds, and local infrastructure on top.
    add_surface_patch("central_civic_sea_band", -1.15, 1.15, pymath.radians(-126), pymath.radians(126), INNER_RADIUS, mats["water"], lift=-0.07, angle_steps=64, x_steps=4)
    for i, (x0, x1) in enumerate([(-8.2, -6.1), (-5.8, -3.6), (3.6, 5.8), (6.1, 8.2)]):
        add_surface_patch(f"plain_grass_region_{i}", x0, x1, pymath.radians(-118), pymath.radians(118), INNER_RADIUS, mats["farm"], angle_steps=36, x_steps=3)
    for i, (x0, x1, a0, a1) in enumerate([
        (-6.0, -4.1, -108, -74),
        (-4.9, -3.2, 48, 86),
        (3.1, 4.7, -92, -58),
        (5.0, 6.9, 68, 106),
        (6.8, 8.4, -30, 18),
    ]):
        add_surface_patch(f"forest_region_{i}", x0, x1, pymath.radians(a0), pymath.radians(a1), INNER_RADIUS, mats["forest"], lift=-0.12, angle_steps=12, x_steps=3)
    for i, (x0, x1, a0, a1) in enumerate([
        (-7.4, -6.0, 48, 86),
        (-3.1, -1.7, -88, -50),
        (1.8, 3.4, 40, 82),
        (5.4, 7.0, -112, -76),
    ]):
        add_surface_patch(f"district_city_region_{i}", x0, x1, pymath.radians(a0), pymath.radians(a1), INNER_RADIUS, mats["district"], lift=-0.16, angle_steps=8, x_steps=3)
        for bx in [x0 + 0.25, (x0 + x1) / 2, x1 - 0.25]:
            for ba in [pymath.radians(a0 + 7), pymath.radians((a0 + a1) / 2), pymath.radians(a1 - 7)]:
                add_surface_box(f"city_block_{i}_{bx:.1f}_{ba:.2f}", bx, ba, mats["city"], size=(0.18, 0.1, 0.16), radial_lift=-0.27)
    road_specs = [
        [(-8.4, -90), (-6.8, -70), (-5.2, -42), (-3.2, -18), (-1.1, -6), (1.1, 4), (3.4, 25), (5.8, 48), (8.2, 74)],
        [(-7.8, 92), (-5.0, 72), (-2.4, 50), (0.0, 38), (2.7, 55), (5.2, 83), (8.0, 104)],
        [(-8.0, -22), (-5.6, -10), (-3.3, 10), (-1.2, 32), (0.8, 42), (2.8, 34), (5.4, 12), (8.1, -14)],
    ]
    for i, spec in enumerate(road_specs):
        add_surface_curve(f"wrapped_road_graph_{i}", [(x, pymath.radians(a)) for x, a in spec], INNER_RADIUS, 0.018, mats["road"], lift=-0.24)
    river_specs = [
        [(-8.1, 18), (-6.5, 10), (-4.9, -4), (-3.2, -20), (-1.0, -32)],
        [(1.0, 18), (2.6, 5), (4.4, -12), (6.2, -28), (8.1, -42)],
    ]
    for i, spec in enumerate(river_specs):
        add_surface_curve(f"wrapped_river_{i}", [(x, pymath.radians(a)) for x, a in spec], INNER_RADIUS, 0.04, mats["water"], lift=-0.18)
    for i, (x, a, sx) in enumerate([(-5.5, -42, 0.65), (-2.0, 62, 0.5), (2.4, -66, 0.55), (5.9, 25, 0.7)]):
        add_surface_patch(f"interior_cloud_patch_{i}", x - sx, x + sx, pymath.radians(a - 8), pymath.radians(a + 8), 3.1, mats["cloud"], lift=0.0, angle_steps=8, x_steps=2)

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
    bpy.context.object.data.ortho_scale = 18.0

    bpy.ops.object.camera_add(location=(-0.8, 9.5, -7.5))
    detail_camera = bpy.context.object
    detail_camera.name = "Camera_Interior_World"
    aim_camera(detail_camera, (0.0, 0.0, 0.0))
    detail_camera.data.type = "ORTHO"
    detail_camera.data.ortho_scale = 9.0

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
    bpy.ops.wm.save_as_mainfile(filepath=str(blend_path.resolve()))
    bpy.context.scene.camera = bpy.data.objects["Camera_Bloom_Cutaway"]
    bpy.context.scene.render.filepath = str(render_path.resolve())
    bpy.ops.render.render(write_still=True)
    bpy.context.scene.camera = bpy.data.objects["Camera_Interior_World"]
    bpy.context.scene.render.filepath = str(detail_render_path.resolve())
    bpy.ops.render.render(write_still=True)
    print("AETHERIA_BLOOM_BLEND", blend_path.resolve())
    print("AETHERIA_BLOOM_RENDER", render_path.resolve())
    print("AETHERIA_BLOOM_INTERIOR_RENDER", detail_render_path.resolve())
    group = bpy.data.node_groups.get("VG Bloom Light Spine")
    if group:
        print("AETHERIA_BLOOM_GN_GROUP", group.name, len(group.nodes), len(group.links))


if __name__ == "__main__":
    main()

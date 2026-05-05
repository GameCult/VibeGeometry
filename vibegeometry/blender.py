"""Thin bpy helpers for scene construction and inspection renders."""

from __future__ import annotations


def add_material(name, color, emission=False, strength=0.0, alpha=1.0):
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


def add_mesh_parts(name, verts, faces, material):
    import bpy

    mesh = bpy.data.meshes.new(name + "Mesh")
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    obj.data.materials.append(material)
    return obj


def add_multi_polyline_curve(name, lines, bevel, material, resolution=2):
    import bpy

    curve = bpy.data.curves.new(name + "Curve", "CURVE")
    curve.dimensions = "3D"
    curve.resolution_u = resolution
    curve.bevel_depth = bevel
    curve.bevel_resolution = 2
    for line in lines:
        spline = curve.splines.new("POLY")
        spline.points.add(len(line) - 1)
        for point, co in zip(spline.points, line):
            point.co = (co[0], co[1], co[2], 1.0)
    obj = bpy.data.objects.new(name, curve)
    bpy.context.collection.objects.link(obj)
    obj.data.materials.append(material)
    return obj


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


def aim_camera(obj, target):
    from mathutils import Vector

    direction = Vector(target) - obj.location
    obj.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()


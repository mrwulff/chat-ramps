import bpy, sys

argv = sys.argv
argv = argv[argv.index("--") + 1:]

svg_a, svg_b, out_path = argv[:3]

params = list(map(float, argv[3:]))

xA, yA, sA, rA, hA, xB, yB, sB, rB, hB = params


def import_svg(path):
    bpy.ops.import_curve.svg(filepath=path)
    objs = bpy.context.selected_objects

    bpy.ops.object.convert(target='MESH')

    bpy.ops.object.join()
    obj = bpy.context.active_object

    # APPLY TRANSFORMS
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

    # CENTER GEOMETRY TO ORIGIN
    bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='BOUNDS')
    obj.location = (0,0,0)

    return obj


def place(obj, x, y, scale, rot, height):
    # SCALE XY ONLY
    factor = scale / 10.0
    obj.scale.x *= factor
    obj.scale.y *= factor
    obj.scale.z = 1.0

    bpy.ops.object.transform_apply(scale=True)

    # ROTATION
    obj.rotation_euler[2] = rot * 3.14159 / 180.0

    # POSITION (CENTER BASED)
    obj.location.x = x
    obj.location.y = y

    # Z HEIGHT
    bbox = [v[2] for v in obj.bound_box]
    min_z = min(bbox)

    obj.location.z += (height - min_z)


# IMPORT + PLACE
logoA = import_svg(svg_a)
place(logoA, xA, yA, sA, rA, hA)

if svg_b and svg_b != "None":
    logoB = import_svg(svg_b)
    place(logoB, xB, yB, sB, rB, hB)


# EXPORT
bpy.ops.export_mesh.stl(filepath=out_path)
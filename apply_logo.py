import bpy, sys
import bmesh
from mathutils import Vector
import math


argv = sys.argv
argv = argv[argv.index("--") + 1 :]

svg_a, svg_b, out_path = argv[:3]

params = list(map(float, argv[3:]))

xA, yA, sA, rA, hA, xB, yB, sB, rB, hB = params


def import_svg(path):
    print(f"\nIMPORTING: {path}")

    before = set(bpy.data.objects)

    bpy.ops.import_curve.svg(filepath=path)

    after = set(bpy.data.objects)
    new_objs = list(after - before)

    if not new_objs:
        raise RuntimeError(f"SVG IMPORT FAILED: {path}")

    print(f"Imported {len(new_objs)} objects")

    # join all curves into one
    bpy.ops.object.select_all(action="DESELECT")
    for o in new_objs:
        o.select_set(True)

        if o.type == "CURVE":
            o.data.extrude = 0.001  # keep your extrusion

    bpy.context.view_layer.objects.active = new_objs[0]
    bpy.ops.object.join()

    # CENTER OBJECT TO ORIGIN (CRITICAL)

    obj = bpy.context.active_object
    obj.name = "name"

    bpy.context.view_layer.update()

    # get mesh
    if obj.type == "CURVE":
        bpy.ops.object.convert(target="MESH")

    mesh = obj.data

    # enter edit mode
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.mode_set(mode="EDIT")

    bm = bmesh.from_edit_mesh(mesh)

    # compute center in LOCAL space
    xs = [v.co.x for v in bm.verts]
    ys = [v.co.y for v in bm.verts]

    cx = (min(xs) + max(xs)) / 2
    cy = (min(ys) + max(ys)) / 2

    # move geometry to origin
    for v in bm.verts:
        v.co.x -= cx
        v.co.y -= cy

    bmesh.update_edit_mesh(mesh)

    bpy.ops.object.mode_set(mode="OBJECT")

    # reset object location
    obj.location.x = 0
    obj.location.y = 0

    print("GEOMETRY NORMALIZED (REAL)")
    return obj


def place(obj, target_x, target_y, target_width, target_rot, z_height):
    print("\n========== NEW LOGO ==========")
    print("INPUT:", target_x, target_y, target_width, target_rot, z_height)

    bpy.context.view_layer.objects.active = obj

    # -----------------------------
    # INITIAL BBOX
    # -----------------------------
    bbox = [obj.matrix_world @ Vector(v) for v in obj.bound_box]

    min_x = min(v.x for v in bbox)
    max_x = max(v.x for v in bbox)
    min_y = min(v.y for v in bbox)
    max_y = max(v.y for v in bbox)

    width = max_x - min_x

    print("INITIAL WIDTH:", width)

    # -----------------------------
    # SCALE (NO APPLY)
    # -----------------------------
    if width > 0:
        scale_factor = target_width / width
        obj.scale *= scale_factor

    # -----------------------------
    # ROTATION
    # -----------------------------
    obj.rotation_euler[2] = math.radians(target_rot)

    # -----------------------------
    # UPDATE + NEW BBOX
    # -----------------------------
    bpy.context.view_layer.update()

    bbox = [obj.matrix_world @ Vector(v) for v in obj.bound_box]

    min_x = min(v.x for v in bbox)
    max_x = max(v.x for v in bbox)
    min_y = min(v.y for v in bbox)
    max_y = max(v.y for v in bbox)

    center_x = (min_x + max_x) / 2
    center_y = (min_y + max_y) / 2

    print("CENTER AFTER SCALE:", center_x, center_y)

    # -----------------------------
    # MOVE USING CENTER
    # -----------------------------
    dx = target_x - center_x
    dy = target_y - center_y

    obj.location.x += dx
    obj.location.y += dy

    print("MOVE DELTA:", dx, dy)

    # -----------------------------
    # Z HEIGHT (IMPORTANT FIX)
    # -----------------------------
    # -----------------------------
    # FIX Z USING BOTTOM OF MESH
    # -----------------------------
    bpy.context.view_layer.update()

    bbox = [obj.matrix_world @ Vector(v) for v in obj.bound_box]
    min_z = min(v.z for v in bbox)

    dz = z_height - min_z
    obj.location.z += dz

    print("Z FIX:", min_z, "->", z_height, "delta:", dz)
    print("FINAL LOCATION:", obj.location)


# IMPORT + PLACE
logoA = import_svg(svg_a)
place(logoA, xA, yA, sA, rA, hA)

if svg_b and svg_b != "None":
    logoB = import_svg(svg_b)
    place(logoB, xB, yB, sB, rB, hB)


# EXPORT
bpy.ops.export_mesh.stl(filepath=out_path)

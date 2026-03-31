import bpy
import bmesh
import sys
import math

argv = sys.argv
argv = argv[argv.index("--") + 1 :]

svg_a, svg_b, out_path = argv[0], argv[1], argv[2]

xA = argv[3]
yA = argv[4]
scaleA = argv[5]
# rotA = argv[6]
# colorA = argv[7]

# xB, yB, scaleB, rotB = map(float, argv[9:13])
# colorB = argv[14]


# -------------------------------
# IMPORT + NORMALIZE SVG
# -------------------------------
def import_svg(path, name):
    print(f"\nIMPORTING: {path}")

    before = set(bpy.data.objects)
    bpy.ops.import_curve.svg(filepath=path)
    after = set(bpy.data.objects)

    new_objs = list(after - before)

    if not new_objs:
        raise RuntimeError(f"SVG IMPORT FAILED: {path}")

    curves = [o for o in new_objs if o.type == "CURVE"]
    if not curves:
        raise RuntimeError("No CURVE objects found")

    bpy.ops.object.select_all(action="DESELECT")

    for o in curves:
        o.select_set(True)
        o.data.extrude = 0.001  # temporary

    bpy.context.view_layer.objects.active = curves[0]
    bpy.ops.object.join()

    obj = bpy.context.active_object
    obj.name = name

    bpy.context.view_layer.update()

    if obj.type != "MESH":
        bpy.ops.object.convert(target="MESH")

    mesh = obj.data

    # ---- EDIT MODE ----
    bpy.ops.object.mode_set(mode="EDIT")
    bm = bmesh.from_edit_mesh(mesh)

    # CENTER
    xs = [v.co.x for v in bm.verts]
    ys = [v.co.y for v in bm.verts]

    min_x, max_x = min(xs), max(xs)
    min_y, max_y = min(ys), max(ys)

    cx = (min_x + max_x) / 2
    cy = (min_y + max_y) / 2

    for v in bm.verts:
        v.co.x -= cx
        v.co.y -= cy

    # NORMALIZE WIDTH → 1
    xs = [v.co.x for v in bm.verts]
    min_x, max_x = min(xs), max(xs)
    width = max_x - min_x

    if width == 0:
        raise RuntimeError("Invalid SVG width")

    scale_to_unit = 1.0 / width

    for v in bm.verts:
        v.co.x *= scale_to_unit
        v.co.y *= scale_to_unit

    bmesh.update_edit_mesh(mesh)
    bpy.ops.object.mode_set(mode="OBJECT")

    # reset transforms
    obj.location = (0, 0, 0)
    obj.rotation_euler = (0, 0, 0)
    obj.scale = (1, 1, 1)

    print("NORMALIZED → center=0, width=1")

    return obj


# -------------------------------
# APPLY TRANSFORMS (FINAL)
# -------------------------------
def place_logo(obj, x, y, scale, rot, height):
    print("\n========== PLACE LOGO ==========")
    print("INPUT:", x, y, scale, rot, height)

    # SCALE (XY ONLY)
    obj.scale = (scale, scale, 1)

    # ROTATION (FIXED DIRECTION)
    obj.rotation_euler[2] = math.radians(-rot)

    # POSITION (DIRECT — no offsets anymore)
    obj.location.x = x
    obj.location.y = y

    bpy.context.view_layer.update()

    # --- Z: SET TRUE HEIGHT (NOT SCALE) ---
    mesh = obj.data

    bpy.ops.object.mode_set(mode="EDIT")
    bm = bmesh.from_edit_mesh(mesh)

    # flatten first (reset any weird Z)
    for v in bm.verts:
        v.co.z = 0

    # extrude upward
    bmesh.ops.extrude_face_region(bm, geom=bm.faces)
    bm.verts.ensure_lookup_table()

    for v in bm.verts:
        if v.co.z > 0:
            v.co.z = height

    bmesh.update_edit_mesh(mesh)
    bpy.ops.object.mode_set(mode="OBJECT")

    # --- SNAP TO RAMP (Z=0 BASE) ---
    obj.location.z = 0

    print("FINAL LOCATION:", obj.location)


# -------------------------------
# RUN PIPELINE
# -------------------------------
print("START CLEAN PIPELINE")

logo_a = import_svg(svg_a, "LOGO_A")
logo_b = import_svg(svg_b, "LOGO_B")

place_logo(logo_a, xA, yA, scaleA, rotA, heightA)
place_logo(logo_b, xB, yB, scaleB, rotB, heightB)


# -------------------------------
# EXPORT STL (BLENDER 5 FIX)
# -------------------------------
bpy.ops.object.select_all(action="SELECT")
bpy.ops.wm.stl_export(filepath=out_path)

print("DONE")

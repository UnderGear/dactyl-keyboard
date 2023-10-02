import bpy
import bmesh
import os
import sys
import time
import mathutils
from math import pi, radians, sin, cos
from contextlib import contextmanager

debug_trace = True

def __init__():
    pass

def debugprint(info):
    if debug_trace:
        print(info)


def clear_selection():
    # debugprint("CLEARING SELECTION")
    bpy.context.view_layer.objects.active = None
    bpy.ops.object.select_all(action='DESELECT')

def select(shape):
    debugprint("SELECTING:  {}".format(shape))
    clear_selection()
    shape.select_set(1)
    bpy.context.view_layer.objects.active = shape

def duplicate(shape):
    clear_selection()
    select(shape)
    bpy.ops.object.duplicate()
    shape.select_set(0)
    new_shape = bpy.context.object
    debugprint("DUPLICATING:  {} to {}".format(shape, new_shape))
    return new_shape

def delete_shapes(shapes):
    debugprint("DELETING SHAPES:  {}".format(shapes))
    for item in shapes:
        debugprint("DELETING SHAPE:  {}".format(item))
        select(item)
        bpy.ops.object.delete(use_global=False, confirm=False)
        clear_selection()

def box(width, height, depth):
    clear_selection()
    bpy.ops.mesh.primitive_cube_add(
        size=1,
        enter_editmode=False,
        align='WORLD',
        location=(0, 0, 0),
        scale=(width, height, depth)
    )
    shape = bpy.context.object
    clear_selection()
    debugprint("CREATED BOX:  {}".format(shape))
    return shape


def cylinder(radius, height, segments=8):
    clear_selection()
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=segments, radius=radius, depth=height, location=(0, 0, 0), rotation=(0, 0, 0)
    )
    shape = bpy.context.object
    clear_selection()
    debugprint("CREATED CYLINDER:  {}".format(shape))
    return shape


def sphere(radius, subdivisions=3):
    clear_selection()
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=subdivisions, radius=radius)
    shape = bpy.context.object
    clear_selection()
    debugprint("CREATED SPHERE:  {}".format(shape))
    return shape


def cone(r1, r2, height, vertices=32):
    clear_selection()
    bpy.ops.mesh.primitive_cone_add(vertices=vertices, radius1=r1, radius2=r2, depth=height)  # , center=True)
    shape = bpy.context.object
    clear_selection()
    debugprint("CREATED CONE:  {}".format(shape))
    return shape


def rotate(shape, angle):
    debugprint("ROTATE:  {} @ {}".format(shape, angle))
    select(shape)
    bpy.ops.transform.rotate(value=-radians(angle[0]), orient_axis='X', center_override=(0.0, 0.0, 0.0))
    bpy.ops.transform.rotate(value=-radians(angle[1]), orient_axis='Y', center_override=(0.0, 0.0, 0.0))
    bpy.ops.transform.rotate(value=-radians(angle[2]), orient_axis='Z', center_override=(0.0, 0.0, 0.0))
    clear_selection()
    return shape


def translate(shape, vector):
    debugprint("TRANSLATE:  {} @ {}".format(shape, vector))
    select(shape)
    bpy.ops.transform.translate(
        value=vector,
        orient_type='GLOBAL',
        orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)),
        orient_matrix_type='GLOBAL',
        mirror=True,
        use_proportional_edit=False,
        proportional_edit_falloff='SMOOTH',
        proportional_size=1,
        use_proportional_connected=False,
        use_proportional_projected=False)
    clear_selection()
    return shape


def mirror(shape, plane=None):
    debugprint("MIRROR:  {} @ {}".format(shape, plane))
    planes = {
        'XY': [0, 0, 1],
        'YX': [0, 0, -1],
        'XZ': [0, 1, 0],
        'ZX': [0, -1, 0],
        'YZ': [1, 0, 0],
        'ZY': [-1, 0, 0],
    }
    if plane in ['XY', 'YX']:
        orient_matrix = [[1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, -1.0]]
        constraint_axis = (False, False, True)
    elif plane in ['XZ', 'ZX']:
        orient_matrix = [[1.0, 0.0, 0.0], [0.0, -1.0, 0.0], [0.0, 0.0, 1.0]]
        constraint_axis = (False, True, False)
    else:  # plane in ['YZ', 'ZY']:
        orient_matrix = [[-1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]]
        constraint_axis = (True, False, False)

    debugprint('mirror()')
    select(shape)

    bpy.ops.transform.mirror(
        orient_type='GLOBAL',
        orient_matrix=orient_matrix,
        orient_matrix_type='GLOBAL',
        constraint_axis=constraint_axis,
        gpencil_strokes=False,
        center_override=(0.0, 0.0, 0.0),
        release_confirm=False,
        use_accurate=False
    )
    clear_selection()
    return shape

def boolean_cleanup(
        shape,
        remove_doubles_threshold=.01,
        dissolve_limited=True,
        vert_connect_concave=True,
        dissolve_degenerate=True,
        delete_loose=True,
        collapse_non_manifold=False,
        beautify_faces=False,
        recalc_normals=True,
):
    debugprint("CLEANING UP: {}".format(shape))
    select(shape)

    bpy.ops.object.editmode_toggle()
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.fill_holes()

    if remove_doubles_threshold is not None:
        bpy.ops.mesh.remove_doubles(threshold=remove_doubles_threshold)

    bpy.ops.mesh.quads_convert_to_tris(quad_method='BEAUTY', ngon_method='BEAUTY')

    if (dissolve_limited):
        bpy.ops.mesh.dissolve_limited(angle_limit=0.01)

    if (vert_connect_concave):
        bpy.ops.mesh.vert_connect_concave()
    if (dissolve_degenerate):
        bpy.ops.mesh.dissolve_degenerate()

    if (delete_loose):
        bpy.ops.mesh.delete_loose()

    bpy.ops.mesh.tris_convert_to_quads()

    bpy.ops.object.editmode_toggle()
    # if (delete_operands):
    #     D.objects.remove(bool_ob, do_unlink=True)

    if (dissolve_limited):
        bpy.ops.object.modifier_add(type='DECIMATE')
        bpy.context.object.modifiers["Decimate"].decimate_type = 'DISSOLVE'
        bpy.context.object.modifiers["Decimate"].angle_limit = 0.001
        bpy.ops.object.modifier_apply(modifier="Decimate")

    bpy.ops.object.editmode_toggle()
    bpy.ops.mesh.select_all(action='SELECT')

    if (dissolve_degenerate):
        bpy.ops.mesh.dissolve_degenerate()

    bpy.ops.mesh.quads_convert_to_tris(quad_method='BEAUTY', ngon_method='BEAUTY')

    bpy.ops.mesh.select_mode(use_extend=False, use_expand=False, type='VERT')
    bpy.ops.mesh.select_all(action='DESELECT')

    bpy.ops.mesh.select_non_manifold(extend=True, use_wire=True, use_boundary=True, use_multi_face=True,
                                     use_non_contiguous=False, use_verts=True)
    bpy.ops.object.editmode_toggle()

    selected_verts = list(filter(lambda v: v.select, shape.data.vertices))

    if (len(selected_verts) != 0):
        print("Non manifold geometry found.")
        if (collapse_non_manifold):
            bpy.ops.object.editmode_toggle()
            bpy.ops.mesh.merge(type='COLLAPSE')
            bpy.ops.mesh.delete_loose()
            bpy.ops.object.editmode_toggle()

    if (beautify_faces):
        bpy.ops.object.editmode_toggle()
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.mesh.beautify_fill(angle_limit=3.14159)
        bpy.ops.object.editmode_toggle()

    if (recalc_normals):
        bpy.ops.object.editmode_toggle()
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.mesh.normals_make_consistent(inside=False)
        bpy.ops.object.editmode_toggle()

    return True


def union(shapes, cleanup=True):
    clear_selection()
    shape = None
    debugprint("UNION SHAPES: {}".format(shapes))
    for item in shapes:
        if item is None:
            continue
        if shape is None:
            shape = item

        elif not item == shape:
            select(shape)
            bpy.ops.object.modifier_add(type='BOOLEAN')
            bpy.context.object.modifiers["Boolean"].operation = 'UNION'
            bpy.context.object.modifiers["Boolean"].solver = 'EXACT'
            bpy.context.object.modifiers["Boolean"].object = item
            bpy.ops.object.modifier_apply(modifier="Boolean")
            boolean_cleanup(shape)
            clear_selection()
            delete_shapes([item])
            # select(item)
            # bpy.ops.object.delete(use_global=False, confirm=False)
            clear_selection()
            if cleanup:
                boolean_cleanup(shape)
    debugprint("UNIONED SHAPE: {}".format(shape))
    return shape

def add(shapes):
    debugprint('add()')
    return shapes


def difference(shape, shapes, cleanup=True):
    debugprint('DIFFERENCE: {} sub {}'.format(shape, shapes))
    for item in shapes:
        select(shape)
        bpy.ops.object.modifier_add(type='BOOLEAN')
        bpy.context.object.modifiers["Boolean"].operation = 'DIFFERENCE'
        bpy.context.object.modifiers["Boolean"].solver = 'EXACT'
        bpy.context.object.modifiers["Boolean"].object = item
        bpy.ops.object.modifier_apply(modifier="Boolean")
        clear_selection()
        delete_shapes([item])
        if cleanup:
            boolean_cleanup(shape)
    return shape

def intersect(shape1, shape2,  cleanup=True):
    debugprint('INTERSECT {} and {}'.format(shape1, shape2))
    select(shape1)
    bpy.ops.object.modifier_add(type='BOOLEAN')
    bpy.context.object.modifiers["Boolean"].operation = 'INTERSECT'
    bpy.context.object.modifiers["Boolean"].solver = 'EXACT'
    bpy.context.object.modifiers["Boolean"].object = shape2
    bpy.ops.object.modifier_apply(modifier="Boolean")
    delete_shapes([shape2])
    clear_selection()
    if cleanup:
        boolean_cleanup(shape1)
    debugprint("RESULT: {}".format(shape1))
    return shape1

def add_points(shape, points):
    debugprint("ADD POINTS: {} to {}".format(points, shape))
    if points is not None:
        select(shape)
        mesh = bpy.data.meshes[shape.data.name]
        for v in points:
            mesh.verts.new(v)
        clear_selection()
    return shape


def hull_from_points(points, cleanup=True):
    debugprint("HULL POINTS: {}".format(points))
    clear_selection()
    bm = bmesh.new()
    for v in points:
        bm.verts.new(v)

    me = bpy.data.meshes.new("Hull")
    bm.to_mesh(me)

    ob = bpy.data.objects.new("Hull", me)
    bpy.data.collections["Collection"].objects.link(ob)
    clear_selection()
    ob2 = hull_from_shapes([ob])
    delete_shapes([ob])
    if cleanup:
        clear_selection()
    boolean_cleanup(ob2)
    return ob2


def hull_from_shapes(shapes, points=None, cleanup=True):
    debugprint("HULL FROM SHAPES: {}, {}".format(shapes, points))
    clear_selection()

    if len(shapes) > 1:
            shape = union(shapes, cleanup=False)
    else:
        shape = shapes[0]
    select(shape)
    if points is not None:
        shape = add_points(shape, points)
    select(shape)
    if not shape.data.is_editmode:
        bpy.ops.object.editmode_toggle()
    debugprint("EDITMODE = {}".format(shape.data.is_editmode))
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.convex_hull(
        delete_unused=True, use_existing_faces=False, make_holes=False, join_triangles=True,
        face_threshold=0.1, shape_threshold=0.1, uvs=False, vcols=False, seam=False,
        sharp=False, materials=False
    )
    if shape.data.is_editmode:
        bpy.ops.object.editmode_toggle()
    debugprint("EDITMODE = {}".format(shape.data.is_editmode))
    clear_selection()
    debugprint("SHAPE: {}".format(shape))
    if cleanup:
        boolean_cleanup(shape)
    return shape


def tess_hull(shapes, sl_tol=.5, sl_angTol=1):
    return hull_from_shapes(shapes)


def triangle_hulls(shapes):
    debugprint("TRIANGLE HULLS: {}".format(shapes))

    hulls = []
    for i in range(len(shapes) - 2):
        hull_shapes = []
        for shp in shapes[i: (i + 3)]:
            hull_shapes.append(duplicate(shp))
        hulls.append(hull_from_shapes(hull_shapes))
    debugprint("HULLS: {}".format(hulls))
    shape = union(hulls)
    delete_shapes(shapes)
    debugprint("COMPLETED HULL: {}".format(shape))
    return shape

def bottom_hull(p, height=0.001):
    debugprint("BOTTOM HULLS: {}".format(p))
    shape = None
    for item in p:
        item2 = duplicate(item)
        item2 = translate(item2, (0, 0, -10))
        t_shape = hull_from_shapes([item, item2])

        if shape is None:
            shape = t_shape
        else:
            shape = union([shape, t_shape])
    return shape


def polyline(point_list):
    debugprint("POLYGON: {}".format(point_list))
    clear_selection()
    bm = bmesh.new()
    for v in point_list:
        bm.verts.new((v[0], v[1], 0))
    bm.faces.new(bm.verts)

    bm.normal_update()

    me = bpy.data.meshes.new("Polygon")
    bm.to_mesh(me)

    ob = bpy.data.objects.new("Polygon", me)
    bpy.data.collections["Collection"].objects.link(ob)
    clear_selection()
    debugprint("COMPLETED POLYGON: {}".format(ob))
    return ob


def extrude_poly(outer_poly, inner_polys=None, height=1):
    debugprint("EXTRUDE POLYGON: {}".format(outer_poly))
    select(outer_poly)
    bpy.ops.object.editmode_toggle()
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.extrude_region_move(
        MESH_OT_extrude_region={"use_normal_flip": False, "use_dissolve_ortho_edges": False, "mirror": False},
        TRANSFORM_OT_translate={"value": (0, 0, 2.2568), "orient_type": 'NORMAL',
                                "orient_matrix": ((1, 0, 0), (0, 1, 0), (0, 0, 1)),
                                "orient_matrix_type": 'NORMAL', "constraint_axis": (False, False, True),
                                "mirror": False, "use_proportional_edit": False, "proportional_edit_falloff": 'SMOOTH',
                                "proportional_size": height, "use_proportional_connected": False,
                                "use_proportional_projected": False, "snap": False, "snap_target": 'CLOSEST',
                                "snap_point": (0, 0, 0), "snap_align": False, "snap_normal": (0, 0, 0),
                                "gpencil_strokes": False, "cursor_transform": False, "texture_space": False,
                                "remove_on_cancel": False, "release_confirm": False, "use_accurate": False,
                                "use_automerge_and_split": False})
    bpy.ops.object.editmode_toggle()
    clear_selection()

    shapes = []
    if inner_polys is not None:
        debugprint("REMOVE INNER: {}".format(inner_polys))
        shape = union(inner_polys)
        shape = extrude_poly(outer_poly=shape, height=height)
        outer_poly = difference(outer_poly, shape)
        clear_selection()
    else:
        clear_selection()

    debugprint("COMPLETED POLYGON: {}".format(outer_poly))
    return outer_poly


def import_file(fname, convexity=5):
    debugprint("IMPORTING FROM {}".format(fname))
    clear_selection()
    bpy.ops.import_mesh.stl(
        filepath=fname,
        filter_glob='*.stl',
        files=None,
        directory='',
        global_scale=1.0,
        use_scene_unit=False,
        use_facet_normal=False,
        axis_forward='Y',
        axis_up='Z'
    )
    shape = bpy.context.object
    clear_selection()
    return shape


def export_file(shape, fname):
    debugprint("EXPORTING TO {}".format(fname))
    select(shape)

    dat = bpy.ops.export_mesh.stl(
        filepath='',
        check_existing=True,
        filter_glob='*.stl',
        use_selection=True,
        global_scale=1.0,
        use_scene_unit=False,
        ascii=False,
        use_mesh_modifiers=True,
        batch_mode='OFF',
        global_space=((0.0, 0.0, 0.0, 0.0), (0.0, 0.0, 0.0, 0.0), (0.0, 0.0, 0.0, 0.0), (0.0, 0.0, 0.0, 0.0)),
        axis_forward='Y',
        axis_up='Z'
    )
    clear_selection()
    return dat


def export_dxf(shape, fname):
    debugprint("NO DXF EXPORT FOR SOLID".format(fname))
    pass

if __name__ == '__main__':
#    bs=[]
#    bs.append(box(1,10,1))
#    bs.append(box(10,1,1))
#    debugprint(bs)

#    b2 = union(bs)

#    b2 = translate(b2, (5,1,1))
#    clear_selection()
#    select(b2)
#    b3 = bpy.ops.object.duplicate()
#    b2 = mirror(b2, 'ZX')

    # item = bpy.data.objects['Cube.002']
    # dat = hull_from_shapes([item])
    dat = hull_from_points([[1,1,1], [-1,1,1],[-1,-1,1],[-1,-1,-1],[1,-1,1],[1,-1,-1],[1,1,-1],[-1,1,-1]])
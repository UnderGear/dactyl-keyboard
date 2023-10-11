import os
import sys
run_dir = r'E:\Users\jashreve\git\dactyl-keyboard-JSTEST\src'

import os
import sys
import json


# run_dir comes from the file generator that pulls this file.
# This approach is used to simplify execution in Blender by generating the file to execute base on run location.
config_fpath = os.path.join(run_dir, "blender_config.json")
with open(config_fpath, mode='r') as fid:
    config = json.load(fid)
os.remove(config_fpath)


f_to_smooth = config['f_to_smooth']
pl_to_smooth = config['pl_to_smooth']
blender_presmooth = config['blender_presmooth']
blender_presubdivide = config['blender_presubdivide']
blender_smooth = config['blender_smooth']
blender_controlled_smooth = config['blender_controlled_smooth']
blender_dir = config['blender_dir']
# blender_packages_path = config['blender_packages_path']
current_dir = config['current_dir']

# sys.path.insert(0, blender_packages_path )
sys.path.append(current_dir)
print(os.getcwd())
os.chdir(current_dir)
print(os.getcwd())

import helpers_blender as bdr

bdr_shape = bdr.import_file(fname=f_to_smooth + ".stl")
shared_shape = bdr.import_file(fname=pl_to_smooth + ".stl")

bdr_shape2 = bdr.duplicate(bdr_shape)
bdr_shape2.name = "shape2_baseline"
bdr_shape = bdr.boolean_cleanup(
    bdr_shape,
    dissolve_degenerate=1.0,
    dissolve_limited=0,
)
# bdr_shape = bdr.boolean_post_cleanup(
#     bdr_shape,
#     # remove_doubles_threshold=0.01,
#     dissolve_limited=0,
#     dissolve_degenerate=1.0,
#     z=[1.5, 9999],
# )

bdr_shape = bdr.dissolve_for_smooth(bdr_shape, shared_shape)
if blender_presmooth:
    bdr_shape = bdr.subdivide_mesh(bdr_shape, level=blender_presmooth, simple=True)

if blender_presubdivide:
    bdr_shape = bdr.direct_subdivide_mesh(bdr_shape, cuts=blender_presubdivide)

bdr_shape = bdr.crease_base_vertices(bdr_shape, z=(-1, 2.0))
bdr_shape3 = bdr.duplicate(bdr_shape)
bdr_shape3.name = "shape3_post_base_crease"
if blender_controlled_smooth:
    bdr_shape = bdr.crease_key_vertices(bdr_shape, shared_shape, tol=blender_controlled_smooth)
    bdr_shape4 = bdr.duplicate(bdr_shape)
    bdr_shape4.name = "shape4_post_key_crease"
bdr_shape = bdr.subdivide_mesh(bdr_shape, level=blender_smooth)
bdr_shape5 = bdr.duplicate(bdr_shape)
bdr_shape5.name = "shape5_post_smooth"

# bdr_shape = bdr.boolean_post_cleanup(
#     bdr_shape,
#     remove_doubles_threshold=0.01,
#     dissolve_limited=0.01,
#     dissolve_degenerate=0.1,
#     delete_loose=True,
#     beautify_faces=False,
#     recalc_normals=True,
#     tris_to_quads=False,
#     z=[2.0, 9999],
# )

# bdr_shape = bdr.boolean_cleanup(
#     bdr_shape,
#     dissolve_degenerate=.2,
#     dissolve_limited=0,
#     remove_doubles_threshold=0.001,
#     vert_connect_concave=False,
#     delete_loose=True,
#     collapse_non_manifold=False,
#     beautify_faces=False,
#     recalc_normals=False,
#     quads_to_tris=False,
#     tris_to_quads=True,
# )

bdr_shape6 = bdr.duplicate(bdr_shape)
bdr_shape6.name = "shape6_post_cleanup"

# raise Exception("END!")

f_smoothed = os.path.join(r"..", "things", r"smoothed.stl")
bdr.export_file(bdr_shape, fname=f_smoothed)

print('PROCESSING COMPLETE')

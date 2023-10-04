import cadquery as cq
from OCP import StlAPI
from OCP import TopoDS
from OCP.TopExp import TopExp_Explorer
from OCP.TopAbs import TopAbs_FACE
# from OCP import BRepBuilderAPI
# from OCP.gp import gp_Trsf as Trsf
def import_stl(fname, convexity=None):
    print("IMPORTING FROM {}".format(fname))
    shape = TopoDS.TopoDS_Shape()
    stl_reader = StlAPI.StlAPI_Reader()
    stl_reader.Read(shape, fname)
    print(shape)
    if shape.IsNull():
        raise AssertionError("Shape is null.")
    # shape2 = BRepBuilderAPI.BRepBuilderAPI_Transform(shape, Trsf(), True)
    topExp = TopExp_Explorer()
    topExp.Init(shape, TopAbs_FACE)
    faces=[]
    while topExp.More():
        faces.append(TopoDS.TopoDS_Face(topExp.Current()))
        topExp.Next()
    solid_object = cq.Solid.makeSolid(cq.Shell.makeShell(faces))
    return cq.Workplane('XY').add(solid_object)


fname = r'E:\Users\jashreve\git\dactyl-keyboard-JS\things\smoothed.stl'
print("IMPORTING FROM {}".format(fname))
shape = TopoDS.TopoDS_Shape()
stl_reader = StlAPI.StlAPI_Reader()
stl_reader.Read(shape, fname)
print(shape)
if shape.IsNull():
    raise AssertionError("Shape is null.")

topExp = TopExp_Explorer()
topExp.Init(shape, TopAbs_FACE)
faces=[]
while topExp.More():
    faces.append(cq.Face(topExp.Current()))
    topExp.Next()
solid_object = cq.Solid.makeSolid(cq.Shell.makeShell(faces))
shape = cq.Workplane('XY').add(solid_object)


# shape = import_stl(r'E:\Users\jashreve\git\dactyl-keyboard-JS\things\smoothed.stl')
box = cq.Workplane('XY').union(cq.Solid.makeBox(10, 10, 10))
shape.union(box)
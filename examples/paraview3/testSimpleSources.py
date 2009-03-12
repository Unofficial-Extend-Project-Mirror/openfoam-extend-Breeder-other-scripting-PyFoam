# Demonstrates the creation of some simple objects

# To be run using "Tools -> Python Shell -> Run Script" inside of paraFoam
# assumes that one OpenFOAM-case is opened



from PyFoam.Paraview import readerObject
from PyFoam.Paraview.SimpleSources import Point,Sphere,Cube,Text,Line,Plane,Arrow,Glyph
from PyFoam.Paraview.SimpleFilters import Group

from PyFoam.Basics.DataStructures import Vector

ro=readerObject()

bnds=ro.getBounds()

pl=Plane("Plane",ro.getCenter(),ro.getMax(),ro.getCenter()+Vector(1,1,1)^ro.getExtent())

ln=Line("Line",ro.getMin(),ro.getMax())

pt1=Point("Point1",ro.getMin())
pt2=Point("Point2",ro.getMax())

grp=Group("thePoints")
grp.add(pt1)
grp.add(pt2)

sp=Sphere("Sphere",ro.getCenter())

cp=Cube("Cube",ro.getMin()-0.2*ro.getExtent(),ro.getMax()+0.2*ro.getExtent())

txt=Text("Text","Don't Panic")

arrow=Arrow("Arrow",ro.getMax(),ro.getMax()+ro.getExtent())

gly=Glyph("Glyph",ro.getMin(),ro.getMin()-ro.getExtent())

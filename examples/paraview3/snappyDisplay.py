# Displays important features of the snappyHexMeshDict

# To be run using "Tools -> Python Shell -> Run Script" inside of paraFoam
# assumes that one OpenFOAM-case is opened


from PyFoam.RunDictionary.ParsedParameterFile import ParsedParameterFile

from PyFoam.Paraview import caseDirectory
from PyFoam.Paraview.SimpleSources import Sphere,Cube,STL,Point

from os import path

sol=caseDirectory()

snap=ParsedParameterFile(path.join(sol.systemDir(),"snappyHexMeshDict"))

pointInMesh=tuple(snap["castellatedMeshControls"]["locationInMesh"])
print "PointInMesh:",pointInMesh
pt=Point("PointInMesh",pointInMesh)

pt.repr.DiffuseColor = (1,0,0)

geometries=[]

for name,spec in snap["geometry"].iteritems():
    if spec["type"]=="triSurfaceMesh":
        fn=path.join(sol.constantDir(),"triSurface",name)
        nm=spec["name"]
        print "STL:",fn,"Name:",nm
        ob=STL(nm,fn)
    elif spec["type"]=="searchableBox":
        pt1=tuple(spec["min"])
        pt2=tuple(spec["max"])
        print "Box:",pt1,pt2,"Name:",name
        ob=Cube(name,pt1,pt2)
    elif spec["type"]=="searchableSphere":
        ct=tuple(spec["centre"])
        radius=spec["radius"]
        print "Sphere:",radius,ct,"Name:",name
        ob=Sphere(name,ct,absRadius=radius)
    else:
        print "Unknown Geometry type ",spec["type"]

    ob.repr.Opacity=0.7
    ob.repr.DiffuseColor=(0,1,0)

    geometries.append(ob)
    

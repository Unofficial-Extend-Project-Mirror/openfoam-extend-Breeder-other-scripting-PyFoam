# draws a vector in the direction of the gravity using vtk-primitves

# to be used as a "Programmable Source"

from PyFoam.RunDictionary.ParsedParameterFile import ParsedParameterFile
from PyFoam.Paraview import caseDirectory
from os import path
import paraview

env=ParsedParameterFile(path.join(caseDirectory().constantDir(),"environmentalProperties"))
g=env["g"][2]
pdo=self.GetPolyDataOutput()
pdo.Allocate(1,1)
pts=paraview.vtk.vtkPoints()
pts.InsertPoint(0,(0.0,0.0,0.0))
pts.InsertPoint(1,g)
line=paraview.vtk.vtkPolyLine()
line.GetPointIds().SetNumberOfIds(2)
line.GetPointIds().SetId(0,0)
line.GetPointIds().SetId(1,1)
pdo.InsertNextCell(line.GetCellType(), line.GetPointIds())
pdo.SetPoints(pts)

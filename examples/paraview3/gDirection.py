from PyFoam.RunDictionary.ParsedParameterFile import ParsedParameterFile
from os import path
import paraview

casepath="."

env=ParsedParameterFile(path.join(casepath,"constant","environmentalProperties"))
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

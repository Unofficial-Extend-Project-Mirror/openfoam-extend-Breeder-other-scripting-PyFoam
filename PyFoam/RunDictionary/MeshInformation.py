"""Gets information about the mesh of a case. Makes no attempt to manipulate
the mesh, because this is better left to the OpenFOAM-utilities"""

from SolutionDirectory import SolutionDirectory
from ListFile import ListFile

class MeshInformation:
    """Reads Information about the mesh on demand"""
    
    def __init__(self,case):
        """@param case: Path to the case-directory"""
        self.sol=SolutionDirectory(case)
        
    def nrOfFaces(self):
        try:
            return self.faces
        except AttributeError:
            faces=ListFile(self.sol.polyMeshDir(),"faces")
            self.faces=faces.getSize()
            return self.faces

    def nrOfPoints(self):
        try:
            return self.points
        except AttributeError:
            points=ListFile(self.sol.polyMeshDir(),"points")
            self.points=points.getSize()
            return self.points

    def nrOfCells(self):
        raise "NotImplemented"

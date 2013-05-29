
import unittest

from .ParameterFile import theSuite as ParameterFile
from .ParsedParameterFile import theSuite as ParsedParameterFile
from .ParsedBlockMeshDict import theSuite as ParsedBlockMeshDict
from .BoundaryDict import theSuite as BoundaryDict
from .MeshInformation import theSuite as MeshInformation
from .SolutionFile import theSuite as SolutionFile
from .SolutionDirectory import theSuite as SolutionDirectory
from .SampleDirectory import theSuite as SampleDirectory
from .TimeDirectory import theSuite as TimeDirectory

theSuite=unittest.TestSuite()

theSuite.addTest(ParameterFile)
theSuite.addTest(ParsedParameterFile)
theSuite.addTest(ParsedBlockMeshDict)
theSuite.addTest(BoundaryDict)
theSuite.addTest(MeshInformation)
theSuite.addTest(SolutionFile)
theSuite.addTest(SolutionDirectory)
theSuite.addTest(SampleDirectory)
theSuite.addTest(TimeDirectory)

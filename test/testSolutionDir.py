
import sys

from PyFoam.RunDictionary.SolutionDirectory import SolutionDirectory

dName=sys.argv[1]

sd=SolutionDirectory(dName)

sd.lastToArchive("test")
sd.clearResults()


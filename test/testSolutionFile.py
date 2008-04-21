
from PyFoam.RunDictionary.SolutionFile import SolutionFile
from PyFoam.RunDictionary.SolutionDirectory import SolutionDirectory

import sys

file=sys.argv[1]
name=sys.argv[2]
bc =sys.argv[3]
neu=sys.argv[4]

dire=SolutionDirectory(file,archive="TestArchive")
sol=SolutionFile(dire.initialDir(),name)

print "Old internal",sol.readInternal()

sol.replaceInternal(neu)

print "New internal",sol.readInternal()

sol.purgeFile()

print "Reset internal",sol.readInternal()

print "Old boundary",sol.readBoundary(bc)

sol.replaceBoundary(bc,neu)

print "New boundary",sol.readBoundary(bc)

sol.purgeFile()

print "Reset boundary",sol.readBoundary(bc)

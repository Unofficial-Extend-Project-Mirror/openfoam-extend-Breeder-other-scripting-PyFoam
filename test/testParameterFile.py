
from PyFoam.RunDictionary.ParameterFile import ParameterFile
import sys

file=sys.argv[1]
name=sys.argv[2]
neu =sys.argv[3]

para=ParameterFile(file)

print "Old value", para.readParameter(name)

para.replaceParameter(name,neu)

print "new value", para.readParameter(name)

para.purgeFile()

print "reset value", para.readParameter(name)

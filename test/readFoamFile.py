
from PyFoam.Basics.FoamFileGenerator import FoamFileGenerator
from PyFoam.RunDictionary.ParsedParameterFile import ParsedParameterFile

import sys

fname=sys.argv[1]

print "Parsing: "+fname

f=ParsedParameterFile(fname,listLengthUnparsed=100)
print "\nHeader:"
print f.header
print "\nContent:"
print f.content
print "\nReconstructed: "
print str(f)
print "Writing to file"
tmpFile="/tmp/readFoam.test"
o=open(tmpFile,"w")
o.write(str(f))
o.close()
print "Reparsing"
g=ParsedParameterFile(tmpFile,listLengthUnparsed=100)
print g.content
print
if g.content==f.content:
    print "Reparsed content is equal to original"
else:
    print "Reparsed content differs"
    

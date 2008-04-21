import sys

from PyFoam.RunDictionary.ParsedBlockMeshDict import ParsedBlockMeshDict

bm=ParsedBlockMeshDict(sys.argv[1])
print "Vertices: "
print bm.vertices()
print "Blocks: "
print bm.blocks()
print "Patches:"
print bm.patches()
print "Arcs:"
print bm.arcs()
print "Min/Max",bm.getBounds()
print "Typical Length: ",bm.typicalLength()
print bm["edges"]

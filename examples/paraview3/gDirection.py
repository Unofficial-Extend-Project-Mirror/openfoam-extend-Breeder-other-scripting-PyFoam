# Draws a vector in the direction of gravity

# To be run using "Tools -> Python Shell -> Run Script" inside of paraFoam
# assumes that one OpenFOAM-case is opened

from PyFoam.Paraview import readerObject,caseDirectory
from PyFoam.Paraview.SimpleSources import Glyph,Arrow

from PyFoam.RunDictionary.ParsedParameterFile import ParsedParameterFile
from os import path

ro=readerObject()

env=ParsedParameterFile(path.join(caseDirectory().constantDir(),"environmentalProperties"))
g=env["g"][2]

# gly=Glyph("Gravity",ro.getCenter(),ro.getCenter()+0.5*g*abs(ro.getExtent())/abs(g))
gly=Arrow("Gravity",ro.getCenter(),ro.getCenter()+0.5*g*abs(ro.getExtent())/abs(g))

gly.repr.Color=(0,0,0)

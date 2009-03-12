# Draws the probes from the control Dict

# To be run using "Tools -> Python Shell -> Run Script" inside of paraFoam
# assumes that one OpenFOAM-case is opened


from PyFoam.RunDictionary.ParsedParameterFile import ParsedParameterFile

from PyFoam.Paraview import caseDirectory
from PyFoam.Paraview.SimpleSources import Point
from PyFoam.Paraview.SimpleFilters import Group

from os import path

sol=caseDirectory()

ctrl=ParsedParameterFile(path.join(sol.systemDir(),"controlDict"))

probes=[]

probeNr=0
groupNr=0

grps=[]

name="Nix"

if "functions" in ctrl:
    for f in ctrl["functions"]:
        if type(f)==str:
            print "Group:",f
            name=f
        else:
            if f["type"]=="probes":
                pObs=[]
                for p in f["probeLocations"]:
                    probes.append(p)
                    pObs.append(Point("Probe_%d_in_%s" % (probeNr,name),p))
                    probeNr += 1
                grp=Group("Probes_%s" % name)
                groupNr += 1
                for o in pObs:
                    grp.add(o)
                    o.repr.Visibility = False
                grp.repr.Color = (1,0,0)
                grps.append(grp)
                
print "Probes:",probes

if len(grps)>1:
    total=Group("AllProbes")
    for o in grps:
        total.add(o)
        o.repr.Visibility = False
    total.repr.Color = (1,0,0)

# Draws the probes from the control Dict

# To be run using "Tools -> Python Shell -> Run Script" inside of paraFoam
# assumes that one OpenFOAM-case is opened


from PyFoam.RunDictionary.ParsedParameterFile import ParsedParameterFile

from PyFoam.Basics.DataStructures import DictProxy

from PyFoam.Paraview import caseDirectory
from PyFoam.Paraview.SimpleSources import Point,Line
from PyFoam.Paraview.SimpleFilters import Group

from os import path

sol=caseDirectory()

ctrl=ParsedParameterFile(
    path.join(sol.systemDir(),"controlDict"),
    doMacroExpansion=True
)

probes=[]
sets=[]

probeNr=0
setsNr=0
groupNr=0

grps=[]

name="Nix"

def readLines(f,name):
    global setsNr,groupNr,grps
    
    pObs=[]
    lst=f["sets"]
    for n,v in [(lst[i],lst[i+1]) for i in range(0,len(lst),2)]:
        if ("start" in v) and ("end" in v):
            sets.append("%s_%s" %(name,n))
            pObs.append(Line("Line_%s_in_%s" % (n,name),v["start"],v["end"]))
        setsNr += 1
    grp=Group("Sets_%s" % name)
    groupNr += 1
    for o in pObs:
        grp.add(o)
        o.repr.Visibility = False
    grp.repr.DiffuseColor = (1,0,0)
    grps.append(grp)
    
if "functions" in ctrl:
    lst=ctrl["functions"]
    if type(lst) in [dict,DictProxy]:
        pass
    for name,f in lst.iteritems():
        print "Group:",name,
        if f["type"].find("probes")>=0:
            print "= probes"
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
            grp.repr.DiffuseColor = (1,0,0)
            grps.append(grp)
        elif f["type"].find("sets")>=0:
            print "= sets"
            readLines(f,name)
        else:
            print

if path.exists(path.join(sol.systemDir(),"sampleDict")):
    print "Reading sampleDict"
    readLines(ParsedParameterFile(path.join(sol.systemDir(),"sampleDict")),"sampleDict")

print "Probes:",probes
print "Sets:",sets

if len(grps)>1:
    total=Group("AllProbesAndSets")
    for o in grps:
        total.add(o)
        o.repr.Visibility = False
        total.repr.DiffuseColor = (1,0,0)

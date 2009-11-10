#! /usr/bin/python

"""Given a pre-OpenFOAM-1.4 fvSolution file, this script transforms the solvers
section into the equivalen 1.4-format
Incomplete, because it doesn't support (B)DCG and GaussSeidl but should work for
instance for all the tutorials"""

import sys

from PyFoam.RunDictionary.ParsedParameterFile import ParsedParameterFile
from PyFoam.Basics.DataStructures import TupleProxy

if len(sys.argv)<2:
    print "I need at least one fvSolution-file to work with"
    sys.exit(1)
    
for fName in sys.argv[1:]:
    print "Working on",fName
    try:
        f=ParsedParameterFile(fName)
        sol=f["solvers"]
        for name,val in sol.iteritems():
            if type(name)!=str or type(val)!=TupleProxy or len(val)<3:
                # this is not an old-school entry
                continue
            solver=val[0]
            tol=val[1]
            rTol=val[2]
            if solver=="ICCG":
                new=( "PCG" , { "preconditioner":"DIC" } )
            elif solver=="BICCG":
                new=( "PBiCG" , { "preconditioner":"DILU" } )
            elif solver=="AMG":
                new=( "GAMG" , { "agglomerator":"faceAreaPair",
                                 "nCellsInCoarsestLevel":val[3],
                                 "mergeLevels":1,
                                 "smoother":"GaussSeidel"} )
            else:
                print "Unsupported solver",solver
                continue
            new[1]["tolerance"]=tol
            new[1]["relTol"]=rTol
            sol[name]=new
    except IOError:
        print "File",fName,"does not exist"
    except KeyError:
        print "File",fName,"is not a fvSolution-file"

    try:
        f.writeFile()
    except IOError:
        print "Can't write file. Content would have been:"
        print f
        

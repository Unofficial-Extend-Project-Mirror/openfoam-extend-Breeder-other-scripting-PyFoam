#! /usr/bin/env python

# Example that demonstrates how to read application data
# to be used on a pickledData-file that is written at the end of a run

import sys
from PyFoam.Applications.EchoPickledApplicationData import EchoPickledApplicationData

pickle=sys.argv[1]
pd=EchoPickledApplicationData(args=["--pickled-file="+pickle])
linear=pd.getData()["analyzed"]["Linear"]

data={}
namemax=0

for k in linear:
    if k.find("_iterations")<0 and k.find("_final")<0:
        data[k]={}
        namemax=max(namemax,len(k))

for k in linear:
    if k.find("_iterations")<0 and k.find("_final")<0:
        data[k]["initial"]=linear[k]
    else:
        n,e=k.split("_")
        data[n][e]=linear[k]

format="%"+str(namemax+1)+"s : %-12g  (%10e) - %5d"

for k,d in data.iteritems():
    print format % (k,d["initial"],d["final"],d["iterations"])
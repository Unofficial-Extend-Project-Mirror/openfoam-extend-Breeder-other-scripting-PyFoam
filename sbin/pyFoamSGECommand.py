#! /usr/bin/python

from os import environ as env
from os import path,system

from time import sleep

import sys

trigger=sys.argv[1]

f=open("/nfs/Temp/migrate","w+")
print >>f,env
f.close()

theDir=env["SGE_CKPT_DIR"]
if theDir=="NONE":
    theDir=env["SGE_O_WORKDIR"]
    
jobName=env["JOB_NAME"]
jobId=env["JOB_ID"]

timeout=36000
waiting=10

fName=path.join(theDir,"%s.%s" % (jobName,jobId))
if env.has_key("TASK_IS"):
    fName+=".%s" % env["TASK_ID"]
fName+=".pyFoam.clusterjob"

if trigger=="clean":
    system("rm -f "+fName+"*")
    sys.exit(0)
    
if not path.exists(fName):
    print "Job does not seem to exist"
    sys.exit(-1)

trigger=fName+"."+trigger
# trigger=fName+".checkpoint"

f=open(trigger,"w")
f.write("Tu was")
f.close()

expired=0L

while expired<timeout and path.exists(trigger):
    expired+=waiting
    sleep(waiting)

if path.exists(trigger):
    print "Timed out"
    sys.exit(-1)
    

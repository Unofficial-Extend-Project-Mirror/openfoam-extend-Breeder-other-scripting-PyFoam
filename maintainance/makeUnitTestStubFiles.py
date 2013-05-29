#! /usr/bin/env python

from os import path,listdir,mkdir

libStart="PyFoam"
testStart="unittests"

dMissing=0
fCreated=0

def checkForTests(lib,test):
    global dMissing,fCreated

    libDir=path.join(*lib)
    testDir=path.join(*test)
    print "Comparing",libDir,"to",testDir
    for f in listdir(libDir):
        if f[:2]=="__" or f in ["ThirdParty","Paraview"]:
            continue
        if path.isdir(path.join(libDir,f)):
            if not path.exists(path.join(testDir,f)):
                print "Subdirectory",f,"missing in",testDir
                mkdir(path.join(testDir,f))
                dMissing+=1
            checkForTests(lib+[f],test+[f])
        elif f[-3:]==".py":
            newFile=path.join(testDir,f)
            className=f[:-3]
            if not path.exists(newFile):
                print "Creating",newFile
                open(newFile,"w").write("""import unittest

from %s import %s

theSuite=unittest.TestSuite()
""" % (".".join(lib+[className]),className))
                fCreated+=1

checkForTests([libStart],[testStart])

print
print dMissing,"directories missing"
print fCreated,"files created"
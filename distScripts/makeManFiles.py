#! /usr/bin/env python

import sys,glob,subprocess
from os import path

from PyFoam.Basics.RestructuredTextHelper import RestructuredTextHelper as rh

binDir=sys.argv[1]
manDir=sys.argv[2]

for f in glob.glob(path.join(binDir,"*.py")):
    util=path.basename(f)
    print util

    rst=rh().buildHeading(util,level=rh.LevelChapter)+"\n"

    out=open(path.join(manDir,util+".1"),"w")
    p1=subprocess.Popen([f,"-h"],stdout=subprocess.PIPE)
    rst+=p1.communicate()[0]
    p2=subprocess.Popen(["rst2man-2.7.py"],stdin=subprocess.PIPE,stdout=out)
    p2.communicate(rst)
    print "Ran:",p2.wait()

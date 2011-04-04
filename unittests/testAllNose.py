#! /usr/bin/env python

import nose
import sys

from os import listdir,path
import re

files=[]
for d in listdir("."):
    if path.isdir(d):
        for f in listdir(d):
            if re.compile("[^\._].+\.py$").match(f):
                files.append(path.join(d,f))

sys.argv+=files

nose.main()


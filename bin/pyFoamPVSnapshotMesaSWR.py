#! /usr/bin/env python

from PyFoam.Applications.ChangePython import changePython

changePython("pvpython","PVSnapshot",options=["--mesa-swr"])

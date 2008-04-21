#! /usr/bin/python

"""Attempts to replace 'tail -f'. No real purpose for that except as
a demonstration of the Watcher-class"""

import sys

from PyFoam.Execution.BasicWatcher import BasicWatcher

fName=sys.argv[1]

watcher=BasicWatcher(fName)

watcher.start()

#! /usr/bin/env  python 

description="""\
Analyzes a Log written by foamJob.  Needs the name of the Logfile to
be analyzed the data is being written to a directory that has the same
name with _analyzed appended
"""

from PyFoam.Basics.FoamOptionParser import FoamOptionParser

parse=FoamOptionParser(description=description,usage="%prog [options] <logfile>",interspersed=True)

parse.parse(nr=1)

from PyFoam.LogAnalysis.BoundingLogAnalyzer import BoundingLogAnalyzer
from PyFoam.LogAnalysis.LogAnalyzerApplication import LogAnalyzerApplication

analyze=LogAnalyzerApplication(BoundingLogAnalyzer())

analyze.run(pfad=parse.getArgs()[0])

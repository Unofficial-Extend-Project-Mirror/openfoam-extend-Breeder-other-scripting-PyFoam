#!/usr/bin/env python
# Provided by Mark Olesen

description="""
print setup
"""
import os
import PyFoam
import PyFoam.FoamInformation

try:
    print "PYTHONPATH:", os.environ["PYTHONPATH"]
except KeyError:
    print "not set"
    
print "OpenFOAM", PyFoam.FoamInformation.foamVersion(),"of the installed versions",PyFoam.FoamInformation.foamInstalledVersions()
if PyFoam.FoamInformation.oldAppConvention():
    print "  This version of OpenFOAM uses the old calling convention"
print "pyFoam-Version:",PyFoam.versionString()
print "Configuration search path:",PyFoam.configuration().configSearchPath()
print "Configuration files (used):",PyFoam.configuration().configFiles()

def testLibrary(name,textMissing=None):
    print "%-20s : " % name,

    try:
        exec("import "+name)
        print "Yes"
        return True
    except ImportError:
        print "No",
        if textMissing:
            print "\t",textMissing,
        print
        return False
    except RuntimeError:
        print "Problem",
        if textMissing:
            print "\t",textMissing,
        print
        return False
        
print "\nInstalled libraries:"
testLibrary("Gnuplot","Not a problem. Version from ThirdParty is used")
testLibrary("ply","Not a problem. Version from ThirdParty is used")
numericPresent=testLibrary("Numeric","Not a problem if numpy is present")
numpyPresent=testLibrary("numpy","Not a problem if Numeric is present")
if not numpyPresent and numericPresent:
    print "Numeric will be used for plotting, but numpy is preferred"
if numpyPresent and numericPresent:
    print "numpy will be used for plotting (Numeric is ignored)"
testLibrary("matplotlib","Only Gnuplot-plotting possible")
# testLibrary("matplotlib.pyplot","Only Gnuplot-plotting possible")
testLibrary("psyco","Not a problem. Acceleration not possible")
testLibrary("hotshot","Not a problem. Can't profile using this library")
testLibrary("profile","Not a problem. Can't profile using this library")
testLibrary("cProfile","Not a problem. Can't profile using this library")
testLibrary("PyQt4","Only some experimental GUI-stuff relies on this")
testLibrary("PyQt4.Qwt5","Only an alternate plotting back-end")
testLibrary("vtk","Not a problem. Only used for some utilities")
testLibrary("Tkinter","Not a problem. Used for the old version of DisplayBlockmesh and some matplotlib-implementations")

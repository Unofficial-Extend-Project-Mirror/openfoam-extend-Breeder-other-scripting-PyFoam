#!/usr/bin/env python
# Original provided by Mark Olesen

description="""
print setup
"""
import os,sys

print "Python version:",sys.version
print

try:
    print "PYTHONPATH:", os.environ["PYTHONPATH"]
except KeyError:
    print "not set"

try:
    import PyFoam
    import PyFoam.FoamInformation
except ImportError:
    print "PyFoam not in PYTHONPATH. Don't see no sense in continuing"
    sys.exit(-1)
    
print
print "OpenFOAM", PyFoam.FoamInformation.foamVersion(),"of the installed versions",PyFoam.FoamInformation.foamInstalledVersions()
if PyFoam.FoamInformation.oldAppConvention():
    print "  This version of OpenFOAM uses the old calling convention"
print
print "pyFoam-Version:",PyFoam.versionString()
print
print "Configuration search path:",PyFoam.configuration().configSearchPath()
print "Configuration files (used):",PyFoam.configuration().configFiles()

def testLibrary(name,textMissing=None):
    print "%-20s : " % name,

    try:
        exec("import "+name)
        print "Yes",
        version=None
        try:
            version=eval(name+".__version__")
        except AttributeError:
            pass
        if version:
            print "\t version:",version
        else:
            print
            
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
    except SyntaxError:
        print "Syntax Error",
        if textMissing:
            print "\t",textMissing,
        print
        return False
        
print "\nInstalled libraries:"
testLibrary("Gnuplot","Not a problem. Version from ThirdParty is used")
testLibrary("ply","Not a problem. Version from ThirdParty is used")
numericPresent=testLibrary("Numeric","Not supported anymore. No need to install it")
numpyPresent=testLibrary("numpy","Plotting and data comparison won't work")
if not numpyPresent and numericPresent:
    print "Numeric no longer supported for plotting. Install numpy"
if numpyPresent and numericPresent:
    print "numpy will be used for plotting (Numeric is no longer supported)"
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
testLibrary("mercurial","Not a problem. Used for experimental case handling")

if sys.version_info<(2,3):
    print "\nUnsupported Python-version (at least 2.3)"
elif sys.version_info<(2,4):
    print "\nThis Python version does not support all features needed by PyFoam (get at least 2.4"


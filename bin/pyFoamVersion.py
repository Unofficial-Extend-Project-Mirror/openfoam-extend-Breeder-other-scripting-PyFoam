#!/usr/bin/env python
# Original provided by Mark Olesen

import os,sys
from platform import uname

# from __future__ import print_function
try:
    from PyFoam.ThirdParty.six import print_
except ImportError:
    def print_(*args):
        # Simple workaround to report the failure
        for a in args:
            sys.stdout.write(str(a))
            sys.stdout.write(" ")
        sys.stdout.write("\n")

    print_("PROBLEM:")
    print_("'from PyFoam.ThirdParty.six import print_' did not work. Seems that this is not the correct PyFoam-library\n")

description="""
print_ setup
"""

print_("Machine info:"," | ".join(uname()))
print_()
print_("Python version:",sys.version)
print_()

if sys.version_info<(2,3):
    print_("\nUnsupported Python-version (at least 2.3). Recommended is 2.6 or 2.7")
elif sys.version_info<(2,4):
    print_("\nThis Python version does not support all features needed by PyFoam (get at least 2.4. Recommended is 2.6 or 2.7")
elif sys.version_info<(2,6):
    print_("This version may not work anymore due to the port of PyFoam to Python 3")
elif sys.version_info>=(3,):
    print_("PyFoam is not yet fully functional with Python 3")

try:
    print_("PYTHONPATH:", os.environ["PYTHONPATH"])
except KeyError:
    print_("PYTHONPATH is not set")
print_()

print_("Location of this utility:",sys.argv[0])
print_()

try:
    import PyFoam
    import PyFoam.FoamInformation
except ImportError:
    print_("PyFoam not in PYTHONPATH or regular search path. Don't see no sense in continuing")
    print_("Regular Python search-path:",sys.path)
    print_()
    sys.exit(-1)

print_("OpenFOAM", PyFoam.FoamInformation.foamVersion(),"of the installed versions",PyFoam.FoamInformation.foamInstalledVersions())
if PyFoam.FoamInformation.oldAppConvention():
    print_("  This version of OpenFOAM uses the old calling convention")
print_()
print_("pyFoam-Version:",PyFoam.versionString())
# hardcodedVersion=(0,6,0,"development")
hardcodedVersion=(0,6,0)
if PyFoam.version()!=hardcodedVersion:
    print_("ALERT: Reported version",PyFoam.version(),
           "is different from hardcoded version",
            hardcodedVersion,"-> probably inconsistent library installation")
print_()
print_("Path where PyFoam was found (PyFoam.__path__) is",PyFoam.__path__)
print_()
print_("Configuration search path:",PyFoam.configuration().configSearchPath())
print_("Configuration files (used):",PyFoam.configuration().configFiles())

def testLibrary(name,textMissing=None,textThere=None):
    print_("%-20s : " % name, end=' ')

    try:
        exec("import "+name)
        print_("Yes", end=' ')
        version=None
        try:
            version=eval(name+".__version__")
        except AttributeError:
            pass
        if version:
            print_("\t version:",version, end=' ')
        if textThere:
            print_("\t",textThere, end=' ')
        print_()

        return True
    except ImportError:
        print_("No", end=' ')
        if textMissing:
            print_("\t",textMissing, end=' ')
        print_()
        return False
    except RuntimeError:
        print_("Problem", end=' ')
        if textMissing:
            print_("\t",textMissing, end=' ')
        print_()
        return False
    except SyntaxError:
        print_("Syntax Error", end=' ')
        if textMissing:
            print_("\t",textMissing, end=' ')
        print_()
        return False

print_("\nInstalled libraries:")
testLibrary("Gnuplot","Not a problem. Version from ThirdParty is used")
testLibrary("ply","Not a problem. Version from ThirdParty is used")
numericPresent=testLibrary("Numeric","Not supported anymore. No need to install it")
numpyPresent=testLibrary("numpy","Plotting and data comparison won't work")
if not numpyPresent and numericPresent:
    print_("Numeric no longer supported for plotting. Install numpy")
if numpyPresent and numericPresent:
    print_("numpy will be used for plotting (Numeric is no longer supported)")
if not numpyPresent:
    numpypyPresent=testLibrary("numpypy","This workaround for PyPy does not work","This seems to by PyPy")
    if numpypyPresent:
        numpyPresent=testLibrary("numpy","Does not work in pypy","Numpy works with workaround")
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
testLibrary("nose","Only needed for running the unit-tests (developers only)")
testLibrary("twisted","Not yet used. Possibly reimplement MetaServer with it")
testLibrary("pandas","Not yet used. Maybe handling of timelines will be reimplemented with it")
testLibrary("scipy","Not yet used. Possibly use signal-fitting etc")

# Should work with Python3 and Python2

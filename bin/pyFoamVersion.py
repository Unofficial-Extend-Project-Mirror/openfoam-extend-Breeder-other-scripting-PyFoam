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
print_("Python executable:",sys.executable)
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

installed=PyFoam.FoamInformation.foamInstalledVersions()

print_("Version", PyFoam.FoamInformation.foamVersion(),
       "Fork",PyFoam.FoamInformation.foamFork(),
       "of the installed",len(installed),"versions:")
installedKeys=installed.keys()
installedKeys.sort()

formatString="%%%ds : %%s" % max([1+len(a[0])+len(a[1]) for a in installedKeys])
for k in installedKeys:
    print_(formatString % (k[0]+"-"+k[1],installed[k]))

if PyFoam.FoamInformation.oldAppConvention():
    print_("  This version of OpenFOAM uses the old calling convention")
print_()
print_("pyFoam-Version:",PyFoam.versionString())
# hardcodedVersion=(0,6,4,"development")
hardcodedVersion=(0,6,3)
if PyFoam.version()!=hardcodedVersion:
    print_("ALERT: Reported version",PyFoam.version(),
           "is different from hardcoded version",
            hardcodedVersion,"-> probably inconsistent library installation")
print_()
print_("Path where PyFoam was found (PyFoam.__path__) is",PyFoam.__path__)
print_()
print_("Configuration search path:",PyFoam.configuration().configSearchPath())
print_("Configuration files (used):",PyFoam.configuration().configFiles())

libLoc={}

def testLibrary(name,
                textMissing=None,
                subModule=None,
                textThere=None,
                minVersion=None,
                versionAttribute="__version__"):
    global libLoc
    print_("%-20s : " % name, end=' ')

    try:
        module=name
        exec("import "+name)
        if subModule:
            exec("from "+name+" import "+subModule)
            module=subModule

        print_("Yes", end=' ')
        version=None
        try:
            version=eval(module+"."+versionAttribute)
        except AttributeError:
            pass
        if version:
            print_("\t version:",version, end=' ')
            if minVersion:
                if version<minVersion:
                    print_("Insufficient version. At least",minVersion,
                           "recommended for all features",end=' ')
                else:
                    print_("Matches required version",minVersion,end=' ')
        if textThere:
            print_("\t",textThere, end=' ')
        print_()

        libLoc[name]=eval(name+'.__file__')
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
testLibrary("cython","Not used. Maybe will by used later to spped up parts of PyFoam")
testLibrary("cProfile","Not a problem. Can't profile using this library")
testLibrary("docutils","Not necessary. Needed for RestructuredText to HTML conversion")
testLibrary("Gnuplot","Not a problem. Version from ThirdParty is used")
testLibrary("hotshot","Not a problem. Can't profile using this library")
testLibrary("ipdb","Not necessary. Only makes debugging more comfortable")
testLibrary("IPython",
            "Not necessary. But the interactive shell may be more comfortable",
            minVersion="2.0.0")
testLibrary("matplotlib","Only Gnuplot-plotting possible")
# testLibrary("matplotlib.pyplot","Only Gnuplot-plotting possible")
testLibrary("mercurial","Not a problem. Used for experimental case handling",
            subModule="config",versionAttribute="util.version()")
testLibrary("nose","Only needed for running the unit-tests (developers only)")
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
testLibrary("openpyxl","Not a problem. Only used for exporting pandas-data to Excel-files (advanced)")
testLibrary("pandas","Not a problem. Only used for handling of advanced data-handling")
testLibrary("ply","Not a problem. Version from ThirdParty is used")
testLibrary("profile","Not a problem. Can't profile using this library")
testLibrary("psyco","Not a problem. Acceleration not possible")
testLibrary("PyQt4","Only some experimental GUI-stuff relies on this",
            subModule="Qt",versionAttribute="QT_VERSION_STR")
testLibrary("PyQt4.Qwt5","Only an alternate plotting back-end")
testLibrary("scipy","Not yet used. Possibly use signal-fitting etc")
testLibrary("Tkinter","Not a problem. Used for the old version of DisplayBlockmesh and some matplotlib-implementations")
testLibrary("twisted","Not yet used. Possibly reimplement MetaServer with it")
testLibrary("vtk","Not a problem. Only used for some utilities",
            versionAttribute="VTK_VERSION")
testLibrary("xlwt","Not a problem. Only used for exporting pandas-data to Excel-files",
            versionAttribute="__VERSION__")

print_()
print_("Library locations")
for l in sorted(libLoc.keys(),lambda a,b:cmp(a.lower(),b.lower())):
    print_("%-20s : %s" % (l,libLoc[l]))

# Should work with Python3 and Python2

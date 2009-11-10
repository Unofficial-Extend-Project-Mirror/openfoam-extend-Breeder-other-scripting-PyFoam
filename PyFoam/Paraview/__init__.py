#  ICE Revision: $Id: __init__.py 10791 2009-09-01 07:47:51Z bgschaid $ 
""" Paraview interaction

Classes that help to interact with a Python-enabled paraFoam/paraview
"""

hasSimpleModule=True
try:
    from paraview import simple
except ImportError:
    hasSimpleModule=False
    
# this import prevents python-source-tools that ude introspection from working
# because it prevents import into a normal python
from paraview import servermanager
    
from PyFoam.Error import warning
from PyFoam.RunDictionary.SolutionDirectory import SolutionDirectory

from math import sqrt
from os import path

from SourceBase import SourceBase

proxyManager=servermanager.ProxyManager()

def version():
    """Tries to determine the paraview-version"""
    return (proxyManager.GetVersionMajor(),
            proxyManager.GetVersionMinor(),
            proxyManager.GetVersionPatch())

def paraFoamReader():
    """ Get the paraFoam reader.
    Currently only works if there is only one reader"""

    result=None
    
    src=proxyManager.GetProxiesInGroup("sources")
    
    for s in src:
        if type(src[s])==servermanager.sources.PV3FoamReader:
            if result==None:
                result=src[s]
            else:
                warning("Found a second paraFoam-reader:",s)

    if result==None:
        warning("No paraFoam-reader found")

    return result

def readerObject():
    """Gets the only reader wrapped as a SourceBase-object"""
    return SourceBase(paraFoamReader())

def renderView():
    """ Get the render view.
    Currently just takes the first view"""

    result=None
    
    src=proxyManager.GetProxiesInGroup("views")
    
    for s in src:
        if result==None:
            result=src[s]
        else:
            warning("Found a second render view:",s)

    if result==None:
        warning("No render view found")

    return result

def getBounds():
    """Return the size of the object covered by the paraFoam-Reader"""
    return readerObject().getBounds()

def getCenter():
    """Return the center of the object covered by the paraFoam-Reader"""
    return readerObject().getCenter()

def characteristicLength():
    """The characteristic length of the geometry"""
    return readerObject().characteristicLength()

def viewTime():
    """Time that is currently displayed"""
    return renderView().ViewTime.GetData()

def caseDirectory():
    """The directory in which the case is stored"""
    return SolutionDirectory(
        path.dirname(paraFoamReader().FileName.GetData()),
        archive=None,
        paraviewLink=False)

def timeDirectory():
    return caseDirectory()[viewTime()]

def transformsModule():
    """Workaround to get to the transformations in Paraview 3.4"""
    return servermanager.createModule("transforms")

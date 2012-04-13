#  ICE Revision: $Id: /local/openfoam/Python/PyFoam/PyFoam/__init__.py 7974 2012-04-13T16:39:16.800544Z bgschaid  $ 
""" Utility-classes for OpenFOAM

Module for the Execution of OpenFOAM-commands and processing their output
"""

from Infrastructure.Configuration import Configuration

def version():
    """@return: Version number as a tuple"""
    #    return (0,6,0,"development")
    return (0,5,7)

def versionString():
    """@return: Version number of PyFoam"""
    v=version()

    vStr="%d" % v[0]
    for d in v[1:]:
        if type(d)==int:
            vStr+=(".%d" % d)
        else:
            vStr+=("-%s" % str(d))
    return vStr

def foamVersionString():
    from FoamInformation import foamVersionString
    return foamVersionString()

_configuration = Configuration()

def configuration():
    """@return: The Configuration information of PyFoam"""
    return _configuration


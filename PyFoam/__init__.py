#  ICE Revision: $Id: /local/openfoam/Python/PyFoam/PyFoam/__init__.py 7412 2011-04-04T21:42:02.146584Z bgschaid  $ 
""" Utility-classes for OpenFOAM

Module for the Execution of OpenFOAM-commands and processing their output
"""

from Infrastructure.Configuration import Configuration

def version():
    """@return: Version number as a tuple"""
    return (0,5,5)

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


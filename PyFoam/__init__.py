#  ICE Revision: $Id: /local/openfoam/Python/PyFoam/PyFoam/__init__.py 3057 2008-04-20T15:14:35.009832Z bgschaid  $ 
""" Utility-classes for OpenFOAM

Module for the Execution of OpenFOAM-commands and processing their output
"""

from Infrastructure.Configuration import Configuration

def version():
    """@return: Version number as a tuple"""
    return (0,4,3)

def versionString():
    """@return: Version number of PyFoam"""
    v=version()

    vStr="%d" % v[0]
    for d in v[1:]:
        vStr+=(".%d" % d)

    return vStr

_configuration = Configuration()

def configuration():
    """@return: The Configuration information of PyFoam"""
    return _configuration


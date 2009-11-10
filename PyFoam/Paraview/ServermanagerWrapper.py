#  ICE Revision: $Id: ServermanagerWrapper.py 10792 2009-09-01 14:01:48Z bgschaid $ 
""" Wrapper class for the paraview servermanager

Sets up the servermanager to be used with OpenFOAM-Data. Especially makes sure that
the plugins for the OpenFOAM-Data are loaded"""

from math import sqrt
from paraview import servermanager
from PyFoam.Paraview import version
if version()>=(3,6):
    from paraview import simple
    
from os import environ,path,uname

from PyFoam.Error import error

class ServermanagerWrapper(object):
    """Wrapper class for the servermanager

    Load the plugins and build a connection"""

    def __init__(self):
        """Sets up the Servermanager in such a way that it is usable
        with OpenFOAM-data."""
        
        self.con=servermanager.Connect()

        dyExt="so"
        if uname()[0]=="Darwin":
            dyExt="dylib"
        elif uname()[0]=="Linux":
            try:
                import ctypes
                lib=ctypes.CDLL(path.join(environ["FOAM_LIBBIN"],"libPV3FoamReader.so"),mode=ctypes.RTLD_GLOBAL)
            except ImportError:
                error("The Workaround for Linux-Systems won't work because there is no ctypes library")
                
        plug1="libPV3FoamReader."+dyExt
        plug2="libPV3FoamReader_SM."+dyExt
        
        loaded=False
        for p in environ["PV_PLUGIN_PATH"].split(":"):
            if path.exists(path.join(p,plug1)):
                if version()>=(3,6):
                    simple.LoadPlugin(path.join(p,plug1),ns=globals())
                    try:
                        simple.LoadPlugin(path.join(p,plug2),ns=globals())
                    except NameError:
                        print dir(self.module())
                        pass
                else:
                    servermanager.LoadPlugin(path.join(p,plug1))
                    servermanager.LoadPlugin(path.join(p,plug2))
                loaded=True
                break

        if not loaded:
            error("The plugin",plug1,"was not found in the PV_PLUGIN_PATH",environ["PV_PLUGIN_PATH"])
        if not "PV3FoamReader" in dir(servermanager.sources):
            error("The plugin was not properly loaded. PV3FoamReader not found in the list of sources")
            
    def __getattr__(self,attr):
        """Delegate Attributes to the servermanager-module"""

        return getattr(servermanager,attr)
    
    def __setattr__(self,attr,val):
        """Delegate Attributes to the servermanager-module"""

        return setattr(servermanager,attr,val)

    def module(self):
        """Return the actual module (for developing)"""
        return servermanager

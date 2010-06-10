#!/usr/bin/env python

try:
    import PyQt4
    from PyFoam.Applications.DisplayBlockMeshQt import DisplayBlockMesh
except ImportError:
    from PyFoam.Error import warning
    warning("Falling back to the old Tkinter-implementation because no PyQT4 was found")
    from PyFoam.Applications.DisplayBlockMesh import DisplayBlockMesh
    
DisplayBlockMesh()

#!/usr/bin/env python

try:
    import PyQt4
    from PyFoam.Applications.DisplayBlockMeshQt import DisplayBlockMesh
except ImportError:
    try:
        from PyFoam.Error import warning
        warning("Falling back to the old Tkinter-implementation because no PyQT4 was found")
        from PyFoam.Applications.DisplayBlockMesh import DisplayBlockMesh
    except ImportError:
        print "Seems like PyFoam is not in the PYTHONPATH"
        import sys
        sys.exit(-1)
        
DisplayBlockMesh()

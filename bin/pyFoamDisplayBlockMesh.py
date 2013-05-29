#!/usr/bin/env python

from PyFoam.ThirdParty.six import print_

try:
    import PyQt4
    from PyFoam.Applications.DisplayBlockMeshQt import DisplayBlockMesh
except ImportError:
    try:
        from PyFoam.Error import warning
        warning("Falling back to the old Tkinter-implementation because no PyQT4 was found")
        from PyFoam.Applications.DisplayBlockMesh import DisplayBlockMesh
    except ImportError:
        print_("Seems like PyFoam is not in the PYTHONPATH")
        import sys
        sys.exit(-1)

DisplayBlockMesh()

# Should work with Python3 and Python2

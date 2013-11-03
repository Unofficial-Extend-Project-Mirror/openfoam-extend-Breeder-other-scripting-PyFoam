import unittest

from PyFoam.ThirdParty.six import PY3

try:
    import PyQt4
    if not PY3:
        from PyFoam.Applications.DisplayBlockMeshQt import DisplayBlockMeshDialog
except:
    pass

theSuite=unittest.TestSuite()

import unittest

from PyFoam.ThirdParty.six import PY3

if not PY3:
    from PyFoam.Applications.CreateModuleFile import CreateModuleFile

theSuite=unittest.TestSuite()

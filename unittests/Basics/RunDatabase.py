import unittest

import sys
if sys.version_info[0]>2 or sys.version_info[1]>5:
    from PyFoam.Basics.RunDatabase import RunDatabase

theSuite=unittest.TestSuite()

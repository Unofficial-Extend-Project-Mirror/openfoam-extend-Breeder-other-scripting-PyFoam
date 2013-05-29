import unittest

from PyFoam.ThirdParty.six import PY3

if not PY3:
    from PyFoam.Infrastructure.FoamMetaServer import FoamMetaServer

    theSuite=unittest.TestSuite()

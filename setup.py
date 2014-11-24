from distutils.core import setup

import glob,os,sys

scriptlist =glob.glob(os.path.join('bin', '*.py'))
scriptlist+=glob.glob(os.path.join('sbin', '*.py'))

from PyFoam import versionString
from PyFoam.ThirdParty.six import print_

setup(name='PyFoam',
      version=versionString(),
      packages=['PyFoam',
                'PyFoam.Applications',
                'PyFoam.Basics',
                'PyFoam.Execution',
                'PyFoam.Infrastructure',
                'PyFoam.IPythonHelpers',
                'PyFoam.LogAnalysis',
                'PyFoam.RunDictionary',
                'PyFoam.Paraview',
                'PyFoam.Site',
                'PyFoam.ThirdParty',
                'PyFoam.ThirdParty.ply',
                'PyFoam.ThirdParty.Gnuplot',
                'PyFoam.Wrappers'],
      description='Python Utilities for OpenFOAM',
      url='http://www.ice-sf.at',
      author='Bernhard Gschaider',
      author_email='bgschaid@ice-sf.at',
      scripts=scriptlist,
      )

try:
    import numpy
except ImportError:
    print_("\n\n")
    print_("numpy python-package not installed. Plotting won't work")
    print_("\n\n")

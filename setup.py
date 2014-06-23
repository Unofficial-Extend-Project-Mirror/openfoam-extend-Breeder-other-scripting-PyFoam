from distutils.core import setup

import glob,os

scriptlist =glob.glob(os.path.join('bin', '*.py'))
scriptlist+=glob.glob(os.path.join('sbin', '*.py'))

from PyFoam import versionString

setup(name='PyFoam',
      version=versionString(),
      packages=['PyFoam',
                'PyFoam.Applications',
                'PyFoam.Basics',
                'PyFoam.Execution',
                'PyFoam.IPython',
                'PyFoam.LogAnalysis',
                'PyFoam.RunDictionary',
                'PyFoam.Infrastructure',
                'PyFoam.Paraview',
                'PyFoam.ThirdParty',
                'PyFoam.ThirdParty.ply',
                'PyFoam.ThirdParty.Gnuplot',
                'PyFoam.Wrappers'],
      description='Python Utilities for OpenFOAM',
      url='http://www.ice-sf.at',
      author='Bernhard Gschaider',
      author_email='Bernhard.Gschaider@ice-sf.at',
      scripts=scriptlist,
      )

try:
    import numpy
except ImportError,e:
    try:
        import Numeric
        print "\n\n"
        print "numpy python-package not installed. Using Numeric instead"
        print "\n\n"
    except ImportError,e:
        print "\n\n"
        print "Neither numpy nor Numeric python-package installed. Plotting won't work"
        print "\n\n"

#  ICE Revision: $Id: /local/openfoam/Python/PyFoam/PyFoam/LogAnalysis/FileLineAnalyzer.py 1906 2007-08-28T16:16:19.392553Z bgschaid  $ 
"""Line analyzer with output"""

from GeneralLineAnalyzer import GeneralLineAnalyzer

class FileLineAnalyzer(GeneralLineAnalyzer):
    """Base class for analyzers that write data to files

    Just a stub to enable legacy code"""
        
    def __init__(self,titles=[]):
        """
        @param titles: The titles of the data elements
        """
        GeneralLineAnalyzer.__init__(self,doFiles=True,titles=titles)
        


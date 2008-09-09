#  ICE Revision: $Id: FileLineAnalyzer.py 7832 2007-08-28 13:07:26Z bgschaid $ 
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
        


#  ICE Revision: $Id: OutputFile.py 7581 2007-06-27 15:29:14Z bgschaid $ 
"""Output of time-dependent data"""

from BasicFile import BasicFile

class OutputFile(BasicFile):
    """output of time dependent data"""
    
    def __init__(self,name,titles=[]):
        """
        @param name: name of the file
        @param titles: Titles of the columns
        """
        BasicFile.__init__(self,name)

        self.setTitles(titles)

#    def __del__(self):
#            print "Deleting File",self.name
        
    def setTitles(self,titles):
        """
        Sets the titles anew. Only has an effect if the file hasn't been opened yet
        
        @param titles: The new titles
        """
        self.titles=titles
        
    def outputAtStart(self):
        """
        Write column titles if present
        """
        if len(self.titles)>0:
            fh=self.getHandle()
            fh.write("# time")
            for c in self.titles:
                fh.write(" \t"+c)
            fh.write("\n")
            
    def write(self,time,data):
        """write data set

        @param time: the current time
        @param data: tuple with data"""
        self.writeLine( (time,)+data)
        

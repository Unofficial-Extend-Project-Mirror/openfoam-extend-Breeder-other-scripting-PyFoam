#  ICE Revision: $Id: /local/openfoam/Python/PyFoam/PyFoam/Basics/BasicFile.py 1532 2007-06-29T11:15:55.577361Z bgschaid  $ 
"""Basic file output"""

class BasicFile(object):
    """File for data output

    The format of the file is: one data-set per line
    Values are separated by tabs
    
    The file is created the first time it is written"""
    
    def __init__(self,name):
        """name - name of the file"""
        self.name=name
        self.isOpen=False
        self.handle=None

    def outputAtStart(self):
        """A hook for outputting stuff at the beginning of the file"""
        pass
    
    def outputAtEnd(self):
        """A hook for outputting stuff at the end of the file"""
        pass
    
    def outputAtLineEnd(self):
        """A hook for outputting stuff at the end of each line"""
        pass
    
    def outputAtLineStart(self):
        """A hook for outputting stuff at the start of each line"""
        pass
    
    def getHandle(self):
        """get the file-handle. File is created and opened if it
        wasn't opened before"""
        if not self.isOpen:
            self.handle=open(self.name,"w")
            self.isOpen=True
            self.outputAtStart()
            
        return self.handle

    def writeLine(self,data):
        """write a data set

        data - a tuple with the data-set"""
        fh=self.getHandle()
        self.outputAtLineStart()
        first=True
        for d in data:
            if not first:
                fh.write(" \t")
            else:
                first=False
            fh.write(str(d))
        self.outputAtLineEnd()
        fh.write("\n")
        fh.flush()

    def close(self):
        """close the file"""
        #        print "Closing file\n"
        if self.handle!=None:
            self.outputAtEnd()
            self.handle.close()
            self.handle=None
            

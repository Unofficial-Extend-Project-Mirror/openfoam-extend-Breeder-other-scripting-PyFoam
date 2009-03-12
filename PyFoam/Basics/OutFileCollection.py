#  ICE Revision: $Id: OutFileCollection.py 10069 2009-03-02 09:39:44Z bgschaid $ 
"""Collections of output files"""

from os import path

from OutputFile import OutputFile

class OutFileCollection(object):
    """Collection of output files

    The files are stored in a common directory and are created on
    first access

    Each file can be identified by a unique name. If a file is
    accessed a second time at the same simulation-time a file with the
    ending _2 is created (incrementing with each access)"""
    
    def __init__(self,
                 basename,
                 titles=[],
                 singleFile=False):
        """
        @param basename: name of the base directory
        @param titles: names of the data columns
        @param singleFile: don't split into multiple files if more than one
        datum is insert per time-step
        """
        self.files={}
        self.lastTime=""
        self.called={}
        self.basename=basename
        self.setTitles(titles)
        self.singleFile=singleFile
        
#    def __del__(self):
#        print "\n  Deleting this OutputFile\n"
        
    def setTitles(self,titles):
        """
        Sets the titles anew

        @param titles: the new titles
        """
        self.titles=titles
        for f in self.files.items():
            f.setTitles(titles)
            
    def checkTime(self,time):
        """check whether the time has changed"""
        if time!=self.lastTime:
            self.lastTime=time
            self.called={}

    def getFile(self,name):
        """get a OutputFile-object"""
        if not self.files.has_key(name):
            fullname=path.join(self.basename,name)
            self.files[name]=OutputFile(fullname,titles=self.titles)
            
        return self.files[name]
                               
    def prevCalls(self,name):
        """checks whether the name was used previously at that time-step"""
        if self.called.has_key(name):
            return self.called[name]
        else:
            return 0

    def incrementCalls(self,name):
        """increments the access counter for name"""
        self.called[name]=1+self.prevCalls(name)
        
    def write(self,name,time,data):
        """writes data to file

        name - name of the file
        time - simulation time
        data - tuple with the data"""
        self.checkTime(time)

        fname=name
        self.incrementCalls(name)
        
        if self.prevCalls(name)>1 and not self.singleFile:
            fname+="_"+str(self.prevCalls(name))

        f=self.getFile(fname)

        f.write(time,data)
        
    def close(self):
        """Force all files to be closed"""

        for f in self.files:
            self.files[f].close()
            

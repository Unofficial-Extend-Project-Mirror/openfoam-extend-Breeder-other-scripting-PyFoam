#  ICE Revision: $Id: /local/openfoam/Python/PyFoam/PyFoam/Basics/OutFileCollection.py 5789 2009-11-06T12:32:54.086322Z bgschaid  $ 
"""Collections of output files"""

from os import path

from OutputFile import OutputFile

from PyFoam import configuration as conf

class OutFileCollection(object):
    """Collection of output files

    The files are stored in a common directory and are created on
    first access

    Each file can be identified by a unique name. If a file is
    accessed a second time at the same simulation-time a file with the
    ending _2 is created (incrementing with each access)"""
    
    maxOpenFiles=10
    
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
        self.openList=[]
        
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
            self.files[name]=OutputFile(fullname,titles=self.titles,parent=self)

        return self.files[name]

    def addToOpenList(self,name):
        """Adds a file to the list of open files. Closes another
        file if limit is reached"""
        try:
            ind=self.openList.index(name)
            self.openList=self.openList[:ind]+self.openList[ind+1:]
        except ValueError:
            if len(self.openList)>=OutFileCollection.maxOpenFiles:
                old=self.files[self.openList[0]]
                self.openList=self.openList[1:]
                #                print "Closing",old.name
                #                assert old.handle!=None
                old.close(temporary=True)
                #                assert old.handle==None

        self.openList.append(name)
        
    def removeFromOpenList(self,name):
        """Adds a file to the list of open files. Closes another
        file if limit is reached"""
        try:
            ind=self.openList.index(name)
            self.openList=self.openList[:ind]+self.openList[ind+1:]            
        except ValueError:
            pass
        
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

        try:
            f.write(time,data)
        except IOError,e:
            print self.openList
            print len(self.files)
            print self.files
            print "Open:",
            cnt=0
            for f in self.files:
                if self.files[f].handle!=None:
                    print f,
                    cnt+=1
            print
            print "Actually open",cnt,"of",len(self.files)
            raise e
        
    def close(self):
        """Force all files to be closed"""

        for f in self.files:
            self.files[f].close()
            
OutFileCollection.maxOpenFiles=int(conf().get("OutfileCollection","maximumOpenFiles"))


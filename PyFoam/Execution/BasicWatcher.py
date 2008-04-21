#  ICE Revision: $Id: /local/openfoam/Python/PyFoam/PyFoam/Execution/BasicWatcher.py 2334 2007-11-16T16:46:56.838187Z bgschaid  $ 
"""Watches the output of Foam-run"""

from os import path
import stat
import os
from time import sleep

from PyFoam.Basics.LineReader import LineReader

class BasicWatcher(object):
    """Base class for watching the output of commands

    Works like the UNIX-command 'tail -f <file>': the last lines of the file are output.
    If the file grows then these lines are output as they arrive"""

    def __init__(self,filename,silent=False,tailLength=1000,sleep=0.1):
        """@param filename: name of the logfile to watch
        @param silent: if True no output is sent to stdout
        @param tailLength: number of bytes at the end of the fail that should be output.
        Because data is output on a per-line-basis
        @param sleep: interval to sleep if no line is returned"""

        self.filename=filename
        self.silent=silent
        self.tail=tailLength
        self.sleep=sleep
        self.isTailing=False
        
        if not path.exists(self.filename):
            print "Error: Logfile ",self.filename,"does not exist"

        self.reader=LineReader()
        
    def getSize(self):
        """@return: the current size (in bytes) of the file"""
        return os.stat(self.filename)[stat.ST_SIZE]
    
    def start(self):
        """Reads the file and does the processing"""

        currSize=self.getSize()
        fh=open(self.filename)
        
        self.startHandle()
        
        while 1:
            status=self.reader.read(fh)
            if status:
                line=self.reader.line
                if (currSize-self.reader.bytesRead())<=self.tail:
                    if not self.isTailing:
                        self.isTailing=True
                        self.timeHandle()
                        self.tailingHandle()
                        
                    if not self.silent:
                        print line
                        
                self.lineHandle(line)
            else:
                if self.reader.userSaidStop():
                    break
                try:
                    sleep(self.sleep)
                except KeyboardInterrupt,e:
                    print "Keyboard interrupt"
                    break
                                
        self.stopHandle()

        fh.close()
        
    def startHandle(self):
        """to be called before the program is started"""
        pass
    
    def stopHandle(self):
        """called after the program has stopped"""
        pass
    
    def tailingHandle(self):
        """called when the first line is output"""
        pass
    
    def lineHandle(self,line):
        """called every time a new line is read"""
        pass
    


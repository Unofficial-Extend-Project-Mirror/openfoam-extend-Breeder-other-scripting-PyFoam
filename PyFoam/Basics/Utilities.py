#  ICE Revision: $Id: /local/openfoam/Python/PyFoam/PyFoam/Basics/Utilities.py 4985 2009-04-27T17:43:32.496023Z bgschaid  $ 
""" Utility functions

Can be used via a class or as functions"""

import sys

if sys.version_info<(2,6):
    from popen2 import popen4
else:
    from subprocess import Popen,PIPE,STDOUT
from os import listdir

import re

class Utilities(object):
    """Class with utility methods

    Can be inherited without side effects by classes that need these
    methods"""

    def __init__(self):
        pass
    
    def execute(self,cmd,debug=False):
        """Execute the command cmd

        Currently no error-handling is done
        @return: A list with all the output-lines of the execution"""
        if debug:
            print cmd
        
        if sys.version_info<(2,6):
            raus,rein = popen4(cmd)
        else:
            p = Popen(cmd, shell=True, 
                      stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=True)
            (rein,raus)=(p.stdin,p.stdout)
        tmp=raus.readlines()
        # line=raus.readline()
        # while line!="":
        #     print line
        #     line=raus.readline()

        return tmp

    def writeDictionaryHeader(self,f):
        """Writes a dummy header so OpenFOAM accepts the file as a dictionary
        @param f: The file to write to
        @type f: file"""

        f.write("""
// * * * * * * * * * //
FoamFile
{
	version 0.5;
	format ascii;
	root "ROOT";
	case "CASE";
	class dictionary;
	object nix;
}
""")

    excludeNames=["^.svn$" , "~$"]
    
    def listDirectory(self,d):
        """Lists the files in a directory, but excludes certain names
        and files with certain endings
        @param d: The directory to list
        @return: List of the found files and directories"""

        result=[]

        excludes=map(re.compile,self.excludeNames)
        
        for n in listdir(d):
            ok=True
            
            for e in excludes:
                if e.search(n):
                    ok=False
                    break

            if ok:
                result.append(n)
            
        return result

def execute(cmd,debug=False):
    """Calls the method of the same name from the Utilites class"""
    return Utilities().execute(cmd,debug)

def writeDictionaryHeader(f):
    """Calls the method of the same name from the Utilites class"""
    Utilities().writeDictionaryHeader(f)
    
def listDirectory(d):
    """Calls the method of the same name from the Utilites class"""
    return Utilities().listDirectory(d)
    

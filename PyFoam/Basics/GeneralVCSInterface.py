#  ICE Revision: $Id: /local/openfoam/Python/PyFoam/PyFoam/Basics/GeneralVCSInterface.py 7239 2011-02-23T17:26:11.661549Z bgschaid  $ 
"""General interface to VCS implementations"""

from PyFoam.Error import notImplemented,error

class GeneralVCSInterface(object):
    """This is an abstract class that implements an interface to general VCS operations"""
    
    def __init__(self,
                 path,
                 init=False):
        """@param path: path which is supposed to be under version control
        @param init: initialize the version control system here"""

        self.path=path

    def commit(self,
               msg):
        """Commit the current state
        @param msg: Commit message"""
        
        notImplemented(self,"commit")

    def addPath(self,
                path,
                rules=[]):
        """Add the path to the repository (no commit)
        @param path: the path (directory or file) to commit
        @param rules: a list of tuples: first is whether to include or exclude
        the regular expression that is the second member of the tuple"""

        notImplemented(self,"addPath")

    def clone(self,
              dest):
        """Clone the repository
        @param dest: the path that should be clones to"""

        notImplemented(self,"clone")

    def addRegexpToIgnore(self,
                          expr):
        """Add to the ignore-facility of the current VCS
        @param expr: a regular expression"""

        notImplemented(self,"addRegexpToIgnore")

    def addGlobToIgnore(self,
                          expr):
        """Add to the ignore-facility of the current VCS
        @param expr: a glob expression"""

        notImplemented(self,"addGlobToIgnore")

    def addStandardIgnores(self):
        """Add the usual ignores"""
        self.addGlobToIgnore("*.gz")
        self.addRegexpToIgnore(".*\\.logfile")
        
def getVCS(vcs,
           path,
           init=False):
    """Factory to create a proper VCS-interface
    @param vcs: name of the VCS-implementation
    @param path: path which is under version control
    @param init: whether the Version-control should be initialized here"""

    table = { "hg" : "HgInterface" }

    if vcs not in table:
        error("Unknown VCS",vcs,". Known are",table.keys())

    modName=table[vcs]

    exec "from "+modName+" import "+modName

    return eval(modName+"(path,init)")


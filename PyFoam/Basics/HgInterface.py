#  ICE Revision: $Id: /local/openfoam/Python/PyFoam/PyFoam/Basics/HgInterface.py 7224 2011-02-14T21:24:21.439959Z bgschaid  $ 
"""A VCS-interface to Mercurial"""

from PyFoam.Error import warning,error

from GeneralVCSInterface import GeneralVCSInterface

from os import uname
from os import path as opath
from mercurial import commands,ui,hg

class HgInterface(GeneralVCSInterface):
    """The interface class to mercurial"""
    
    def __init__(self,
                 path,
                 init=False):

        GeneralVCSInterface.__init__(self,path,init)
        self.ui=ui.ui()
        if init:
            commands.init(self.ui,path)
            open(opath.join(path,".hgignore"),"w").write("syntax: re\n\n")
            
        self.repo=hg.repository(self.ui,path)
        
        if init:
            self.addPath(opath.join(self.repo.root,".hgignore"))
            self.addStandardIgnores()
            
    def addPath(self,
                path,
                rules=[]):
        include=[]
        exclude=[]
        if rules!=[]:
            for inclQ,patt in rules:
                if inclQ:
                    include.append("re:"+patt)
                else:
                    exclude.append("re:"+patt)

        commands.add(self.ui,
                     self.repo,
                     path,
                     include=include,
                     exclude=exclude)

    def clone(self,
              dest):
        commands.clone(self.ui,
                       self.repo,
                       dest)
        
    def commit(self,
               msg):
        commands.commit(self.ui,
                        self.repo,
                        message=msg)

    def addGlobToIgnore(self,expr):
        self.addToHgIgnore("glob:"+expr)

    def addRegexpToIgnore(self,expr):
        self.addToHgIgnore("re:"+expr)

    def addToHgIgnore(self,expr):
        open(opath.join(self.repo.root,".hgignore"),"a").write(expr+"\n")

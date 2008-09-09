"""
Application-class that implements pyFoamPackCase.py
"""

from PyFoamApplication import PyFoamApplication

from PyFoam.RunDictionary.SolutionDirectory import SolutionDirectory

from os import path

class PackCase(PyFoamApplication):
    def __init__(self,args=None):
        description="""
Packs a case into a tar-file copying the system, constant and 0-directories.
Excludes all .svn-direcotries and all files ending with ~
"""
        PyFoamApplication.__init__(self,
                                   args=args,
                                   description=description,
                                   usage="%prog <case>",
                                   interspersed=True,
                                   changeVersion=False,
                                   nr=1)

    def addOptions(self):
        self.parser.add_option("--last",
                         action="store_true",
                         dest="last",
                         default=False,
                         help="Also add the last time-step")
        self.parser.add_option("--pyfoam",
                         action="store_true",
                         dest="pyfoam",
                         default=False,
                         help="Add all files starting with PyFoam to the tarfile")
        self.parser.add_option("--chemkin",
                         action="store_true",
                         dest="chemkin",
                         default=False,
                         help="Also add the Chemkin-directory")
        self.parser.add_option("--add",
                         action="append",
                         dest="additional",
                         default=[],
                         help="Add all files and directories in the case directory that fit a glob-pattern to the tar (can be used more than once)")
        self.parser.add_option("--exclude",
                         action="append",
                         dest="exclude",
                         default=[],
                         help="Exclude all files and directories that fit this glob pattern from being added, no matter at level (can be used more than once)")
        self.parser.add_option("--tarname",
                         action="store",
                         dest="tarname",
                         default=None,
                         help='Name of the tarfile. If unset the name of the case plus ".tgz" will be used')
        
    def run(self):
        sName=self.parser.getArgs()[0]
        if sName[-1]==path.sep:
            sName=sName[:-1]
            
        if self.parser.getOptions().tarname!=None:
            dName=self.parser.getOptions().tarname
        else:
            dName=sName+".tgz"
        if self.parser.getOptions().pyfoam:
            self.parser.getOptions().additional.append("PyFoam*")
            
        sol=SolutionDirectory(sName,archive=None,paraviewLink=False)

        if self.parser.getOptions().chemkin:
            sol.addToClone("chemkin")
            
        sol.packCase(dName,
                     last=self.parser.getOptions().last,
                     additional=self.parser.getOptions().additional,
                     exclude=self.parser.getOptions().exclude)

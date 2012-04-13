"""
Application-class that implements pyFoamSTLUtility.py
"""
from optparse import OptionGroup

from PyFoamApplication import PyFoamApplication
from PyFoam.Basics.STLFile import STLFile
from PyFoam.Basics.RestructuredTextHelper import RestructuredTextHelper

from os import path

class STLUtility(PyFoamApplication):
    def __init__(self,args=None):
        description="""\
This utility does some basic manipulations with STL-files        
"""
        PyFoamApplication.__init__(self,
                                   args=args,
                                   description=description,
                                   usage="%prog <source1.stl> <source2.stl> ...",
                                   interspersed=True,
                                   changeVersion=False,
                                   nr=1,
                                   exactNr=False)

    def addOptions(self):
        action=OptionGroup(self.parser,
                           "Action",
                           "What to do")
        self.parser.add_option_group(action)
        action.add_option("--join-to",
                          action="store",
                          dest="joinTo",
                          default=None,
                          help="Join the STLs into a single file")

        action.add_option("--patch-names",
                          action="store_true",
                          dest="patchNames",
                          default=False,
                          help="Print the names of the patches (if names are given)")
        
        action.add_option("--info",
                          action="store_true",
                          dest="info",
                          default=False,
                          help="Info about the patches in the STL")
        
    def run(self):
        sources=[STLFile(f) for f in self.parser.getArgs()]
        rst=RestructuredTextHelper()
        
        if self.opts.patchNames:
            print rst.buildHeading("Patch names",level=RestructuredTextHelper.LevelSection)
            for s in sources:
                print rst.buildHeading(s.filename(),level=RestructuredTextHelper.LevelSubSection)
                for p in s.patchInfo():
                    print p["name"]

        if self.opts.info:
            print rst.buildHeading("Patch info",level=RestructuredTextHelper.LevelSection)
            for s in sources:
                print rst.buildHeading(s.filename(),level=RestructuredTextHelper.LevelSubSection)
                tab=rst.table()
                tab[0]=["name","facets","range in file","bounding box"]
                tab.addLine(head=True)
                for i,p in enumerate(s.patchInfo()):
                    tab[(i+1,0)]=p["name"]
                    tab[(i+1,1)]=p["facets"]
                    tab[(i+1,2)]="%d-%d" % (p["start"],p["end"])
                    tab[(i+1,3)]="(%g %g %g) - (%g %g %g)" % tuple(p["min"]+p["max"])

                print tab
                    
        if self.opts.joinTo:
            if path.exists(self.opts.joinTo):
                self.error("File",self.opts.joinTo,"does allready exist")

            result=STLFile()
            for s in sources:
                result+=s

            result.writeTo(self.opts.joinTo)
            
            

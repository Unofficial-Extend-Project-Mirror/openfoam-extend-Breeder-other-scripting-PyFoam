#  ICE Revision: $Id: Decomposer.py 9973 2009-02-05 12:47:31Z bgschaid $ 
"""
Class that implements pyFoamDecompose
"""

from optparse import OptionGroup

from PyFoamApplication import PyFoamApplication
from PyFoam.Basics.FoamFileGenerator import FoamFileGenerator
from PyFoam.Error import error
from PyFoam.Basics.Utilities import writeDictionaryHeader
from PyFoam.Execution.UtilityRunner import UtilityRunner
from PyFoam.RunDictionary.SolutionDirectory import SolutionDirectory
from PyFoam.RunDictionary.RegionCases import RegionCases
from PyFoam.FoamInformation import oldAppConvention as oldApp

from CommonMultiRegion import CommonMultiRegion
from CommonStandardOutput import CommonStandardOutput
from CommonServer import CommonServer

from os import path,system
import sys,string

class Decomposer(PyFoamApplication,
                 CommonStandardOutput,
                 CommonServer,
                 CommonMultiRegion):
    def __init__(self,args=None):
        description="""
Generates a decomposeParDict for a case and runs the decompose-Utility on that case
"""
        PyFoamApplication.__init__(self,
                                   args=args,
                                   description=description,
                                   usage="%prog [options] <case> <procnr>",
                                   interspersed=True,
                                   nr=2)

    decomposeChoices=["metis","simple","hierarchical","manual"]
    
    def addOptions(self):
        spec=OptionGroup(self.parser,
                         "Decomposition Specification",
                         "How the case should be decomposed")
        spec.add_option("--method",
                        type="choice",
                        default="metis",
                        dest="method",
                        action="store",
                        choices=self.decomposeChoices,
                        help="The method used for decomposing (Choices: "+string.join(self.decomposeChoices,", ")+") Default: %default")
        
        spec.add_option("--n",
                        dest="n",
                        action="store",
                        default=None,
                        help="Number of subdivisions in coordinate directions. A python list or tuple (for simple and hierarchical)")
        
        spec.add_option("--delta",
                        dest="delta",
                        action="store",
                        type="float",
                        default=None,
                        help="Cell skew factor (for simple and hierarchical)")
        
        spec.add_option("--order",
                        dest="order",
                        action="store",
                        default=None,
                        help="Order of decomposition (for hierarchical)")
        
        spec.add_option("--processorWeights",
                        dest="processorWeights",
                        action="store",
                        default=None,
                        help="The weights of the processors. A python list. Used for metis")
        
        spec.add_option("--dataFile",
                        dest="dataFile",
                        action="store",
                        default=None,
                        help="File with the allocations. (for manual)")
        self.parser.add_option_group(spec)

        behave=OptionGroup(self.parser,
                           "Decomposition behaviour",
                           "How the program should behave during decomposition")
        behave.add_option("--test",
                          dest="test",
                          action="store_true",
                          default=False,
                          help="Just print the resulting dictionary")

        behave.add_option("--clear",
                          dest="clear",
                          action="store_true",
                          default=False,
                          help="Clear the case of previous processor directories")
        
        behave.add_option("--no-decompose",
                          dest="doDecompose",
                          action="store_false",
                          default=True,
                          help="Don't run the decomposer (only writes the dictionary")
        
        behave.add_option("--decomposer",
                               dest="decomposer",
                               action="store",
                               default="decomposePar",
                               help="The decompose Utility that should be used")
        self.parser.add_option_group(behave)
        
        CommonMultiRegion.addOptions(self)
        CommonStandardOutput.addOptions(self)
        CommonServer.addOptions(self,False)
        
    def run(self):
        if self.opts.keeppseudo and (not self.opts.regions and self.opts.region==None):
            warning("Option --keep-pseudocases only makes sense for multi-region-cases")

        nr=int(self.parser.getArgs()[1])
        if nr<2:
            error("Number of processors",nr,"too small (at least 2)")
            
        case=self.parser.getArgs()[0]
        method=self.opts.method

        result={}
        result["numberOfSubdomains"]=nr
        result["method"]=method

        coeff={}
        result[method+"Coeffs"]=coeff

        if method=="metis":
            if self.opts.processorWeights!=None:
                weigh=eval(self.opts.processorWeights)
                if nr!=len(weigh):
                    error("Number of processors",nr,"and length of",weigh,"differ")
                coeff["processorWeights"]=weigh
        elif method=="manual":
            if self.opts.dataFile==None:
                error("Missing required option dataFile")
            else:
                coeff["dataFile"]="\""+self.opts.dataFile+"\""
        elif method=="simple" or method=="hierarchical":
            if self.opts.n==None or self.opts.delta==None:
                error("Missing required option n or delta")
            n=eval(self.opts.n)
            if len(n)!=3:
                error("Needs to be three elements, not",n)
            if nr!=n[0]*n[1]*n[2]:
                error("Subdomains",n,"inconsistent with processor number",nr)
            coeff["n"]="(%d %d %d)" % (n[0],n[1],n[2])

            coeff["delta"]=float(self.opts.delta)
            if method=="hierarchical":
                if self.opts.order==None:
                    error("Missing reuired option order")
                if len(self.opts.order)!=3:
                    error("Order needs to be three characters")
                coeff["order"]=self.opts.order
        else:
            error("Method",method,"not yet implementes")

        gen=FoamFileGenerator(result)
        
        if self.opts.test:
            print str(gen)
            sys.exit(-1)
        else:
            f=open(path.join(case,"system","decomposeParDict"),"w")
            writeDictionaryHeader(f)
            f.write(str(gen))
            f.close()
            
        if self.opts.clear:
            system("rm -rf "+path.join(case,"processor*"))

        if self.opts.doDecompose:
            regionNames=[self.opts.region]
            regions=None

            if self.opts.regions or self.opts.region!=None:
                print "Building Pseudocases"
                sol=SolutionDirectory(case)
                regions=RegionCases(sol,clean=True)

                if self.opts.regions:
                    regionNames=sol.getRegions()
                
            for theRegion in regionNames:
                theCase=path.normpath(case)
                if theRegion!=None:
                    theCase+="."+theRegion

                if oldApp():
                    argv=[self.opts.decomposer,".",theCase]
                else:
                    argv=[self.opts.decomposer,"-case",theCase]

                self.setLogname(default="Decomposer",useApplication=False)
                
                run=UtilityRunner(argv=argv,
                                  silent=self.opts.progress,
                                  logname=self.opts.logname,
                                  server=self.opts.server,
                                  noLog=self.opts.noLog)
                run.start()

                if theRegion!=None:
                    print "Syncing into master case"
                    regions.resync(theRegion)

            if regions!=None:
                if not self.opts.keeppseudo:
                    print "Removing pseudo-regions"
                    regions.cleanAll()
                else:
                    for r in sol.getRegions():
                        if r not in regionNames:
                            regions.clean(r)


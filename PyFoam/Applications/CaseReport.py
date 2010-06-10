#  ICE Revision: $Id: CaseReport.py 11364 2010-03-16 17:32:12Z bgschaid $ 
"""
Application class that implements pyFoamCasedReport.py
"""

import sys,string
from optparse import OptionGroup

from fnmatch import fnmatch

from PyFoamApplication import PyFoamApplication
from PyFoam.RunDictionary.SolutionDirectory import SolutionDirectory
from PyFoam.RunDictionary.BoundaryDict import BoundaryDict
from PyFoam.RunDictionary.MeshInformation import MeshInformation
from PyFoam.RunDictionary.ParsedParameterFile import PyFoamParserError,ParsedBoundaryDict,ParsedParameterFile

from PyFoam.Error import error,warning

from math import log10,ceil
from os import path

class CaseReport(PyFoamApplication):
    def __init__(self,args=None):
        description="""
Produces human-readable reports about a case. Attention: the amount of
information in the reports is limited. The truth is always in the
dictionary-files
        """
        
        PyFoamApplication.__init__(self,
                                   args=args,
                                   description=description,
                                   usage="%prog [options] <casedir>",
                                   nr=1,
                                   changeVersion=False,
                                   interspersed=True)
        
    def addOptions(self):
        report=OptionGroup(self.parser,
                           "Reports",
                           "What kind of reports should be produced")
        self.parser.add_option_group(report)
        select=OptionGroup(self.parser,
                           "Selection",
                           "Which data should be used for the reports")
        self.parser.add_option_group(select)
        internal=OptionGroup(self.parser,
                             "Internal",
                             "Details of the parser")
        self.parser.add_option_group(internal)
        output=OptionGroup(self.parser,
                             "Output",
                             "How Output should be generated")
        self.parser.add_option_group(output)
        
        output.add_option("--file",
                          action="store",
                          default=None,
                          dest="file",
                          help="Write the output to a file instead of the console")
        
        report.add_option("--short-bc-report",
                          action="store_true",
                          default=False,
                          dest="shortBCreport",
                          help="Gives a short overview of the boundary-conditions in the case")
        
        report.add_option("--long-bc-report",
                          action="store_true",
                          default=False,
                          dest="longBCreport",
                          help="Gives a full overview of the boundary-conditions in the case")
        
        report.add_option("--dimensions",
                          action="store_true",
                          default=False,
                          dest="dimensions",
                          help="Show the dimensions of the fields")
        
        report.add_option("--internal-field",
                          action="store_true",
                          default=False,
                          dest="internal",
                          help="Show the internal value of the fields (the initial conditions)")
        
        report.add_option("--linear-solvers",
                          action="store_true",
                          default=False,
                          dest="linearSolvers",
                          help="Print the linear solvers and their tolerance")
        
        report.add_option("--relaxation-factors",
                          action="store_true",
                          default=False,
                          dest="relaxationFactors",
                          help="Print the relaxation factors (if there are any)")
        
        select.add_option("--time",
                          action="store",
                          type="float",
                          default=None,
                          dest="time",
                          help="Time to use as the basis for the reports")
        
        select.add_option("--region",
                          dest="region",
                          default=None,
                          help="Do the report for a special region for multi-region cases")
        
        select.add_option("--parallel",
                          action="store_true",
                          default=False,
                          dest="parallel",
                          help="Print the relaxation factors (if there are any)")
        
        internal.add_option("--long-field-threshold",
                            action="store",
                            type="int",
                            default=100,
                            dest="longlist",
                            help="Fields that are longer than this won't be parsed, but read into memory (and compared as strings)")

        select.add_option("--patches",
                          action="append",
                          default=None,
                          dest="patches",
                          help="Patches which should be processed (pattern, can be used more than once)")

        select.add_option("--exclude-patches",
                          action="append",
                          default=None,
                          dest="expatches",
                          help="Patches which should not be processed (pattern, can be used more than once)")

        report.add_option("--processor-matrix",
                          action="store_true",
                          default=False,
                          dest="processorMatrix",
                          help="Prints the matrix how many faces from one processor interact with another")

        report.add_option("--case-size",
                          action="store_true",
                          default=False,
                          dest="caseSize",
                          help="Report the number of cells, points and faces in the case")

        report.add_option("--decomposition",
                               action="store_true",
                               default=False,
                               dest="decomposition",
                               help="Reports the size of the parallel decomposition")
        
    def run(self):
        if self.opts.file:
            sys.stdout=open(self.opts.file,"w")
            
        sol=SolutionDirectory(self.parser.getArgs()[0],
                              archive=None,
                              parallel=self.opts.parallel,
                              paraviewLink=False,
                              region=self.opts.region)
        if self.opts.time:
            try:
                self.opts.time=sol.timeName(sol.timeIndex(self.opts.time,minTime=True))
            except IndexError:
                error("The specified time",self.opts.time,"doesn't exist in the case")
            print "Using time t="+self.opts.time+"\n"
            
        needsPolyBoundaries=False
        needsInitialTime=False
        
        if self.opts.longBCreport:
            needsPolyBoundaries=True
            needsInitialTime=True
        if self.opts.shortBCreport:
            needsPolyBoundaries=True
            needsInitialTime=True
        if self.opts.dimensions:
            needsInitialTime=True
        if self.opts.internal:
            needsInitialTime=True
        if self.opts.decomposition:
            needsPolyBoundaries=True
            
        defaultProc=None
        if self.opts.parallel:
            defaultProc=0
            
        if needsPolyBoundaries:
            proc=None
            boundary=BoundaryDict(sol.name,
                                  region=self.opts.region,
                                  time=self.opts.time,
                                  processor=defaultProc)

            boundMaxLen=0
            boundaryNames=[]
            for b in boundary:
                if b.find("procBoundary")!=0:
                    boundaryNames.append(b)
            if self.opts.patches!=None:
                tmp=boundaryNames
                boundaryNames=[]
                for b in tmp:
                    for p in self.opts.patches:
                        if fnmatch(b,p):
                            boundaryNames.append(b)
                            break

            if self.opts.expatches!=None:
                tmp=boundaryNames
                boundaryNames=[]
                for b in tmp:
                    keep=True
                    for p in self.opts.expatches:
                        if fnmatch(b,p):
                            keep=False
                            break
                    if keep:
                        boundaryNames.append(b)
                        
            for b in boundaryNames:
                boundMaxLen=max(boundMaxLen,len(b))
            boundaryNames.sort()

        if self.opts.time==None:
            procTime="constant"
        else:
            procTime=self.opts.time
            
        if needsInitialTime:
            fields={}

            if self.opts.time==None:
                try:
                    time=sol.timeName(0)
                except IndexError:
                    error("There is no timestep in the case")
            else:
                time=self.opts.time

            tDir=sol[time]

            nameMaxLen=0
            
            for f in tDir:
                try:
                    fields[f.baseName()]=f.getContent(listLengthUnparsed=self.opts.longlist)
                    nameMaxLen=max(nameMaxLen,len(f.baseName()))
                except PyFoamParserError,e:
                    warning("Couldn't parse",f.name,"because of an error:",e," -> skipping")
                    
            fieldNames=fields.keys()
            fieldNames.sort()

        if self.opts.caseSize:
            print "Size of the case"
            nFaces=0
            nPoints=0
            nCells=0
            if self.opts.parallel:
                procs=range(sol.nrProcs())
                print "Accumulated from",sol.nrProcs(),"processors"
            else:
                procs=[None]
            print

            for p in procs:
                info=MeshInformation(sol.name,
                                     processor=p,
                                     time=self.opts.time)
                nFaces+=info.nrOfFaces()
                nPoints+=info.nrOfPoints()
                try:
                    nCells+=info.nrOfCells()
                except:
                    nCells="Not available"
            print "Faces:  \t",nFaces
            print "Points: \t",nPoints
            print "Cells:  \t",nCells
            
        if self.opts.decomposition:
            if sol.nrProcs()<2:
                print "This case is not decomposed"
                return
            
            print "Case is decomposed for",sol.nrProcs(),"processors"

            nCells=[]
            nFaces=[]
            nPoints=[]
            for p in sol.processorDirs():
                info=MeshInformation(sol.name,
                                     processor=p,
                                     time=self.opts.time)
                nPoints.append(info.nrOfPoints())
                nFaces.append(info.nrOfFaces())
                nCells.append(info.nrOfCells())
                
            digits=int(ceil(log10(max(sol.nrProcs(),
                                      max(nCells),
                                      max(nFaces),
                                      max(nPoints)
                                      ))))+2
            nameLen=max(len("Points"),boundMaxLen)
            
            nrFormat  ="%%%dd" % digits
            nameFormat="%%%ds" % nameLen
            
            print " "*nameLen,"|",
            for i in range(sol.nrProcs()):
                print nrFormat % i,
            print

            print "-"*(nameLen+3+(digits+1)*sol.nrProcs())
            
            print nameFormat % "Points","|",
            for p in nPoints:
                print nrFormat % p,
            print
            print nameFormat % "Faces","|",
            for p in nFaces:
                print nrFormat % p,
            print
            print nameFormat % "Cells","|",
            for p in nCells:
                print nrFormat % p,
            print
            
            print "-"*(nameLen+3+(digits+1)*sol.nrProcs())

            for b in boundaryNames:
                print nameFormat % b,"|",
                for p in sol.processorDirs():
                    try:
                        nFaces= ParsedBoundaryDict(sol.boundaryDict(processor=p,
                                                                    time=self.opts.time)
                                                   )[b]["nFaces"]
                    except KeyError:
                        nFaces=0
                        
                    print nrFormat % nFaces,
                print
                
        if self.opts.longBCreport:
            print "\nThe boundary conditions for t =",time

            for b in boundaryNames:
                print "\nBoundary: \t",b
                bound=boundary[b]
                print " type:\t",bound["type"],
                if "physicalType" in bound:
                    print "( Physical:",bound["physicalType"],")",
                print " \t Faces:",bound["nFaces"]
                for fName in fieldNames:
                    print "   ",fName,
                    f=fields[fName]
                    if "boundaryField" not in f:
                        print " "*(nameMaxLen-len(fName)+2)+": Not a field file"
                    elif b not in f["boundaryField"]:
                        print " "*(nameMaxLen-len(fName)+2)+": MISSING !!!"
                    else:
                        bf=f["boundaryField"][b]
                        maxKeyLen=0
                        for k in bf:
                            maxKeyLen=max(maxKeyLen,len(k))
                            
                        print " "*(nameMaxLen-len(fName)+2)+"type "+" "*(maxKeyLen-4)+": ",bf["type"]
                        for k in bf:
                            if k!="type":
                                print " "*(nameMaxLen+6),k," "*(maxKeyLen-len(k))+": ",
                                cont=str(bf[k])
                                if cont.find("\n")>=0:
                                    print cont[:cont.find("\n")],"..."
                                else:
                                    print cont

        if self.opts.shortBCreport:
            print "\nTable of boundary conditions for t =",time
            print
            
            colLen = {}
            types={}
            hasPhysical=False
            nameMaxLen=max(nameMaxLen,len("Patch Type"))
            for b in boundary:
                colLen[b]=max(len(b),len(boundary[b]["type"]))
                colLen[b]=max(len(b),len(str(boundary[b]["nFaces"])))
                if "physicalType" in boundary[b]:
                    hasPhysical=True
                    nameMaxLen=max(nameMaxLen,len("Physical Type"))
                    colLen[b]=max(colLen[b],len(boundary[b]["physicalType"]))
                    
                types[b]={}
            
                for fName in fields:
                    f=fields[fName]
                    try:
                        if b not in f["boundaryField"]:
                            types[b][fName]="MISSING"
                        else:
                            types[b][fName]=f["boundaryField"][b]["type"]
                    except KeyError:
                        types[b][fName]="Not a field"
                        
                    colLen[b]=max(colLen[b],len(types[b][fName]))

            print " "*(nameMaxLen),
            nr=nameMaxLen+1
            for b in boundaryNames:
                print "| "+b+" "*(colLen[b]-len(b)),
                nr+=colLen[b]+3
            print
            print "-"*nr
            print "Patch Type"+" "*(nameMaxLen-len("Patch Type")),
            for b in boundaryNames:
                t=boundary[b]["type"]
                print "| "+t+" "*(colLen[b]-len(t)),
            print
            if hasPhysical:
                print "Physical Type"+" "*(nameMaxLen-len("Physical Type")),
                for b in boundaryNames:
                    t=""
                    if "physicalType" in boundary[b]:
                        t=boundary[b]["physicalType"]
                    print "| "+t+" "*(colLen[b]-len(t)),
                print
            print "Length"+" "*(nameMaxLen-len("Length")),
            for b in boundaryNames:
                s=str(boundary[b]["nFaces"])
                print "| "+s+" "*(colLen[b]-len(s)),
            print
            print "-"*nr
            for fName in fieldNames:
                print fName+" "*(nameMaxLen-len(fName)),
                for b in boundaryNames:
                    t=types[b][fName]
                    print "| "+t+" "*(colLen[b]-len(t)),
                print
                
            print
                        
        if self.opts.dimensions:
            print "\nDimensions of fields for t =",time
            print

            head="Name"+" "*(nameMaxLen-len("Name"))+" : [kg m s K mol A cd]"
            print head
            print "-"*len(head)
            for fName in fieldNames:
                f=fields[fName]
                try:
                    dim=f["dimensions"]
                    print fName+" "*(nameMaxLen-len(fName))+" :",dim
                except KeyError:
                    print fName,"is not a field file"
                    
        if self.opts.internal:
            print "\Internal value of fields for t =",time
            print

            head="Name"+" "*(nameMaxLen-len("Name"))+" : Value              "
            print head
            print "-"*len(head)
            for fName in fieldNames:
                f=fields[fName]

                print fName+" "*(nameMaxLen-len(fName))+" :",

                try:
                    cont=str(f["internalField"])
                    if cont.find("\n")>=0:
                        print cont[:cont.find("\n")],"..."
                    else:
                        print cont
                except KeyError:
                    print "Not a field file"
                    
        if self.opts.processorMatrix:
            if sol.nrProcs()<2:
                print "This case is not decomposed"
                
                return
            
            matrix=[ [0,]*sol.nrProcs() for i in range(sol.nrProcs())]

            for i,p in enumerate(sol.processorDirs()):
                bound=ParsedBoundaryDict(path.join(sol.name,p,procTime,"polyMesh","boundary"))
                for j in range(sol.nrProcs()):
                    name="procBoundary%dto%d" %(j,i)
                    name2="procBoundary%dto%d" %(i,j)
                    if name in bound:
                        matrix[i][j]=bound[name]["nFaces"]
                    if name2 in bound:
                        matrix[i][j]=bound[name2]["nFaces"]
                        
            print "Matrix of processor interactions (faces)"
            print
            
            digits=int(ceil(log10(sol.nrProcs())))+2
            colDigits=int(ceil(log10(max(digits,max(max(matrix))))))+2
            
            format="%%%dd" % digits
            colFormat="%%%dd" % colDigits

            print " "*(digits),"|",
            for j in range(sol.nrProcs()):
                print colFormat % j,
            print
            print "-"*(digits+3+(colDigits+1)*sol.nrProcs())
                       
            for i,col in enumerate(matrix):
                print format % i,"|",
                for j,nr in enumerate(col):
                    print colFormat % matrix[i][j],
                print
                
        if self.opts.linearSolvers:
            fvSol=ParsedParameterFile(path.join(sol.systemDir(),"fvSolution"))
            allInfo={}
            for sName in fvSol["solvers"]:
                raw=fvSol["solvers"][sName]
                info={}
                info["solver"]=raw[0]
                try:
                    info["tolerance"]=raw[1]["tolerance"]
                except KeyError:
                    info["tolerance"]=1.
                try:
                    info["relTol"]=raw[1]["relTol"]
                except KeyError:
                    info["relTol"]=0.
                    
                allInfo[sName]=info

            title="%15s | %15s | %10s | %8s" % ("name","solver","tolerance","relative")
            print title
            print "-"*len(title)
            for n,i in allInfo.iteritems():
                print "%15s | %15s | %10g | %8g" % (n,i["solver"],i["tolerance"],i["relTol"])
            print
            
        if self.opts.relaxationFactors:
            fvSol=ParsedParameterFile(path.join(sol.systemDir(),"fvSolution"))
            if "relaxationFactors" in fvSol:
                title="%20s | %15s" % ("name","factor")
                print title
                print "-"*len(title)
                for n,f in fvSol["relaxationFactors"].iteritems():
                    print "%20s | %15g" % (n,f)
                print
            else:
                print "No relaxation factors defined for this case"

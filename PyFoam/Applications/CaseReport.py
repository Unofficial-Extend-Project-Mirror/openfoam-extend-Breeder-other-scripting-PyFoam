#  ICE Revision: $Id: /local/openfoam/Python/PyFoam/PyFoam/Applications/CaseReport.py 2962 2008-03-31T17:30:07.010870Z bgschaid  $ 
"""
Application class that implements pyFoamCasedReport.py
"""

import sys,string

from PyFoamApplication import PyFoamApplication
from PyFoam.RunDictionary.SolutionDirectory import SolutionDirectory
from PyFoam.RunDictionary.BoundaryDict import BoundaryDict
from PyFoam.RunDictionary.ParsedParameterFile import PyFoamParserError

from PyFoam.Error import error,warning

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
                                   interspersed=True)
        
    def addOptions(self):
        self.parser.add_option("--short-bc-report",
                               action="store_true",
                               default=False,
                               dest="shortBCreport",
                               help="Gives a short overview of the boundary-conditions in the case")
        
        self.parser.add_option("--long-bc-report",
                               action="store_true",
                               default=False,
                               dest="longBCreport",
                               help="Gives a full overview of the boundary-conditions in the case")
        
        self.parser.add_option("--dimensions",
                               action="store_true",
                               default=False,
                               dest="dimensions",
                               help="Show the dimensions of the fields")
        
        self.parser.add_option("--internal-field",
                               action="store_true",
                               default=False,
                               dest="internal",
                               help="Show the internal value of the fields (the initial conditions)")
        
        self.parser.add_option("--time",
                               action="store",
                               type="float",
                               default=None,
                               dest="time",
                               help="Time to use as the basis for the reports")
        
        self.parser.add_option("--region",
                               dest="region",
                               default=None,
                               help="Do the report for a special region for multi-region cases")
        
        self.parser.add_option("--long-field-threshold",
                               action="store",
                               type="int",
                               default=100,
                               dest="longlist",
                               help="Fields that are longer than this won't be parsed, but read into memory (nad compared as strings)")

    def run(self):
        sol=SolutionDirectory(self.parser.getArgs()[0],archive=None,paraviewLink=False,region=self.opts.region)
        
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

        if needsPolyBoundaries:
            boundary=BoundaryDict(sol.name,region=self.opts.region)

            boundMaxLen=0
            boundaryNames=[]
            for b in boundary:
                boundMaxLen=max(boundMaxLen,len(b))
                boundaryNames.append(b)

            boundaryNames.sort()
            
        if needsInitialTime:
            fields={}
            
            if self.opts.time==None:
                time=sol.timeName(0)
            else:
                time=sol.timeName(sol.timeIndex(self.opts.time,minTime=True))

            #        print "Using time: ",time

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
                    if b not in f["boundaryField"]:
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
                    if b not in f["boundaryField"]:
                        types[b][fName]="MISSING"
                    else:
                        types[b][fName]=f["boundaryField"][b]["type"]
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

                print fName+" "*(nameMaxLen-len(fName))+" :",f["dimensions"]

        if self.opts.internal:
            print "\Internal value of fields for t =",time
            print

            head="Name"+" "*(nameMaxLen-len("Name"))+" : Value              "
            print head
            print "-"*len(head)
            for fName in fieldNames:
                f=fields[fName]

                print fName+" "*(nameMaxLen-len(fName))+" :",

                cont=str(f["internalField"])
                if cont.find("\n")>=0:
                    print cont[:cont.find("\n")],"..."
                else:
                    print cont

"""
Application-class that implements pyFoamListProfilingInfo.py
"""
from optparse import OptionGroup

from .PyFoamApplication import PyFoamApplication
from .CommonSelectTimesteps import CommonSelectTimesteps

from PyFoam.ThirdParty.six import print_

from PyFoam.RunDictionary.ParsedParameterFile import ParsedParameterFile
from PyFoam.RunDictionary.SolutionDirectory import SolutionDirectory

from os import path
from glob import glob

class ListProfilingInfo(PyFoamApplication,
                        CommonSelectTimesteps):
    def __init__(self,
                 args=None,
                 **kwargs):
        description="""\
List the profiling information in time directories  (either created by a
patched OpenFOAM-version, Foam-extend or by a OpenFOAM-version with the
profiling-patch applied) and prints them in a human-readable form. Either
gets files or a case directory from which it tries to get the proper files. If
more than one file is specified it is assumed that this is a parallel run and
the data is accumulated

Results are printed as a table. The first column is the name of the
profiling entry. Children entries (entries that are called by that
entry) are indented.  The first numeric column is the percentage that
this entry used of the total time (including time spent in
children). The next entry is the percentages of the 'self' time
(the time spent in this entry minus the time spent in the
children) as the percentage of the total execution time.  After
that the percentages of the parent time (total and 'self').
After that the number of times this
entry was called is printed. Then the total time spent in this entry
and the time without the child entries are printed.

If the data from multiple processors is used then the totalTime and the calls
are the average of all processors. Also are there three more columns: the range
of the totalTime (maximum-minimum). How big that range is compared to the average
totalTime and the range of the calls
"""
        examples="""\
%prog aCase/100/uniform/profilingInfo

  Print the profiling info of a case named aCase at time 100

%prog aCase --time=100

  Also print the profiling info of a case named aCase at time 100

%prog aCase --latest-time

  Print the profiling info from the latest timestep in case aCase

%prog aCase --latest-time --parallel

  Print the profiling information from the latest timestep in the case aCase
  but use the data from all processors and accumulate them

%prog aCase --latest-time --parallel --sort-by=totalTime --depth=2

  Sort the profiling data by the total time that was used and only
  print the first two levels
"""

        PyFoamApplication.__init__(self,
                                   args=args,
                                   description=description,
                                   examples=examples,
                                   usage="%prog [<caseDirectory>|<profiling file>]",
                                   interspersed=True,
                                   changeVersion=True,
                                   nr=1,
                                   exactNr=False,
                                   **kwargs)

    def addOptions(self):
        CommonSelectTimesteps.addOptions(self,False,singleTime=True)
        output=OptionGroup(self.parser,
                           "Output",
                           "How data should be output")
        self.parser.add_option_group(output)
        sortModes=["id","totalTime","selfTime","description","calls"]
        output.add_option("--sort-by",
                          type="choice",
                          dest="sortBy",
                          default="id",
                          choices=sortModes,
                          help="How the entries should be sorted in their 'subtree'. Possible values are "+", ".join(sortModes)+". Default is 'id' which is more or less the order in which these entries were registered")
        output.add_option("--depth",
                          type="int",
                          dest="depth",
                          default=0,
                          help="How many levels of the tree should be printed. If 0 or smaller then everything is printed")

    def readProfilingInfo(self,fName):
        """Read the info from a file and return a tuple with (date,children,root)"""
        pf=ParsedParameterFile(fName,
                               treatBinaryAsASCII=True)

        try:
            # Foam-extend and Patch
            pi=pf["profilingInfo"]
            newFormat=False
        except KeyError:
            try:
                pi=pf["profiling"]
                newFormat=True
            except KeyError:
                self.error("No profiling info found in",fName)

        data={}
        children={}
        root=None

        for p in pi:
            if newFormat:
                p=pi[p]
            if p["id"] in data:
                print_("Duplicate definition of",p["id"])
                sys.exit(-1)
            if p["description"][0]=='"':
                p["description"]=p["description"][1:]
            if p["description"][-1]=='"':
                p["description"]=p["description"][:-1]

            data[p["id"]]=p
            if "parentId" in p:
                if p["parentId"] in children:
                    children[p["parentId"]].append(p["id"])
                else:
                    children[p["parentId"]]=[p["id"]]
            else:
                if root!=None:
                    print_("Two root elements")
                    sys-exit(-1)
                else:
                    root=p["id"]
            p["selfTime"]=p["totalTime"]-p["childTime"]

        return data,children,root

    def printProfilingInfo(self,data,children,root,parallel=False):
        """Prints the profiling info in a pseudo-graphical form"""
        def depth(i):
            if i in children:
                return max([depth(j) for j in children[i]])+1
            else:
                return 0
        maxdepth=depth(root)

        depths={}

        def nameLen(i,d=0):
            depths[i]=d
            maxi=len(data[i]["description"])
            if i in children:
                maxi=max(maxi,max([nameLen(j,d+1) for j in children[i]]))
            if self.opts.depth>0 and depths[i]>self.opts.depth:
                return 0
            else:
                return maxi+3

        maxLen=nameLen(root)

        format=" %5.1f%% (%5.1f%%) - %5.1f%% (%5.1f%%) | %8d %9.4gs %9.4gs"
        if parallel:
            parallelFormat=" | %9.4gs %5.1f%% %9.4g"
        totalTime=data[root]["totalTime"]

        header=" "*(maxLen)+" |  total  ( self ) - parent ( self ) |    calls      total      self "
        if parallel:
            header+="| range(total) / %   range(calls) "
        print_(header)
        print_("-"*len(header))

        def printItem(i):
            result=""
            if self.opts.depth>0 and depths[i]>self.opts.depth:
                return ""
            if depths[i]>1:
                result+="  "*(depths[i]-1)
            if depths[i]>0:
                result+="|- "
            result+=data[i]["description"]
            result+=" "*(maxLen-len(result)+1)+"| "

            parentTime=data[i]["totalTime"]
            if "parentId" in data[i]:
                parentTime=data[data[i]["parentId"]]["totalTime"]

            tt=data[i]["totalTime"]
            ct=data[i]["childTime"]
            st=data[i]["selfTime"]

            result+=format % (100*tt/totalTime,
                              100*st/totalTime,
                              100*tt/parentTime,
                              100*st/tt,
                              data[i]["calls"],
                              tt,
                              st)
            if parallel:
                timeRange=data[i]["totalTimeMax"]-data[i]["totalTimeMin"]
                result+=parallelFormat % (timeRange,
                                          100*timeRange/tt,
                                          data[i]["callsMax"]-data[i]["callsMin"])
            print_(result)
            if i in children:
                def getKey(k):
                    def keyF(i):
                        return data[i][k]
                    return keyF

                #make sure that children are printed in the correct order
                if self.opts.sortBy=="id":
                    children[i].sort()
                else:
                    children[i].sort(
                        key=getKey(self.opts.sortBy),
                        reverse=self.opts.sortBy in ["totalTime","selfTime","calls"])
                for c in children[i]:
                    printItem(c)

        printItem(root)

    def run(self):
        files=self.parser.getArgs()[0:]
        if len(files)==1 and path.isdir(files[0]):
            sol=SolutionDirectory(
                self.parser.getArgs()[0],
                archive=None,
                parallel=self.opts.parallelTimes,
                paraviewLink=False)
            self.processTimestepOptions(sol)
            if len(self.opts.time)<1:
                self.error("No time specified")
            globStr=self.parser.getArgs()[0]
            if self.opts.parallelTimes:
                globStr=path.join(globStr,"processor*")
            usedTime=sol.timeName(self.opts.time[0])
            globStr=path.join(globStr,
                              usedTime,
                              "uniform","profiling*")

            files=glob(globStr)
            print_("Profiling info from time",usedTime)
        if len(files)<1:
            self.error("No profiling data found")
        elif len(files)>1:
            lst=[]
            for f in files:
                lst.append(self.readProfilingInfo(f))
            dataAll,children0,root0=lst[0]
            for i in dataAll:
                d=dataAll[i]
                d["totalTimeMin"]=d["totalTime"]
                d["totalTimeMax"]=d["totalTime"]
                d["callsMin"]=d["calls"]
                d["callsMax"]=d["calls"]
            for data,children,root in lst[1:]:
                if root0!=root or children!=children0 or data.keys()!=dataAll.keys():
                    self.error("Inconsistent profiling data. Probably not from same run/timestep")
                for i in data:
                    d=data[i]
                    s=dataAll[i]
                    s["totalTime"]+=d["totalTime"]
                    s["totalTimeMin"]=min(s["totalTimeMin"],d["totalTime"])
                    s["totalTimeMax"]=max(s["totalTimeMax"],d["totalTime"])
                    s["calls"]+=d["calls"]
                    s["callsMin"]=min(s["callsMin"],d["calls"])
                    s["callsMax"]=max(s["callsMax"],d["calls"])
                    s["childTime"]+=d["childTime"]
            for i in dataAll:
                d=dataAll[i]
                d["totalTime"]=d["totalTime"]/len(lst)
                d["childTime"]=d["childTime"]/len(lst)
                d["calls"]=d["calls"]/len(lst)
            self.printProfilingInfo(dataAll,children,root,True)
        else:
            data,children,root=self.readProfilingInfo(files[0])
            self.printProfilingInfo(data,children,root)

#  ICE Revision: $Id: /local/openfoam/Python/PyFoam/PyFoam/Applications/Benchmark.py 7393 2011-03-29T14:55:03.425417Z bgschaid  $ 
"""
Class that implements pyFoamBenchmark
"""

from PyFoamApplication import PyFoamApplication

from fnmatch import fnmatch

import sys,string,ConfigParser

from os import path,uname
from time import time,localtime,asctime
from PyFoam.Execution.BasicRunner import BasicRunner
from PyFoam.FoamInformation import foamTutorials
from PyFoam.RunDictionary.SolutionDirectory import SolutionDirectory
from PyFoam.RunDictionary.SolutionFile import SolutionFile
from PyFoam.RunDictionary.ParameterFile import ParameterFile
from PyFoam.RunDictionary.BlockMesh import BlockMesh
from PyFoam.Execution.ParallelExecution import LAMMachine
from PyFoam.Basics.Utilities import execute
from PyFoam.Basics.CSVCollection import CSVCollection
from PyFoam.FoamInformation import oldAppConvention as oldApp

class Benchmark(PyFoamApplication):
    def __init__(self,args=None):
        description="""
        Runs a set of benchmarks specified in a config files
        """
        PyFoamApplication.__init__(self,args=args,description=description,usage="%prog [options] <specification>",interspersed=True,nr=1)

    def addOptions(self):
        self.parser.add_option("--nameAddition",
                               action="store",
                               dest="nameAddition",
                               default=None,
                               help="Addition to the name that helps to distinguish different runs of the same configuration")
        self.parser.add_option("--removeCases",
                               action="store_true",
                               dest="removeCases",
                               default=False,
                               help="Remove the case directories and log files for all successfully run cases")
        self.parser.add_option("--exclude-cases",
                               action="append",
                               default=None,
                               dest="excases",
                               help="Cases which should not be processed (pattern, can be used more than once)")
        self.parser.add_option("--cases",
                               action="append",
                               default=None,
                               dest="cases",
                               help="Cases which should be processed (pattern, can be used more than once)")
        
    def run(self):
        config=ConfigParser.ConfigParser()
        files=self.parser.getArgs()

        good=config.read(files)
        # will work with 2.4
        # if len(good)!=len(files):
        #    print "Problem while trying to parse files",files
        #    print "Only ",good," could be parsed"
        #    sys.exit(-1)

        benchName=config.get("General","name")
        if self.opts.nameAddition!=None:
            benchName+="_"+self.opts.nameAddition
        if self.opts.foamVersion!=None:
            benchName+="_v"+self.opts.foamVersion
            
        isParallel=config.getboolean("General","parallel")
        lam=None

        if isParallel:
            nrCpus=config.getint("General","nProcs")
            machineFile=config.get("General","machines")
            if not path.exists(machineFile):
                self.error("Machine file ",machineFile,"needed for parallel run")
            lam=LAMMachine(machineFile,nr=nrCpus)
            if lam.cpuNr()>nrCpus:
                self.error("Wrong number of CPUs: ",lam.cpuNr())

            print "Running parallel on",lam.cpuNr(),"CPUs"

        if config.has_option("General","casesDirectory"):
            casesDirectory=path.expanduser(config.get("General","casesDirectory"))
        else:
            casesDirectory=foamTutorials()

        if not path.exists(casesDirectory):
            self.error("Directory",casesDirectory,"needed with the benchmark cases is missing")
        else:
            print "Using cases from directory",casesDirectory

        benchCases=[]
        config.remove_section("General")

        for sec in config.sections():
            print "Reading: ",sec
            skipIt=False
            skipReason=""
            if config.has_option(sec,"skip"):
                skipIt=config.getboolean(sec,"skip")
                skipReason="Switched off in file"
            if self.opts.excases!=None and not skipIt:
                for p in self.opts.excases:
                    if fnmatch(sec,p):
                        skipIt=True
                        skipReason="Switched off by pattern '"+p+"'"
            if self.opts.cases!=None:
                for p in self.opts.cases:
                    if fnmatch(sec,p):
                        skipIt=False
                        skipReason=""
                
            if skipIt:
                print "Skipping case ..... Reason:"+skipReason
                continue
            sol=config.get(sec,"solver")
            cas=config.get(sec,"case")
            pre=eval(config.get(sec,"prepare"))
            preCon=[]
            if config.has_option(sec,"preControlDict"):
                preCon=eval(config.get(sec,"preControlDict"))
            con=eval(config.get(sec,"controlDict"))
            bas=config.getfloat(sec,"baseline")
            wei=config.getfloat(sec,"weight")
            add=[]
            if config.has_option(sec,"additional"):
                add=eval(config.get(sec,"additional"))
                print "Adding: ", add
            util=[]
            if config.has_option(sec,"utilities"):
                util=eval(config.get(sec,"utilities"))
                print "Utilities: ", util    
            nr=99999
            if config.has_option(sec,"nr"):
                nr=eval(config.get(sec,"nr"))
            sp=None
            if config.has_option(sec,"blockSplit"):
                sp=eval(config.get(sec,"blockSplit"))
            toRm=[]
            if config.has_option(sec,"filesToRemove"):
                toRm=eval(config.get(sec,"filesToRemove"))
            setInit=[]
            if config.has_option(sec,"setInitial"):
                setInit=eval(config.get(sec,"setInitial"))

            parallelOK=False
            if config.has_option(sec,"parallelOK"):
                parallelOK=config.getboolean(sec,"parallelOK")

            deMet=["metis"]
            if config.has_option(sec,"decomposition"):
                deMet=config.get(sec,"decomposition").split()

            if deMet[0]=="metis":
                pass
            elif deMet[0]=="simple":
                if len(deMet)<2:
                    deMet.append(0)
                else:
                    deMet[1]=int(deMet[1])
            else:
                print "Unimplemented decomposition method",deMet[0],"switching to metis"
                deMet=["metis"]

            if isParallel==False or parallelOK==True:
                if path.exists(path.join(casesDirectory,sol,cas)):
                    benchCases.append( (nr,sec,sol,cas,pre,con,preCon,bas,wei,add,util,sp,toRm,setInit,deMet) )
                else:
                    print "Skipping",sec,"because directory",path.join(casesDirectory,sol,cas),"could not be found"
            else:
                print "Skipping",sec,"because not parallel"

        benchCases.sort()

        parallelString=""
        if isParallel:
            parallelString=".cpus="+str(nrCpus)

        resultFile=open("Benchmark."+benchName+"."+uname()[1]+parallelString+".results","w")

        totalSpeedup=0
        minSpeedup=None
        maxSpeedup=None
        totalWeight =0
        runsOK=0
        currentEstimate = 1.

        print "\nStart Benching\n"
        
        csv=CSVCollection("Benchmark."+benchName+"."+uname()[1]+parallelString+".csv")
        
#        csvHeaders=["description","solver","case","caseDir","base",
#                    "benchmark","machine","arch","cpus","os","version",
#                    "wallclocktime","cputime","cputimeuser","cputimesystem","maxmemory","cpuusage","speedup"]

        for nr,description,solver,case,prepare,control,preControl,base,weight,additional,utilities,split,toRemove,setInit,decomposition in benchCases:
            #    control.append( ("endTime",-2000) )
            print "Running Benchmark: ",description
            print "Solver: ",solver
            print "Case: ",case
            caseName=solver+"_"+case+"_"+benchName+"."+uname()[1]+".case"
            print "Short name: ",caseName
            caseDir=caseName+".runDir"

            csv["description"]=description
            csv["solver"]=solver
            csv["case"]=case
            csv["caseDir"]=caseDir
            csv["base"]=base

            csv["benchmark"]=benchName
            csv["machine"]=uname()[1]
            csv["arch"]=uname()[4]
            if lam==None:
                csv["cpus"]=1
            else:
                csv["cpus"]=lam.cpuNr()
            csv["os"]=uname()[0]
            csv["version"]=uname()[2]
            
            workDir=path.realpath(path.curdir)

            orig=SolutionDirectory(path.join(casesDirectory,solver,case),
                                   archive=None,
                                   paraviewLink=False)
            for a in additional+utilities:
                orig.addToClone(a)
            orig.cloneCase(path.join(workDir,caseDir))

            if oldApp():
                argv=[solver,workDir,caseDir]
            else:
                argv=[solver,"-case",path.join(workDir,caseDir)]
                
            run=BasicRunner(silent=True,argv=argv,logname="BenchRunning",lam=lam)
            runDir=run.getSolutionDirectory()
            controlFile=ParameterFile(runDir.controlDict())

            for name,value in preControl:
                print "Setting parameter",name,"to",value,"in controlDict"
                controlFile.replaceParameter(name,value)

            for rm in toRemove:
                fn=path.join(caseDir,rm)
                print "Removing file",fn
                execute("rm -f "+fn)

            for field,bc,val in setInit:
                print "Setting",field,"on",bc,"to",val
                SolutionFile(runDir.initialDir(),field).replaceBoundary(bc,val)

            oldDeltaT=controlFile.replaceParameter("deltaT",0)

            for u in utilities:
                print "Building utility ",u
                execute("wmake 2>&1 >%s %s" % (path.join(caseDir,"BenchCompile."+u),path.join(caseDir,u)))

            print "Preparing the case: "
            if lam!=None:
                prepare=prepare+[("decomposePar","")]
                if decomposition[0]=="metis":
                    lam.writeMetis(SolutionDirectory(path.join(workDir,caseDir)))
                elif decomposition[0]=="simple":
                    lam.writeSimple(SolutionDirectory(path.join(workDir,caseDir)),decomposition[1])

            if split:
                print "Splitting the mesh:",split
                bm=BlockMesh(runDir.blockMesh())
                bm.refineMesh(split)

            for pre,post in prepare:
                print "Doing ",pre," ...."
                post=post.replace("%case%",caseDir)
                if oldApp():
                    args=string.split("%s %s %s %s" % (pre,workDir,caseDir,post))
                else:
                    args=string.split("%s -case %s %s" % (pre,path.join(workDir,caseDir),post))
                util=BasicRunner(silent=True,argv=args,logname="BenchPrepare_"+pre)
                util.start()

            controlFile.replaceParameter("deltaT",oldDeltaT)

            #    control.append(("endTime",-1000))
            for name,value in control:
                print "Setting parameter",name,"to",value,"in controlDict"
                controlFile.replaceParameter(name,value)

            print "Starting at ",asctime(localtime(time()))
            print " Baseline is %f, estimated speedup %f -> estimated end at %s " % (base,currentEstimate,asctime(localtime(time()+base/currentEstimate)))
            print "Running the case ...."
            run.start()

            speedup=None
            cpuUsage=0
            speedupOut=-1

            try:
                speedup=base/run.run.wallTime()
                cpuUsage=100.*run.run.cpuTime()/run.run.wallTime()
            except ZeroDivisionError:
                print "Division by Zero: ",run.run.wallTime()

            if not run.runOK():
                print "\nWARNING!!!!"
                print "Run had a problem, not using the results. Check the log\n"
                speedup=None

            if speedup!=None:
                speedupOut=speedup

                totalSpeedup+=speedup*weight
                totalWeight +=weight
                runsOK+=1
                if maxSpeedup==None:
                    maxSpeedup=speedup
                elif speedup>maxSpeedup:
                    maxSpeedup=speedup
                if minSpeedup==None:
                    minSpeedup=speedup
                elif speedup<minSpeedup:
                    minSpeedup=speedup

            print "Wall clock: ",run.run.wallTime()
            print "Speedup: ",speedup," (Baseline: ",base,")"
            print "CPU Time: ",run.run.cpuTime()
            print "CPU Time User: ",run.run.cpuUserTime()
            print "CPU Time System: ",run.run.cpuSystemTime()
            print "Memory: ",run.run.usedMemory()
            print "CPU Usage: %6.2f%%" % (cpuUsage)

            csv["wallclocktime"]=run.run.wallTime()
            csv["cputime"]=run.run.cpuTime()
            csv["cputimeuser"]=run.run.cpuUserTime()
            csv["cputimesystem"]=run.run.cpuSystemTime()
            csv["maxmemory"]=run.run.usedMemory()
            csv["cpuusage"]=cpuUsage
            if speedup!=None:
                csv["speedup"]=speedup
            else:
                csv["speedup"]="##"
                
            csv.write()
            
            resultFile.write("Case %s WallTime %g CPUTime %g UserTime %g SystemTime %g Memory %g MB  Speedup %g\n" %(caseName,run.run.wallTime(),run.run.cpuTime(),run.run.cpuUserTime(),run.run.cpuSystemTime(),run.run.usedMemory(),speedupOut))

            resultFile.flush()
            
            if speedup!=None:
                currentEstimate=totalSpeedup/totalWeight

            if self.opts.removeCases:
                print "Clearing case",
                if speedup==None:
                    print "not ... because it failed"
                else:
                    print "completely"
                    execute("rm -rf "+caseDir)

            print
            print
        
        if lam!=None:
            lam.stop()

        print "Total Speedup: ",currentEstimate," ( ",totalSpeedup," / ",totalWeight, " ) Range: [",minSpeedup,",",maxSpeedup,"]"

        print runsOK,"of",len(benchCases),"ran OK"

        resultFile.write("Total Speedup: %g\n" % (currentEstimate))
        if minSpeedup and maxSpeedup:
            resultFile.write("Range: [ %g , %g ]\n" % (minSpeedup,maxSpeedup))

        resultFile.close()

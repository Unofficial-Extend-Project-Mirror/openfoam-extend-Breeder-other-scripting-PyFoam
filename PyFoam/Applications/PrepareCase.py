"""
Application-class that implements pyFoamPrepareCase.py
"""
from optparse import OptionGroup

from .PyFoamApplication import PyFoamApplication

from PyFoam.RunDictionary.SolutionDirectory import SolutionDirectory
from PyFoam.Basics.DataStructures import DictProxy
from PyFoam.Basics.Utilities import rmtree,copytree,execute,remove
from PyFoam.RunDictionary.ParsedParameterFile import ParsedParameterFile,WriteParameterFile
from PyFoam.Basics.TemplateFile import TemplateFile
from PyFoam.Execution.BasicRunner import BasicRunner
from PyFoam.Basics.RestructuredTextHelper import RestructuredTextHelper

from PyFoam.FoamInformation import foamFork,foamVersion

from .CommonTemplateFormat import CommonTemplateFormat
from .CommonTemplateBehaviour import CommonTemplateBehaviour

from PyFoam.ThirdParty.six import print_,iteritems,exec_

from PyFoam import configuration

from os import path,listdir,mkdir
from shutil import copymode,copy,move
from collections import OrderedDict
import time
import re

def buildFilenameExtension(paraList,valueStrings):
    ext=""
    if len(paraList)>0:
        ext="_".join([path.basename(p) for p in paraList])
    if len(valueStrings)>0:
        d={}
        for v in valueStrings:
            d.update(eval(v))
        ext+="_"+"_".join(["%s=%s" % (n,str(v)) for n,v in iteritems(d)])
    if ext=="":
        return "_vanilla"
    else:
        return "_"+ext

class PrepareCase(PyFoamApplication,
                  CommonTemplateBehaviour,
                  CommonTemplateFormat):

    parameterOutFile="PyFoamPrepareCaseParameters"

    def __init__(self,
                 args=None,
                 exactNr=True,
                 interspersed=True,
                 usage="%prog <caseDirectory>",
                 examples=None,
                 nr=1,
                 description=None,
                 **kwargs):
        self.defaultMeshCreate=configuration().get("PrepareCase","MeshCreateScript")
        self.defaultCaseSetup=configuration().get("PrepareCase","CaseSetupScript")
        self.defaultParameterFile=configuration().get("PrepareCase","DefaultParameterFile")
        self.defaultIgnoreDirecotries=configuration().getList("PrepareCase","IgnoreDirectories")

        description2="""\
Prepares a case for running. This is intended to be the replacement for
boiler-plate scripts. The steps done are

  1. Clear old data from the case (including processor directories)

  2. if a folder 0.org is present remove the 0 folder too

  3. go through all folders and for every found file with the extension .template
do template expansion using the pyratemp-engine (automatically create variables
casePath and caseName)

  4. create a mesh (either by using a script or if a blockMeshDict is present by
running blockMesh. If none of these is present assume that there is a valid mesh
present)

  5. copy every foo.org that is found to to foo (recursively if directory)

  6. do template-expansion for every file with the extension .postTemplate

  7. execute another preparation script (caseSetup.sh). If no such script is found
but a setFieldsDict in system then setFields is executed

  8. do final template-expansion for every file with the extension .finalTemplate

The used parameters are written to a file 'PyFoamPrepareCaseParameters' and are used by other utilities
"""
        examples2="""\
%prog . --paramter-file=parameters.base

  Prepare the current case with the parameters list in parameters.base

%prog . --paramter-file=parameters.base --values-string="{'visco':1e-3}"

  Changes the value of the parameter visco

%prog . --no-mesh-create

  Skip the mesh creation phase
"""
        PyFoamApplication.__init__(self,
                                   args=args,
                                   description=description if description else description2,
                                   usage=usage,
                                   examples=examples if examples else examples2,
                                   interspersed=interspersed,
                                   nr=nr,
                                   exactNr=exactNr,
                                   findLocalConfigurationFile=self.localConfigInArgs,
                                   **kwargs)

    def addOptions(self):
        output=OptionGroup(self.parser,
                         "Output",
                         "What information should be given")
        self.parser.add_option_group(output)
        output.add_option("--fatal",
                          action="store_true",
                          dest="fatal",
                        default=False,
                        help="If non-cases are specified the program should abort")
        output.add_option("--no-complain",
                          action="store_true",
                          dest="noComplain",
                          default=False,
                          help="Don't complain about non-case-files")
        output.add_option("--quiet",
                          action="store_false",
                          dest="verbose",
                          default=True,
                          help="Do not report what is being done")
        output.add_option("--no-write-parameters",
                          action="store_false",
                          dest="writeParameters",
                          default=True,
                          help="Usually a file '"+self.parameterOutFile+"' with a dictionary of the used parameters is written to the case directory. ")
        output.add_option("--no-write-report",
                          action="store_false",
                          dest="writeReport",
                          default=True,
                          help="Usually a file '"+self.parameterOutFile+".rst' with a ReST-file that reports the used parameters is written to the case directory. ")
        output.add_option("--warn-on-wrong-options",
                          action="store_false",
                          dest="failOnWrongOption",
                          default=True,
                          help="Only issue a warning if a value was set that is not found in the list of valid options")

        extensions=OptionGroup(self.parser,
                               "Extensions",
                               "File extensions that are used in actions")
        self.parser.add_option_group(extensions)
        extensions.add_option("--template-extension",
                              action="store",
                              dest="templateExt",
                              default=".template",
                              help="Extension for template files. Default: %default")
        extensions.add_option("--post-template-extension",
                              action="store",
                              dest="postTemplateExt",
                              default=".postTemplate",
                              help="Extension for post-template files. Default: %default")
        extensions.add_option("--final-template-extension",
                              action="store",
                              dest="finalTemplateExt",
                              default=".finalTemplate",
                              help="Extension for final-template files. Default: %default")
        extensions.add_option("--original-extension",
                              action="store",
                              dest="originalExt",
                              default=".org",
                              help="Extension for files and directories that are copied. Default: %default")
        extensions.add_option("--extension-addition",
                              action="append",
                              dest="extensionAddition",
                              default=[],
                              help="Addtional extension that is added to templates and originals to allow overrides. For instance if an addition 'steady' is specified and a file 'T.template' and 'T.template.steady' is found then the later is used. Can be specied more than once. The last instance is used.")

        inputs=OptionGroup(self.parser,
                           "Inputs",
                           "Inputs for the templating process")
        self.parser.add_option_group(inputs)

        inputs.add_option("--parameter-file",
                          action="append",
                          default=[],
                          dest="valuesDicts",
                          help="Name of a dictionary-file in OpenFOAM-format. Can be specified more than once. Values in later files override old values. If a file "+self.defaultParameterFile+" is present it is read before all other paraemter files")
        inputs.add_option("--no-default-parameter-file",
                          action="store_false",
                          default=True,
                          dest="useDefaultParameterFile",
                          help="Even if present do NOT use the file "+self.defaultParameterFile+" before the other parameter files")
        inputs.add_option("--values-string",
                          action="append",
                          default=[],
                          dest="values",
                          help="String with the values that are to be inserted into the template as a dictionaty in Python-format. Can be specified more than once and overrides values from the parameter-files")

        special=OptionGroup(self.parser,
                           "Special files and directories",
                           "Files and directories that get special treatment")
        self.parser.add_option_group(special)

        special.add_option("--directories-to-clean",
                          action="append",
                          default=["0"],
                          dest="cleanDirectories",
                          help="Directory from which templates are cleaned (to avoid problems with decomposePar). Can be specified more than once. Default: %default")
        special.add_option("--overload-directory",
                           action="append",
                           default=[],
                           dest="overloadDirs",
                           help="Before starting the preparation process load files from this directory recursively into this case. Caution: existing files will be overwritten. Can be specified more than once. Directories are then copied in the specified order")
        special.add_option("--clone-case",
                          default=None,
                          dest="cloneCase",
                           help="If this is set then this directory is cloned to the specified directory and setup is done there (the target directory must not exist except if the name is build with --automatic-casename)")
        special.add_option("--automatic-casename",
                           action="store_true",
                           dest="autoCasename",
                           default=False,
                           help="If used with --clone-case then the casename is built from the original casename, the names of the parameter-files and the set values")
        special.add_option("--ignore-directories",
                           action="append",
                           dest="ignoreDirectories",
                           default=list(self.defaultIgnoreDirecotries),
                           help="Regular expression. Directories that match this expression are ignored. Can be used more than once. Already set: "+", ".join(["r'"+e+"'" for e in self.defaultIgnoreDirecotries]))
        CommonTemplateFormat.addOptions(self)
        CommonTemplateBehaviour.addOptions(self)

        stages=OptionGroup(self.parser,
                           "Stages",
                           "Which steps should be executed")
        self.parser.add_option_group(stages)

        stages.add_option("--only-variables",
                          action="store_true",
                          dest="onlyVariables",
                          default=False,
                          help="Do nothing. Only read the variables")

        stages.add_option("--no-clear",
                          action="store_false",
                          dest="doClear",
                          default=True,
                          help="Do not clear the case")

        stages.add_option("--no-templates",
                          action="store_false",
                          dest="doTemplates",
                          default=True,
                          help="Do not rework the templates")

        stages.add_option("--no-mesh-create",
                          action="store_false",
                          dest="doMeshCreate",
                          default=True,
                          help="Do not execute a script to create a mesh")

        stages.add_option("--no-copy",
                          action="store_false",
                          dest="doCopy",
                          default=True,
                          help="Do not copy original directories")

        stages.add_option("--no-post-templates",
                          action="store_false",
                          dest="doPostTemplates",
                          default=True,
                          help="Do not rework the post-templates")

        stages.add_option("--no-case-setup",
                          action="store_false",
                          dest="doCaseSetup",
                          default=True,
                          help="Do not execute a script to set initial conditions etc")

        stages.add_option("--no-final-templates",
                          action="store_false",
                          dest="doFinalTemplates",
                          default=True,
                          help="Do not rework the final-templates")

        stages.add_option("--no-template-clean",
                          action="store_false",
                          dest="doTemplateClean",
                          default=True,
                          help="Do not clean template files from 0-directory")

        scripts=OptionGroup(self.parser,
                            "Scripts",
                            "Specification of scripts to be executed")
        self.parser.add_option_group(scripts)

        scripts.add_option("--mesh-create-script",
                          action="store",
                          dest="meshCreateScript",
                          default=None,
                          help="Script that is executed after the template expansion to create the mesh. If not specified then the utility looks for "+self.defaultMeshCreate+" and executes this. If this is also not found blockMesh is executed if a blockMeshDict is found")
        stages.add_option("--no-keep-zero-directory-from-mesh-create",
                          action="store_false",
                          dest="keepZeroDirectoryFromMesh",
                          default=True,
                          help="If the script that creates the mesh generates a '0'-directory with data then this data will be removed. Otherwise it is kept")
        scripts.add_option("--case-setup-script",
                          action="store",
                          dest="caseSetupScript",
                          default=None,
                          help="Script that is executed after the original files have been copied to set initial conditions or similar. If not specified then the utility looks for "+self.defaultCaseSetup+" and executes this.")
        scripts.add_option("--derived-parameters-script",
                          action="store",
                          dest="derivedParametersScript",
                          default="derivedParameters.py",
                          help="If this script is found then it is executed after the parameters are read. All variables set in this script can then be used in the templates. Default: %default")
        scripts.add_option("--allow-derived-changes",
                          action="store_true",
                          dest="allowDerivedChanges",
                          default=False,
                          help="Allow that the derived script changes existing values")
        scripts.add_option("--continue-on-script-failure",
                          action="store_false",
                          dest="failOnScriptFailure",
                          default=True,
                          help="Don't fail the whole process even if a script fails")

        variables=OptionGroup(self.parser,
                              "Variables",
                              "Variables that are automatically defined")
        self.parser.add_option_group(variables)
        variables.add_option("--number-of-processors",
                             action="store",
                             type=int,
                             dest="numberOfProcessors",
                             default=1,
                             help="Value of the variable numberOfProcessors. Default: %default")

    def info(self,*args):
        """Information output"""
        if self.opts.verbose:
            print_(*args)

    def listdir(self,d,ext):
        """Private copy of listdir. Returns a list of pairs: first element is
        the real file-name. Second the name with the extensions stripped off or
        None if the file doesn't match any extensions"""

        extAdditions=[""]+["."+e for e in self.opts.extensionAddition]
        allFiles=listdir(d)
        result=[]
        templated=set()

        for f in allFiles:
            isPlain=True
            for e in extAdditions:
                ee=ext+e
                if len(f)>len(ee):
                    if f[-len(ee):]==ee:
                        isPlain=False
                        templated.add(f[:-len(ee)])
            if isPlain:
                result.append((f,None))

        for t in templated:
            found=None
            for e in extAdditions:
                tt=t+ext+e
                if tt in allFiles:
                    found=tt
            if found==None:
                self.error("This should not happen. Nothing found for",t,"with extensions",
                           extAdditions,"in files",allFiles)
            else:
                result.append((found,t))

        return result

    def copyOriginals(self,startDir):
        """Go recursivly through directories and copy foo.org to foo"""
        self.info("Looking for originals in",startDir)
        for f,t in self.listdir(startDir,self.opts.originalExt):
            if f[0]==".":
                self.info("Skipping",f)
                continue
            src=path.join(startDir,f)
            if t!=None:
                dst=path.join(startDir,t)
                if path.exists(dst):
                    self.info("Replacing",dst,"with",src)
                    rmtree(dst)
                else:
                    self.info("Copying",src,"to",dst)
                copytree(src,dst,force=True)
            elif path.isdir(src):
                self.copyOriginals(src)

    def cleanExtension(self,
                       startDir,
                       ext):
        """Go recursivly through directories and remove all files that have a specific extension"""
        self.info("Looking for extension",ext,"in",startDir)
        for f in listdir(startDir):
            if f[0]==".":
                self.info("Skipping",f)
                continue

            src=path.join(startDir,f)
            if path.splitext(src)[1]==ext or path.splitext(path.splitext(src)[0])[1]==ext:
                if not path.isdir(src):
                    self.info("Removing",src)
                    remove(src)
            if path.isdir(src):
                self.cleanExtension(src,ext)

    def searchAndReplaceTemplates(self,
                                  startDir,
                                  values,
                                  templateExt,
                                  ignoreDirectories=[]):
        """Go through the directory recursively and replate foo.template with
        foo after inserting the values"""
        self.info("Looking for templates with extension",templateExt,"in ",startDir)
        for f,t in self.listdir(startDir,templateExt):
            if f[0]==".":
                self.info("Skipping",f)
                continue
            if path.isdir(path.join(startDir,f)):
                matches=None
                for p in ignoreDirectories:
                    if re.compile(p+"$").match(f):
                        matches=p
                        break
                if matches:
                    self.info("Skipping directory",f,"because it matches",matches)
                    continue
                self.searchAndReplaceTemplates(
                    path.join(startDir,f),
                    values,
                    templateExt)
            elif t!=None:
                tName=path.join(startDir,t)
                fName=path.join(startDir,f)
                self.info("Found template for",tName)
                t=TemplateFile(name=fName,
                               tolerantRender=self.opts.tolerantRender,
                               allowExec=self.opts.allowExec,
                               expressionDelimiter=self.opts.expressionDelimiter,
                               assignmentDebug=self.pickAssignmentDebug(fName),
                               assignmentLineStart=self.opts.assignmentLineStart)
                t.writeToFile(tName,values)
                copymode(fName,tName)

    def overloadDir(self,here,there):
        """Copy files recursively. Overwrite local copies if they exist"""
        for f in listdir(there):
            fSrc=path.join(there,f)
            fDst=path.join(here,f)
            if path.isdir(fSrc):
                if not path.exists(fDst):
                    self.info("Creating directory",fDst)
                    mkdir(fDst)
                elif not path.isdir(fDst):
                    self.error("Destination path",fDst,"exists, but is no directory")
                self.overloadDir(fDst,fSrc)
            elif path.isfile(fSrc):
                isThere=False
                rmDest=None
                if path.exists(fDst):
                    isThere=True
                elif path.splitext(fSrc)[1]==".gz" and \
                     path.exists(path.splitext(fDst)[0]):
                    rmDest=path.splitext(fDst)[0]
                elif path.splitext(fSrc)[1]=="" and \
                     path.exists(fDst+".gz"):
                    rmDest=fDst+".gz"

                if rmDest:
                    remove(rmDest)
                if isThere:
                    if not path.isfile(fDst):
                        self.error("Desination",fDst,"exists but is no file")

                self.info("Copying",fSrc,"to",fDst)
                copy(fSrc,fDst)
            else:
                self.errr("Source file",fSrc,"is neither file nor directory")

    def run(self):
        cName=self.parser.getArgs()[0]
        if self.opts.cloneCase:
            if self.opts.autoCasename:
                cName=path.join(cName,
                                path.basename(self.opts.cloneCase)+
                                buildFilenameExtension(self.opts.valuesDicts,
                                                       self.opts.values))
            if path.exists(cName):
                self.error(cName,"already existing (case should not exist when used with --clone-case)")
            if self.checkCase(self.opts.cloneCase,
                              fatal=self.opts.fatal,
                              verbose=not self.opts.noComplain):
                self.addLocalConfig(self.opts.cloneCase)
            orig=SolutionDirectory(self.opts.cloneCase,
                                   archive=None,paraviewLink=False)
            sol=orig.cloneCase(cName)
        else:
            if self.checkCase(cName,
                              fatal=self.opts.fatal,
                              verbose=not self.opts.noComplain):
                self.addLocalConfig(cName)
            sol=SolutionDirectory(cName,archive=None,paraviewLink=False)
        try:
            self.__lastMessage=None
            self.prepare(sol,cName=cName)
        except:
            if self.__lastMessage:
                self.__writeToStateFile(sol,self.__lastMessage+" failed")
            raise

    def __strip(self,val):
        """Strip extra " from strings"""
        if isinstance(val,(str,)):
            if len(val)>2:
                if val[0]=='"' and val[-1]=='"':
                    return val[1:-1]
        return val

    def processDefault(self,raw):
        """Process a dictionary and return a 'flattened' dictionary with the
        values and a dictionary with the meta-data"""
        values=OrderedDict()
        meta=OrderedDict()
        meta[""]={}

        for k,v in iteritems(raw):
            isNormal=True

            if isinstance(v,(DictProxy,dict)):
                if "description" in v:
                    if "default" in v:
                        if "values" in v:
                            self.warning(k+" has also a 'values'-entry. Might be a subgroup")
                        vMeta={}
                        for a in v:
                            if a=="description":
                                vMeta[a]=self.__strip(v[a])
                            else:
                                vMeta[a]=v[a]
                        meta[""][k]=vMeta
                    elif "values" in v:
                        isNormal=False

            if isNormal:
                if k in values:
                    self.error(k,"defined twice in defaults")
                if not k in meta[""]:
                    meta[""][k]={"default":v}
                    values[k]=v
                else:
                    values[k]=meta[""][k]["default"]
            else:
                pVal,pMeta=self.processDefault(v["values"])
                meta[k]=(self.__strip(v["description"]),pMeta)
                for a in pVal:
                    if a in values:
                        self.error(a,"already defined in sub-directory")
                    else:
                        values[a]=pVal[a]

        return values,meta

    def getDefaultValues(self,cName):
        """Process the file with the default values - if present
        Returns a dictionary with the values and a dictionary with the meta-data
        about the parameters"""
        defFile=path.join(path.abspath(cName),self.defaultParameterFile)
        if self.opts.useDefaultParameterFile and path.exists(defFile):
            self.info("Using default values from",defFile)
            return self.processDefault(
                ParsedParameterFile(defFile,
                                    noHeader=True,
                                    doMacroExpansion=True).getValueDict())
        else:
            return {},{}

    def addDictValues(self,name,description,values):
        """Add values from a dictionary"""
        meta=dict([(k,{"default":v}) for k,v in iteritems(values)])
        self.metaData[name]=(description,{"":meta})
        return values

    def makeReport(self,values,level=2,meta=None):
        if meta is None:
            meta=self.metaData
        helper=RestructuredTextHelper(defaultHeading=level)
        val=""

        for k in meta:
            if k=="":
                if len(meta[k])==0:
                    continue
                tab=helper.table(labeled=True)
                for kk in meta[k]:
                    if "default" in meta[k][kk] and values[kk]!=meta[k][kk]["default"]:
                        changed=True
                        tab.addRow(helper.strong(kk))
                    else:
                        changed=False
                        tab.addRow(kk)
                    for a,v in iteritems(meta[k][kk]):
                        tab.addItem(a,v)
                    if changed:
                        tab.addItem("Value",helper.strong(values[kk]))
                    else:
                        tab.addItem("Value",values[kk])
                val+=str(tab)
            else:
                descr,newMeta=meta[k]
                val+=helper.heading(descr)
                val+="\nShort name: "+helper.literal(k)+"\n"
                val+=self.makeReport(values,
                                     level=level+1,
                                     meta=newMeta)
        return val

    def checkCorrectOptions(self,values,meta=None):
        if meta is None:
            meta=self.metaData

        for k in meta:
            if k=="":
                for kk in meta[k]:
                    if "options" in meta[k][kk] and values[kk] not in meta[k][kk]["options"]:
                        if self.opts.failOnWrongOption:
                            func=self.error
                        else:
                            func=self.warning

                        func("Value",values[kk],"for parameter",kk,
                             "not in list of allowed options:",
                             ", ".join([str(v) for v in meta[k][kk]["options"]]))
            else:
                self.checkCorrectOptions(values,meta[k][1])

    def executeScript(self,scriptName,workdir,echo):
        """Execute a script and write a corresponding logfile"""

        ret,txt=execute([scriptName],
                        workdir=workdir,
                        echo=echo,
                        getReturnCode=True)

        result="".join(txt)
        open(scriptName+".log","w").write(result)

        if ret not in [0,None]:
            self.info(scriptName,"failed with code",ret)
            if self.opts.failOnScriptFailure:
                self.error("Script",scriptName,"failed with code",ret)

    def __writeToStateFile(self,sol,message):
        """Write a message to a state file"""
        self.__lastMessage=message
        open(path.join(sol.name,"PyFoamState.TheState"),"w").write("Prepare: "+message+"\n")

    def prepare(self,sol,
                cName=None,
                overrideParameters=None,
                numberOfProcessors=None):
        """Do the actual preparing
        :param numberOfProcessors: If set this overrides the value set in the
        command line"""

        if cName==None:
            cName=sol.name

        if self.opts.onlyVariables:
            self.opts.verbose=True

        vals={}
        vals,self.metaData=self.getDefaultValues(cName)
        vals.update(self.addDictValues("System",
                                       "Automatically defined values",
                                       {
                                           "casePath" : '"'+path.abspath(cName)+'"',
                                           "caseName" : '"'+path.basename(path.abspath(cName))+'"',
                                           "foamVersion" : foamVersion(),
                                           "foamFork" : foamFork(),
                                           "numberOfProcessors" : numberOfProcessors if numberOfProcessors!=None else self.opts.numberOfProcessors
                                       }))

        if len(self.opts.extensionAddition)>0:
            vals.update(self.addDictValues("ExtensionAdditions",
                                           "Additional extensions to be processed",
                                           dict((e,True) for e in self.opts.extensionAddition)))

        valsWithDefaults=set(vals.keys())

        self.info("Looking for template values",cName)
        for f in self.opts.valuesDicts:
            self.info("Reading values from",f)
            vals.update(ParsedParameterFile(f,
                                            noHeader=True,
                                            doMacroExpansion=True).getValueDict())

        setValues={}
        for v in self.opts.values:
            self.info("Updating values",v)
            vals.update(eval(v))
            setValues.update(eval(v))

        if overrideParameters:
            vals.update(overrideParameters)

        unknownValues=set(vals.keys())-valsWithDefaults
        if len(unknownValues)>0:
            self.warning("Values for which no default was specified: "+
                         ", ".join(unknownValues))

        if self.opts.verbose and len(vals)>0:
            print_("\nUsed values\n")
            nameLen=max(len("Name"),
                        max(*[len(k) for k in vals.keys()]))
            format="%%%ds - %%s" % nameLen
            print_(format % ("Name","Value"))
            print_("-"*40)
            for k,v in sorted(iteritems(vals)):
                print_(format % (k,v))
            print_("")
        else:
            self.info("\nNo values specified\n")

        self.checkCorrectOptions(vals)

        derivedScript=path.join(cName,self.opts.derivedParametersScript)
        derivedAdded=None
        derivedChanged=None
        if path.exists(derivedScript):
            self.info("Deriving variables in script",derivedScript)
            scriptText=open(derivedScript).read()
            glob={}
            oldVals=vals.copy()
            exec_(scriptText,glob,vals)
            derivedAdded=[]
            derivedChanged=[]
            for k,v in iteritems(vals):
                if k not in oldVals:
                    derivedAdded.append(k)
                elif vals[k]!=oldVals[k]:
                    derivedChanged.append(k)
            if len(derivedChanged)>0 and (not self.opts.allowDerivedChanges and not configuration().getboolean("PrepareCase","AllowDerivedChanges")):
                self.error(self.opts.derivedParametersScript,
                           "changed values of"," ".join(derivedChanged),
                           "\nTo allow this set --allow-derived-changes or the configuration item 'AllowDerivedChanges'")
            if len(derivedAdded)>0:
                self.info("Added values:"," ".join(derivedAdded))
            if len(derivedChanged)>0:
                self.info("Changed values:"," ".join(derivedChanged))
            if len(derivedAdded)==0 and len(derivedChanged)==0:
                self.info("Nothing added or changed")
        else:
            self.info("No script",derivedScript,"for derived values")

        if self.opts.onlyVariables:
            return

        self.__writeToStateFile(sol,"Starting")

        if self.opts.doClear:
            self.info("Clearing",cName)
            self.__writeToStateFile(sol,"Clearing")
            sol.clear(processor=True,
                      pyfoam=True,
                      vtk=True,
                      removeAnalyzed=True,
                      keepParallel=False,
                      clearHistory=False,
                      clearParameters=True,
                      additional=["postProcessing"])
            self.__writeToStateFile(sol,"Done clearing")

        if self.opts.writeParameters:
            fName=path.join(cName,self.parameterOutFile)
            self.info("Writing parameters to",fName)
            with WriteParameterFile(fName,noHeader=True) as w:
                w.content.update(vals,toString=True)
                w["foamVersion"]=vals["foamVersion"]
                w.writeFile()

        if self.opts.writeReport:
            fName=path.join(cName,self.parameterOutFile+".rst")
            self.info("Writing report to",fName)
            with open(fName,"w") as w:
                helper=RestructuredTextHelper(defaultHeading=1)
                w.write(".. title:: "+self.__strip(vals["caseName"])+"\n")
                w.write(".. sectnum::\n")
                w.write(".. header:: "+self.__strip(vals["caseName"])+"\n")
                w.write(".. header:: "+time.asctime()+"\n")
                w.write(".. footer:: ###Page### / ###Total###\n\n")

                w.write("Parameters set in case directory "+
                        helper.literal(self.__strip(vals["casePath"]))+" at "+
                        helper.emphasis(time.asctime())+"\n\n")
                w.write(".. contents::\n\n")
                if len(self.opts.valuesDicts):
                    w.write(helper.heading("Parameter files"))
                    w.write("Parameters read from files\n\n")
                    w.write(helper.enumerateList([helper.literal(f) for f in self.opts.valuesDicts]))
                    w.write("\n")
                if len(setValues)>0:
                    w.write(helper.heading("Overwritten parameters"))
                    w.write("These parameters were set from the command line\n\n")
                    w.write(helper.definitionList(setValues))
                    w.write("\n")
                w.write(helper.heading("Parameters with defaults"))
                w.write(self.makeReport(vals))
                if len(unknownValues)>0:
                    w.write(helper.heading("Unspecified parameters"))
                    w.write("If these parameters are actually used then specify them in "+
                            helper.literal(self.defaultParameterFile)+"\n\n")
                    tab=helper.table(True)
                    for u in unknownValues:
                        tab.addRow(u)
                        tab.addItem("Value",vals[u])
                    w.write(str(tab))
                if not derivedAdded is None:
                    w.write(helper.heading("Derived Variables"))
                    w.write("Script with derived Parameters"+
                            helper.literal(derivedScript)+"\n\n")
                    if len(derivedAdded)>0:
                        w.write("These values were added:\n")
                        tab=helper.table(True)
                        for a in derivedAdded:
                            tab.addRow(a)
                            tab.addItem("Value",str(vals[a]))
                        w.write(str(tab))
                    if len(derivedChanged)>0:
                        w.write("These values were changed:\n")
                        tab=helper.table(True)
                        for a in derivedChanged:
                            tab.addRow(a)
                            tab.addItem("Value",str(vals[a]))
                            tab.addItem("Old",str(oldVals[a]))
                        w.write(str(tab))
                    w.write("The code of the script:\n")
                    w.write(helper.code(scriptText))

        self.addToCaseLog(cName)

        for over in self.opts.overloadDirs:
            self.info("Overloading files from",over)
            self.__writeToStateFile(sol,"Overloading")
            self.overloadDir(sol.name,over)

        self.__writeToStateFile(sol,"Initial")

        zeroOrig=path.join(sol.name,"0.org")

        hasOrig=path.exists(zeroOrig)
        cleanZero=True

        if not hasOrig:
            self.info("Not going to clean '0'")
            self.opts.cleanDirectories.remove("0")
            cleanZero=False

        if self.opts.doCopy:
            if hasOrig:
                self.info("Found 0.org. Clearing 0")
                zeroDir=path.join(sol.name,"0")
                if path.exists(zeroDir):
                    rmtree(zeroDir)
                else:
                    self.info("No 0-directory")

            self.info("")
        else:
            cleanZero=False

        if self.opts.doTemplates:
            self.__writeToStateFile(sol,"Templates")
            self.searchAndReplaceTemplates(sol.name,
                                           vals,
                                           self.opts.templateExt,
                                           ignoreDirectories=self.opts.ignoreDirectories)

            self.info("")

        backupZeroDir=None

        if self.opts.doMeshCreate:
            self.__writeToStateFile(sol,"Meshing")
            if self.opts.meshCreateScript:
                scriptName=path.join(sol.name,self.opts.meshCreateScript)
                if not path.exists(scriptName):
                    self.error("Script",scriptName,"does not exist")
            elif path.exists(path.join(sol.name,self.defaultMeshCreate)):
                scriptName=path.join(sol.name,self.defaultMeshCreate)
            else:
                scriptName=None

            if scriptName:
                self.info("Executing",scriptName,"for mesh creation")
                if self.opts.verbose:
                    echo="Mesh: "
                else:
                    echo=None
                self.executeScript(scriptName,workdir=sol.name,echo=echo)
            else:
                self.info("No script for mesh creation found. Looking for 'blockMeshDict'")
                if sol.blockMesh()!="":
                    self.info(sol.blockMesh(),"found. Executing 'blockMesh'")
                    bm=BasicRunner(argv=["blockMesh","-case",sol.name])
                    bm.start()
                    if not bm.runOK():
                        self.error("Problem with blockMesh")
                for r in sol.regions():
                    self.info("Checking region",r)
                    s=SolutionDirectory(sol.name,region=r,
                                        archive=None,paraviewLink=False)
                    if s.blockMesh()!="":
                        self.info(s.blockMesh(),"found. Executing 'blockMesh'")
                        bm=BasicRunner(argv=["blockMesh","-case",sol.name,
                                             "-region",r])
                        bm.start()
                        if not bm.runOK():
                            self.error("Problem with blockMesh")

            self.info("")

            if cleanZero and path.exists(zeroDir):
                self.warning("Mesh creation recreated 0-directory")
                if self.opts.keepZeroDirectoryFromMesh:
                    backupZeroDir=zeroDir+".bakByPyFoam"
                    self.info("Backing up",zeroDir,"to",backupZeroDir)
                    move(zeroDir,backupZeroDir)
                else:
                    self.info("Data in",zeroDir,"will be removed")
            self.__writeToStateFile(sol,"Done Meshing")

        if self.opts.doCopy:
            self.__writeToStateFile(sol,"Copying")
            self.copyOriginals(sol.name)

            self.info("")

            if backupZeroDir:
                self.info("Copying backups from",backupZeroDir,"to",zeroDir)
                self.overloadDir(zeroDir,backupZeroDir)
                self.info("Removing backup",backupZeroDir)
                rmtree(backupZeroDir)

        if self.opts.doPostTemplates:
            self.__writeToStateFile(sol,"Post-templates")
            self.searchAndReplaceTemplates(sol.name,
                                           vals,
                                           self.opts.postTemplateExt,
                                           ignoreDirectories=self.opts.ignoreDirectories)

            self.info("")

        if self.opts.doCaseSetup:
            self.__writeToStateFile(sol,"Case setup")
            if self.opts.caseSetupScript:
                scriptName=path.join(sol.name,self.opts.caseSetupScript)
                if not path.exists(scriptName):
                    self.error("Script",scriptName,"does not exist")
            elif path.exists(path.join(sol.name,self.defaultCaseSetup)):
                scriptName=path.join(sol.name,self.defaultCaseSetup)
            else:
                scriptName=None

            if scriptName:
                self.info("Executing",scriptName,"for case setup")
                if self.opts.verbose:
                    echo="Case:"
                else:
                    echo=None
                self.executeScript(scriptName,workdir=sol.name,echo=echo)
            elif path.exists(path.join(sol.name,"system","setFieldsDict")):
                self.info("So setup script found. But 'setFieldsDict'. Executing setFields")
                sf=BasicRunner(argv=["setFields","-case",sol.name])
                sf.start()
                if not sf.runOK():
                    self.error("Problem with setFields")
            else:
                self.info("No script for case-setup found. Nothing done")
            self.info("")
            self.__writeToStateFile(sol,"Done case setup")

        if self.opts.doFinalTemplates:
            self.__writeToStateFile(sol,"Final templates")
            self.searchAndReplaceTemplates(sol.name,
                                           vals,
                                           self.opts.finalTemplateExt,
                                           ignoreDirectories=self.opts.ignoreDirectories)

        if self.opts.doTemplateClean:
            self.info("Clearing templates")
            for d in self.opts.cleanDirectories:
                for e in [self.opts.templateExt,
                          self.opts.postTemplateExt,
                          self.opts.finalTemplateExt]:
                    self.cleanExtension(path.join(sol.name,d),e)
            self.info("")

        self.info("Case setup finished")
        self.__writeToStateFile(sol,"Finished OK")

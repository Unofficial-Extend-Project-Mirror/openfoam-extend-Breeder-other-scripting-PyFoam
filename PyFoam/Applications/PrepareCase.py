"""
Application-class that implements pyFoamPrepareCase.py
"""
from optparse import OptionGroup

from .PyFoamApplication import PyFoamApplication

from PyFoam.RunDictionary.SolutionDirectory import SolutionDirectory
from PyFoam.Basics.Utilities import rmtree,copytree,execute,remove
from PyFoam.RunDictionary.ParsedParameterFile import ParsedParameterFile,WriteParameterFile
from PyFoam.Basics.TemplateFile import TemplateFile
from PyFoam.Execution.BasicRunner import BasicRunner

from PyFoam.FoamInformation import foamFork,foamVersion

from .CommonTemplateFormat import CommonTemplateFormat
from .CommonTemplateBehaviour import CommonTemplateBehaviour

from PyFoam.ThirdParty.six import print_,iteritems

from PyFoam import configuration

from os import path,listdir,mkdir
from shutil import copymode,copy

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

  7. execute another preparation script

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
        extensions.add_option("--original-extension",
                              action="store",
                              dest="originalExt",
                              default=".org",
                              help="Extension for files and directories that are copied. Default: %default")

        inputs=OptionGroup(self.parser,
                           "Inputs",
                           "Inputs for the templating process")
        self.parser.add_option_group(inputs)

        inputs.add_option("--parameter-file",
                          action="append",
                          default=[],
                          dest="valuesDicts",
                          help="Name of a dictionary-file in OpenFOAM-format. Can be specified more than once. Values in later files override old values")
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
        scripts.add_option("--case-setup-script",
                          action="store",
                          dest="caseSetupScript",
                          default=None,
                          help="Script that is executed after the original files have been copied to set initial conditions or similar. If not specified then the utility looks for "+self.defaultCaseSetup+" and executes this.")

    def copyOriginals(self,startDir):
        """Go recursivly through directories and copy foo.org to foo"""
        if self.opts.verbose:
            print_("Looking for originals in",startDir)
        for f in listdir(startDir):
            if f[0]==".":
                if self.opts.verbose:
                    print_("Skipping",f)
                continue
            src=path.join(startDir,f)
            if path.splitext(f)[1]==self.opts.originalExt:
                dst=path.join(startDir,path.splitext(f)[0])
                if path.exists(dst):
                    if self.opts.verbose:
                        print_("Replacing",dst,"with",src)
                    rmtree(dst)
                else:
                    if self.opts.verbose:
                        print_("Copying",src,"to",dst)
                copytree(src,dst,force=True)
            elif path.isdir(src):
                self.copyOriginals(src)

    def cleanExtension(self,
                       startDir,
                       ext):
        """Go recursivly through directories and remove all files that have a specific extension"""
        if self.opts.verbose:
            print_("Looking for extension",ext,"in",startDir)
        for f in listdir(startDir):
            if f[0]==".":
                if self.opts.verbose:
                    print_("Skipping",f)
                continue
            src=path.join(startDir,f)
            if path.splitext(f)[1]==ext and not path.isdir(src):
                if self.opts.verbose:
                    print_("Removing",src)
                remove(src)
            elif path.isdir(src):
                self.cleanExtension(src,ext)

    def searchAndReplaceTemplates(self,
                                  startDir,
                                  values,
                                  templateExt):
        """Go through the directory recursively and replate foo.template with
        foo after inserting the values"""
        if self.opts.verbose:
            print_("Looking for templates with extension",templateExt,"in ",startDir)
        for f in listdir(startDir):
            if f[0]==".":
                if self.opts.verbose:
                    print_("Skipping",f)
                continue
            if path.isdir(path.join(startDir,f)):
                self.searchAndReplaceTemplates(
                    path.join(startDir,f),
                    values,
                    templateExt)
            elif path.splitext(f)[1]==templateExt:
                fName=path.join(startDir,path.splitext(f)[0])
                if self.opts.verbose:
                    print_("Found template for",fName)
                t=TemplateFile(name=fName+templateExt,
                               tolerantRender=self.opts.tolerantRender,
                               allowExec=self.opts.allowExec,
                               expressionDelimiter=self.opts.expressionDelimiter,
                               assignmentDebug=self.pickAssignmentDebug(fName),
                               assignmentLineStart=self.opts.assignmentLineStart)
                t.writeToFile(fName,values)
                copymode(fName+templateExt,fName)

    def overloadDir(self,here,there):
        """Copy files recursively. Overwrite local copies if they exist"""
        for f in listdir(there):
            fSrc=path.join(there,f)
            fDst=path.join(here,f)
            if path.isdir(fSrc):
                if not path.exists(fDst):
                    if self.opts.verbose:
                        print_("Creating directory",fDst)
                    mkdir(fDst)
                elif not path.isdir(fDst):
                    self.error("Destination path",fDst,"exists, but is no directory")
                self.overloadDir(fDst,fSrc)
            elif path.isfile(fSrc):
                if path.exists(fDst):
                    if not path.isfile(fDst):
                        self.error("Desination",fDst,"exists but is no file")
                if self.opts.verbose:
                    print_("Copying",fSrc,"to",fDst)
                copy(fSrc,fDst)
            else:
                self.errr("Source file",fSrc,"is neither file nor directory")

    def run(self):
        cName=self.parser.getArgs()[0]
        if self.checkCase(cName,fatal=self.opts.fatal,verbose=not self.opts.noComplain):
            self.addLocalConfig(cName)
        sol=SolutionDirectory(cName,archive=None,paraviewLink=False)
        self.prepare(sol,cName=cName)

    def prepare(self,sol,cName=None,overrideParameters=None):
        if cName==None:
            cName=sol.name

        if self.opts.onlyVariables:
            self.opts.verbose=True

        vals={}
        vals["casePath"]='"'+path.abspath(cName)+'"'
        vals["caseName"]='"'+path.basename(path.abspath(cName))+'"'
        vals["foamVersion"]=foamVersion()
        vals["foamFork"]=foamFork()

        if self.opts.verbose:
            print_("Looking for template values",cName)
        for f in self.opts.valuesDicts:
            if self.opts.verbose:
                print_("Reading values from",f)
            vals.update(ParsedParameterFile(f,
                                            noHeader=True,
                                            doMacroExpansion=True).getValueDict())
        for v in self.opts.values:
            if self.opts.verbose:
                print_("Updating values",v)
            vals.update(eval(v))

        if overrideParameters:
            vals.update(overrideParameters)

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
        elif self.opts.verbose:
            print_("\nNo values specified\n")

        if self.opts.onlyVariables:
            return

        if self.opts.doClear:
            if self.opts.verbose:
                print_("Clearing",cName)
            sol.clear(processor=True,
                      pyfoam=True,
                      vtk=True,
                      removeAnalyzed=True,
                      keepParallel=False,
                      clearHistory=False,
                      clearParameters=True,
                      additional=["postProcessing"])

        if self.opts.writeParameters:
            fName=path.join(cName,self.parameterOutFile)
            if self.opts.verbose:
                print_("Writing parameters to",fName)
            with WriteParameterFile(fName,noHeader=True) as w:
                w.content.update(vals,toString=True)
                w["foamVersion"]=vals["foamVersion"]
                w.writeFile()

        self.addToCaseLog(cName)

        for over in self.opts.overloadDirs:
            if self.opts.verbose:
                print_("Overloading files from",over)
                self.overloadDir(sol.name,over)

        zeroOrig=path.join(sol.name,"0.org")

        hasOrig=path.exists(zeroOrig)
        if not hasOrig:
            if self.opts.verbose:
                print_("Not going to clean '0'")
            self.opts.cleanDirectories.remove("0")

        if self.opts.doCopy:
            if hasOrig:
                if self.opts.verbose:
                    print_("Found 0.org. Clearing 0")
                zeroDir=path.join(sol.name,"0")
                if path.exists(zeroDir):
                    rmtree(zeroDir)
                elif self.opts.verbose:
                    print_("No 0-directory")

            if self.opts.verbose:
                print_("")

        if self.opts.doTemplates:
            self.searchAndReplaceTemplates(sol.name,
                                           vals,
                                           self.opts.templateExt)

            if self.opts.verbose:
                print_("")

        if self.opts.doMeshCreate:
            if self.opts.meshCreateScript:
                scriptName=path.join(sol.name,self.opts.meshCreateScript)
                if not path.exists(scriptName):
                    self.error("Script",scriptName,"does not exist")
            elif path.exists(path.join(sol.name,self.defaultMeshCreate)):
                scriptName=path.join(sol.name,self.defaultMeshCreate)
            else:
                scriptName=None

            if scriptName:
                if self.opts.verbose:
                    print_("Executing",scriptName,"for mesh creation")
                if self.opts.verbose:
                    echo="Mesh: "
                else:
                    echo=None
                result="".join(execute([scriptName],workdir=sol.name,echo=echo))
                open(scriptName+".log","w").write(result)
            else:
                if self.opts.verbose:
                    print_("No script for mesh creation found. Looking for 'blockMeshDict'")
                if sol.blockMesh()!="":
                    if self.opts.verbose:
                        print_(sol.blockMesh(),"found. Executing 'blockMesh'")
                    bm=BasicRunner(argv=["blockMesh","-case",sol.name])
                    bm.start()
                    if not bm.runOK():
                        self.error("Problem with blockMesh")
            if self.opts.verbose:
                print_("")

        if self.opts.doCopy:
            self.copyOriginals(sol.name)

            if self.opts.verbose:
                print_("")

        if self.opts.doPostTemplates:
            self.searchAndReplaceTemplates(sol.name,
                                           vals,
                                           self.opts.postTemplateExt)

            if self.opts.verbose:
                print_("")

        if self.opts.doCaseSetup:
            if self.opts.caseSetupScript:
                scriptName=path.join(sol.name,self.opts.caseSetupScript)
                if not path.exists(scriptName):
                    self.error("Script",scriptName,"does not exist")
            elif path.exists(path.join(sol.name,self.defaultCaseSetup)):
                scriptName=path.join(sol.name,self.defaultCaseSetup)
            else:
                scriptName=None

            if scriptName:
                if self.opts.verbose:
                    print_("Executing",scriptName,"for case setup")
                if self.opts.verbose:
                    echo="Case:"
                else:
                    echo=None
                result="".join(execute([scriptName],workdir=sol.name,echo=echo))
                open(scriptName+".log","w").write(result)
            else:
                if self.opts.verbose:
                    print_("No script for case-setup found. Nothing done")
            if self.opts.verbose:
                print_("")

        if self.opts.doTemplateClean:
            if self.opts.verbose:
                print_("Clearing templates")
            for d in self.opts.cleanDirectories:
                for e in [self.opts.templateExt,self.opts.postTemplateExt]:
                    self.cleanExtension(path.join(sol.name,d),e)
            if self.opts.verbose:
                print_("")

        if self.opts.verbose:
            print_("Case setup finished")
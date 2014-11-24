#  ICE Revision: $Id$
"""
Class that implements pyFoamPVSnapshot
"""

from optparse import OptionGroup

from PyFoamApplication import PyFoamApplication

from CommonSelectTimesteps import CommonSelectTimesteps

from PyFoam.RunDictionary.SolutionDirectory import SolutionDirectory
from PyFoam.Paraview.ServermanagerWrapper import ServermanagerWrapper as SM
from PyFoam.Paraview.StateFile import StateFile
from PyFoam.Paraview import version as PVVersion

from PyFoam.FoamInformation import foamVersion

from os import path,unlink
import sys,string

class PVSnapshot(PyFoamApplication,
                 CommonSelectTimesteps ):
    def __init__(self,
                 args=None,
                 **kwargs):
        description="""\
Generates snapshots of an OpenFOAM-case and a predefined
paraview-State-File using the PV3FoamReader that comes with OpenFOAM.

The state-file can be generated using a different case (the script
adjusts it before using) but the original case has to have a similar
structure to the current one. Also exactly one PV3Reader has to be
used in the state-file (this requirement is fullfilled if the
StateFile was generated using paraFoam)

In TextSources the string "%(casename)s" gets replaced by the
casename. Additional replacements can be specified
"""
        CommonSelectTimesteps.__init__(self)

        PyFoamApplication.__init__(self,
                                   args=args,
                                   description=description,
                                   usage="%prog [options] <case>",
                                   interspersed=True,
                                   nr=1,
                                   **kwargs)

    picTypeTable={"png"  :  "vtkPNGWriter",
                  "jpg"  :  "vtkJPEGWriter"}

    geomTypeTable={"x3d"   : "X3DExporter",
                   "x3db"  : "X3DExporterBinary",
                   "vrml"  : "VRMLExporter",
                   "wgl"   : "WebGLExporter",
                   "pov"   : "POVExporter"}

    def addOptions(self):
        CommonSelectTimesteps.addOptions(self,defaultUnique=False)

        paraview=OptionGroup(self.parser,
                           "Paraview specifications",
                           "Options concerning paraview")
        paraview.add_option("--state-file",
                            dest="state",
                            default=None,
                            help="The pvsm-file that should be used. If none is specified the file 'default.pvsm' in the case-directory is used")
        paraview.add_option("--maginfication",
                            dest="magnification",
                            default=1,
                            type="int",
                            help="Magnification factor of the picture (integer). Default: %default")
        paraview.add_option("--type",
                            dest="picType",
                            type="choice",
                            choices=self.picTypeTable.keys(),
                            default="png",
                            help="The type of the bitmap-file. Possibilities are "+", ".join(self.picTypeTable.keys())+". Default: %default")
        paraview.add_option("--no-progress",
                            dest="progress",
                            action="store_false",
                            default=True,
                            help="Paraview will not print the progress of the filters")
        paraview.add_option("--no-offscreen-rendering",
                            dest="offscreenRender",
                            action="store_false",
                            default=True,
                            help="Do not do offscreen rendering (use if offscreen rendering produces a segmentation fault)")
        self.parser.add_option_group(paraview)

        geometry=OptionGroup(self.parser,
                             "Geometry specification",
                             "Options for writing out geometry files")
        geometry.add_option("--geometry-type",
                            dest="geomType",
                            type="choice",
                            choices=self.geomTypeTable.keys(),
                            default=None,
                            help="The type of the geometry-files. Possibilities are "+", ".join(self.geomTypeTable.keys())+". Default: unset. Nothing is written")
        geometry.add_option("--no-picture-with-geometry",
                            dest="pictureWithGeometry",
                            action="store_false",
                            default=True,
                            help="Do not write a picture if geometries are written. Default is that pictures are written as well")
        geometry.add_option("--get-sources-list",
                            dest="sourcesList",
                            action="store_true",
                            default=False,
                            help="Get a list of all the sources. Nothing is written")
        geometry.add_option("--sources",
                           dest="sources",
                           default=[],
                           action="append",
                           help="Only write sources where the name matches this substring. Can be specified more than once (will write more than one file)")
        self.parser.add_option_group(geometry)

        filename=OptionGroup(self.parser,
                             "Filename specifications",
                             "The names of the resulting files")
        filename.add_option("--file-prefix",
                            dest="prefix",
                            default="Snapshot",
                            help="Start of the filename for the bitmap-files")
        filename.add_option("--no-casename",
                            dest="casename",
                            action="store_false",
                            default=True,
                            help="Do not add the casename to the filename")
        filename.add_option("--no-timename",
                          dest="timename",
                          action="store_false",
                          default=True,
                          help="Do not append the string 't=<time>' to the filename")
        self.parser.add_option_group(filename)

        replace=OptionGroup(self.parser,
                            "Replacements etc",
                            "Manipuations of the statefile")
        replace.add_option("--replacements",
                            dest="replacements",
                            default="{}",
                            help="Dictionary with replacement strings. Default: %default")
        replace.add_option("--casename-key",
                            dest="casenameKey",
                            default="casename",
                            help="Key with which the caename should be replaced. Default: %default")
        self.parser.add_option_group(replace)

        behaviour=OptionGroup(self.parser,
                            "Behaviour",
                            "General behaviour of the utility")
        behaviour.add_option("--verbose",
                            dest="verbose",
                            action="store_true",
                            default=False,
                            help="Print more information")
        self.parser.add_option_group(behaviour)

    def say(self,*stuff):
        if not self.opts.verbose:
            return
        print "Say:",
        for s in stuff:
            print s,
        print

    def run(self):
        doPic=True
        doGeom=False
        doSources=False
        if self.opts.geomType:
             if PVVersion()<(3,9):
                  self.error("This paraview version does not support geometry writing")
             doGeom=True
             doPic=self.opts.pictureWithGeometry
             if len(self.opts.sources)==0:
                 self.opts.sources=[""] # add empty string as token
        if self.opts.sourcesList:
             doPic=False
             doGeom=False
             doSources=True

        self.say("Paraview version",PVVersion(),"FoamVersion",foamVersion())
        if PVVersion()>=(3,6):
            self.warning("This is experimental because the API in Paraview>=3.6 has changed. But we'll try")

        case=path.abspath(self.parser.getArgs()[0])
        short=path.basename(case)

        if self.opts.state==None:
            self.opts.state=path.join(case,"default.pvsm")

        if not path.exists(self.opts.state):
            self.error("The state file",self.opts.state,"does not exist")

        timeString=""

        if self.opts.casename:
            timeString+="_"+short
        timeString+="_%(nr)05d"
        if self.opts.timename:
            timeString+="_t=%(t)s"

        sol=SolutionDirectory(case,
                              paraviewLink=False,
                              archive=None)

        times=self.processTimestepOptions(sol)
        if len(times)<1:
            self.warning("Can't continue without time-steps")
            return

        dataFile=path.join(case,short+".OpenFOAM")
        createdDataFile=False
        if not path.exists(dataFile):
            self.say("Creating",dataFile)
            createdDataFile=True
            f=open(dataFile,"w")
            f.close()

        self.say("Opening state file",self.opts.state)
        sf=StateFile(self.opts.state)
        self.say("Setting data to",dataFile)
        sf.setCase(dataFile)

        values=eval(self.opts.replacements)
        values[self.opts.casenameKey]=short
        sf.rewriteTexts(values)
        newState=sf.writeTemp()

        self.say("Setting session manager with reader type",sf.readerType())
        sm=SM(requiredReader=sf.readerType())
        exporterType=None
        if doGeom:
             self.say("Getting geometry exporter",self.geomTypeTable[self.opts.geomType])
             exporters=sm.createModule("exporters")
             exporterType=getattr(exporters,self.geomTypeTable[self.opts.geomType])

        # make sure that the first snapshot is rendered correctly
        import paraview.simple
        paraview.simple._DisableFirstRenderCameraReset()

        if not self.opts.progress:
            self.say("Toggling progress")
            sm.ToggleProgressPrinting()

        self.say("Loading state")
        sm.LoadState(newState)
        self.say("Getting Views")
        views=sm.GetRenderViews()

        if len(views)>1:
            self.warning("More than 1 view in state-file. Generating multiple series")
            timeString="_View%(view)02d"+timeString
        timeString=self.opts.prefix+timeString

        self.say("Setting Offscreen rendering")
        offWarn=True
        for view in views:
            if self.opts.offscreenRender:
                view.UseOffscreenRenderingForScreenshots=True
                if offWarn:
                    self.warning("Trying offscreen rendering. If writing the file fails with a segmentation fault try --no-offscreen-rendering")
            elif offWarn:
                self.warning("No offscreen rendering. Camera perspective will probably be wrong")
            offWarn=False

        allSources=None
        alwaysSources=None

        self.say("Starting times",times)
        for i,t in enumerate(times):
            self.say("Nr",i,"time",t)
            print "Snapshot ",i," for t=",t,
            sys.stdout.flush()
            self.say()
            for j,view in enumerate(views):
                if len(views)>0:
                    print "View %d" % j,
                    sys.stdout.flush()
                    self.say()
                view.ViewTime=float(t)
                if doPic:
                     print self.opts.picType,
                     sys.stdout.flush()

                     fn = (timeString % {'nr':i,'t':t,'view':j})+"."+self.opts.picType
                     if PVVersion()<(3,6):
                         self.say("Old Paraview writing")
                         view.WriteImage(fn,
                                         self.picTypeTable[self.opts.picType],
                                         self.opts.magnification)
                     else:
                         self.say("New Paraview writing")
                         from paraview.simple import SetActiveView,Render,WriteImage
                         self.say("Setting view")
                         SetActiveView(view)
                         self.say("Rendering")
                         Render()
                         self.say("Writing image",fn,"type",self.picTypeTable[self.opts.picType])
                         # This may produce a segmentation fault with offscreen rendering
                         WriteImage(fn,
                                    view,
     #                               Writer=self.picTypeTable[self.opts.picType],
                                    Magnification=self.opts.magnification)
                         self.say("Finished writing")
                if doGeom:
                     from paraview.simple import Show,Hide,GetSources

                     print self.opts.geomType,
                     sys.stdout.flush()
                     for select in self.opts.sources:
                         fn = (timeString % {'nr':i,'t':t,'view':j})
                         if select!="":
                             print "*"+select+"*",
                             sys.stdout.flush()
                             fn+="_"+select
                             sources=GetSources()
                             for n,s in sources.iteritems():
                                 if n[0].find(select)>=0:
                                     Show(s,view)
                                 else:
                                     Hide(s,view)
                         fn += "."+self.opts.geomType
                         self.say("Creating exporter for file",fn)
                         ex=exporterType(FileName=fn)
                         ex.SetView(view)
                         ex.Write()
                if doSources:
                    from paraview.simple import GetSources
                    srcNames=[]
                    sources=GetSources()
                    for n in sources:
                         srcNames.append(n[0])
                    if allSources==None:
                         allSources=set(srcNames)
                         alwaysSources=set(srcNames)
                    else:
                         allSources|=set(srcNames)
                         alwaysSources&=set(srcNames)
            print

        if doSources:
             print
             print "List of found sources (* means that it is present in all timesteps)"
             for n in allSources:
                  if n in alwaysSources:
                       flag="*"
                  else:
                       flag=" "
                  print "  %s  %s" % (flag,n)

        if createdDataFile:
            self.warning("Removing pseudo-data-file",dataFile)
            unlink(dataFile)

        del sm

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
    def __init__(self,args=None):
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
                                   nr=1)

    typeTable={"png":"vtkPNGWriter",
               "jpg":"vtkJPEGWriter"}

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
                            dest="type",
                            type="choice",
                            choices=self.typeTable.keys(),
                            default="png",
                            help="The type of the bitmap-file. Possibilities are "+string.join(self.typeTable.keys(),", ")+". Default: %default")
        paraview.add_option("--no-progress",
                            dest="progress",
                            action="store_false",
                            default=True,
                            help="Paraview will not print the progress of the filters")
        self.parser.add_option_group(paraview)

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

    def run(self):
        if foamVersion()>=(1,6):
            self.warning("This utilitiy currently does not work with OF>=1.6 because the API in Paraview>=3.6 has changed. But we'll try")

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
        timeString+="."+self.opts.type

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
            createdDataFile=True
            f=open(dataFile,"w")
            f.close()

        sf=StateFile(self.opts.state)
        sf.setCase(dataFile)

        values=eval(self.opts.replacements)
        values[self.opts.casenameKey]=short
        sf.rewriteTexts(values)
        newState=sf.writeTemp()

        sm=SM(requiredReader=sf.readerType())

        # make sure that the first snapshot is rendered correctly
        import paraview.simple
        paraview.simple._DisableFirstRenderCameraReset()

        if not self.opts.progress:
            sm.ToggleProgressPrinting()

        #        print dir(sm.module())
        sm.LoadState(newState)
        views=sm.GetRenderViews()

        if len(views)>1:
            self.warning("More than 1 view in state-file. Generating multiple series")
            timeString="_View%(view)02d"+timeString
        timeString=self.opts.prefix+timeString

        for view in views:
            view.UseOffscreenRenderingForScreenshots=True

        for i,t in enumerate(times):
            print "Snapshot ",i," for t=",t,
            for j,view in enumerate(views):
                if len(views)>0:
                    print "View %d" % j,
                view.ViewTime=float(t)
                fn = timeString % {'nr':i,'t':t,'view':j}
                if PVVersion()<(3,6):
                    view.WriteImage(fn,
                                    self.typeTable[self.opts.type],
                                    self.opts.magnification)
                else:
                    from paraview.simple import SetActiveView,Render,WriteImage
                    SetActiveView(view)
                    Render()
                    # This always produces segmentation fauklts for me
                    WriteImage(fn,
                               view,
#                               Writer=self.typeTable[self.opts.type],
                               Magnification=self.opts.magnification)
            print
        if createdDataFile:
            self.warning("Removing pseudo-data-file",dataFile)
            unlink(dataFile)

        del sm

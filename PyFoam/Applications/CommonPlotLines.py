
"""
Class that implements common functionality for collecting plot-lines
"""

import sys
from os import path
from optparse import OptionGroup

from PyFoam.Error import error,warning
from PyFoam.LogAnalysis.RegExpLineAnalyzer import RegExpLineAnalyzer

from PyFoam.Basics.CustomPlotInfo import readCustomPlotInfo

class CommonPlotLines(object):
    """ This class collects the lines that should be plotted
    """

    def __init__(self):
        self.lines_=[]
        
    def plotLines(self):
        return self.lines_
    
    def addPlotLine(self,line):
        """Add a single line"""
        self.lines_+=readCustomPlotInfo(line)

    def addPlotLines(self,lines):
        """Adds a list of lines"""
        if lines:
            for l in lines:
                self.lines_+=readCustomPlotInfo(l)

    def addFileRegexps(self,fName):
        """Adds the lines from a file to the custom regular expressions
        @param fName: The name of the file"""
        f=open(fName)
        txt=f.read()
        f.close()
        self.lines_+=readCustomPlotInfo(txt)
                
    def addOptions(self):
        grp=OptionGroup(self.parser,
                        "Regular expression",
                        "Where regular expressions for custom plots are found")
        
        grp.add_option("--custom-regexp",
                       action="append",
                       default=None,
                       dest="customRegex",
                       help="Add a custom regular expression to be plotted (can be used more than once)")

        grp.add_option("--regexp-file",
                       action="append",
                       default=None,
                       dest="regexpFile",
                       help="A file with regulare expressions that are treated like the expressions given with --custom-regexp")
        
        grp.add_option("--no-auto-customRegexp",
                       action="store_false",
                       default=True,
                       dest="autoCustom",
                       help="Do not automatically load the expressions from the file customRegexp")

        grp.add_option("--dump-custom-regegexp",
                       action="store_true",
                       default=False,
                       dest="dumpCustomRegexp",
                       help="Dump the used regular expressions in a format suitable to put into a customRegexp-file and finish the program")
        self.parser.add_option_group(grp)
        
        grp2=OptionGroup(self.parser,
                        "Data files",
                        "How data files are written")
        grp2.add_option("--single-data-files-only",
                       action="store_true",
                       default=False,
                       dest="singleDataFilesOnly",
                       help="Don't create consecutive data files 'value', 'value_2', 'value_3' etc but put all the data into a single file")

        self.parser.add_option_group(grp2)

    def processPlotLineOptions(self,autoPath=None):
        """Process the options that have to do with plot-lines"""

        self.addPlotLines(self.opts.customRegex)
        
        if self.opts.regexpFile!=None:
            for f in self.opts.regexpFile:
                print " Reading regular expressions from",f
                self.addFileRegexps(f)

            
        if autoPath!=None and  self.opts.autoCustom:
            autoFile=path.join(autoPath,"customRegexp")
            if path.exists(autoFile):
                print " Reading regular expressions from",autoFile
                self.addFileRegexps(autoFile)

        if self.opts.dumpCustomRegexp:
            print "\nDumping customRegexp:\n"
            for l in self.lines_:
                print l
            sys.exit(-1)
            
        

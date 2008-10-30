"""
Class that implements common functionality for collecting plot-lines
"""

from os import path
from optparse import OptionGroup

from PyFoam.Error import error,warning
from PyFoam.LogAnalysis.RegExpLineAnalyzer import RegExpLineAnalyzer

class CommonPlotLines(object):
    """ This class collects the lines that should be plotted
    """

    def __init__(self):
        self.lines_=None
        
    def plotLines(self):
        return self.lines_
    
    def addPlotLine(self,line):
        """Add a single line"""
        
        if self.lines_==None:
            self.lines_=[line]
        else:
            if type(line)==str:
                self.lines_.append(line)
            else:
                error(line,"is not a string, but",type(line))
                
    def addPlotLines(self,lines):
        """Adds a list of lines"""
        
        if type(lines)!=list:
            if type(lines==None):
                return
            else:
                error(lines,"is not a list, but",type(lines))
        for l in lines:
            self.addPlotLine(l)

    def addFileRegexps(self,fName):
        """Adds the lines from a file to the custom regular expressions
        @param fName: The name of the file"""
        f=open(fName)

        for l in f.readlines():
            l=l.strip()
            if len(l)==0:
                continue
            if l[0]=='"' and l[-1]=='"':
                l=l[1:-1]
            if len(l)>0:
                self.addPlotLine(l)
                
        f.close()

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
        self.parser.add_option_group(grp)
        
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
        
    def addPlotLineAnalyzers(self,runner):
        if self.lines_!=None:
            for i in range(len(self.lines_)):
                name="Custom%02d" % i
                runner.addAnalyzer(name,RegExpLineAnalyzer(name.lower(),self.lines_[i],doTimelines=False,doFiles=True))
                    
        

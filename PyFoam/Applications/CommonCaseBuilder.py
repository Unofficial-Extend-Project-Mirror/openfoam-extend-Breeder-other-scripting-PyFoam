"""
Class that implements the common functionality for CaseBuilder-applications
"""

from optparse import OptionGroup
from os import path

from PyFoam import configuration as config
from CaseBuilderBackend import CaseBuilderDescriptionList
from PyFoam.Error import error

class CommonCaseBuilder(object):
    """ The class that implements common CaseBuilder-functionality
    """

    def addOptions(self):
        cb=OptionGroup(self.parser,
                       "Casebuilder",
                       "Information related to the Casebuilder")
        self.parser.add_option_group(cb)
        
        cb.add_option("--list-of-desciptions",
                      action="store_true",
                      dest="listDescr",
                      default=False,
                      help="List the available case descriptions")

        cb.add_option("--description-path",
                      action="store_true",
                      dest="descPath",
                      default=False,
                      help="Show the directories that are searched for case descriptions")

        select=OptionGroup(self.parser,
                           "Selection",
                           "How the description file is chosen")
        self.parser.add_option_group(select)
        
        select.add_option("--search",
                          action="store_true",
                          dest="search",
                          default=False,
                          help="Search the description file in the path (and appends .pfcb to the given name")
                
    def pathInfo(self):
        if self.opts.descPath:
            print
            print "Directories that are searched for pfcb-files:"
            print
            for i,d in enumerate(config().get("CaseBuilder","descriptionpath")):
                status="<not existing>"
                if path.isdir(d):
                    status=" "*len(status)
                print "%2d: %s %s" %(i+1,status,d)
            return True

        if self.opts.listDescr:
            dl=CaseBuilderDescriptionList()

            print
            print "Available description files:"
            print

            for i,d in enumerate(dl):
                print "%4d: %s" % (i+1,d[1])
                print "    %s  -  %s" % (d[2],d[3])

            return True

        return False
        
    def searchDescriptionFile(self,name):
        if self.opts.search:
            fName=None
            for d in config().get("CaseBuilder","descriptionpath"):
                if path.exists(path.join(d,name)):
                    fName=path.join(d,name)
                    break
                if path.exists(path.join(d,name+".pfcb")):
                    fName=path.join(d,name+".pfcb")
                    break
            if not fName:
                error("Description",name,"does not exist in search path",config().get("CaseBuilder","descriptionpath"))
            else:
                print "Found",fName
        else:
            fName=name
            if not path.exists(fName):
                error("The description file",fName,"does not exist")
        
        return fName
    

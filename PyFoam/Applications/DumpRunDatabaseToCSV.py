"""
Application-class that implements pyFoamDumpRunDatabaseToCSV.py
"""
from optparse import OptionGroup

from .PyFoamApplication import PyFoamApplication
from PyFoam.Basics.RunDatabase import RunDatabase

class DumpRunDatabaseToCSV(PyFoamApplication):
    def __init__(self,args=None):
        description="""\
Dump the contents of a SQLite database that holds run information to
a CSV-file
"""
        PyFoamApplication.__init__(self,
                                   args=args,
                                   description=description,
                                   usage="%prog <database.db> <dump.csv>",
                                   interspersed=True,
                                   changeVersion=False,
                                   nr=2,
                                   exactNr=True)

    def addOptions(self):
        how=OptionGroup(self.parser,
                        "Behavior",
                        "How the application should behave")
        self.parser.add_option_group(how)

        how.add_option("--verbose",
                       action="store_true",
                       dest="verbose",
                       default=False,
                       help="Tell about the data dumped")

        what=OptionGroup(self.parser,
                         "What",
                         "Which information should be dumped")
        self.parser.add_option_group(what)

        what.add_option("--selection",
                       action="append",
                       dest="selection",
                       default=[],
                       help="""Regular expression (more than one can be
                       specified) to select data with (all the basic
                       run-data will be dumped anyway)""")



    def run(self):
        source=self.parser.getArgs()[0]
        dest=self.parser.getArgs()[1]

        db=RunDatabase(source,
                       verbose=self.opts.verbose)

        selections=[]
        if self.opts.selection:
            selections=self.opts.selection

        db.dumpToCSV(dest,selection=selections)

# Should work with Python3 and Python2

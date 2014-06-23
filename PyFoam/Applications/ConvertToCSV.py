"""
Application-class that implements pyFoamConvertToCSV.py
"""
from optparse import OptionGroup

from .PyFoamApplication import PyFoamApplication
from PyFoam.Basics.SpreadsheetData import SpreadsheetData

from os import path

class ConvertToCSV(PyFoamApplication):
    def __init__(self,
                 args=None,
                 **kwargs):
        description="""\
Takes a plain file with column-oriented data and converts it to a
csv-file.  If more than one file are specified, they are joined
according to the first column.

Note: the first file determines the resolution of the time-axis
"""
        PyFoamApplication.__init__(self,
                                   args=args,
                                   description=description,
                                   usage="%prog <source> ... <dest.csv>",
                                   interspersed=True,
                                   changeVersion=False,
                                   nr=2,
                                   exactNr=False,
                                   **kwargs)

    def addOptions(self):
        data=OptionGroup(self.parser,
                         "Data",
                         "Specification on the data that is read in")
        self.parser.add_option_group(data)
        data.add_option("--time-name",
                        action="store",
                        dest="time",
                        default=None,
                        help="Name of the time column")
        data.add_option("--column-names",
                        action="append",
                        default=[],
                        dest="columns",
                        help="The columns (names) which should be copied to the CSV. All if unset")

        how=OptionGroup(self.parser,
                         "How",
                         "How the data should be joined")
        self.parser.add_option_group(how)

        how.add_option("--force",
                       action="store_true",
                       dest="force",
                       default=False,
                       help="Overwrite the destination csv if it already exists")
        how.add_option("--extend-data",
                       action="store_true",
                       dest="extendData",
                       default=False,
                       help="Extend the time range if other files exceed the range of the first file")
        how.add_option("--delimiter",
                       action="store",
                       dest="delimiter",
                       default=',',
                       help="Delimiter to be used between the values. Default: %default")

    def run(self):
        dest=self.parser.getArgs()[-1]
        if path.exists(dest) and not self.opts.force:
            self.error("CSV-file",dest,"exists already. Use --force to overwrite")
        sources=self.parser.getArgs()[0:-1]

        data=SpreadsheetData(txtName=sources[0],
                             timeName=self.opts.time,
                             validData=self.opts.columns,
                             title=path.splitext(path.basename(sources[0]))[0])

        if self.opts.time==None:
            self.opts.time=data.names()[0]

        for s in sources[1:]:
            addition=path.splitext(path.basename(s))[0]
            sData=SpreadsheetData(txtName=s)
            for n in sData.names():
                if n!=self.opts.time and (self.opts.columns==[] or n in self.opts.columns):
                    d=data.resample(sData,
                                    n,
                                    time=self.opts.time,
                                    extendData=self.opts.extendData)
                    data.append(addition+" "+n,d)

        data.writeCSV(dest,
                      delimiter=self.opts.delimiter)

# Should work with Python3 and Python2

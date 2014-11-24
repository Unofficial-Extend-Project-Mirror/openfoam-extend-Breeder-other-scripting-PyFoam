"""
Class that implements the common functionality for reading and writing CSV-files
"""

from optparse import OptionGroup

from os import path

from PyFoam.ThirdParty.six import print_

class CommonReadWriteCSV(object):
    """ The class implement common functionality
    """

    def addOptions(self):
        calc=OptionGroup(self.parser,
                         "Calculations",
                         "Calculations to be performed on the data. Format is '<name>:::<expr>' (three colons should not appear in variable names). In the expressions there are variables that correspond to the column names. Also a variable 'data' that can be subscripted (for columns that are not valid variable names)")
        calc.add_option("--recalc-columns",
                         action="append",
                         dest="recalcColumns",
                         default=[],
                         help="Columns that should be recalculated after reading. Can be specified more than once. In the expression a variable 'this' can reference the variable itself")
        calc.add_option("--regular-expression-for-recalculation",
                        action="store_true",
                        dest="regularExpressionRecalc",
                        default=False,
                        help="The name in recalculations is a regular expression that must match the existing names")
        calc.add_option("--raw-data-add-column",
                         action="append",
                         dest="rawAddColumns",
                         default=[],
                         help="Columns that should be added to the data after reading")
        calc.add_option("--joined-data-add-column",
                         action="append",
                         dest="joinedAddColumns",
                         default=[],
                         help="Columns that should be added to the data before writing")
        self.parser.add_option_group(calc)

        info=OptionGroup(self.parser,
                         "Info",
                         "Information about the data")
        info.add_option("--print-columns",
                         action="store_true",
                         dest="printColums",
                         default=False,
                         help="Print the column names found")
        self.parser.add_option_group(info)

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
        data.add_option("--regexp-column-names",
                        action="store_true",
                        default=False,
                        dest="columnsRegexp",
                        help="The column names should be matched as regular expressions")

        formt=OptionGroup(self.parser,
                           "Format",
                           "Specification on the format of the data read and written")
        self.parser.add_option_group(formt)
        formt.add_option("--write-excel-file",
                         action="store_true",
                         dest="writeExcel",
                         default=False,
                         help="Write to Excel-file instead of plain CSV. Onle works with the python-libraries pandas and xlwt")
        formt.add_option("--read-excel-file",
                         action="store_true",
                         dest="readExcel",
                         default=False,
                         help="Read from Excel-file instead of plain CSV. Onle works with the python-libraries pandas and xlrd")
        formt.add_option("--automatic-format",
                         action="store_true",
                         dest="automaticFormat",
                         default=False,
                         help="Determine from the file extension whether the files are CSV, Excel or plain text")
        formt.add_option("--delimiter",
                         action="store",
                         dest="delimiter",
                         default=',',
                         help="Delimiter to be used between the values. Default: %default")


    def printColumns(self,fName,data):
        if self.opts.printColums:
            print_("Columns in",fName,":",", ".join(data.names()))

    def recalcColumns(self,data):
        self.__processColumns(data,self.opts.recalcColumns)

    def rawAddColumns(self,data):
        self.__processColumns(data,self.opts.rawAddColumns,create=True)

    def joinedAddColumns(self,data):
        self.__processColumns(data,self.opts.joinedAddColumns,create=True)

    def __processColumns(self,data,specs,create=False):
        for s in specs:
            try:
                name,expr=s.split(":::")
            except ValueError:
                self.error(s,"can not be split correctly with ':::':",s.split(":::"))
            if not create and self.opts.regularExpressionRecalc:
                import re
                rex=re.compile(name)
                for n in data.names():
                    if rex.match(n):
                        data.recalcData(n,expr)
            else:
                data.recalcData(name,expr,create)

    def dataFormatOptions(self,name):
        dataFormat="csv"

        if self.opts.readExcel:
            dataFormat="excel"
        if self.opts.automaticFormat:
            ext=path.splitext(name)[1]
            if ext in [".csv"]:
                dataFormat="csv"
            elif ext in [".xls"]:
                dataFormat="excel"
            elif ext in [".txt",""]:
                dataFormat="txt"
            else:
                dataFormat=ext[1:]
        options={"csvName" : None,
                 "txtName" : None,
                 "excelName" : None}
        if dataFormat=="csv":
            options["csvName"]=name
        elif dataFormat=="excel":
            options["excelName"]=name
        elif dataFormat=="txt":
            options["txtName"]=name
        else:
            self.error("Unsupported format",dataFormat)

        return options

# Should work with Python3 and Python2

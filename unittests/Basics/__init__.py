
import unittest

theSuite=unittest.TestSuite()

from .FoamFileGenerator import theSuite as FoamFileGenerator
from .DataStructures import theSuite as DataStructures
from .TemplateFile import theSuite as TemplateFile
from .CustomPlotInfo import theSuite as CustomPlotInfo
from .SpreadsheetData import theSuite as SpreadsheetData

theSuite.addTest(FoamFileGenerator)
theSuite.addTest(DataStructures)
theSuite.addTest(TemplateFile)
theSuite.addTest(CustomPlotInfo)
theSuite.addTest(SpreadsheetData)

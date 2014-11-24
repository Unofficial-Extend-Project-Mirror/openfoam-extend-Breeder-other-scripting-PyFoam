#  ICE Revision: $Id$
"""
Common class with options that describe the behaviour of the template parser
"""

from optparse import OptionGroup

from os import path

class CommonTemplateBehaviour(object):
    def addOptions(self):
        behaviour=OptionGroup(self.parser,
                              "Behaviour",
                              "The behaviour of the parser")
        self.parser.add_option_group(behaviour)
        behaviour.add_option("--tolerant-expression-evaluation",
                             action="store_true",
                             default=False,
                             dest="tolerantRender",
                             help="Instead of failing when encountering a problem during an evaluation a string with the error message is inserted into the output")
        behaviour.add_option("--allow-exec-instead-of-assignment",
                             action="store_true",
                             default=False,
                             dest="allowExec",
                             help="Allows exectution of non-assignments in $$-lines. This is potentially unsafe as it allows 'import' and calling of external programs")
        behaviour.add_option("--add-assignment-debug",
                             action="store_true",
                             default=False,
                             dest="addAssignmentDebug",
                             help="Adds a commented out line for each assignment with the name of the variable and the used value")

    def pickAssignmentDebug(self,fName):
        """Pick the correct comment prefix according to the file extension.
        Fall back to // for no/unknown extension (assuming foam-file)"""
        if not self.opts.addAssignmentDebug:
            return None
        ext=path.splitext(fName)
        if ext!="":
            ext=ext[1:]
        if ext in ["sh","py"]:
            return "#"
        else:
            return "//"

# Should work with Python3 and Python2

#  ICE Revision: $Id$
"""Manipulate a C{blockMeshDict}"""

import re,os

from PyFoam.Basics.LineReader import LineReader
from .FileBasis import FileBasisBackup

class BlockMesh(FileBasisBackup):
    """Represents a C{blockMeshDict}-file"""

    def __init__(self,name,backup=False):
        """@param name: The name of the parameter file
        @param backup: create a backup-copy of the file"""

        FileBasisBackup.__init__(self,name,backup=backup)

    def refineMesh(self,factors,offset=(0,0,0)):
        """Refine the Mesh by multiplying the number of cells in the blocks
        @param factors: either a scalar to scale in all directions or a
        tuple with the value for each direction
        @param offset: an optional tuple for an additionnal offset value
        for each direction"""

        if type(factors)!=tuple:
            f=(factors,factors,factors)
        else:
            f=factors

        startPattern=re.compile("^\s*blocks")
        endPattern=re.compile("^\s\);")
        hexPattern=re.compile("^(\s*hex\s*\(.+\)\s+\(\s*)(\d+)\s+(\d+)\s+(\d+)(\s*\).*)$")

        inBlock=False

        l=LineReader()
        self.openFile()

        (fh,fn)=self.makeTemp()

        while l.read(self.fh):
            toPrint=l.line

            if not inBlock:
                if startPattern.match(l.line):
                    inBlock=True
            else:
                if endPattern.match(l.line):
                    inBlock=False
                else:
                    m=hexPattern.match(l.line)
                    if m!=None:
                        g=m.groups()
                        toPrint =self.removedString+l.line+"\n"
                        toPrint+="%s%d %d %d%s" % (
                            g[0],
                            int(g[1])*f[0]+offset[0],
                            int(g[2])*f[1]+offset[1],
                            int(g[3])*f[2]+offset[2],
                            g[4])
                        toPrint+=" "+self.addedString

            fh.write(toPrint+"\n")

        self.closeFile()
        fh.close()
        os.rename(fn,self.name)

# Should work with Python3 and Python2

#  ICE Revision: $Id$
"""Read a STL file and do simple manipulations"""

from os import path
from PyFoam.Error import error

from PyFoam.ThirdParty.six import next as iterNext

class STLFile(object):
    """Store a complete STL-file and do simple manipulations with it"""

    noName="<no name given>"

    def __init__(self,fName=None):
        """
	@param fName: filename of the STL-file. If None then an empty file is created
	"""
        self._filename=fName

        if fName!=None:
            self._contents=[l.strip() for l in open(fName).readlines()]
        else:
            self._contents=[]

        self.resetInfo()

    def resetInfo(self):
        """Set cached info to nothing"""
        self._patchInfo=None

    def filename(self):
        """The filename (without the full patch)"""
        if self._filename==None:
            return "<no filename given>"
        else:
            return path.basename(self._filename)

    def expectedToken(self,l,token,i):
        if l.strip().find(token)!=0:
            error("'%s' expected in line %d of %s" % (token,i+1,self.filename()))

    def patchInfo(self):
        """Get info about the patches. A list of dictionaries with the relevant information"""
        if self._patchInfo:
            return self._patchInfo

        self._patchInfo=[]

        newPatch=True

        e=enumerate(self._contents)

        goOn=True
        while goOn:
            try:
                i,l=iterNext(e)
                if newPatch:
                    self.expectedToken(l,"solid",i)
                    info={}
                    if len(l.split())<2:
                        info["name"]=self.noName
                    else:
                        info["name"]=l.split()[1]
                    info["start"]=i+1
                    info["facets"]=0
                    info["min"]=[1e100]*3
                    info["max"]=[-1e100]*3
                    newPatch=False
                elif l.strip().find("endsolid")==0:
                    info["end"]=i+1
                    self._patchInfo.append(info)
                    newPatch=True
                else:
                    self.expectedToken(l,"facet normal",i)
                    i,l=iterNext(e)
                    self.expectedToken(l,"outer loop",i)
                    for v in range(3):
                        i,l=iterNext(e)
                        self.expectedToken(l,"vertex",i)
                        info["min"]=[min(m) for m in zip(info["min"],
                                                         [float(v) for v in l.strip().split()[1:4]])]
                        info["max"]=[max(m) for m in zip(info["max"],
                                                         [float(v) for v in l.strip().split()[1:4]])]
                    i,l=iterNext(e)
                    self.expectedToken(l,"endloop",i)
                    i,l=iterNext(e)
                    self.expectedToken(l,"endfacet",i)
                    info["facets"]+=1
            except StopIteration:
                goOn=False


        if not newPatch:
            error("File",self.filename(),"seems to be incomplete")

        return self._patchInfo

    def writeTo(self,fName):
        """Write to a file"""
        f=open(fName,"w")
        f.write("\n".join(self._contents))

    def __iter__(self):
        for l in self._contents:
            yield l

    def __iadd__(self,other):
        self.resetInfo()

        fName=path.splitext(other.filename())[0]
        moreThanOne=len(other.patchInfo())>1

        nr=1

        for l in other:
            if l.strip().find("solid")==0:
                parts=l.split()
                if len(parts)==1:
                    l=parts[0]+" "+fName
                    if moreThanOne:
                        l+="_%04d" % nr
                else:
                    l=parts[0]+" %s:%s" %(fName," ".join(parts[1:]))
                nr+=1

            self._contents.append(l)

        return self

# Should work with Python3 and Python2

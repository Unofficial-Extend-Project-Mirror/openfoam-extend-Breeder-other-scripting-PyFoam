#  ICE Revision: $Id: ReadDictionary.py 7581 2007-06-27 15:29:14Z bgschaid $ 
"""
Application class that implements pyFoamCompareDictionary.py
"""

import re
from os import path

from PyFoamApplication import PyFoamApplication

from PyFoam.RunDictionary.ParsedParameterFile import ParsedParameterFile
from PyFoam.Basics.DataStructures import DictProxy,Dimension,Tensor,SymmTensor,Vector,Field,TupleProxy
from PyFoam.Basics.FoamFileGenerator import makeString

from PyFoam.Error import error,warning

class CompareDictionary(PyFoamApplication):
    def __init__(self,args=None):
        description="""
Takes two dictionary and compares them semantically (by looking at the
structure, not the textual representation. If the dictionaries do not
have the same name, it looks for the destination file by searching the
equivalent place in the destination case
        """
        
        PyFoamApplication.__init__(self,args=args,description=description,usage="%prog [options] <source> <destination-case>",nr=2,interspersed=True)
        
    def addOptions(self):
        self.parser.add_option("--not-equal",
                               action="store_true",
                               default=False,
                               dest="notequal",
                               help="Allow source and destination to have different names")
        self.parser.add_option("--debug",
                               action="store_true",
                               default=False,
                               dest="debug",
                               help="Debug the comparing process")
        self.parser.add_option("--long-field-threshold",
                               action="store",
                               type="int",
                               default=None,
                               dest="longlist",
                               help="Fields that are longer than this won't be parsed, but read into memory (and compared as strings)")

        self.parser.add_option("--no-header",
                               action="store_true",
                               default=False,
                               dest="noHeader",
                               help="Don't expect a header while parsing")
        
        self.parser.add_option("--boundary",
                               action="store_true",
                               default=False,
                               dest="boundaryDict",
                               help="Expect that this file is a boundary dictionary")
        self.parser.add_option("--list",
                               action="store_true",
                               default=False,
                               dest="listDict",
                               help="Expect that this file only contains a list")
        

    
    def run(self):
        sName=path.abspath(self.parser.getArgs()[0])
        dName=path.abspath(self.parser.getArgs()[1])

        try:
            source=ParsedParameterFile(sName,backup=False,listLengthUnparsed=self.opts.longlist,noHeader=self.opts.noHeader,boundaryDict=self.opts.boundaryDict,listDict=self.opts.listDict)
        except IOError,e:
            self.error("Problem with file",sName,":",e)

        found=False

        if path.isfile(sName) and path.isfile(dName):
            found=True
            
        if not found and not self.opts.notequal and path.basename(sName)!=path.basename(dName):
            parts=sName.split(path.sep)
            for i in range(len(parts)):
                tmp=apply(path.join,[dName]+parts[-(i+1):])
                
                if path.exists(tmp):
                    found=True
                    dName=tmp
                    warning("Found",dName,"and using this")
                    break
                
            if not found:
                error("Could not find a file named",path.basename(sName),"in",dName)
                
        if path.samefile(sName,dName):
            error("Source",sName,"and destination",dName,"are the same")
        
        try:
            dest=ParsedParameterFile(dName,backup=False,listLengthUnparsed=self.opts.longlist,noHeader=self.opts.noHeader,boundaryDict=self.opts.boundaryDict,listDict=self.opts.listDict)
        except IOError,e:
            self.error("Problem with file",dName,":",e)

        self.pling=False

        if not self.opts.boundaryDict and not self.opts.listDict:
            self.compareDict(source.content,dest.content,1,path.basename(sName))
        else:
            self.compareIterable(source.content,dest.content,1,path.basename(sName))

        if not self.pling:
            print "\nNo differences found"
            
    def dictString(self,path,name):
        return "%s[%s]" % (path,name)

    def iterString(self,path,index):
        return "%s[%d]" % (path,index)

    def compare(self,src,dst,depth,name):
        if type(src)!=type(dst):
            print ">><<",name,": Types differ\n>>Source:\n",makeString(src),"\n<<Destination:\n",makeString(dst)
            self.pling=True
        elif type(src) in [tuple,list,TupleProxy]:
            self.compareIterable(src,dst,depth,name)
        elif type(src) in [str,float,int,long,type(None)]:
            self.comparePrimitive(src,dst,depth,name)
        elif src.__class__ in [Dimension,Tensor,SymmTensor,Vector]:
            self.comparePrimitive(src,dst,depth,name)            
        elif src.__class__==Field:
            self.compareField(src,dst,depth,name)            
        elif type(src) in [DictProxy,dict]:
            self.compareDict(src,dst,depth,name)            
        else:
            warning("Type of",name,"=",type(src),"unknown")
            if self.opts.debug:
                try:
                    print "Class of",name,"=",src.__class__,"unknown"
                except:
                    pass
                
    def compareField(self,src,dst,depth,name):
        if src!=dst:
            self.pling=True
            print ">><< Field",name,": Differs\n>>Source:\n",
            if src.uniform:
                print src
            else:
                print "nonuniform - field not printed"
            print "<<Destination:\n",
            if dst.uniform:
                print dst
            else:
                print "nonuniform - field not printed"
            
    def comparePrimitive(self,src,dst,depth,name):
        if src!=dst:
            print ">><<",name,": Differs\n>>Source:\n",src,"\n<<Destination:\n",dst
            self.pling=True
            
    def compareIterable(self,src,dst,depth,name):
        nr=min(len(src),len(dst))
        
        for i in range(nr):
            if self.opts.debug:
                print "Comparing",self.iterString(name,i)
            self.compare(src[i],dst[i],depth+1,self.iterString(name,i))
            
        if nr<len(src):
            print ">>>>",self.iterString(name,nr),"to",self.iterString(name,len(src)-1),"missing from destination\n",makeString(src[nr:])
            self.pling=True
        elif nr<len(dst):
            print "<<<<",self.iterString(name,nr),"to",self.iterString(name,len(dst)-1),"missing from source\n",makeString(dst[nr:])
            self.pling=True
            
    def compareDict(self,src,dst,depth,name):
        for n in src:
            if not n in dst:
                print ">>>>",self.dictString(name,n),": Missing from destination\n",makeString(src[n])
                self.pling=True
            else:
                if self.opts.debug:
                    print "Comparing",self.dictString(name,n)
                self.compare(src[n],dst[n],depth+1,self.dictString(name,n))
                
        for n in dst:
            if not n in src:
                print "<<<<",self.dictString(name,n),": Missing from source\n",makeString(dst[n])
                self.pling=True
                

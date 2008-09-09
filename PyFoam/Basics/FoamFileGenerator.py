#  ICE Revision: $Id: FoamFileGenerator.py 9163 2008-08-04 08:01:10Z bgschaid $ 
"""Transform a Python data-structure into a OpenFOAM-File-Representation"""

from PyFoam.Error import error,PyFoamException
from PyFoam.Basics.DataStructures import Vector,Field,Dimension,TupleProxy,DictProxy,Tensor,SymmTensor,Unparsed,UnparsedList

import string

class FoamFileGenerator(object):
    """Class that generates a OpenFOAM-compatible representation of a
    data-structure"""

    primitiveTypes=[SymmTensor,Tensor,Vector,Dimension,Field,Unparsed]
    
    def __init__(self,data,header=None):
        """@param data: data structure that will be turned into a
        Foam-compatible file
        @param header: header information that is to be prepended
        """
        
        self.data=data
        self.header=header
        
    def __str__(self):
        """turns the data into a string"""
        result=""
        if self.header:
            result+="FoamFile\n{\n"+self.strDict(self.header,indent=1)+"}\n\n"

        if type(self.data) in [dict,DictProxy]:
            result+=self.strDict(self.data)
        elif type(self.data) in [tuple,TupleProxy]:
            result+=self.strTuple(self.data)
        elif type(self.data) in [list,UnparsedList]:
            result+=self.strList(self.data)
        elif self.data==None:
            raise FoamFileGeneratorError("<None> found")
        else:
            result+=self.strPrimitive(self.data)
            
        return result

    def strPrimitive(self,pri):
        if type(pri) in [int,float,long,str,unicode]:
            return str(pri)
        elif type(pri)==bool:
            if pri:
                return "yes"
            else:
                return "no"
        elif pri.__class__ in self.primitiveTypes:
            return str(pri)
        else:
            error("List, Dict or valid primitve expected,",type(pri),"found in",pri)
            
    def strDict(self,dic,indent=0):
        s=""
        if type(dic)==DictProxy:
            order=dic._order
        else:
            order=dic.keys()
            order.sort()
            
        for k in order:
            v=dic[k]
            if k.find("anonymValue")==0:
                k=""
                
            s+=(" "*indent)+k
            if type(v)in [unicode,str]:
                s+=" "+v+";\n"
            elif type(v) in [dict,DictProxy]:
                s+="\n"+(" "*indent)+"{\n"
                s+=self.strDict(v,indent+2)
                s+=(" "*indent)+"}\n"
            elif type(v) in [list,UnparsedList]:
                s+="\n"
                s+=self.strList(v,indent+2)
                if s[-1]=="\n":
                    s=s[:-1]
                s+=";\n"
            elif type(v) in [tuple,TupleProxy]:
                s+=" "+self.strTuple(v,indent+2)+";\n"
            elif type(v) in [int,float,long]:
                s+=" "+str(v)+";\n"
            elif v.__class__ in self.primitiveTypes:
                s+=" "+str(v)+";\n"
            elif v==None:
                s+=" /* empty */ ;\n"
            else:
                error("Unhandled type",type(v)," for",v)
        return s
    
    def strList(self,lst,indent=0):
        s=""

        if type(lst)==UnparsedList:
            s+=(" "*indent)+str(len(lst))+" ("
            s+=lst.data
            if lst.data[-1]!="\n":
                s+="\n"
            s+=(" "*indent)+")\n"
            return s
        
        theLen=len(lst)
        
        if len(lst)>2 and len(lst)%2==0:
            if type(lst[0])in [unicode,str] and (type(lst[1]) in [dict,DictProxy]):
                theLen=len(lst)/2

        isFixedType=False
        if len(lst)==3 or len(lst)==9 or len(lst)==6:
            isFixedType=True
            for l in lst:
                try:
                    val=float(l)
                except (ValueError,TypeError):
                    isFixedType=False
                    
        if isFixedType:
            s+="("+string.join(map(lambda v:"%g"%v,lst))+")"
        else:
            if theLen>20:
                s+=(" "*indent)+str(theLen)+"\n"
            s+=(" "*indent)+"(\n"
            for v in lst:
                if type(v)in [unicode,str]:
                    s+=(" "*(indent+2))+v+"\n"
                elif type(v) in [dict,DictProxy]:
                    s+="\n"+(" "*(indent+2))+"{\n"
                    s+=self.strDict(v,indent+4)
                    s+="\n"+(" "*(indent+2))+"}\n"
                elif type(v) in [list,UnparsedList]:
                    s+="\n"
                    s+=self.strList(v,indent+2)
                elif type(v)==tuple:
                    s+=" "+self.strTuple(v,indent+2)+" "
                else:
                    s+=(" "*(indent+2))+str(v)+"\n"

            s+=(" "*indent)+")\n"
        
        return s

    def strTuple(self,lst,indent=0):
        s=""

        for v in lst:
            if type(v)in [unicode,str]:
                s+=v+" "
            elif type(v) in [dict,DictProxy]:
                s+="{\n"
                s+=self.strDict(v,indent+4)
                s+=(" "*(indent+2))+"} "
            elif type(v) in [list,UnparsedList]:
                s+=" "
                s+=self.strList(v,indent+2)
            else:
                s+=(" "*(indent+2))+str(v)+" "
            
        return s

def makeString(data):
    return str(FoamFileGenerator(data))

class FoamFileGeneratorError(PyFoamException):
    def __init__(self,descr):
        PyFoamException.__init__(self,descr)

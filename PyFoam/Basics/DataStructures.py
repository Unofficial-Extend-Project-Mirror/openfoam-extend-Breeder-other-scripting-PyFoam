"""Data structures in Foam-Files that can't be directly represented by Python-Structures"""

import FoamFileGenerator
from copy import deepcopy
import string,math
import re

class FoamDataType(object):
    def __repr__(self):
        return "'"+str(self)+"'"
    

class Field(FoamDataType):
    def __init__(self,val,name=None):
        self.val=val
        self.name=name
        if self.name==None:
            self.uniform=True
        elif type(val) in[list,UnparsedList]:
            self.uniform=False
            
    def __str__(self):
        result=""
        if self.uniform:
            result+="uniform "
        else:
            result+="nonuniform "+self.name+" "
        result+=str(FoamFileGenerator.FoamFileGenerator(self.val))
        return result

    def __cmp__(self,other):
        if other==None or type(other)!=Field:
            return 1
        if self.uniform!=other.uniform:
            return cmp(self.uniform,other.uniform)
        elif self.name!=other.name:
            return cmp(self.name,other.name)
        else:
            return cmp(self.val,other.val)

    def __getitem__(self,key):
        assert(not self.uniform)
        return self.val[key]

    def __setitem__(self,key,value):
        assert(not self.uniform)
        self.val[key]=value

    def isUniform(self):
        return self.uniform
    
    def value(self):
        return self.val

    def setUniform(self,data):
        self.val=data
        self.uniform=True
        self.name=None
        
class Dimension(FoamDataType):
    def __init__(self,*dims):
        assert(len(dims)==7)
        self.dims=list(dims)

    def __str__(self):
        result="[ "
        for v in self.dims:
            result+=str(v)+" "
        result+="]"
        return result

    def __cmp__(self,other):
        if other==None:
            return 1
        return cmp(self.dims,other.dims)
    
    def __getitem__(self,key):
        return self.dims[key]

    def __setitem__(self,key,value):
        self.dims[key]=value

class FixedLength(FoamDataType):
    def __init__(self,vals):
        self.vals=vals[:]

    def __str__(self):
        return "("+string.join(map(lambda v:"%g"%v,self.vals))+")"
    
    def __cmp__(self,other):
        if other==None or not issubclass(type(other),FixedLength):
            return 1
        return cmp(self.vals,other.vals)
    
    def __getitem__(self,key):
        return self.vals[key]

    def __setitem__(self,key,value):
        self.vals[key]=value

    def __len__(self):
        return len(self.vals)

class Vector(FixedLength):
    def __init__(self,x,y,z):
        FixedLength.__init__(self,[x,y,z])

    def __add__(self,y):
        x=self
        if type(y)==Vector:
            return Vector(x[0]+y[0],x[1]+y[1],x[2]+y[2])
        elif type(y) in [int,float,long]:
            return Vector(x[0]+y,x[1]+y,x[2]+y)            
        else:
            return NotImplemented
        
    def __radd__(self,y):
        x=self
        if type(y) in [int,float,long]:
            return Vector(x[0]+y,x[1]+y,x[2]+y)            
        else:
            return NotImplemented
        
    def __sub__(self,y):
        x=self
        if type(y)==Vector:
            return Vector(x[0]-y[0],x[1]-y[1],x[2]-y[2])
        elif type(y) in [int,float,long]:
            return Vector(x[0]-y,x[1]-y,x[2]-y)            
        else:
            return NotImplemented
        
    def __rsub__(self,y):
        x=self
        if type(y) in [int,float,long]:
            return Vector(y-x[0],y-x[1],y-x[2])            
        else:
            return NotImplemented
        
    def __mul__(self,y):
        x=self
        if type(y)==Vector:
            return Vector(x[0]*y[0],x[1]*y[1],x[2]*y[2])
        elif type(y) in [int,float,long]:
            return Vector(x[0]*y,x[1]*y,x[2]*y)            
        else:
            return NotImplemented
        
    def __rmul__(self,y):
        x=self
        if type(y) in [int,float,long]:
            return Vector(y*x[0],y*x[1],y*x[2])            
        else:
            return NotImplemented

    def __div__(self,y):
        x=self
        if type(y)==Vector:
            return Vector(x[0]/y[0],x[1]/y[1],x[2]/y[2])
        elif type(y) in [int,float,long]:
            return Vector(x[0]/y,x[1]/y,x[2]/y)            
        else:
            return NotImplemented

    def __xor__(self,y):
        x=self
        if type(y)==Vector:
            return Vector(x[1]*y[2]-x[2]*y[1],
                          x[2]*y[0]-x[0]*y[2],
                          x[0]*y[1]-x[1]*y[0])
        else:
            return NotImplemented

    def __abs__(self):
        x=self
        return math.sqrt(x[0]*x[0]+x[1]*x[1]+x[2]*x[2])

    def __neg__(self):
        x=self
        return Vector(-x[0],-x[1],-x[2])

    def __pos__(self):
        x=self
        return Vector( x[0], x[1], x[2])

class Tensor(FixedLength):
    def __init__(self,v1,v2,v3,v4,v5,v6,v7,v8,v9):
        FixedLength.__init__(self,[v1,v2,v3,v4,v5,v6,v7,v8,v9])
        
class SymmTensor(FixedLength):
    def __init__(self,v1,v2,v3,v4,v5,v6):
        FixedLength.__init__(self,[v1,v2,v3,v4,v5,v6])
        
class DictProxy(dict):
    """A class that acts like a dictionary, but preserves the order
    of the entries. Used to beautify the output"""

    def __init__(self):
        dict.__init__(self)
        self._order=[]
        self._decoration={}
        self._regex=[]
        
    def __setitem__(self,key,value):
        isRegex=False
        if type(key)==str:
            if key[0]=='"' and key[-1]=='"':
                isRegex=True
        if isRegex:
            exp=re.compile(key[1:-1])
            self._regex=[(key,exp,value)]+self._regex
        else:
            dict.__setitem__(self,key,value)
        if key not in self._order or isRegex:
            self._order.append(key)

    def __getitem__(self,key):
        try:
            return dict.__getitem__(self,key)
        except KeyError:
            for k,e,v in self._regex:
                if e.match(key):
                    return v
            raise KeyError(key)
        
    def __delitem__(self,key):
        dict.__delitem__(self,key)
        self._order.remove(key)
        if key in self._decoration:
            del self._decoration[key]
            
    def __deepcopy__(self,memo):
        new=DictProxy()
        for k in self._order:
            try:
                new[k]=deepcopy(self[k],memo)
            except KeyError:
                new[k]=deepcopy(self.getRegexpValue(k),memo)
            
        return new

    def __contains__(self,key):
        if dict.__contains__(self,key):
            return True
        else:
            for k,e,v in self._regex:
                if e.match(key):
                    return True
            return False

    def keys(self):
        return self._order[:]

    def addDecoration(self,key,text):
        if key in self:
            self._decoration[key]=text

    def getDecoration(self,key):
        if key in self._decoration:
            return " \t"+self._decoration[key]
        else:
            return ""

    def getRegexpValue(self,key):
        for k,e,v in self._regex:
            if k==key:
                return v
        raise KeyError(key)
    
class TupleProxy(list):
    """Enables Tuples to be manipulated"""

    def __init__(self,tup=()):
        list.__init__(self,tup)

class Unparsed(object):
    """A class that encapsulates an unparsed string"""

    def __init__(self,data):
        self.data=data

    def __str__(self):
        return self.data
    
class UnparsedList(object):
    """A class that encapsulates a list that was not parsed for
    performance reasons"""

    def __init__(self,lngth,data):
        self.data=data
        self.length=lngth
        
    def __len__(self):
        return self.length
    
    def __cmp__(self,other):
        return cmp(self.data,other.data)

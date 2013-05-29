"""Data structures in Foam-Files that can't be directly represented by Python-Structures"""

from __future__ import division

import PyFoam.Basics.FoamFileGenerator

from copy import deepcopy
import string,math
import re

from PyFoam.ThirdParty.six import integer_types,PY3,iteritems

if PY3:
    def cmp(a,b):
        if a<b:
            return -1
        elif a==b:
            return 0
        else:
            return 1

class FoamDataType(object):
    def __repr__(self):
        return "'"+str(self)+"'"

    def __eq__(self,other):
        """Implementation to make __cmp__ work again in Python3

        Implementing this method means that these objects are not hashable.
        But that is OK
        """
        return self.__cmp__(other)==0

    def __lt__(self,other):
        "Implementation to make __cmp__ work again in Python3"
        return self.__cmp__(other)<0

    def __ne__(self,other):
        return self.__cmp__(other)!=0

    def __gt__(self,other):
        return self.__cmp__(other)>0

    def __ge__(self,other):
        return self.__cmp__(other)>=0

    def __le__(self,other):
        return self.__cmp__(other)<=0

class Field(FoamDataType):
    def __init__(self,val,name=None):
        self.val=val
        self.name=name
        if type(val) in[list,UnparsedList,BinaryList]:
            self.uniform=False
        elif self.name==None:
            self.uniform=True
        else:
            raise TypeError("Type",type(val),"of value",val,"can not be used to determine uniformity")

    def __str__(self):
        result=""
        if self.uniform:
            result+="uniform "
        else:
            result+="nonuniform "
            if self.name:
                result+=self.name+" "

        result+=str(PyFoam.Basics.FoamFileGenerator.FoamFileGenerator(self.val,
                                                    longListThreshold=-1))
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

    def isBinary(self):
        return type(self.val)==BinaryList

    def binaryString(self):
        return "nonuniform "+self.name+" <BINARY DATA>"

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
        return "("+" ".join(["%g"%v for v in self.vals])+")"

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
        elif type(y) in integer_types+(float,):
            return Vector(x[0]+y,x[1]+y,x[2]+y)
        else:
            return NotImplemented

    def __radd__(self,y):
        x=self
        if type(y) in integer_types+(float,):
            return Vector(x[0]+y,x[1]+y,x[2]+y)
        else:
            return NotImplemented

    def __sub__(self,y):
        x=self
        if type(y)==Vector:
            return Vector(x[0]-y[0],x[1]-y[1],x[2]-y[2])
        elif type(y) in integer_types+(float,):
            return Vector(x[0]-y,x[1]-y,x[2]-y)
        else:
            return NotImplemented

    def __rsub__(self,y):
        x=self
        if type(y) in integer_types+(float,):
            return Vector(y-x[0],y-x[1],y-x[2])
        else:
            return NotImplemented

    def __mul__(self,y):
        x=self
        if type(y)==Vector:
            return Vector(x[0]*y[0],x[1]*y[1],x[2]*y[2])
        elif type(y) in integer_types+(float,):
            return Vector(x[0]*y,x[1]*y,x[2]*y)
        else:
            return NotImplemented

    def __rmul__(self,y):
        x=self
        if type(y) in integer_types+(float,):
            return Vector(y*x[0],y*x[1],y*x[2])
        else:
            return NotImplemented

    def __div__(self,y):
        x=self
        if type(y)==Vector:
            return Vector(x[0]/y[0],x[1]/y[1],x[2]/y[2])
        elif type(y) in integer_types+(float,):
            return Vector(x[0]/y,x[1]/y,x[2]/y)
        else:
            return NotImplemented

    def __truediv__(self,y):
        return self.__div__(y)

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

class DictRedirection(object):
    """This class is in charge of handling redirections to other directories"""
    def __init__(self,fullCopy,reference,name):
        self._fullCopy=fullCopy
        self._reference=reference
        self._name=name

    def useAsRedirect(self):
        self._fullCopy=None

    def getContent(self):
        result=self._fullCopy
        self._fullCopy=None
        return result

    def __call__(self):
        return self._reference

    def __str__(self):
        return "$"+self._name

    def __float__(self):
        return float(self._reference)

class DictProxy(dict):
    """A class that acts like a dictionary, but preserves the order
    of the entries. Used to beautify the output"""

    def __init__(self):
        dict.__init__(self)
        self._order=[]
        self._decoration={}
        self._regex=[]
        self._redirects=[]

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
            for r in self._redirects:
                try:
                    return r()[key]
                except KeyError:
                    pass

            raise KeyError(key)

    def __delitem__(self,key):
        dict.__delitem__(self,key)
        self._order.remove(key)
        if key in self._decoration:
            del self._decoration[key]

    def __deepcopy__(self,memo):
        new=DictProxy()
        for k in self._order:
            if type(k)==DictRedirection:
                new.addRedirection(k)
            else:
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
            for r in self._redirects:
                if key in r():
                    return True

            return False

    def keys(self):
        return [x for x in self._order if type(x)!=DictRedirection]

    def __str__(self):
        first=True
        result="{"
        for k in self.keys():
            v=self[k]
            if first:
                first=False
            else:
                result+=", "
            result+="%s: %s" % (repr(k),repr(v))
        result+="}"
        return result

    def addDecoration(self,key,text):
        if key in self:
            if key not in self._decoration:
                self._decoration[key]=""
            self._decoration[key]+=text

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

    def addRedirection(self,redir):
        self._order.append(redir)
        redir.useAsRedirect()
        self._redirects.append(redir)

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

    def __hash__(self):
        return hash(self.data)

    def __lt__(self,other):
        return self.data<other.data

class BinaryBlob(Unparsed):
    """Represents a part of the file with binary data in it"""
    def __init__(self,data):
        Unparsed.__init__(self,data)

class Codestream(str):
    """A class that encapsulates an codestream string"""

    def __str__(self):
        return "#{" + str.__str__(self) + "#}"

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

    def __eq__(self,other):
        return self.data==other.data

    def __lt__(self,other):
        return self.data<other.data

class BinaryList(UnparsedList):
    """A class that represents a list that is saved as binary data"""

    def __init__(self,lngth,data):
        UnparsedList.__init__(self,lngth,data)

# Should work with Python3 and Python2

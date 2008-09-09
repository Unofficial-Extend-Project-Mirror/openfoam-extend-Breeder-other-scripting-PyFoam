#  ICE Revision: $Id: TimeLineCollection.py 8847 2008-05-18 19:30:54Z bgschaid $ 
"""Collection of array of timelines"""

from PyFoam.Error import error

def mean(a,b):
    """Mean value of a and b"""
    return 0.5*(a+b)

def signedMax(a,b):
    """Absolute Maximum of a and b with the sign preserved"""
    if a<0. or b<0.:
        return min(a,b)
    else:
        return max(a,b)

class TimeLineCollection(object):

    possibleAccumulations=["first", "last", "min", "max", "average", "sum"]
    
    def __init__(self,deflt=0.,extendCopy=False,splitThres=None,splitFun=None,accumulation="first"):
        """@param deflt: default value for timelines if none has been defined before
        @param extendCopy: Extends the timeline by cpying the last element
        @param splitThres: Threshold after which the number of points is halved
        @param splitFun: Function that is used for halving. If none is specified the mean function is used
        @param accumulation: if more than one value is given at any time-step, how to accumulate them (possible values: "first", "last", "min", "max", "average", "sum")
        """
        
        self.cTime=None
        self.times=[]
        self.values={}
        self.setDefault(deflt)
        self.setExtend(extendCopy)
        self.thres=None
        self.fun=None

        if not (accumulation in TimeLineCollection.possibleAccumulations):
            error("Value",accumulation,"not in list of possible values:",TimeLineCollection.possibleAccumulations)
        self.accumulation=accumulation
        self.accumulations={}
        self.occured={}
        
        self.setSplitting(splitThres=splitThres,splitFun=splitFun)

    def setAccumulator(self,name,accu):
        """Sets a special accumulator fopr a timeline
        @param name: Name of the timeline
        @param accu: Name of the accumulator"""
        if not (accu in TimeLineCollection.possibleAccumulations):
            error("Value",accu,"not in list of possible values:",TimeLineCollection.possibleAccumulations,"When setting for",name)
        self.accumulations[name]=accu
        
    def setSplitting(self,splitThres=None,splitFun=None):
        """Sets the parameters for splitting"""
        if splitThres:
            self.thres=splitThres
            if (self.thres % 2)==1:
                self.thres+=1

        if splitFun:
            self.fun=splitFun
        elif not self.fun:
            self.fun=mean
            
    def setDefault(self,deflt):
        """@param deflt: default value to be used"""
        self.defaultValue=float(deflt)

    def setExtend(self,mode):
        """@param mode: whether or not to extend the timeline by copying or setting the default value"""
        self.extendCopy=mode
        
    def nr(self):
        """Number of elements in timelines"""
        return len(self.times)
    
    def setTime(self,time):
        """Sets the time. If time is new all the timelines are extended
        @param time: the new current time"""
        
        dTime=float(time)
        
        if dTime!=self.cTime:
            self.cTime=dTime
            self.times.append(self.cTime)
            for v in self.values.values():
                if len(v)>0 and self.extendCopy:
                    val=v[-1]
                else:
                    val=self.defaultValue
                v.append(val)
            if self.thres:
                if len(self.times)==self.thres:
                    self.times=self.split(self.times,min)
                    for k in self.values.keys():
                        self.values[k]=self.split(self.values[k],self.fun)
            self.occured={}

    def split(self,array,func):
        """Makes the array smaller by joining every two points
        @param array: the field to split
        @param func: The function to use for joining two points"""

        newLen=len(array)/2
        newArray=[0.]*newLen

        for i in range(newLen):
            newArray[i]=func(array[2*i],array[2*i+1])

        return newArray
    
    def getTimes(self):
        """@return: A list of the time values"""
        return self.times
    
    def getValueNames(self):
        """@return: A list with the names of the safed values"""
        return self.values.keys()
    
    def getValues(self,name):
        """Gets a timeline
        @param name: Name of the timeline
        @return: List with the values"""
        
        if not self.values.has_key(name):
            self.values[name]=self.nr()*[self.defaultValue]
        return self.values[name]
            
    def setValue(self,name,value):
        """Sets the value of the last element in a timeline
        @param name: name of the timeline
        @param value: the last element"""
        data=self.getValues(name)
        val=float(value)
        if len(data)>0:
            if not self.occured.has_key(name):
                newValue=val
                self.occured[name]=1
            else:
                oldValue=data[-1]
                n=self.occured[name]
                self.occured[name]+=1
                accu=self.accumulation
                if name in self.accumulations:
                    accu=self.accumulations[name]
                if accu=="first":
                    newValue=oldValue
                elif accu=="last":
                    newValue=val
                elif accu=="max":
                    newValue=max(val,oldValue)
                elif accu=="min":
                    newValue=min(val,oldValue)
                elif accu=="sum":
                    newValue=val+oldValue
                elif accu=="average":
                    newValue=(n*oldValue+val)/(n+1)
                else:
                    error("Unimplemented accumulator",accu,"for",name)
                    
            data[-1]=newValue

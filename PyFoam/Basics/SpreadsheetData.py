#  ICE Revision: $Id: $ 
"""
Data that can go into a spreadsheet (title line and rectangular data)
"""

import numpy,copy

from PyFoam.Error import error,FatalErrorPyFoamException,warning

class WrongDataSize(FatalErrorPyFoamException):
    def __init__(self):
        FatalErrorPyFoamException.__init__(self,"Size of the arrays differs")
        
class SpreadsheetData(object):
    """
    Collects data that could go into a spreadsheet. The focus of this class is on
    storing all the data at once
    """
    def __init__(self,
                 csvName=None,
                 txtName=None,
                 data=None,
                 names=None,
                 title=None):
        """Either this is constructed from a file or from the data and the column headers
        
        @param csvName: name of the CSV-file the data should be constructed from,
        @param txtName: name of a file the data should be constructed from,
        @param data: the actual data to use
        @param names: the names for the column header
        @param title: a name that is used to make unique heades names"""

        self.title=title
        
        if csvName and data:
            error("SpreadsheetData is either constructed from data or from a file")

        if csvName:
            try:
                rec=numpy.recfromcsv(csvName)
                data=[tuple(float(x) for x in i) for i in rec]
                names=list(rec.dtype.names)
            except AttributeError:
                # for old numpy-versions
                data=map(tuple,numpy.loadtxt(csvName,delimiter=',',skiprows=1))
                names=open(csvName).readline().strip().split(',')
                
            # redo this to make sure that everything is float
            self.data=numpy.array(data,dtype=zip(names,['f8']*len(names)))
        elif txtName:
            try:
                rec=numpy.recfromtxt(txtName,names=True)
                data=[tuple(float(x) for x in i) for i in rec]
                names=list(rec.dtype.names)
            except AttributeError:
                # for old numpy-versions
                data=map(tuple,numpy.loadtxt(txtName))
                names=open(txtName).readline().strip().split()[1:]
                
            # redo this to make sure that everything is float
            self.data=numpy.array(data,dtype=zip(names,['f8']*len(names)))            
        else:
            if data!=None and names==None:
                error("No names given for the data")

            self.data=numpy.array(map(tuple,data),dtype=zip(names,['f8']*len(names)))

        if self.title!=None:
            self.data.dtype.names=[self.data.dtype.names[0]]+map(lambda x:self.title+" "+x,self.data.dtype.names[1:])

    def names(self):
        return copy.copy(self.data.dtype.names)

    def size(self):
        return self.data.size
    
    def writeCSV(self,fName,
                 delimiter=","):
        """Write data to a CSV-file
        @param fName: Name of the file
        @param delimiter: Delimiter to be used in the CSV-file"""

        f=open(fName,"w")
        f.write(delimiter.join(self.names())+"\n")
        numpy.savetxt(f,self.data,delimiter=delimiter)

    def tRange(self,time=None):
        """Return the range of times
        @param time: name of the time. If None the first column is used"""
        if time==None:
            time=self.names()[0]
        t=self.data[time]

        return (t[0],t[-1])
    
    def join(self,other,time=None,prefix=None):
        """Join this object with another. Assume that they have the same
        amount of rows and that they have one column that designates the
        time and is called the same and has the same values
        @param other: the other array
        @param time: name of the time. If None the first column is used
        @param prefix: String that is added to the other names. If none is given then
        the title is used"""
        if time==None:
            time=self.names()[0]
        if prefix==None:
            prefix=other.title
            if prefix==None:
                prefix="other_"
            else:
                prefix+="_"
                
        t1=self.data[time]
        t2=other.data[time]
        if len(t1)!=len(t2):
            raise WrongDataSize()
        if max(abs(t1-t2))>1e-10:
            error("Times do not have the same values")

        names=[]
        data=[]
        for n in self.names():
            names.append(n)
            data.append(self.data[n])

        for n in other.names():
            if n!=time:
                if n in self.names():
                    names.append(prefix+n)
                else:
                    names.append(n)
                data.append(other.data[n])

        return SpreadsheetData(names=names,
                               data=numpy.array(data).transpose())

    def __add__(self,other):
        """Convinience function for joining data"""
        return self.join(other)

    def append(self,
               name,
               data,
               allowDuplicates=False):
        """Add another column to the data. Assumes that the number of rows is right
        @param name: the name of the column
        @param data: the actual data
        @param allowDuplicates: If the name already exists make it unique by appending _1, _2 ..."""

        arr = numpy.asarray(data)
        newname=name
        if newname in self.names() and allowDuplicates:
            cnt=1
            while newname in self.names():
                newname="%s_%d" % (name,cnt)
                cnt+=1
            warning("Changing name",name,"to",newname,"bacause it already exists in the data")
        newdtype = numpy.dtype(self.data.dtype.descr + [(newname, 'f8')])
        newrec = numpy.empty(self.data.shape, dtype=newdtype)
        for field in self.data.dtype.fields:
            newrec[field] = self.data[field]
            newrec[name] = arr

        self.data=newrec
        
    def __call__(self,
                 t,
                 name,
                 time=None,
                 invalidExtend=False,
                 noInterpolation=False):
        """'Evaluate' the data at a specific time by linear interpolation
        @param t: the time at which the data should be evaluated
        @param name: name of the data column to be evaluated. Assumes that that column
        is ordered in ascending order
        @param time: name of the time column. If none is given then the first column is assumed
        @param invalidExtend: if t is out of the valid range then use the smallest or the biggest value. If False use nan
        @param noInterpolation: if t doesn't exactly fit a data-point return 'nan'"""
        
        if time==None:
            time=self.names()[0]

        x=self.data[time]
        y=self.data[name]
        
        # get extremes
        if t<x[0]:
            if invalidExtend:
                return y[0]
            else:
                return float('nan')
        elif t>x[-1]:
            if invalidExtend:
                return y[-1]
            else:
                return float('nan')
        
        if noInterpolation:
            if t==x[0]:
                return y[0]
            elif t==x[-1]:
                return y[-1]
            
        iLow=0
        iHigh=len(x)-1

        while (iHigh-iLow)>1:
            iNew = iLow + (iHigh-iLow)/2

            if x[iNew]==t:
                # we got lucky
                return y[iNew]
            elif t < x[iNew]:
                iHigh=iNew
            else:
                iLow=iNew
        if noInterpolation:
            return float('nan')
        else:
            return y[iLow] + (y[iHigh]-y[iLow])*(t-x[iLow])/(x[iHigh]-x[iLow])

    def addTimes(self,times,time=None,interpolate=False,invalidExtend=False):
        """Extend the data so that all new times are represented (add rows
        if they are not there)
        @param time: the name of the column with the time
        @param times: the times that shoild be there
        @param interpolate: interpolate the data in new rows. Otherwise
        insert 'nan'
        @param invalidExtend: if t is out of the valid range then use
        the smallest or the biggest value. If False use nan"""

        if time==None:
            time=self.names()[0]

        if len(times)==len(self.data[time]):
            same=True
            for i in range(len(times)):
                if times[i]!=self.data[time][i]:
                    same=False
                    break
            if same:
                # No difference between the times
                return
        
        newData=[]
        otherI=0
        originalI=0
        while otherI<len(times):
            goOn=originalI<len(self.data[time])
            while goOn and times[otherI]>self.data[time][originalI]:
                newData.append(self.data[originalI])
                originalI+=1
                goOn=originalI<len(self.data[time])

            append=True
            if originalI<len(self.data[time]):
                if times[otherI]==self.data[time][originalI]:
                    newData.append(self.data[originalI])
                    originalI+=1
                    otherI+=1
                    append=False
                
            if append:
                t=times[otherI]
                newRow=[]
                for n in self.names():
                    if n==time:
                        newRow.append(t)
                    elif interpolate:
                        newRow.append(self(t,n,time=time,invalidExtend=invalidExtend))
                    else:
                        newRow.append(float('nan'))
                newData.append(newRow)
                otherI+=1

        while originalI<len(self.data[time]):
            newData.append(self.data[originalI])
            originalI+=1

        self.data=numpy.array(map(tuple,newData),dtype=self.data.dtype)
        
    def resample(self,
                 other,
                 name,
                 time=None,
                 invalidExtend=False,
                 extendData=False,
                 noInterpolation=False):
        """Calculate values from another dataset at the same times as in this data-set
        @param other: the other data-set
        @param name: name of the data column to be evaluated. Assumes that that column
        is ordered in ascending order
        @param time: name of the time column. If none is given then the first column is assumed
        @param invalidExtend: see __call__
        @param extendData: if the time range of x is bigger than the range then extend the range before resampling
        @param noInterpolation: if t doesn't exactly fit a data-point return 'nan'"""
        if time==None:
            time=self.names()[0]
            
        if extendData and (
            self.data[time][0] > other.data[time][0] or \
            self.data[time][-1] < other.data[time][-1]):
            pre=[]
            i=0
            while other.data[time][i] < self.data[time][0]:
                data=[]
                for n in self.names():
                    if n==time:
                        data.append(other.data[time][i])
                    else:
                        data.append(float('nan'))
                pre.append(data)
                i+=1
                if i>=len(other.data[time]):
                    break
            if len(pre)>0:
                self.data=numpy.concatenate((numpy.array(map(tuple,pre),dtype=self.data.dtype),self.data))
            
            post=[]
            i=-1
            while other.data[time][i] > self.data[time][-1]:
                data=[]
                for n in self.names():
                    if n==time:
                        data.append(other.data[time][i])
                    else:
                        data.append(float('nan'))
                post.append(data)
                i-=1
                if abs(i)>=len(other.data[time])+1:
                    break
                
            post.reverse()
            if len(post)>0:
                self.data=numpy.concatenate((self.data,numpy.array(map(tuple,post),dtype=self.data.dtype)))

        result=[]
        
        for t in self.data[time]:
            result.append(other(t,name,
                                time=time,
                                invalidExtend=invalidExtend,
                                noInterpolation=noInterpolation))

        return result
    
    def compare(self,other,name,time=None):
        """Compare this data-set with another. The time-points of this dataset are used as
        a reference. Returns a dictionary with a number of norms: maximum absolute
        difference, average absolute difference
        on all timepoints, average absolute difference weighted by time
        @param other: the other data-set
        @param name: name of the data column to be evaluated. Assumes that that column
        is ordered in ascending order
        @param time: name of the time column. If none is given then the first column is assumed"""

        if time==None:
            time=self.names()[0]
            
        x=self.data[time]
        y=self.data[name]
        y2=self.resample(other,name,time=time,invalidExtend=True)
        
        maxDiff=0
        sumDiff=0
        sumWeighted=0
        
        for i,t in enumerate(x):
            val1=y[i]
            val2=y2[i]
            diff=abs(val1-val2)
            maxDiff=max(diff,maxDiff)
            sumDiff+=diff
            weight=0
            if i>0:
                weight+=(t-x[i-1])/2
            if i<(len(x)-1):
                weight+=(x[i+1]-t)/2
            sumWeighted+=weight*diff

        return { "max" : maxDiff,
                 "average" : sumDiff/len(x),
                 "wAverage" : sumWeighted/(x[-1]-x[0]),
                 "tMin": x[0],
                 "tMax": x[-1]}

    def metrics(self,name,time=None):
        """Calculates the metrics for a data set. Returns a dictionary
        with a number of norms: minimum, maximum, average, average weighted by time
        @param name: name of the data column to be evaluated. Assumes that that column
        is ordered in ascending order
        @param time: name of the time column. If none is given then the first column is assumed"""

        if time==None:
            time=self.names()[0]
            
        x=self.data[time]
        y=self.data[name]

        minVal=1e40
        maxVal=-1e40
        sum=0
        sumWeighted=0
        
        for i,t in enumerate(x):
            val=y[i]
            maxVal=max(val,maxVal)
            minVal=min(val,minVal)
            sum+=val
            weight=0
            if i>0:
                weight+=(t-x[i-1])/2
            if i<(len(x)-1):
                weight+=(x[i+1]-t)/2
            sumWeighted+=weight*val

        return { "max" : maxVal,
                 "min" : minVal,
                 "average" : sum/len(x),
                 "wAverage" : sumWeighted/(x[-1]-x[0]),
                 "tMin": x[0],
                 "tMax": x[-1]}
    

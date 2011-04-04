#  ICE Revision: $Id: /local/openfoam/Python/PyFoam/PyFoam/Basics/RestructuredTextHelper.py 6716 2010-06-18T15:41:13.274387Z bgschaid  $ 
"""Helps formatting output for restructured text"""

import os

from PyFoam.Error import error

class RestructuredTextHelper(object):
    """Helper class that formats stuff for restructured text"""

    LevelPart           = 0
    LevelChapter        = 1
    LevelSection        = 2
    LevelSubSection     = 3
    LevelSubSubSection  = 4
    LevelParagraph      = 5
    
    def __init__(self,defaultHeading=LevelSection):
        self.defaultHeading=defaultHeading

    def buildHeading(self,*text,**keywords):
        """General method to build a heading
        @param text: list of items that build the heading text
        @param level: The level of the heading"""

        level=RestructuredTextHelper.LevelSection
        if "level" in keywords:
            level=keywords["level"]
            
        header=None
        for t in text:
            if header==None:
                header=""
            else:
                header+=" "
            header+=str(t)
        overline=False
        if level==RestructuredTextHelper.LevelPart:
            c="#"
            overline=True
        elif level==RestructuredTextHelper.LevelChapter:
            c="*"
            overline=True
        elif level==RestructuredTextHelper.LevelSection:
            c="="
        elif level==RestructuredTextHelper.LevelSubSection:
            c="-"
        elif level==RestructuredTextHelper.LevelSubSubSection:
            c="^"
        elif level==RestructuredTextHelper.LevelParagraph:
            c='"'
        else:
            error("Unknown level",level,"for headers")

        underline=c*len(header)

        result="\n"
        
        if overline:
            result+=underline+"\n"

        result+=header+"\n"
        result+=underline+"\n"

        return result

    def heading(self,*text):
        """Build a heading on the default level"""

        keys={"level":self.defaultHeading}
        
        return self.buildHeading(*text,**keys)

    def table(self):
        """Creates a new ReSTTable-object"""
        return ReSTTable()

class ReSTTable(object):
    """Class that administrates a two-dimensional table and prints it as
    a restructured text-table when asked"""

    def __init__(self):
        self.data=[[]]
        self.lines=set()
        self.head=-1;
        
    def addLine(self,val=None,head=False):
        """Add a line after that row
        @param val: the row after which to add. If None a line will be added after the
        current last row"""
        if val==None:
            now=len(self.data)-1
        else:
            now=int(val)
        self.lines.add(now)
        if head:
            self.head=now
            
    def __str__(self):
        """Output the actual table"""
        widths=[1]*len(self.data[0])
        for r in self.data:
            for i,v in enumerate(r):
                try:
                    widths[i]=max(widths[i],len(v))
                except TypeError:
                    if i==0:
                        widths[i]=max(widths[i],2)
                    else:
                        widths[i]=max(widths[i],1)
                        
        head=None
        for w in widths:
            if head==None:
                head=""
            else:
                head+=" "
            head+="="*w

        inter=head.replace("=","-")
        
        txt=head+"\n"

        for i,r in enumerate(self.data):
            line=""
            for j,v in enumerate(r):
                if v==None or v=="":
                    if j==0:
                        t=".."
                    else:
                        t=""
                else:
                    t=v
                if j>0:
                    line+=" "
                line+=t+" "*(widths[j]-len(t))
            txt+=line+"\n"
            if i==(len(self.data)-1):
                txt+=head+"\n"
            elif i in self.lines:
                if i==self.head:
                    txt+=head+"\n"
                else:
                    txt+=inter+"\n"
                
        return "\n"+txt
    
    def __setitem__(self,index,value):
        """Sets an item of the table
        @param index: a tuple with a row and a column. If it is a single integer then the
        row is assumed
        @param value: the value to set. If only the row was specified it is a list with the column
        values"""

        try:
            row,col=index
            self.setElement(row,col,value)
        except TypeError:
            row=index
            for col,v in enumerate(value):
                self.setElement(row,col,v)
                
    def setElement(self,row,col,value):
        """Sets a specific element
        @param row: the row
        @param col: column
        @param value: the used value"""
        
        if len(self.data)<=row:
            self.data+=[[None]*len(self.data[0])]*(row-len(self.data)+1)
        if len(self.data[row])<=col:
            for r in self.data:
                r+=[None]*(col-len(r)+1)

        self.data[row][col]=str(value)
        

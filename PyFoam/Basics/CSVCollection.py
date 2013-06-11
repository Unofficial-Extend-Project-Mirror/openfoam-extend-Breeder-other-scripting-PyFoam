#  ICE Revision: $Id: $ 
"""
Collects data and writes it to a CSV-file
"""

import csv

class CSVCollection(object):
    """
    Collects data like a dictionary. Writes it to a line in a CSV-file.
    If the dictionary is extended the whole file is rewritten
    """
    def __init__(self,name):
        """@param name: name of the file"""
        self.name=name
        self.headers=[]
        self.headerDict={}
        self.data=[self.headerDict]
        self.current={}
        self.file=None
        self.writer=None
        self.renew=True
        
    def __setitem__(self,key,value):
        """Sets a value in the current dataset
        @param key: the key
        @param value: and it's value"""

        if not key in self.headers:
            self.headers.append(key)
            self.renew=True
            self.headerDict[key]=key

        self.current[key]=value

    def write(self):
        """Writes a line to disk and starts a new one"""
        
        self.data.append(self.current)
        if self.renew:
            if self.file!=None:
                self.file.close()
            self.file=file(self.name,"w")
            self.writer=csv.DictWriter(self.file,self.headers)
            self.writer.writerows(self.data)
            self.renew=False
        else:
            self.writer.writerow(self.current)
        self.current={}
        self.file.flush()
        
    def clear(self):
        """Resets the last line"""
        self.current={}

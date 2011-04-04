#  ICE Revision: $Id: /local/openfoam/Python/PyFoam/PyFoam/Basics/Helpers.py 1532 2007-06-29T11:15:55.577361Z bgschaid  $ 
"""Utility functions"""

from os import listdir

def getLinearNames(d):
    """get a list of all the files with information about the
    residuals of the linear solver (only the ones without _2 etc

    d - the directory"""
    names=[]
    for f in listdir(d):
        tmp=f.split("_")
        if len(tmp)>1:
            if tmp[0]=="linear":
                name=tmp[1]
                if names.count(name)==0:
                    names.append(name)
                    
    return names

        
    

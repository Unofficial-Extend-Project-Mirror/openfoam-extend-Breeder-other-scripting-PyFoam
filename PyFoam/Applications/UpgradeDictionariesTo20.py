#  ICE Revision: $Id: /local/openfoam/Python/PyFoam/PyFoam/Applications/UpgradeDictionariesTo20.py 7660 2012-01-07T16:44:40.128256Z bgschaid  $ 
"""
Application class that implements pyFoamUpgradeDictionariesTo20
"""

import sys,re
from os import path

from UpgradeDictionariesTo17 import UpgradeDictionariesTo17,DictionaryUpgradeInfo

from PyFoam.RunDictionary.ParsedParameterFile import ParsedParameterFile
from PyFoam.Basics.DataStructures import DictProxy,TupleProxy
from PyFoam.Error import error,warning

class BlockMeshUpgradeInfo(DictionaryUpgradeInfo):
    def __init__(self):
        DictionaryUpgradeInfo.__init__(self)

    def location(self):
        return path.join("constant","polyMesh","blockMeshDict")

    def checkUpgrade(self,content):
        return "boundary" not in content

    def manipulate(self,content):
        p=content["patches"]
        bnd=[]
        for t,n,f in zip(p[0::3],p[1::3],p[2::3]):
            bnd+=[ n, { "type" : t,
                        "faces" : f }]
        content["boundary"]=bnd
        
class ThermophysicalUpgradeInfo(DictionaryUpgradeInfo):
    def __init__(self):
        DictionaryUpgradeInfo.__init__(self)

    def location(self):
        return path.join("constant","thermophysicalProperties")

    def analyzeThermoType(self,content):
        return content["thermoType"].replace('>','').split('<')
    
    def checkUpgrade(self,content):
        tt=self.analyzeThermoType(content)
        if len(tt)!=6:
            return False

        for nm in content:
            data=content[nm]
            if type(data) in  [tuple,TupleProxy]:
                if len(data)>4: # Maybe there is a better criterium
                    return True
            
        return False

    def manipulate(self,content):
        what,mix,trans,spec,therm,gas=self.analyzeThermoType(content)
        for nm in content:
            data=content[nm]
            used=0

            if type(data) not in  [tuple,TupleProxy]:
                continue
            if len(data)<5:
                continue

            transDict={}
            if trans=="constTransport":
                transDict["Pr"]=data[-1-used]
                transDict["mu"]=data[-2-used]
                used+=2
            elif trans=="sutherlandTransport":
                transDict["Ts"]=data[-1-used]
                transDict["As"]=data[-2-used]
                used+=2
            else:
                error("Transport type",trans,"not implemented")
                
            thermDict={}
            if therm=="hConstThermo":
                thermDict["Hf"]=data[-1-used]
                thermDict["Cp"]=data[-2-used]
                used+=2
            elif therm=="eConstThermo":
                thermDict["Hf"]=data[-1-used]
                thermDict["Cv"]=data[-2-used]
                used+=2
            elif therm=="janafThermo":
                thermDict["lowCpCoeffs"]=data[-7-used:-0-used]
                thermDict["highCpCoeffs"]=data[-14-used:-7-used]
                thermDict["Tcommon"]=data[-15-used]
                thermDict["Thigh"]=data[-16-used]
                thermDict["Tlow"]=data[-17-used]
                used+=2*7+3
            else:
                error("Thermodynamics type",therm,"not implemented")

            specDict={}
            if spec=="specieThermo":
                specDict["molWeight"]=data[-1-used]
                specDict["nMoles"]=data[-2-used]
                used+=2
            else:
                error("Specie type",spec,"not implemented")

            if len(data)!=used+1:
                warning("Not all data for",nm,"used")

            comment=self.makeComment(data)
            content[nm]={"specie":specDict,
                         "thermodynamics":thermDict,
                         "transport":transDict}
            content.addDecoration(nm,comment)
            
##            gasDict={}
##            if gas=="perfectGas":
##                pass
##            else:
##                error("Gas type",gas,"not implemented")
            
class UpgradeDictionariesTo20(UpgradeDictionariesTo17):
    def __init__(self,args=None):
        description="""\
Examines dictionaries in a case and tries to upgrade them to a form
that is compatible with OpenFOAM 2.0
        """
        
        UpgradeDictionariesTo17.__init__(self,
                                         args=args,
                                         description=description)
        
    def addDicts(self):
        UpgradeDictionariesTo17.addDicts(self)
        
        self.dicts.append(BlockMeshUpgradeInfo())
        self.dicts.append(ThermophysicalUpgradeInfo())

##    def addOptions(self):
##        UpgradeDictionariesTo17.addOptions(self)
    

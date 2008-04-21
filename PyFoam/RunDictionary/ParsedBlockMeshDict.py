#  ICE Revision: $Id$ 
"""A parsed blockMeshDict"""

from ParsedParameterFile import ParsedParameterFile

class ParsedBlockMeshDict(ParsedParameterFile):
    """ A parsed version of a blockMeshDict-file. Adds some
    convenience-methods to access parts of the file"""

    def __init__(self,name,backup=False,debug=False):
        ParsedParameterFile.__init__(self,name,backup=backup,debug=debug)
        
    def convertToMeters(self):
        return float(self["convertToMeters"])
    
    def vertices(self):
        factor=self.convertToMeters()
        return map(lambda x:map(lambda y:float(y)*factor,x),self["vertices"])

    def blocks(self):
        result=[]
        i=1
        while i<len(self["blocks"]):
            result.append(map(int,self["blocks"][i]))
            if type(self["blocks"][i+1])==str:
                i+=6
            else:
                i+=5
            
        return result

    def patches(self):
        result={}
        for i in range(1,len(self["patches"]),3):
            result[self["patches"][i]]=map(lambda x:map(int,x),self["patches"][i+1])
            
        return result

    def arcs(self):
        factor=self.convertToMeters()
        result=[]
        for i in range(len(self["edges"])):
            if str(self["edges"][i])=='arc':
                result.append((int(self["edges"][i+1]),
                               map(lambda y:float(y)*factor,self["edges"][i+3]),
                               int(self["edges"][i+2])))
        return result
    
    def getBounds(self):
        v=self.vertices()
        mi=[ 1e10, 1e10, 1e10]
        ma=[-1e10,-1e10,-1e10]
        for p in v:
            for i in range(3):
                mi[i]=min(p[i],mi[i])
                ma[i]=max(p[i],ma[i])
        return mi,ma

    def typicalLength(self):
        mi,ma=self.getBounds()

        biggest=max(ma[0]-mi[0],ma[1]-mi[1],ma[2]-mi[2])
        smallest=min(ma[0]-mi[0],ma[1]-mi[1],ma[2]-mi[2])

        #        return 2*biggest*smallest/(biggest+smallest)
        return (biggest+smallest)/2

#! /usr/bin/env python

from PyFoam.Infrastructure.CTestRun import CTestRun

class MulitRegionHeater(CTestRun):
    def init(self):
        self.setParameters(solver="chtMultiRegionFoam",
                           originalCase="$FOAM_TUTORIALS/heatTransfer/chtMultiRegionFoam/multiRegionLiquidHeater",
                           sizeClass="small")

        self.addToClone("makeCellSets.setSet")

    def meshPrepare(self):
        self.shell("rm -rf constant/polyMesh/sets")

        self.execute("blockMesh")

        self.shell("setSet -batch makeCellSets.setSet")

        self.shell("rm -f constant/polyMesh/sets/*_old")

        self.execute("setsToZones -noFlipMap")
        self.execute("splitMeshRegions -cellZones -overwrite")

        self.shell("""
# remove fluid fields from solid regions (important for post-processing)
for i in heater leftSolid rightSolid
do
   rm -f 0*/$i/{mut,alphat,epsilon,k,p_rgh,p,U}
done

# remove solid fields from fluid regions (important for post-processing)
for i in bottomWater topAir
do
   rm -f 0*/$i/{cp,K,rho}
done

for i in bottomWater topAir heater leftSolid rightSolid
do
   changeDictionary -region $i > log.changeDictionary.$i 2>&1
done
""")

    def casePrepare(self):
        self.status("Modifying controlDict")
        self.controlDict()["endTime"]=10
        self.controlDict()["writeInterval"]=5
        self.controlDict().writeFile()

if __name__=='__main__':
    MulitRegionHeater().run()

#! /usr/bin/env python

from PyFoam.Infrastructure.CTestRun import CTestRun
from PyFoam.Applications.SamplePlot import SamplePlot
from PyFoam.Basics.Data2DStatistics import Data2DStatistics

class BasicPitzDailyRun(CTestRun):
    def init(self):
        self.setParameters(solver="simpleFoam",
                           originalCase="$FOAM_TUTORIALS/incompressible/simpleFoam/pitzDaily",
                           sizeClass="small",
                           referenceData="PitzDailyData",
                           # headLength=7,
                           # tailLength=5,
                           velocityRelativeTolerance=1e-3,
                           velocityAbsoluteTolerance=1e-3,
                           minimumRunTime=100)

    def postprocess(self):
        self.execute("sample")

    def casePrepare(self):
        self.status("Modifying controlDict")
        self.controlDict()["endTime"]=2000
        self.controlDict().writeFile()

    def postRunTestCheckConverged(self):
        self.isNotEqual(
            value=self.runInfo()["time"],
            target=self.controlDict()["endTime"],
#            tolerance=1e-2,
            message="Reached endTime -> not converged")

    def postRunTestVelocityProfiles(self):
        comparison=self.compareSamples(
            data="sets",
            reference="referenceSet",
            fields=["U"])
        print
        print "Relative error on sample lines"
        print comparison.relativeError()
        self.isEqual(
            value=comparison.relativeError().max(),
            tolerance=self["velocityRelativeTolerance"],
            message="Relative error of fluid velocity")
        
    def postRunTestVelocityProfilesAbsolute(self):
        comparison=self.compareSamples(
            data="sets",
            reference="referenceSet",
            fields=["U"])
        print
        print "Absolute error on sample lines"
        print comparison.compare()["max"]
        self.isEqual(
            value=comparison.compare()["max"].max(),
            tolerance=self["velocityAbsoluteTolerance"],
            message="Absolute error of fluid velocity")
        
    def postRunTestVelocityProfilesOldSchool(self):
        # Just as an example how to do it detailed
        sample=SamplePlot(args=[self.caseDir,
                                "--silent",
                                "--dir=sets",
                                "--reference-dir=referenceSet",
                                "--latest-time",
                                "--tolerant-reference-time",
                                "--field=U",
                                "--compare",
                                "--metrics"])
        stat=Data2DStatistics(metrics=sample["metrics"],
                              compare=sample["compare"],
                              noStrings=True)
        relError=stat.relativeError()
        for l in relError.columns():
            for com in relError.rows():
                self.isEqual(
                    value=relError[(com,l)],
                    tolerance=self["velocityRelativeTolerance"],
                    message="Match velocty component %s on line %s" % (com,l))

    def postRunTestPressureDifference(self):
        self.isEqual(
            value=self.runInfo()["analyzed"]["deltaP"]["avg"],
            target=-5.17507, # according to the 2.1-solver
            tolerance=0.1,
            message="Pressure difference between inlet and outlet")

if __name__=='__main__':
    BasicPitzDailyRun().run()

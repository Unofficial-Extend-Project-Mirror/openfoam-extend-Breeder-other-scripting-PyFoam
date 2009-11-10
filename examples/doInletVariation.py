"""Example for an automatic variation of an inlet-Parameter. Runs the solver
and after it has finished runs utilies that postprocess the output.
Collects some results"""

from PyFoam.Execution.ConvergenceRunner import ConvergenceRunner
from PyFoam.Execution.UtilityRunner import UtilityRunner
from PyFoam.LogAnalysis.BoundingLogAnalyzer import BoundingLogAnalyzer
from PyFoam.RunDictionary.SolutionFile import SolutionFile
from PyFoam.RunDictionary.SolutionDirectory import SolutionDirectory

solver="simpleFoam"
case="pitzDaily"
pCmd="calcPressureDifference"
mCmd="calcMassFlow"

dire=SolutionDirectory(case,archive="InletVariation")
dire.clearResults()
dire.addBackup("PyFoamSolve.logfile")
dire.addBackup("PyFoamSolve.analyzed")
dire.addBackup("Pressure.analyzed")
dire.addBackup("MassFlow.analyzed")

sol=SolutionFile(dire.initialDir(),"U")

maximum=1.
nr=10

f=dire.makeFile("InflowVariationResults")

for i in range(nr+1):
    # Set the boundary condition at the inlet
    val=(maximum*i)/nr
    print "Inlet velocity:",val
    sol.replaceBoundary("inlet","(%f 0 0)" %(val))

    # Run the solver
    run=ConvergenceRunner(BoundingLogAnalyzer(),argv=[solver,"-case",case],silent=True)
    run.start()
    
    print "Last Time = ",dire.getLast()

    # Get the pressure difference (Using an external utility)
    pUtil=UtilityRunner(argv=[pCmd,"-case",case],silent=True,logname="Pressure")
    pUtil.add("deltaP","Pressure at .* Difference .*\] (.+)")
    pUtil.start()

    deltaP=pUtil.get("deltaP")[0]

    # Get the mass flow
    mUtil=UtilityRunner(argv=[mCmd,"-case",case,"-latestTime"],silent=True,logname="MassFlow")
    mUtil.add("mass","Flux at (.+?) .*\] (.+)",idNr=1)
    mUtil.start()

    massFlow=mUtil.get("mass",ID="outlet")[0]

    # Archive the results
    dire.lastToArchive("vel=%g" % (val))

    # Clear results
    dire.clearResults()

    # Output current stuff
    print "Vel: ",val,"DeltaP: ",deltaP,"Mass Flow:",massFlow
    f.writeLine( (val,deltaP,massFlow) )
    
sol.purgeFile()

    

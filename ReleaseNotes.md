<div id="table-of-contents">
<h2>Table of Contents</h2>
<div id="text-table-of-contents">
<ul>
<li><a href="#sec-1">1. Version 0.6.4 - 2014-11-24</a>
<ul>
<li><a href="#sec-1-1">1.1. Requirements</a></li>
<li><a href="#sec-1-2">1.2. Future changes</a>
<ul>
<li><a href="#sec-1-2-1">1.2.1. Redundant utilities <code>pyFoamJoinCSV.py</code> and <code>pyFoamConvertToCSV.py</code> unified</a></li>
</ul>
</li>
<li><a href="#sec-1-3">1.3. Major changes</a>
<ul>
<li><a href="#sec-1-3-1">1.3.1. Multi-line regular expressions in <code>customRegexp</code></a></li>
<li><a href="#sec-1-3-2">1.3.2. Enhancement of <code>pyFoamPrepare.py</code></a></li>
<li><a href="#sec-1-3-3">1.3.3. Enhancements of the CSV-utilities</a></li>
<li><a href="#sec-1-3-4">1.3.4. Environment variable <code>PYFOAM_SITE_DIR</code> and <code>PYFOAM_DIR</code></a></li>
</ul>
</li>
<li><a href="#sec-1-4">1.4. Incompatibilities</a>
<ul>
<li><a href="#sec-1-4-1">1.4.1. Option <code>--silent</code> removed from <code>pyFoamPrepareCase.py</code></a></li>
<li><a href="#sec-1-4-2">1.4.2. Keys in <code>RunDatabase</code> with column-names that contain upper-case letters change</a></li>
<li><a href="#sec-1-4-3">1.4.3. Change in unique variable names in <code>pyFoamConvertToCSV.py</code></a></li>
<li><a href="#sec-1-4-4">1.4.4. <code>PyFoam.IPython</code>-module renamed to <code>PyFoam.IPythonHelpers</code></a></li>
</ul>
</li>
<li><a href="#sec-1-5">1.5. Bugfixes</a>
<ul>
<li><a href="#sec-1-5-1">1.5.1. Templates in <code>pyFoamPrepareCase.py</code> did not keep permissions</a></li>
<li><a href="#sec-1-5-2">1.5.2. <code>pyFoamComparator.py</code> failed due to circular dependency</a></li>
<li><a href="#sec-1-5-3">1.5.3. <code>pyFoamDumpRunDatabaseToCSV.py</code> fails if Pandas-data is requested</a></li>
<li><a href="#sec-1-5-4">1.5.4. <code>sort</code> for list broke code on Python 3</a></li>
<li><a href="#sec-1-5-5">1.5.5. Changing the OF-version does not work in Python 3</a></li>
<li><a href="#sec-1-5-6">1.5.6. <code>addData</code> in <code>PyFoamDataFrame</code> extrapolates for invalid values</a></li>
<li><a href="#sec-1-5-7">1.5.7. <code>--keep-last</code> did not work for <code>pyFoamClearCase.py</code> and parallel cases</a></li>
<li><a href="#sec-1-5-8">1.5.8. <code>pyFoamDumpRunDatabaseToCSV.py</code> does not add basic run information</a></li>
<li><a href="#sec-1-5-9">1.5.9. Restore of <code>FileBasisBackup</code> did not work</a></li>
<li><a href="#sec-1-5-10">1.5.10. Remove circular dependency in <code>DataStructures</code></a></li>
</ul>
</li>
<li><a href="#sec-1-6">1.6. New features/Utilities</a>
<ul>
<li><a href="#sec-1-6-1">1.6.1. <code>pyFoamRunParameterVariation.py</code></a></li>
<li><a href="#sec-1-6-2">1.6.2. <code>pyFoamBinarySize.py</code></a></li>
<li><a href="#sec-1-6-3">1.6.3. <code>pyFoamBlockMeshRewrite.py</code></a></li>
</ul>
</li>
<li><a href="#sec-1-7">1.7. Enhancements to Utilities</a>
<ul>
<li><a href="#sec-1-7-1">1.7.1. <code>pyFoamChangeBoundaryType.py</code> allows setting additional values</a></li>
<li><a href="#sec-1-7-2">1.7.2. <code>pyFoamPrepareCase.py</code> now has OF-version and fork as defined variables</a></li>
<li><a href="#sec-1-7-3">1.7.3. <code>pyFoamPrepareCase.py</code> now allows "overloading" another directory</a></li>
<li><a href="#sec-1-7-4">1.7.4. <code>pyFoamIPythonNotebook.py</code> adds improvements to the notebook</a></li>
<li><a href="#sec-1-7-5">1.7.5. <code>pyFoamListCases.py</code> more tolerant to faulty <code>controlDict</code></a></li>
<li><a href="#sec-1-7-6">1.7.6. <code>pyFoamDumpConfiguration.py</code> prints sections and keys alphabetically</a></li>
<li><a href="#sec-1-7-7">1.7.7. <code>pyFoamJoinCSV.py</code> and <code>pyFoamConvertToCSV.py</code> read and write Excel-files</a></li>
<li><a href="#sec-1-7-8">1.7.8. Flexible variable filtering in <code>pyFoamJoinCSV.py</code> and <code>pyFoamConvertToCSV.py</code></a></li>
<li><a href="#sec-1-7-9">1.7.9. Columns in <code>pyFoamJoinCSV.py</code> and <code>pyFoamConvertToCSV.py</code> can be recalculated</a></li>
<li><a href="#sec-1-7-10">1.7.10. Testing for <code>Numeric</code> removed from <code>pyFoamVersion.py</code></a></li>
</ul>
</li>
<li><a href="#sec-1-8">1.8. Enhancements to the Library</a>
<ul>
<li><a href="#sec-1-8-1">1.8.1. Subclass of <code>ClusterJob</code> that support <code>PrepareCase</code></a></li>
<li><a href="#sec-1-8-2">1.8.2. Subclass of <code>ClusterJob</code> that support <code>RunParameterVariation</code></a></li>
<li><a href="#sec-1-8-3">1.8.3. <code>execute</code> in <code>PyFoam/Utilities</code> fails if script is not executable</a></li>
<li><a href="#sec-1-8-4">1.8.4. <code>foamVersion</code> uses a separate wrapper class for <code>tuple</code></a></li>
<li><a href="#sec-1-8-5">1.8.5. Move calculation of disk usage to <code>Utilities</code></a></li>
<li><a href="#sec-1-8-6">1.8.6. Enhancement of <code>--help</code></a></li>
<li><a href="#sec-1-8-7">1.8.7. <code>which</code>-routine in <code>Utitlities</code> uses native Python-routine</a></li>
<li><a href="#sec-1-8-8">1.8.8. <code>FileBasis</code> now allows file handles instead of the filename</a></li>
<li><a href="#sec-1-8-9">1.8.9. <code>BlockMesh</code> doesn't force writing to file anymore</a></li>
<li><a href="#sec-1-8-10">1.8.10. Additional methods for <code>BlockMesh</code>-class</a></li>
<li><a href="#sec-1-8-11">1.8.11. <code>LineReader</code> allows keeping spaces on left</a></li>
<li><a href="#sec-1-8-12">1.8.12. <code>TemplateFile</code> now allows writing of assignment-results in file</a></li>
<li><a href="#sec-1-8-13">1.8.13. <code>SolverJob</code> now allows passing of parameters to the solver</a></li>
<li><a href="#sec-1-8-14">1.8.14. <code>SpreadsheetData</code> now allows reading from an Excel file</a></li>
<li><a href="#sec-1-8-15">1.8.15. <code>SpreadsheetData</code> allows recalculating columns</a></li>
</ul>
</li>
<li><a href="#sec-1-9">1.9. Known bugs</a>
<ul>
<li><a href="#sec-1-9-1">1.9.1. Timelines not forgotten for multiple runner calls</a></li>
</ul>
</li>
</ul>
</li>
<li><a href="#sec-2">2. Version 0.6.3 - 2014-06-23</a>
<ul>
<li><a href="#sec-2-1">2.1. Requirements</a></li>
<li><a href="#sec-2-2">2.2. Major changes</a>
<ul>
<li><a href="#sec-2-2-1">2.2.1. Version changing supports forks of OpenFOAM</a></li>
</ul>
</li>
<li><a href="#sec-2-3">2.3. Incompatibilities</a>
<ul>
<li><a href="#sec-2-3-1">2.3.1. Change of command interface of <code>pyFoamSTLUtility.py</code></a></li>
<li><a href="#sec-2-3-2">2.3.2. If <code>0.org</code> is present <code>pyFoamCloneCase.py</code> and <code>pyFoamPackCase.py</code> ignore <code>0</code></a></li>
</ul>
</li>
<li><a href="#sec-2-4">2.4. Bugfixes</a>
<ul>
<li><a href="#sec-2-4-1">2.4.1. PlotWatcher has long times between updates if pickling takes long</a></li>
<li><a href="#sec-2-4-2">2.4.2. <code>pyFoamPVSnapshot.py</code> fails for newer paraview-versions</a></li>
<li><a href="#sec-2-4-3">2.4.3. SamplePlot failed when valueNames are unspecified</a></li>
<li><a href="#sec-2-4-4">2.4.4. <code>pyFoamTimelinePlot.py</code> failed Numpy/Pandas output of vector fields</a></li>
<li><a href="#sec-2-4-5">2.4.5. <code>alternateAxis</code> ignored for slave</a></li>
<li><a href="#sec-2-4-6">2.4.6. <code>pyFoamCaseReport.py</code> more stable for binary <code>boundary</code>-files</a></li>
<li><a href="#sec-2-4-7">2.4.7. <code>SpreadsheetData</code> returns data which breaks certain Pandas-operations</a></li>
<li><a href="#sec-2-4-8">2.4.8. <code>pyFoamCloneCase.py</code> added duplicates to the archive</a></li>
<li><a href="#sec-2-4-9">2.4.9. <code>nonuniform</code> of length 3 not correctly printed</a></li>
</ul>
</li>
<li><a href="#sec-2-5">2.5. New features/Utilities</a>
<ul>
<li><a href="#sec-2-5-1">2.5.1. <code>pyFoamPrepareCase.py</code> for case preparation</a></li>
<li><a href="#sec-2-5-2">2.5.2. <code>pyFoamIPythonNotebook.py</code> for generating and manipulating IPython-notebooks</a></li>
<li><a href="#sec-2-5-3">2.5.3. Additional sub-module <code>PyFoam.IPython</code></a></li>
<li><a href="#sec-2-5-4">2.5.4. Additional sub-module <code>PyFoam.Wrappers</code></a></li>
</ul>
</li>
<li><a href="#sec-2-6">2.6. Enhancements to Utilities</a>
<ul>
<li><a href="#sec-2-6-1">2.6.1. <code>pyFoamSampleplot</code> has option to use index instead of time in filenames</a></li>
<li><a href="#sec-2-6-2">2.6.2. <code>pyFoamListCases.py</code> Allows addition of custom data</a></li>
<li><a href="#sec-2-6-3">2.6.3. Switch compiler versions</a></li>
<li><a href="#sec-2-6-4">2.6.4. <code>pyFoamVersion.py</code> reports the installed versions better</a></li>
<li><a href="#sec-2-6-5">2.6.5. Offscreen rendering can be switched off in <code>pyFoamPVSnapshot.py</code></a></li>
<li><a href="#sec-2-6-6">2.6.6. Write 3D-data in <code>pyFoamPVSnapshot.py</code></a></li>
<li><a href="#sec-2-6-7">2.6.7. Added capabilities to <code>pyFoamSTLUtility</code></a></li>
<li><a href="#sec-2-6-8">2.6.8. <code>pyFoamDecomposer.py</code> switches off function objects</a></li>
<li><a href="#sec-2-6-9">2.6.9. <code>pyFoamCloneCase.py</code> clones more stuff</a></li>
</ul>
</li>
<li><a href="#sec-2-7">2.7. Enhancements to the Library</a>
<ul>
<li><a href="#sec-2-7-1">2.7.1. <code>BasicRunner</code> now can print the command line that is actually used</a></li>
<li><a href="#sec-2-7-2">2.7.2. <code>ClusterJob</code> now can live without a machinefile</a></li>
<li><a href="#sec-2-7-3">2.7.3. Enhanced treatment of symlinks during cloning</a></li>
<li><a href="#sec-2-7-4">2.7.4. <code>AnalyzedCommon</code> clears the <code>analyzed</code>-directory</a></li>
<li><a href="#sec-2-7-5">2.7.5. <code>TimelineDirectory</code> is more tolerant</a></li>
<li><a href="#sec-2-7-6">2.7.6. Possibility of a subcommand-interface for utilities</a></li>
<li><a href="#sec-2-7-7">2.7.7. <code>STLUtility</code> accepts file-handles</a></li>
<li><a href="#sec-2-7-8">2.7.8. <code>addClone</code> in <code>SolutionDirectory</code> accepts glob patterns</a></li>
<li><a href="#sec-2-7-9">2.7.9. <code>execute</code> in <code>Utilities</code> allows specification of working directory and echoing of output</a></li>
<li><a href="#sec-2-7-10">2.7.10. <code>rmtree</code> and <code>copytree</code> more tolerant</a></li>
<li><a href="#sec-2-7-11">2.7.11. Enhanced support for booleans in the parser</a></li>
<li><a href="#sec-2-7-12">2.7.12. Application classes now allow specifying options as keyword parameters</a></li>
<li><a href="#sec-2-7-13">2.7.13. <code>SolutionDirector</code> now can classify directories in the <code>postProcessing</code>-directory</a></li>
<li><a href="#sec-2-7-14">2.7.14. <code>pyFoamSamplePlot.py</code> now more flexible for distributions</a></li>
<li><a href="#sec-2-7-15">2.7.15. <code>DictProxy</code> now has a <code>dict</code>-like <code>update</code>-method</a></li>
<li><a href="#sec-2-7-16">2.7.16. <code>FoamFileGenerator</code> automatically quotes strings</a></li>
<li><a href="#sec-2-7-17">2.7.17. Children of <code>FileBasis</code> now can be used with the <code>with</code>-statement</a></li>
</ul>
</li>
</ul>
</li>
<li><a href="#sec-3">3. Version 0.6.2 - 2013-11-03</a>
<ul>
<li><a href="#sec-3-1">3.1. Major changes</a>
<ul>
<li><a href="#sec-3-1-1">3.1.1. Use of <code>pandas</code>-library</a></li>
</ul>
</li>
<li><a href="#sec-3-2">3.2. Incompatibilities</a>
<ul>
<li><a href="#sec-3-2-1">3.2.1. Different separator for databases in CSV-files</a></li>
<li><a href="#sec-3-2-2">3.2.2. Change of independent variable name in sample data</a></li>
</ul>
</li>
<li><a href="#sec-3-3">3.3. Bugfixes</a>
<ul>
<li><a href="#sec-3-3-1">3.3.1. <code>pyFoamPackCase.py</code> does not handle symbolic links correctly</a></li>
<li><a href="#sec-3-3-2">3.3.2. <code>pyFoamPotentialRunner.py</code> not working with OpenFOAM 2.0 or newer</a></li>
<li><a href="#sec-3-3-3">3.3.3. <code>pyFoamListCase.py</code> fails with <code>controlDict</code> that use preprocessing</a></li>
<li><a href="#sec-3-3-4">3.3.4. Cloning fails in symlink-mode if files are specified twice</a></li>
</ul>
</li>
<li><a href="#sec-3-4">3.4. Utilities</a>
<ul>
<li><a href="#sec-3-4-1">3.4.1. <code>pyFoamPotentialRunner.py</code> now allows removing of <code>functions</code> and <code>libs</code></a></li>
<li><a href="#sec-3-4-2">3.4.2. The Runner-utilities now have more options for clearing</a></li>
</ul>
</li>
<li><a href="#sec-3-5">3.5. Library</a>
<ul>
<li><a href="#sec-3-5-1">3.5.1. <code>SolutionDirectory</code> and <code>TimeDirectory</code> are more tolerant</a></li>
<li><a href="#sec-3-5-2">3.5.2. <code>ClusterJob</code> now handles template files</a></li>
<li><a href="#sec-3-5-3">3.5.3. Additional parameters in <code>ClusterJob</code></a></li>
<li><a href="#sec-3-5-4">3.5.4. Custom data in directory easier accessible</a></li>
<li><a href="#sec-3-5-5">3.5.5. <code>SolverJob</code> now allows compression of output</a></li>
<li><a href="#sec-3-5-6">3.5.6. <code>PyFoamApplication</code>-class now allows quick access to data</a></li>
</ul>
</li>
<li><a href="#sec-3-6">3.6. New features/Utilities</a>
<ul>
<li><a href="#sec-3-6-1">3.6.1. Post-run hook that sends mail at the end of run</a></li>
<li><a href="#sec-3-6-2">3.6.2. New utility <code>pyFoamCompressCases.py</code></a></li>
<li><a href="#sec-3-6-3">3.6.3. Paraview-module to read additional data</a></li>
</ul>
</li>
<li><a href="#sec-3-7">3.7. Enhancements</a>
<ul>
<li><a href="#sec-3-7-1">3.7.1. <code>pyFoamRedoPlot.py</code> can plot in XKCD-mode</a></li>
<li><a href="#sec-3-7-2">3.7.2. <code>pyFoamListCases.py</code> now displays disk usage in human readable form</a></li>
<li><a href="#sec-3-7-3">3.7.3. <code>pyFoamClearCase.py</code> more flexible in selection of data to be removed</a></li>
<li><a href="#sec-3-7-4">3.7.4. <code>pyFoamFromTemplate.py</code> automatically chooses template and default values</a></li>
<li><a href="#sec-3-7-5">3.7.5. <code>pyFoamDumpRunDatabaseToCSV.py</code> can disable standard-fields</a></li>
<li><a href="#sec-3-7-6">3.7.6. <code>pyFoamDumpRunDatabaseToCSV.py</code> prints <code>pandas</code>-object</a></li>
<li><a href="#sec-3-7-7">3.7.7. Better debugging with <code>ipdb</code></a></li>
<li><a href="#sec-3-7-8">3.7.8. Interactive shell after execution for utilities</a></li>
<li><a href="#sec-3-7-9">3.7.9. Utilities that read quantitative data convert to <code>pandas</code>-data and/or <code>numpy</code></a></li>
<li><a href="#sec-3-7-10">3.7.10. Utilities that read quantitative data write Excel files</a></li>
<li><a href="#sec-3-7-11">3.7.11. Specify additional settings for <code>GnuPlot</code> in <code>customRegexp</code></a></li>
<li><a href="#sec-3-7-12">3.7.12. More flexible data specification for <code>pyFoamSamplePlot.py</code></a></li>
<li><a href="#sec-3-7-13">3.7.13. <code>pyFoamSamplePlot.py</code> now allows specification of x-range</a></li>
</ul>
</li>
</ul>
</li>
<li><a href="#sec-4">4. Version 0.6.1 - 2013-05-24</a>
<ul>
<li><a href="#sec-4-1">4.1. Major changes</a></li>
<li><a href="#sec-4-2">4.2. Bugfixes</a>
<ul>
<li><a href="#sec-4-2-1">4.2.1. Restoring of <code>controlDict</code> after <code>write</code></a></li>
<li><a href="#sec-4-2-2">4.2.2. Custom-plot type <code>slave</code> not working if no <code>master</code> defined</a></li>
<li><a href="#sec-4-2-3">4.2.3. <code>-list-only</code> did not correctly parse lists with a numeric prefix</a></li>
</ul>
</li>
<li><a href="#sec-4-3">4.3. Utilities</a>
<ul>
<li><a href="#sec-4-3-1">4.3.1. <code>pyFoamBuildHelper.py</code> now allow more than one action</a></li>
<li><a href="#sec-4-3-2">4.3.2. Utilities warn if OpenFOAM-version is unset</a></li>
<li><a href="#sec-4-3-3">4.3.3. <code>pyFoamUpgradeDictionariesTo20.py</code> allows single files</a></li>
<li><a href="#sec-4-3-4">4.3.4. <code>pyFoamUpgradeDictionariesTo20.py</code> transforms reaction-schemes</a></li>
<li><a href="#sec-4-3-5">4.3.5. <code>pyFoamUpgradeDictionariesTo20.py</code> transforms thermophysical data</a></li>
<li><a href="#sec-4-3-6">4.3.6. <code>pyFoamCloneCase</code> now allows creating directory that symlinks to the original</a></li>
<li><a href="#sec-4-3-7">4.3.7. <code>pyFoamClearCase.py</code> now removes <code>postProcessing</code> and allows removal of additional files</a></li>
<li><a href="#sec-4-3-8">4.3.8. Improvements to <code>pyFoamVersion.py</code></a></li>
<li><a href="#sec-4-3-9">4.3.9. Additional files automatically cloned</a></li>
<li><a href="#sec-4-3-10">4.3.10. <code>pyFoamDisplayBlockMesh.py</code> uses the same options for template format as <code>pyFoamFromTemplate.py</code></a></li>
</ul>
</li>
<li><a href="#sec-4-4">4.4. Library</a>
<ul>
<li><a href="#sec-4-4-1">4.4.1. Improvements in syntax of <code>ParsedParameterFile</code></a></li>
<li><a href="#sec-4-4-2">4.4.2. <code>Utilities</code>-class now function to find files matching a pattern</a></li>
<li><a href="#sec-4-4-3">4.4.3. VCS ignores more files</a></li>
</ul>
</li>
<li><a href="#sec-4-5">4.5. New features/Utilities</a>
<ul>
<li><a href="#sec-4-5-1">4.5.1. New Utility <code>pyFoamSymlinkToFile.py</code></a></li>
</ul>
</li>
</ul>
</li>
<li><a href="#sec-5">5. Version 0.6.0 - 2013-03-14</a>
<ul>
<li><a href="#sec-5-1">5.1. Major changes</a>
<ul>
<li><a href="#sec-5-1-1">5.1.1. Adaption to work with Python3</a></li>
<li><a href="#sec-5-1-2">5.1.2. New ThirdParty-Libraries</a></li>
<li><a href="#sec-5-1-3">5.1.3. Porting to <code>Windows</code></a></li>
<li><a href="#sec-5-1-4">5.1.4. Experimental port to <code>pypy</code></a></li>
</ul>
</li>
<li><a href="#sec-5-2">5.2. Third-Party</a>
<ul>
<li><a href="#sec-5-2-1">5.2.1. Upgraded <code>ply</code> to 3.4</a></li>
</ul>
</li>
<li><a href="#sec-5-3">5.3. Infrastructure</a>
<ul>
<li><a href="#sec-5-3-1">5.3.1. Parameters can't be modified in <code>CTestRun</code> after initialization</a></li>
<li><a href="#sec-5-3-2">5.3.2. Treat timeouts in the <code>MetaServer</code> right</a></li>
<li><a href="#sec-5-3-3">5.3.3. Add <code>execute</code>-method to <code>ClusterJob</code></a></li>
<li><a href="#sec-5-3-4">5.3.4. Add possibility to run specific modules before or after the solver</a></li>
<li><a href="#sec-5-3-5">5.3.5. Parameters added to the info about the run</a></li>
<li><a href="#sec-5-3-6">5.3.6. Parameter handling in <code>ClusterJob</code> extended</a></li>
<li><a href="#sec-5-3-7">5.3.7. Run data written alongside <code>PickledPlots</code></a></li>
<li><a href="#sec-5-3-8">5.3.8. <code>BasicRunner</code> collects error and warning texts</a></li>
</ul>
</li>
<li><a href="#sec-5-4">5.4. Library</a>
<ul>
<li><a href="#sec-5-4-1">5.4.1. <code>TemplateFile</code> now uses <code>pyratemp</code></a></li>
<li><a href="#sec-5-4-2">5.4.2. Clearer error message in Application-classes</a></li>
<li><a href="#sec-5-4-3">5.4.3. Output is only colored if it goes to the terminal</a></li>
<li><a href="#sec-5-4-4">5.4.4. <code>error</code>-method of application classes now raises an exception</a></li>
<li><a href="#sec-5-4-5">5.4.5. <code>ParsedParameterFile</code> now knows how to handle binary files</a></li>
<li><a href="#sec-5-4-6">5.4.6. <code>LabledReSTTable</code> for more flexible table generation</a></li>
<li><a href="#sec-5-4-7">5.4.7. Plotting classes now allow setting of <code>xlabel</code></a></li>
</ul>
</li>
<li><a href="#sec-5-5">5.5. Utilities</a>
<ul>
<li><a href="#sec-5-5-1">5.5.1. <code>pyFoamFromTemplate.py</code> with new templating engine</a></li>
<li><a href="#sec-5-5-2">5.5.2. <code>pyFoamSamplePlot.py</code> allows using the reference data as basis for comparison</a></li>
<li><a href="#sec-5-5-3">5.5.3. Scaling and offsets are now used in plots of <code>pyFoamSamplePlot.py</code></a></li>
<li><a href="#sec-5-5-4">5.5.4. <code>pyFoamPrintData2DStatistics.py</code> prints relative average error</a></li>
<li><a href="#sec-5-5-5">5.5.5. Enhancements to <code>pyFoamVersion.py</code></a></li>
<li><a href="#sec-5-5-6">5.5.6. <code>pyFoamRunner.py</code> allows hooks</a></li>
<li><a href="#sec-5-5-7">5.5.7. <code>pyFoamRedoPlots.py</code> supports range for plots</a></li>
<li><a href="#sec-5-5-8">5.5.8. <code>pyFoamDisplayBlockMesh.py</code> no supports templates</a></li>
<li><a href="#sec-5-5-9">5.5.9. <code>pyFoamCaseReport.py</code> is tolerant towards binary files</a></li>
<li><a href="#sec-5-5-10">5.5.10. <code>pyFoamSamplePlot.py</code> and <code>pyFoamTimelinePlot.py</code> raise error if no plots are generated</a></li>
<li><a href="#sec-5-5-11">5.5.11. <code>pyFoamSurfacePlot.py</code> can wait for a key</a></li>
<li><a href="#sec-5-5-12">5.5.12. <code>pyFoamEchoDictionary.py</code> is more flexible with binary files</a></li>
<li><a href="#sec-5-5-13">5.5.13. All utilities now have a switch that starts the debugger even with syntax-errors</a></li>
<li><a href="#sec-5-5-14">5.5.14. Utilities now can be killed with <code>USR1</code> and will give a traceback</a></li>
<li><a href="#sec-5-5-15">5.5.15. Switch to switch on <b>all</b> debug options</a></li>
<li><a href="#sec-5-5-16">5.5.16. Plotting utilities now allow specification of x-Axis label</a></li>
<li><a href="#sec-5-5-17">5.5.17. Metrics and compare for <code>pyFoamTimelinePlot.py</code> and <code>pyFoamSamplePlot.py</code> support time ranges</a></li>
<li><a href="#sec-5-5-18">5.5.18. <code>pyFoamDisplayBlockMesh.py</code> allows graphical selection of blocks and patches</a></li>
<li><a href="#sec-5-5-19">5.5.19. <code>pyFoamCloneCase.py</code> and <code>pyFoamPackCase.py</code> accept additional parameters</a></li>
<li><a href="#sec-5-5-20">5.5.20. <code>pyFoamListCases.py</code> now calculates estimated end-times</a></li>
</ul>
</li>
<li><a href="#sec-5-6">5.6. New features</a>
<ul>
<li><a href="#sec-5-6-1">5.6.1. Different "phases" for multi-region solvers</a></li>
<li><a href="#sec-5-6-2">5.6.2. <code>pyFoamChangeBoundaryType.py</code> allows selection of region and time</a></li>
<li><a href="#sec-5-6-3">5.6.3. New class for storing case data in a sqlite-database and associated utilities</a></li>
</ul>
</li>
<li><a href="#sec-5-7">5.7. Bugfixes</a>
<ul>
<li><a href="#sec-5-7-1">5.7.1. Only binary packages of 1.x were found</a></li>
<li><a href="#sec-5-7-2">5.7.2. Option group <i>Regular expressions</i> was listed twice</a></li>
<li><a href="#sec-5-7-3">5.7.3. <code>--clear</code>-option for <code>pyFoamDecompose.py</code> not working</a></li>
<li><a href="#sec-5-7-4">5.7.4. <code>pyFoamDisplayBlockmesh.py</code> not working with variable substitution</a></li>
<li><a href="#sec-5-7-5">5.7.5. Option <code>--function-object-data</code> of <code>pyFoamClearCase.py</code> not working with directories</a></li>
<li><a href="#sec-5-7-6">5.7.6. <code>nonuniform</code> of length 0 not correctly printed</a></li>
<li><a href="#sec-5-7-7">5.7.7. Building of pseudocases with <code>pyFoamRunner.py</code> broken</a></li>
<li><a href="#sec-5-7-8">5.7.8. <code>pyFoamRedoPlot.py</code> did not correctly honor <code>--end</code> and <code>--start</code></a></li>
<li><a href="#sec-5-7-9">5.7.9. <code>WriteParameterFile</code> does not preserve the order of additions</a></li>
<li><a href="#sec-5-7-10">5.7.10. Wrong number of arguments when using <code>TimelinePlot</code> in <code>positions</code>-mode</a></li>
<li><a href="#sec-5-7-11">5.7.11. <code>ClusterJob</code> uses only <code>metis</code> for decomposition</a></li>
<li><a href="#sec-5-7-12">5.7.12. <code>pyFoamSamplePlot.py</code> and <code>pyFoamTimelinePlot.py</code> produced no pictures for regions</a></li>
<li><a href="#sec-5-7-13">5.7.13. Barplots in <code>pyFoamTimelinePlot.py</code> not working if value is a vector</a></li>
<li><a href="#sec-5-7-14">5.7.14. Mysterious deadlocks while plotting long logfiles</a></li>
<li><a href="#sec-5-7-15">5.7.15. Scanning linear expressions form the block coupled solver failed</a></li>
<li><a href="#sec-5-7-16">5.7.16. <code>#include</code> not correctly working with macros in the included file</a></li>
<li><a href="#sec-5-7-17">5.7.17. Macros not correctly expanded to strings</a></li>
<li><a href="#sec-5-7-18">5.7.18. <code>pyFoamPackCase.py</code> in the working directory produces 'invisible' tar</a></li>
<li><a href="#sec-5-7-19">5.7.19. String at the end of a linear solver output makes parsing fail</a></li>
<li><a href="#sec-5-7-20">5.7.20. Paraview utilities not working with higher Paraview versions</a></li>
<li><a href="#sec-5-7-21">5.7.21. Camera settings not honored with <code>pyFoamPVSnapshot.py</code></a></li>
</ul>
</li>
</ul>
</li>
<li><a href="#sec-6">6. Version 0.5.7 - 2012-04-13</a>
<ul>
<li><a href="#sec-6-1">6.1. Parser improvements</a></li>
<li><a href="#sec-6-2">6.2. Utility improvements</a></li>
<li><a href="#sec-6-3">6.3. New Utilities</a></li>
<li><a href="#sec-6-4">6.4. Library improvements</a></li>
<li><a href="#sec-6-5">6.5. Removed utilities</a></li>
<li><a href="#sec-6-6">6.6. Thirdparty</a></li>
<li><a href="#sec-6-7">6.7. Other</a></li>
</ul>
</li>
<li><a href="#sec-7">7. Older Versions</a></li>
</ul>
</div>
</div>



# Version 0.6.4 - 2014-11-24<a id="sec-1" name="sec-1"></a>

## Requirements<a id="sec-1-1" name="sec-1-1"></a>

The only requirement is a python-installation. The main testing and
development has been done with 2.7 and 2.6. Python 2.5 should work
but not for all utilities. Currently 2.6, 2.7 and 3.4 are used
during development.

Certain functionalities need special Python-libraries. The main one
is `numpy` for plotting. Other libraries that might be of interest
are `matplotlib`, `pandas` and `IPython`. For
`pyFoamDisplayBlockmesh.py` the libraries `PyQt4` and `vtk` are
needed. Other libraries are tested for and reported by
`pyFoamVersion.py` but not required (only install if you're sure
that you need it)

## Future changes<a id="sec-1-2" name="sec-1-2"></a>

### Redundant utilities `pyFoamJoinCSV.py` and `pyFoamConvertToCSV.py` unified<a id="sec-1-2-1" name="sec-1-2-1"></a>

These two utilities are almost indistinguishable and will be
unified into one

## Major changes<a id="sec-1-3" name="sec-1-3"></a>

### Multi-line regular expressions in `customRegexp`<a id="sec-1-3-1" name="sec-1-3-1"></a>

If in `customRegexp` an `expr` is found with `\n` then this
expression is matched over multiple consecutive lines. Types like
`dynamic` work as usual.

This makes it possible to match for instance the output of the
`forces`-function objects

### Enhancement of `pyFoamPrepare.py`<a id="sec-1-3-2" name="sec-1-3-2"></a>

The utility which was introduced in the last version is becomong
more usable and will be central to all things that set up the case
(for instance a special `ClusterJob`)

### Enhancements of the CSV-utilities<a id="sec-1-3-3" name="sec-1-3-3"></a>

These utilities are now more flexible and allow writing and
reading of Excel-files too

### Environment variable `PYFOAM_SITE_DIR` and `PYFOAM_DIR`<a id="sec-1-3-4" name="sec-1-3-4"></a>

Both variables are not necessary but `PYFOAM_SITE_DIR` allows
consistent insertion of site-specific libraries and utilities.

`PYFOAM_DIR` is set by some Foam-distributions and tested for by
`pyFoamVersion.py`. It is supposed to point to the currents
PyFoam-installation.

`PYFOAM_SITE_DIR` points to a directory with site-specific scripts
and configurations. The sub-directories supported (and thested py
`pyFoamVersion.py`) are
-   **bin:** directory with scripts. It has to be added to the `PATH`
                 outside of PyFoam (for instance in the `.bashrc`)
-   **etc:** Optional directory which is searched for configuration
    files. Priority is below the user settings and above the
    global settings
-   **lib:** Optional directory to allow mixing in site-specific
    library files. Imported as `PyFoam.Site`: For instance if
    a file `Foo.py` is present in `lib` it can be imported as
    `PyFoam.Site.Foo`. This directory does not have to be (in
    fact: it **shouldn't**) added to `PYTHONPATH`

Purpose of `PYFOAM_SITE_DIR` is to allow administrators to provide
site-wide scripts and settings for all users on a site

## Incompatibilities<a id="sec-1-4" name="sec-1-4"></a>

### Option `--silent` removed from `pyFoamPrepareCase.py`<a id="sec-1-4-1" name="sec-1-4-1"></a>

Option has been renamed to `--no-complain`

### Keys in `RunDatabase` with column-names that contain upper-case letters change<a id="sec-1-4-2" name="sec-1-4-2"></a>

SQLite does not support case-sensitive column-names (`s_max` and
`S_max` are the same). To change this the upper case letters in
the column names are replaced by an underscore and the letter
(`S_max` becomes `_s__max`)

This means that old databases might not be read correctly

### Change in unique variable names in `pyFoamConvertToCSV.py`<a id="sec-1-4-3" name="sec-1-4-3"></a>

The algorithm to make variable names unique has changed (basically
it uses the part of the filenames that differ) and scripts relying
on these names might fail

### `PyFoam.IPython`-module renamed to `PyFoam.IPythonHelpers`<a id="sec-1-4-4" name="sec-1-4-4"></a>

The name of the module crashed in certain instances (especially
unit-testing) with the regular `IPython`-library. To avoid these
crashes it has been renamed to `IPythonHelpers`. This raises two
potential problems:
-   scripts that `import` the module have to be adapted to the new name
-   IPython-notebooks created with `pyFoamIPythonNotebook.py` have
    two imports pointing to this module. These notebooks have to be
    adapted to be usable again

## Bugfixes<a id="sec-1-5" name="sec-1-5"></a>

### Templates in `pyFoamPrepareCase.py` did not keep permissions<a id="sec-1-5-1" name="sec-1-5-1"></a>

This was a problem for script-templates which were not executable
any more. Fixed

### `pyFoamComparator.py` failed due to circular dependency<a id="sec-1-5-2" name="sec-1-5-2"></a>

This has been fixed by adding an import in `BasicRunner.py`

### `pyFoamDumpRunDatabaseToCSV.py` fails if Pandas-data is requested<a id="sec-1-5-3" name="sec-1-5-3"></a>

This is now fixed

### `sort` for list broke code on Python 3<a id="sec-1-5-4" name="sec-1-5-4"></a>

Some calls for `sort` still used the `cmp`-parameter which does
not exist for Python3 anymore. These calls have been replaced with
`key` and `reverse`

### Changing the OF-version does not work in Python 3<a id="sec-1-5-5" name="sec-1-5-5"></a>

Because the output of `subprocess` is now *binary* instead of a
regular string. Fixed

### `addData` in `PyFoamDataFrame` extrapolates for invalid values<a id="sec-1-5-6" name="sec-1-5-6"></a>

This was due to incorrect use of the `interpolate`-method

### `--keep-last` did not work for `pyFoamClearCase.py` and parallel cases<a id="sec-1-5-7" name="sec-1-5-7"></a>

This was because there was a problem in the library code and the
utility did not consider the parallel time-steps. Fixed

### `pyFoamDumpRunDatabaseToCSV.py` does not add basic run information<a id="sec-1-5-8" name="sec-1-5-8"></a>

Basic run information was not added to the file. Now it is with
the prefix `runInfo//`

### Restore of `FileBasisBackup` did not work<a id="sec-1-5-9" name="sec-1-5-9"></a>

The logic for checking whether a file was "backupable" was
wrong. This affected the proper restore of files with utilities
for instance for `--write-all`

### Remove circular dependency in `DataStructures`<a id="sec-1-5-10" name="sec-1-5-10"></a>

According to the bug
<http://sourceforge.net/p/openfoam-extend/ticketspyfoam/219/> it was
not possible to import `DataStructures` because of a circular
dependency with `FoamFileGenerator`. Fixed by moving an import to
the back of the file

## New features/Utilities<a id="sec-1-6" name="sec-1-6"></a>

### `pyFoamRunParameterVariation.py`<a id="sec-1-6-1" name="sec-1-6-1"></a>

This utility takes a template case and a file specifying the
parameter variation and creates cases with the
`pyFoamPrepareCase.py`-engine, runs a solver on these cases and
collects the data into a database. The database can then be
extracted with `pyFoamDumpRunDatabaseToCSV.py`

### `pyFoamBinarySize.py`<a id="sec-1-6-2" name="sec-1-6-2"></a>

Calculates the size of the binaries in an OpenFOAM-installation
separated by compile-option

### `pyFoamBlockMeshRewrite.py`<a id="sec-1-6-3" name="sec-1-6-3"></a>

Assists the user in rewriting the `blockMeshDict` by doing simple,
but error-prone transformations. Assumes "sensible" formatting:
one block/vertex etc per line.

Sub-commands are:
-   **refine:** refines mesh by multiplying cell numbers in the blocks
-   **number:** Adds comments with the vertex numbers. Should help the
    user when editing/modifying the mesh
-   **stripNumber:** Remove the comments added by `number`
-   **mergeVertices:** Adds vertices from other blockMeshes that
    are not present in the current blockMesh
-   **renumberVertices:** Take another `blockMeshDict`, copy over the
    `vertices`-section of that mesh and rewrite `blocks` and
    `patches` so that they conform to these `vertices`. The
    original `vertices` have to be a sub-set of the `vertices` in
    the other mesh
-   **normalizePatches:** Rotates patches so that the lowest number is
    in front

## Enhancements to Utilities<a id="sec-1-7" name="sec-1-7"></a>

### `pyFoamChangeBoundaryType.py` allows setting additional values<a id="sec-1-7-1" name="sec-1-7-1"></a>

The option `--additional-values` allows specifying a dictionary
with additional values for the boundary (stuff that is needed by
`mappedWall` etc)

### `pyFoamPrepareCase.py` now has OF-version and fork as defined variables<a id="sec-1-7-2" name="sec-1-7-2"></a>

This allows to write case-templates that can distinguish between
different OF-versions

### `pyFoamPrepareCase.py` now allows "overloading" another directory<a id="sec-1-7-3" name="sec-1-7-3"></a>

Before doing anything else the contents of different directories
are copied into the current case. This allows for instance to use
tutorial cases as the basis for a case

### `pyFoamIPythonNotebook.py` adds improvements to the notebook<a id="sec-1-7-4" name="sec-1-7-4"></a>

Additional code added to the generated notebook:
-   Code to change the default size of the plots
-   Distribution-directories in subdirectories `distributions`
          (generated by some `swak`-function objects) added

### `pyFoamListCases.py` more tolerant to faulty `controlDict`<a id="sec-1-7-5" name="sec-1-7-5"></a>

If the `controlDict` is acceptable to OpenFOAM but syntactically
incorrect for PyFoam (for instance because of a missing semicolon)
the utility does not fail anymore (but no data is collected for
that case).

### `pyFoamDumpConfiguration.py` prints sections and keys alphabetically<a id="sec-1-7-6" name="sec-1-7-6"></a>

This should make it easier to find items

### `pyFoamJoinCSV.py` and `pyFoamConvertToCSV.py` read and write Excel-files<a id="sec-1-7-7" name="sec-1-7-7"></a>

Both utilities now allow writing Excel-files

In addition to regular text files the first sheet from `xls`-files
can be read

### Flexible variable filtering in `pyFoamJoinCSV.py` and `pyFoamConvertToCSV.py`<a id="sec-1-7-8" name="sec-1-7-8"></a>

Now it is possible to filter for regular expressions

The functionality of the two utilities now is very similar and it
is possible that one of them will be discontinued

### Columns in `pyFoamJoinCSV.py` and `pyFoamConvertToCSV.py` can be recalculated<a id="sec-1-7-9" name="sec-1-7-9"></a>

The two utilities now can add columns or recalculate columns
based on the existing column values

### Testing for `Numeric` removed from `pyFoamVersion.py`<a id="sec-1-7-10" name="sec-1-7-10"></a>

Testing for the library `Numeric` library removed as it is no
longer supported as a fallback for `numpy`. Test also removed from
`setup.py`

## Enhancements to the Library<a id="sec-1-8" name="sec-1-8"></a>

### Subclass of `ClusterJob` that support `PrepareCase`<a id="sec-1-8-1" name="sec-1-8-1"></a>

The class `PrepareCaseJob` supports cases that are set up with
`pyFoamPrepareCase.py`. Additional parameters to the constructor are
-   the name of the parameter-file
-   a list with the parameters. The list is composed of
    name/value-pairs

### Subclass of `ClusterJob` that support `RunParameterVariation`<a id="sec-1-8-2" name="sec-1-8-2"></a>

The class `VariationCaseJob` supports cases that are set up with
`pyFoamRunParameterVariation.py`. Additional parameters to the constructor are
-   the name of the parameter-file
-   the name of the variations-file

### `execute` in `PyFoam/Utilities` fails if script is not executable<a id="sec-1-8-3" name="sec-1-8-3"></a>

The function checks if the file exists and is **not**
executable. The program fails in that case

### `foamVersion` uses a separate wrapper class for `tuple`<a id="sec-1-8-4" name="sec-1-8-4"></a>

This ensures that it is printed in a form that is valid in
OF-dictionaries

### Move calculation of disk usage to `Utilities`<a id="sec-1-8-5" name="sec-1-8-5"></a>

This has until now only been used in `ListCases` but moved to a
separate method/function `diskUsage` in the `Utilities`-module

### Enhancement of `--help`<a id="sec-1-8-6" name="sec-1-8-6"></a>

Added the possibility to have an epilog and usage examples with
the `epilog` and  `examples`-keyword arguments for applications.

These and descriptions now have the possibility for line-breaks:
if two line-breaks are encountered in the text a new paragraph is
created

### `which`-routine in `Utitlities` uses native Python-routine<a id="sec-1-8-7" name="sec-1-8-7"></a>

For Python-version where `shutil` has a `which`-function this is
used instead of calling an external program

### `FileBasis` now allows file handles instead of the filename<a id="sec-1-8-8" name="sec-1-8-8"></a>

This currently only works for reading, Backups, zipping etc won't
work but it makes algorithms more flexible

### `BlockMesh` doesn't force writing to file anymore<a id="sec-1-8-9" name="sec-1-8-9"></a>

Instead content is stored in memory. Old behaviour is the default
to preserve compatibility with old scripts

### Additional methods for `BlockMesh`-class<a id="sec-1-8-10" name="sec-1-8-10"></a>

-   **numberVertices:** Adds comments with the vertex numbers to the
    vertices

### `LineReader` allows keeping spaces on left<a id="sec-1-8-11" name="sec-1-8-11"></a>

Previous behaviour was stripping all spaces from the lines. Now
the left hand spaces can be ket. Old behaviour is still default
for compatibility

### `TemplateFile` now allows writing of assignment-results in file<a id="sec-1-8-12" name="sec-1-8-12"></a>

This allows faster debugging of template-files. This can be
enabled with a switch in the utilities using templates

### `SolverJob` now allows passing of parameters to the solver<a id="sec-1-8-13" name="sec-1-8-13"></a>

And additional parameter `solverArgs` will now be passed to the
solver (if the solver accepts arguments)

### `SpreadsheetData` now allows reading from an Excel file<a id="sec-1-8-14" name="sec-1-8-14"></a>

During construction if an Excel-file is specified and the
`xlrd`-library and `pandas` are installed then the first sheet in
the file is read

### `SpreadsheetData` allows recalculating columns<a id="sec-1-8-15" name="sec-1-8-15"></a>

Columns can be recalculated using expressions. This includes other
data items. Currently present column names are available as
variables. There is also a variable `data` that can be subscripted
for items that are not valid variable names. A variable `this`
points to the item to be recalculated

## Known bugs<a id="sec-1-9" name="sec-1-9"></a>

### Timelines not forgotten for multiple runner calls<a id="sec-1-9-1" name="sec-1-9-1"></a>

This manifests with `pyFoamRunParameterVariation.py`. The custom
timelines are still kept in memory. Not a problem. Just annoying

# Version 0.6.3 - 2014-06-23<a id="sec-2" name="sec-2"></a>

## Requirements<a id="sec-2-1" name="sec-2-1"></a>

The only requirement is a python-installation. The main testing and
development has been done with 2.7 and 2.6. Python 2.5 should work
but not for all utilities. Unit tests run on Python 3.4 but it is
currently not used in a production environment (reports of success
or failure most welcome)

Certain functionalities need special Python-libraries. The main one
is `numpy` for plotting. Other libraries that might be of interest
are `matplotlib`, `pandas` and `IPython`. For
`pyFoamDisplayBlockmesh.py` the libraries `PyQt4` and `vtk` are
needed. Other libraries are tested for and reported by
`pyFoamVersion.py` but not required (only install if you're sure
that you need it)

## Major changes<a id="sec-2-2" name="sec-2-2"></a>

### Version changing supports forks of OpenFOAM<a id="sec-2-2-1" name="sec-2-2-1"></a>

Now `pyFoam` supports different versions of OpenFOAM for switching.
Out of the box `openfoam` and `extend` are supported. If only the
version number is specified (for instance by `--foamVersion=1.7.x`)
and such a version exists only for one fork it is correctly
expanded with the correct fork( in the example with
`openfoam-1.7.x`). If more than one fork has the same version then
the fork name has to be specified as well

Note: additional forks can be easily specified with the
configurations. In section `OpenFOAM` the parameter `forks` has to
be extended. For each new fork a `dirpatterns` and
`installation`-parameter has to be specified

## Incompatibilities<a id="sec-2-3" name="sec-2-3"></a>

### Change of command interface of `pyFoamSTLUtility.py`<a id="sec-2-3-1" name="sec-2-3-1"></a>

The selection of what is to be done is now selected by subcommands
instead of options. This will break scripts using this

### If `0.org` is present `pyFoamCloneCase.py` and `pyFoamPackCase.py` ignore `0`<a id="sec-2-3-2" name="sec-2-3-2"></a>

The reason is that the utilities assume that this directory is
produced from `0.org`

## Bugfixes<a id="sec-2-4" name="sec-2-4"></a>

### PlotWatcher has long times between updates if pickling takes long<a id="sec-2-4-1" name="sec-2-4-1"></a>

The reason was that it used the same throttling that made sense
for the PlotRunner. Fixed

### `pyFoamPVSnapshot.py` fails for newer paraview-versions<a id="sec-2-4-2" name="sec-2-4-2"></a>

Reason is that the class `vtkPythonStdStreamCaptureHelper` does
not support `isatty`

### SamplePlot failed when valueNames are unspecified<a id="sec-2-4-3" name="sec-2-4-3"></a>

Reported in
<https://sourceforge.net/apps/mantisbt/openfoam-extend/view.php?id=208>
and fixed

### `pyFoamTimelinePlot.py` failed Numpy/Pandas output of vector fields<a id="sec-2-4-4" name="sec-2-4-4"></a>

Vector fields only were added to the data fields if they were the
first in the list. Fixed

### `alternateAxis` ignored for slave<a id="sec-2-4-5" name="sec-2-4-5"></a>

This is now fixed. The alternate values have to be specified in
the master (specifying in the slave gives an error)

### `pyFoamCaseReport.py` more stable for binary `boundary`-files<a id="sec-2-4-6" name="sec-2-4-6"></a>

Usually these files are `ascii` (even if the header says
`binary`). In some cases the parsing failed for these. Fixed by
enforcing reading as `ascii`. Can be switched off

### `SpreadsheetData` returns data which breaks certain Pandas-operations<a id="sec-2-4-7" name="sec-2-4-7"></a>

The reason was that if there were duplicate times in the table the
index was non-unique which certain Pandas-operations don't
appreciate. Solved by dropping duplicate times. Can be switched off

### `pyFoamCloneCase.py` added duplicates to the archive<a id="sec-2-4-8" name="sec-2-4-8"></a>

If things are specified twice they were added twice. Now it is
checked whether the item already exists in the tar-file before
adding them

### `nonuniform` of length 3 not correctly printed<a id="sec-2-4-9" name="sec-2-4-9"></a>

The reason was that this was interpreted as a vector and the
numeric prefix was removed. Reported at
<http://sourceforge.net/apps/mantisbt/openfoam-extend/view.php?id=218>

Fixed by introducing an extra parameter to `FoamFileGenerator`

## New features/Utilities<a id="sec-2-5" name="sec-2-5"></a>

### `pyFoamPrepareCase.py` for case preparation<a id="sec-2-5-1" name="sec-2-5-1"></a>

This utility aims to reduce the need for boilerplate scripts to
set up cases. The steps it executes are
1.  Clear old data from the case (including processor directories)
2.  if a folder `0.org` is present remove the `0` folder too
3.  go through all folders and for every found file with the
    extension `.template` do template expansion using the
    pyratemp-engine
4.  create a mesh (either by using a script or if a `blockMeshDict`
    is present by running blockMesh. If none of these is present
    assume that there is a valid mesh present)
5.  copy every `foo.org` that is found to to `foo` (recursively if directory)
6.  do template replacement for every `.postTemplate`
7.  execute another preparation script

### `pyFoamIPythonNotebook.py` for generating and manipulating IPython-notebooks<a id="sec-2-5-2" name="sec-2-5-2"></a>

This utility creates and manipulates IPython-notebooks for
analyzing OpenFOAM cases. It has a number of subcommands:
-   **create:** this is the main command. All other commands assume
    that the notebooks they work with were created with
    this.

    The utility looks at the case specified and creates a
    notebook that has the capabilities to quickly build a
    report about the case:

    -   reporting general properties of the case. This
        basically is the capability of the
        `pyFoamCaseReport.py`-utility
    -   It searches for data that can be visualized by
        `pyFoamTimelinePlot.py` or `pyFoamSamplePlot.py` and
        generates selectors that allow the user to select
        which data to import. The selectors import the data as
        Pandas-=DataFrames= and create the commands
        necessary to do this. It is recommended to erase the
        selector afterwards
    -   Selectors for pickled case data and pickled plot
        generated by PyFoam
    -   Capability to store read data **in** the notebook
        file. This feature is experimental and has
        performance issues for medium to large datasets

    The created notebook can be executed but needs to be
    edited to be useful
-   **clear:** removes selected cells (but only cells created with
    `create`) or output from the notebook.
-   **info:** prints information about the notebook
-   **copy:** copies notebook to a different case and rewrites it so
    that data is read from that case

Recommended way of working with this utility is
1.  Create notebook with utility
2.  Edit it to contain standardized evaluations
3.  Copy it over to another, similar case

### Additional sub-module `PyFoam.IPython`<a id="sec-2-5-3" name="sec-2-5-3"></a>

The purpose of this submodule is to support
`pyFoamIPythonNotebook.py`. It has the classes
-   **Notebook:** read a file and interpret it as an
    IPython-notebook. Do manipulations on this notebook
-   **PermanentStorage:** Implements permanent storage in an
    IPython-notebook. Only works inside a notebook and allows
    only one instance at once. Passing the data from the notebook
    (through JavaScript) to Python currently is a performance
    bottleneck
-   **Case:** Convenience object that exposes the functionality of
    some of the PyFoam-utilities through a simple interface

### Additional sub-module `PyFoam.Wrappers`<a id="sec-2-5-4" name="sec-2-5-4"></a>

Wraps popular Python-libraries to add functions that make it
easier to work with OpenFOAM-data.

Currently only one Wrapper is implemented:

1.  `Pandas`-wrappers

    This provides `PyFoamDataFrame` as a wrapper for `DataFrame`. The
    functionality added is
    -   **addData:** Conveniently add new data from different `Series`,
        `DataFrames`. It is assumed that the index is the
        same property (time or for samples the distance) but
        with a different resolution. The indexes are joined
        and missing data is interpolated
    -   **integrate, validLength, weightedAverage:** uses the index as
        the \(x\)-axis and calculates these properties for a
        `Series`. `validLength` is the extent on which data is
        defined (`weightedAverage` is basically `integrate` divided
        by `validLength`). For `integrate` the trapezoid-rule is used
    -   **describe:** adds the three above quantities to the regular
        `describe`-command

## Enhancements to Utilities<a id="sec-2-6" name="sec-2-6"></a>

### `pyFoamSampleplot` has option to use index instead of time in filenames<a id="sec-2-6-1" name="sec-2-6-1"></a>

The option `-index-instead-of-filename` switches this on. This
makes it easier to generate movies from the files

### `pyFoamListCases.py` Allows addition of custom data<a id="sec-2-6-2" name="sec-2-6-2"></a>

The option `--custom-data` now allows the specification of custom
data items. These are read from the `pickledData`-files and
displayed in the table like regular data items

### Switch compiler versions<a id="sec-2-6-3" name="sec-2-6-3"></a>

Now all utilities allow switching the compiler version (for
instance from `Gcc47` to `Gcc48`). The relevant options are
`--force-system-compiler`, `--force-openfoam-compiler` and
`--force-compiler`

### `pyFoamVersion.py` reports the installed versions better<a id="sec-2-6-4" name="sec-2-6-4"></a>

Now the location of the installations is reported as well

### Offscreen rendering can be switched off in `pyFoamPVSnapshot.py`<a id="sec-2-6-5" name="sec-2-6-5"></a>

This is a workaround where the writer produces a segmentation
fault

### Write 3D-data in `pyFoamPVSnapshot.py`<a id="sec-2-6-6" name="sec-2-6-6"></a>

In addition to writing out bitmaps allows writing out 3D-data (for
importing into other applications). Sources can be selected by name

### Added capabilities to `pyFoamSTLUtility`<a id="sec-2-6-7" name="sec-2-6-7"></a>

The utility can now also:
-   erase selected patches
-   merge selected patches into one

### `pyFoamDecomposer.py` switches off function objects<a id="sec-2-6-8" name="sec-2-6-8"></a>

This now automatically happens for OF-versions that support
it (2.0 and greater). They can be switched on again

### `pyFoamCloneCase.py` clones more stuff<a id="sec-2-6-9" name="sec-2-6-9"></a>

Files that are assumed to be used by `pyFoamPrepareCase.py` are
automatically added to the clone. This includes all files (and
directories) with the extensions `.sh`, `.template` and
`.org`. Also IPython notebooks (extension `.ipynb` are added)

## Enhancements to the Library<a id="sec-2-7" name="sec-2-7"></a>

### `BasicRunner` now can print the command line that is actually used<a id="sec-2-7-1" name="sec-2-7-1"></a>

This should help with diagnosing problems with MPI etc.

Can be switched on in some utilities with `--echo-command-prefix`

### `ClusterJob` now can live without a machinefile<a id="sec-2-7-2" name="sec-2-7-2"></a>

Using the machine-file now can be switched off for job-schedulers
with a tight integration

### Enhanced treatment of symlinks during cloning<a id="sec-2-7-3" name="sec-2-7-3"></a>

If a item in the case itself is a symlink then it used to be a
copy of the file the symlink is pointing to. Now it is created as
a symlink to the target the original symlink. If the
`--follow-symlink`-option is used the old behaviour is used
(copying). In this case the option `noForceSymlink` in the
`Cloning`-section of the configuration can be used to change this
behaviour for selected files

### `AnalyzedCommon` clears the `analyzed`-directory<a id="sec-2-7-4" name="sec-2-7-4"></a>

The directory is cleared if it exits from a previous run.

### `TimelineDirectory` is more tolerant<a id="sec-2-7-5" name="sec-2-7-5"></a>

Used to fail if incompatible data types were used. Now ignores
them

### Possibility of a subcommand-interface for utilities<a id="sec-2-7-6" name="sec-2-7-6"></a>

The subclass `SubclassFoamOptionParser` now allows the parsing of
subclasses. The base class for utilities `PyFoamApplication` now
supports this as an option. As an example this is implemented in
`pyFoamSTLUtilities.py`

### `STLUtility` accepts file-handles<a id="sec-2-7-7" name="sec-2-7-7"></a>

The class checks whether arguments are filehandles and in this
case doesn't try to open a file for reading or writing but uses
the handle

### `addClone` in `SolutionDirectory` accepts glob patterns<a id="sec-2-7-8" name="sec-2-7-8"></a>

If no file matching the name is found it is assumed that this is a
glob-pattern and all matching files are added. This affects all
utilities that use that method (especially `pyFoamCloneCase.py`)

### `execute` in `Utilities` allows specification of working directory and echoing of output<a id="sec-2-7-9" name="sec-2-7-9"></a>

This method now allows the specification of a working
directory. Before executing the command the method changes to the
working directory. Afterwards it changes back to the regular
working directory.

There is also an option `echo` that immediately prints the output
to the screen

### `rmtree` and `copytree` more tolerant<a id="sec-2-7-10" name="sec-2-7-10"></a>

`rmtree` now also works if the "tree" is a file.

`copytree` now has a parameter `force` that allows removing the
destination directory if it exists

### Enhanced support for booleans in the parser<a id="sec-2-7-11" name="sec-2-7-11"></a>

Strings that are usually interpreted as boolean in OF-dictionaries
(for instance `on`, `yes`, &#x2026;) are now stored as a special type
that allows treating them like 'real' booleans.

For instance an expression `test no;` in a dictionary now allows
things like `if d['test']:` in the script

### Application classes now allow specifying options as keyword parameters<a id="sec-2-7-12" name="sec-2-7-12"></a>

Until now the options to be used had to be specified as a list of
string modeled on the way the command line looked like. This is
still possible. In addition it is now possible to specify these
things as keyword parameters on the command line. Rudimentary type
checking is done. The names of the parameters are generated from
the command line options: the `-` are removed and the words are
converted to CamelCase. So for instance `--list-custom-Regexp =
    becomes =listCustomRegexp`. Also for switches like these a boolean
value has to be passed. So the correct usage in a call would be
`listCustomRegexp=True`.

### `SolutionDirector` now can classify directories in the `postProcessing`-directory<a id="sec-2-7-13" name="sec-2-7-13"></a>

A number of properties has been added that list data generated by
function objects:
-   **timelines:** timeline data (like `propes`) that can be
    visualized by `pyFoamTimelinePlot.py`
-   **samples:** data from `set` (assuming it is in `raw`-format) that
    can be processed by `pyFoamSamplePlot.py`
-   **surfaces:** data from `surface` (assumes `VTK`-format) that can
    be used by `pyFoamSurfacePlot.py`
-   **distributions:** special cases of `sample` with distribution
    data

These properties only list the subdirectories of the case with
that data

Additional properties are
-   **pickledData:** a list of pickled data files that are found
-   **pickledPlots:** list of found pickled plots

These lists are sorted in descending temporal order (newest first)

### `pyFoamSamplePlot.py` now more flexible for distributions<a id="sec-2-7-14" name="sec-2-7-14"></a>

Tries to determine the names of the values from the first line in
the files

### `DictProxy` now has a `dict`-like `update`-method<a id="sec-2-7-15" name="sec-2-7-15"></a>

This also allows enforcing string values

### `FoamFileGenerator` automatically quotes strings<a id="sec-2-7-16" name="sec-2-7-16"></a>

If strings are unquoted but contain characters that make it
illegal as a word then the string is quoted before output

### Children of `FileBasis` now can be used with the `with`-statement<a id="sec-2-7-17" name="sec-2-7-17"></a>

This mainly concerns `ParsedParameterFile`

# Version 0.6.2 - 2013-11-03<a id="sec-3" name="sec-3"></a>

## Major changes<a id="sec-3-1" name="sec-3-1"></a>

### Use of `pandas`-library<a id="sec-3-1-1" name="sec-3-1-1"></a>

Starting with this version the `pandas`-library is used for
data-analysis. When possible and appropriate classes return
`pandas`-objects. Currently these are:
-   `CSVCollection`. With a call-operator this class returns the
    collected data as a `DataFrame` of the collected data
-   `SpreadsheetData` now has methods to return `Series` and
    `DataFrame` objects

It is not necessary to install `pandas` if these classes are not
used (and even then most of their functionality works)

## Incompatibilities<a id="sec-3-2" name="sec-3-2"></a>

### Different separator for databases in CSV-files<a id="sec-3-2-1" name="sec-3-2-1"></a>

The class `RunDatabase` (and therefor also the utility
`pyFoamDumpRunDatabaseToCSV.py`) now write as a separator for data
from sub-tables a `//` instead of the space. This especially means
that scripts that rely on a data-item `foo` in `analyzed` might
break because this is now called `analyzed//foo` instead of
`analyzed foo`. On the other hand this makes the names more
consistent and easier to parse as `//` is the saperator for other
levels of dictionaries

### Change of independent variable name in sample data<a id="sec-3-2-2" name="sec-3-2-2"></a>

Instead of `col0` this is now `coord`. This could cause problems
with scripts that use that column name in the resulting
`SpreadsheetData`-object

## Bugfixes<a id="sec-3-3" name="sec-3-3"></a>

### `pyFoamPackCase.py` does not handle symbolic links correctly<a id="sec-3-3-1" name="sec-3-3-1"></a>

Symbolic links were copied as is and did not work correctly
afterwards. This is fixed. If the symbolic link is an absolute
path or points outside the case directory it is replaced with the
file it points to. Otherwise it is preserved as a symbolic link

### `pyFoamPotentialRunner.py` not working with OpenFOAM 2.0 or newer<a id="sec-3-3-2" name="sec-3-3-2"></a>

These versions require an entry `potentialFlow` in the
`fvSolution`-file instead of the old `SIMPLE`

### `pyFoamListCase.py` fails with `controlDict` that use preprocessing<a id="sec-3-3-3" name="sec-3-3-3"></a>

Fixed by first trying to read that with preprocessing. Without if
that fails

### Cloning fails in symlink-mode if files are specified twice<a id="sec-3-3-4" name="sec-3-3-4"></a>

Now using a `set` instead of a `list` makes sure that no file is
cloned twice

## Utilities<a id="sec-3-4" name="sec-3-4"></a>

### `pyFoamPotentialRunner.py` now allows removing of `functions` and `libs`<a id="sec-3-4-1" name="sec-3-4-1"></a>

The utility now allows removing these entries in case that they
don't work with `potentialFoam`

### The Runner-utilities now have more options for clearing<a id="sec-3-4-2" name="sec-3-4-2"></a>

Some of the options of `pyFoamClearCase.py` for clearing cases
(for instance specifying additional files) have been ported to the
`Runner`-utilities. Also is the `postProcessing`-directory
removed by default

## Library<a id="sec-3-5" name="sec-3-5"></a>

### `SolutionDirectory` and `TimeDirectory` are more tolerant<a id="sec-3-5-1" name="sec-3-5-1"></a>

If there are field files and their zipped counterpart than
instead of an error a warning **can** be given

### `ClusterJob` now handles template files<a id="sec-3-5-2" name="sec-3-5-2"></a>

A new method `templateFile` gets the name of a file which is
constructed from a template of the same name plus the extension
`.template`

### Additional parameters in `ClusterJob`<a id="sec-3-5-3" name="sec-3-5-3"></a>

The method `additionalParameters` can return a dictionary with
additional parameters

### Custom data in directory easier accessible<a id="sec-3-5-4" name="sec-3-5-4"></a>

In the written data in the sub-dictionary `analyzed` there is now
a subdictionary `Custom` with the values of the custom expressions
with the prefix `CustomXX_` removed. This means that values that
were available as

    data['Custom02_velCheck']['min']

are now available as

    data['Custom']['velCheck']['min']

The advantage is that the number part which was dependent on the
order the expressions were specified is now no longer necessary
(this should make scripts more stable)

The old notation is still available but deprecated

### `SolverJob` now allows compression of output<a id="sec-3-5-5" name="sec-3-5-5"></a>

The parameter `solverLogCompress` compresses the log-file while
writing it to disc. **Attention:** This may lead to corrupted
log-files if the run crashes

### `PyFoamApplication`-class now allows quick access to data<a id="sec-3-5-6" name="sec-3-5-6"></a>

The dictionary returned by `getData()` now allows access to all
the elements as attributes.

## New features/Utilities<a id="sec-3-6" name="sec-3-6"></a>

### Post-run hook that sends mail at the end of run<a id="sec-3-6-1" name="sec-3-6-1"></a>

The hook-module `MailToAddress` sends a mail at the end of a
run. Prerequisite is an SMTP-Server that doesn't need
authentication

### New utility `pyFoamCompressCases.py`<a id="sec-3-6-2" name="sec-3-6-2"></a>

This utility goes through cases and compresses single files. The
cases can be searched recursively to.

Purpose of this utility is to shrink cases where
`writeCompression` was not turned on during the run

### Paraview-module to read additional data<a id="sec-3-6-3" name="sec-3-6-3"></a>

A new module `PyFoam.Paraview.Data` reads additional data usually
written by OpenFOAM. These are converted to `vtkArray` using the
following functions and can be used in `Programmable filters`:
-   **setSampleData:** reads the data from sampled sets
-   **setTimelineData:** reads data from a timeline directory
-   **setPlotData:** reads pickled plot data using `RedoPlot`

## Enhancements<a id="sec-3-7" name="sec-3-7"></a>

### `pyFoamRedoPlot.py` can plot in XKCD-mode<a id="sec-3-7-1" name="sec-3-7-1"></a>

When used with the option `--implementation=xkcd` and version of
`matplotlib` that supports it is installed then plots are done in
the style of the webcomics <http://xkcd.com>

### `pyFoamListCases.py` now displays disk usage in human readable form<a id="sec-3-7-2" name="sec-3-7-2"></a>

If the disk usage of the cases is calculated then it is displayed
in human readable form (as KB, MB, GB or TB) for sizes larger than
one Kilobyte

### `pyFoamClearCase.py` more flexible in selection of data to be removed<a id="sec-3-7-3" name="sec-3-7-3"></a>

Options to be more flexible in removing data are added:
-   **keep-interval:** keep timesteps at a specified interval. For
    instance `--keep-interval=0.1` will keep times
    like \(1\), \(1.1\) etc but remove \(1.05\)
-   **keep-parallel:** this will not remove any times in the
    `processor`-directories. Also are things like
    `keep-last` now honored for processor directories
-   **remove-analyzed:** Remove the directories with the analyzed data
    too. Old behavior was to remove them. Now they are kept by default

### `pyFoamFromTemplate.py` automatically chooses template and default values<a id="sec-3-7-4" name="sec-3-7-4"></a>

If an output file `foo` is specified and no template then the
utility looks for a file `foo.template` as a template.

If a file `foo.defaults` is present then this file is read and
used as default parameter values. Other specifications override
these defaults

### `pyFoamDumpRunDatabaseToCSV.py` can disable standard-fields<a id="sec-3-7-5" name="sec-3-7-5"></a>

Additional option `--disable-run-data`

### `pyFoamDumpRunDatabaseToCSV.py` prints `pandas`-object<a id="sec-3-7-6" name="sec-3-7-6"></a>

With the `-pandas-print`-option a `DataFrame` is generated and
printed

### Better debugging with `ipdb`<a id="sec-3-7-7" name="sec-3-7-7"></a>

If the `ipdb`-package (basically `pdb` with `IPython`-additions)
is installed then it is used. This gives additions like
tab-completion

### Interactive shell after execution for utilities<a id="sec-3-7-8" name="sec-3-7-8"></a>

The option `--interactive-after-execution` drops the user to an
interactive shell where the namespace can be inspected. If present
`IPython` will be used, otherwise the regular shell is used

### Utilities that read quantitative data convert to `pandas`-data and/or `numpy`<a id="sec-3-7-9" name="sec-3-7-9"></a>

This is mainly to be used on the interactive shell to do further
analysis or write this data out. The utilities are:
-   **pyDumpRunDatabaseToCSV.py:** add an item `dump` with the whole
    data as a `DataFrame`
-   **pyFoamTimelinePlot.py:** add element `series` with all the data
    as `Series` and `dataFrame` with the same data as a `DataFrame`
-   **pyFoamSamplePlot.py:** Like `pyFoamTimelinePlot.py`
-   **pyFoamRedoPlot.py:** Now can get series and the whole plot data
    as pandas-objects

### Utilities that read quantitative data write Excel files<a id="sec-3-7-10" name="sec-3-7-10"></a>

The utilities `pyDumpRunDatabaseToCSV.py`,
`pyFoamTimelinePlot.py`, `pyFoamSamplePlot.py` and
`pyFoamRedoPlot.py` now have options to write Excel-files

### Specify additional settings for `GnuPlot` in `customRegexp`<a id="sec-3-7-11" name="sec-3-7-11"></a>

If an item in `customRegexp` has an item `gnuplotCommands` then
it is assumed that this is a list of strings which are executed
before the first plotting. For instance

    gnuplotCommands (
       "set format y '%.2e'"
     );

changes the number format on the y-axis

### More flexible data specification for `pyFoamSamplePlot.py`<a id="sec-3-7-12" name="sec-3-7-12"></a>

Instead of determining the names of the fields and lines form the
filenames it is now also possible to specify them through options.

The option `--is-distribution` is a shorthand that sets these
options for distribution files

### `pyFoamSamplePlot.py` now allows specification of x-range<a id="sec-3-7-13" name="sec-3-7-13"></a>

The range of the x-axis of the plots can either be set by
automatically scaling to the domains of all the data sets with
`--scale-domain` or by specifying them with `--domain-minimum` or
`--domain-maximum`.

These domains are set for **all** plots

# Version 0.6.1 - 2013-05-24<a id="sec-4" name="sec-4"></a>

## Major changes<a id="sec-4-1" name="sec-4-1"></a>

## Bugfixes<a id="sec-4-2" name="sec-4-2"></a>

### Restoring of `controlDict` after `write`<a id="sec-4-2-1" name="sec-4-2-1"></a>

When activating an on-demand write the `constrolDict` was not
restored because the output-line about the file being read was not
recognized (due to a change in the output in recent
OF-versions). Now a number of different formats is recognized

### Custom-plot type `slave` not working if no `master` defined<a id="sec-4-2-2" name="sec-4-2-2"></a>

That plot-type needs a `master`. Fixed to fail if none is defined

### `-list-only` did not correctly parse lists with a numeric prefix<a id="sec-4-2-3" name="sec-4-2-3"></a>

This did affect all utilities that use that option and also calls
with `listOnly` to the library class

## Utilities<a id="sec-4-3" name="sec-4-3"></a>

### `pyFoamBuildHelper.py` now allow more than one action<a id="sec-4-3-1" name="sec-4-3-1"></a>

If multiple actions like `--update` and `--build` are specified
they are executed in a sensible order (update before build etc)

### Utilities warn if OpenFOAM-version is unset<a id="sec-4-3-2" name="sec-4-3-2"></a>

If the environment variable that determines the OpenFOAM-version
is unset a warning is issued by the utilities

### `pyFoamUpgradeDictionariesTo20.py` allows single files<a id="sec-4-3-3" name="sec-4-3-3"></a>

If  single file is specified then the action to transform it has
can be specified

### `pyFoamUpgradeDictionariesTo20.py` transforms reaction-schemes<a id="sec-4-3-4" name="sec-4-3-4"></a>

Now knows how to transform "old" reaction files (where the
`reactions`-entry was a list) to the new format (where it is a
dictionary). Only a limited number of reaction types is supported.

### `pyFoamUpgradeDictionariesTo20.py` transforms thermophysical data<a id="sec-4-3-5" name="sec-4-3-5"></a>

Now the old form of thermophysical data (lists) is transformed
into the new dictionary-form

### `pyFoamCloneCase` now allows creating directory that symlinks to the original<a id="sec-4-3-6" name="sec-4-3-6"></a>

Now with the option `--symlink-mode` instead of copying the
directories from the original new directories art created and
populated with symlinks to the files in the original. The depth
until which no symlinks to directories are created can be
specified. This allows the clone to share the configuration files
with the original

### `pyFoamClearCase.py` now removes `postProcessing` and allows removal of additional files<a id="sec-4-3-7" name="sec-4-3-7"></a>

The directory `postProcessing` is now automatically removed (can be
switched off with `--keep-postprocessing`). Also with the
`--additional`-option patterns with additional files to remove
can be specified.

### Improvements to `pyFoamVersion.py`<a id="sec-4-3-8" name="sec-4-3-8"></a>

-   Now reports the location of the `python`-executable
-   Reports locations of used libraries

### Additional files automatically cloned<a id="sec-4-3-9" name="sec-4-3-9"></a>

The files `Allrun`, `Allclean` and `0.org` are automatically
added during cloning as these are often used by the standard-utilities

### `pyFoamDisplayBlockMesh.py` uses the same options for template format as `pyFoamFromTemplate.py`<a id="sec-4-3-10" name="sec-4-3-10"></a>

This makes sure that templates are handled consistently and also
allows different delimiters in the `blockMeshDict.template`

## Library<a id="sec-4-4" name="sec-4-4"></a>

### Improvements in syntax of `ParsedParameterFile`<a id="sec-4-4-1" name="sec-4-4-1"></a>

-   Now the new relative scoping that was introduced in OF 2.2 is
    supported

### `Utilities`-class now function to find files matching a pattern<a id="sec-4-4-2" name="sec-4-4-2"></a>

Added a function `find` that approxiamtes the `find`-command

### VCS ignores more files<a id="sec-4-4-3" name="sec-4-4-3"></a>

Some more patterns have been added that will be ignored in a
VSC-controlled case. All of them concerning files that PyFoam
creates during operation

## New features/Utilities<a id="sec-4-5" name="sec-4-5"></a>

### New Utility `pyFoamSymlinkToFile.py`<a id="sec-4-5-1" name="sec-4-5-1"></a>

This utility replaces a symlink with a copy of the
file/directories it points to. To be used after a
`pyFoamCloneCase.py` in `--symlink-mode`

# Version 0.6.0 - 2013-03-14<a id="sec-5" name="sec-5"></a>

## Major changes<a id="sec-5-1" name="sec-5-1"></a>

### Adaption to work with Python3<a id="sec-5-1-1" name="sec-5-1-1"></a>

Sources are adapted so that `PyFoam` works with Python3 too. This
breaks support for Python 2.4 and earlier (possibly also Python
2.5)

Some of the Libraries in `PyFoam.ThirdParty` had to be adapted to
work with Python3:
-   **Gnuplot.py:** The original version 1.8 is quite old. It was
    adapted with the help of the `six`-library (see
    below) to work with Python2 and Python3 (inspired
    by
    [<https://github.com/oblalex/gnuplot.py-py3k/commits/master>]
    which is a pure port to Python3 without backwards
    compatibility)

### New ThirdParty-Libraries<a id="sec-5-1-2" name="sec-5-1-2"></a>

-   **six:** Library that helps supporting Python 2 and Python 3 in
    the same source code. Currently version 1.2 from
    [<https://bitbucket.org/gutworth/six>] is used
-   **pyratemp:** Templating library to support the new templating
    format. Version 0.2.0 from
    [<http://www.simple-is-better.org/template/pyratemp.html>]
    is used

### Porting to `Windows`<a id="sec-5-1-3" name="sec-5-1-3"></a>

Port to allow running PyFoam on Windows was done by Bruno Santos
of blueCAPE (bruno.santos@bluecape.com.pt)

Patch was originally posted at
<http://sourceforge.net/apps/mantisbt/openfoam-extend/view.php?id=166>

**Note**: many of PyFoam's features are not yet fully functional on
Windows.

### Experimental port to `pypy`<a id="sec-5-1-4" name="sec-5-1-4"></a>

Sources are executed in `pypy` but it seems there are problems
with `numpy` and also with code like `for l in open(f).readlines()`

## Third-Party<a id="sec-5-2" name="sec-5-2"></a>

### Upgraded `ply` to 3.4<a id="sec-5-2-1" name="sec-5-2-1"></a>

This brings virtually no changes. `README` with copyright
information has been added

## Infrastructure<a id="sec-5-3" name="sec-5-3"></a>

### Parameters can't be modified in `CTestRun` after initialization<a id="sec-5-3-1" name="sec-5-3-1"></a>

This should help to avoid side-effects

### Treat timeouts in the `MetaServer` right<a id="sec-5-3-2" name="sec-5-3-2"></a>

Due to a previous workaround timeouts when collecting information
about new machines was not treated correctly

### Add `execute`-method to `ClusterJob`<a id="sec-5-3-3" name="sec-5-3-3"></a>

This allows the execution of a shell-script in the directory of
the case

### Add possibility to run specific modules before or after the solver<a id="sec-5-3-4" name="sec-5-3-4"></a>

These modules are found in `PyFoam.Infrastructure.RunHooks`. Two
concrete implementations:
-   **`PrintMessageHook`:** to print a text to the terminal
-   **`SendToWebservice`:** encode an URL and send it to a webservice
    (example for `pushover.net` added)

Hooks are automatically instantiated from the configuration data
(examples are hardcoded))

### Parameters added to the info about the run<a id="sec-5-3-5" name="sec-5-3-5"></a>

The Runner-classes now have a parameter `parameters`. This data
(usually it would be a dictionary) is added verbatim to the run
info.

Most runner applications now have the possibility to add this
info.

Purpose of this facility is to identify different runs in the
database better.

### Parameter handling in `ClusterJob` extended<a id="sec-5-3-6" name="sec-5-3-6"></a>

Parameter values are now handed to the actual job. Also a
dictionary with parameters can be handed to the constructor and
will be used in the relevant callbacks

### Run data written alongside `PickledPlots`<a id="sec-5-3-7" name="sec-5-3-7"></a>

During the run whenever the `PickledPlots`-file is written a file
`pickledUnfinishedData` gets written. This has the current solver
data and is similar to `pickledData`.

Also a file `pickledStartData` gets written that has the data that
is available at the start of the run.

### `BasicRunner` collects error and warning texts<a id="sec-5-3-8" name="sec-5-3-8"></a>

The runner collects
-   at every warning the next 20 lines of the output until a total
    of 500 lines is reached (this avoids filling disk and memory if
    the solver produces too many warnings)
-   All output from an error message until the end

And stores them in the application data

## Library<a id="sec-5-4" name="sec-5-4"></a>

### `TemplateFile` now uses `pyratemp`<a id="sec-5-4-1" name="sec-5-4-1"></a>

The class `TempalteFile` now uses an enhanced templating
engine. The  old implementation is in the class
`TemplateFileOldFormat`

### Clearer error message in Application-classes<a id="sec-5-4-2" name="sec-5-4-2"></a>

If used as classes (not as utilities) these classes print the
class name instead of the calling utilities name

### Output is only colored if it goes to the terminal<a id="sec-5-4-3" name="sec-5-4-3"></a>

Error and warning messages don't decorate the output if it goes to
files or other non-terminal streams

### `error`-method of application classes now raises an exception<a id="sec-5-4-4" name="sec-5-4-4"></a>

An exception is now raised by `self.error()`. This makes it easier
to handle such errors if the application class is used. The
exception is passed up until there is a "real" application

### `ParsedParameterFile` now knows how to handle binary files<a id="sec-5-4-5" name="sec-5-4-5"></a>

When the format of a file is `binary` lists with a length prefix
are being read as binary blobs.

For reading the blobs a simple heuristics is used: a multiple of
the length in bytes is read. If the next character is a `)` and
the characters after that are a certain combination of characters
(newlines and `;`) then it is assumed that the blob has
ended. This may fail on certain occasions:
-   if the combination of characters appears at these places
-   if the objects inside the binary data are of different sizes

It would be hard to work around these restrictions without
reprogramming the full functionality of OpenFOAM

### `LabledReSTTable` for more flexible table generation<a id="sec-5-4-6" name="sec-5-4-6"></a>

New class in the `RestructuredTextHelper` allows more flexible
generation of tables. Items are added with `column` and `row` and
if these don't exist in the first row/column the table is extended
appropriately

### Plotting classes now allow setting of `xlabel`<a id="sec-5-4-7" name="sec-5-4-7"></a>

This is implemented for `Gnuplot` and `Matplotlib`. Default for
the label on the x-Axis is now "Time [s]"

## Utilities<a id="sec-5-5" name="sec-5-5"></a>

### `pyFoamFromTemplate.py` with new templating engine<a id="sec-5-5-1" name="sec-5-5-1"></a>

The utility can now use the pyratemp-templating engine which
allows templates with loops, conditions and other  fancy stuff

### `pyFoamSamplePlot.py` allows using the reference data as basis for comparison<a id="sec-5-5-2" name="sec-5-5-2"></a>

Instead of using the x-values from the original data the y-values
of the reference data can be used for comparing (with the
`--use-reference`-option)

Same for `pyFoamTimelimePlot.py`

### Scaling and offsets are now used in plots of `pyFoamSamplePlot.py`<a id="sec-5-5-3" name="sec-5-5-3"></a>

If scales not equal to \(1\) and offsets not equal to \(0\) are
specified they are used in the `gnuplot`-output

### `pyFoamPrintData2DStatistics.py` prints relative average error<a id="sec-5-5-4" name="sec-5-5-4"></a>

With the `--relative-average-error`-option

### Enhancements to `pyFoamVersion.py`<a id="sec-5-5-5" name="sec-5-5-5"></a>

-   More tolerant if no library was found
-   Reports the location of the PyFoam-Library
-   Checks whether utility version is consistent the library found

### `pyFoamRunner.py` allows hooks<a id="sec-5-5-6" name="sec-5-5-6"></a>

Hooks can be added at the start and the end of a run

### `pyFoamRedoPlots.py` supports range for plots<a id="sec-5-5-7" name="sec-5-5-7"></a>

Added `-end` and `-start`-option to select a range that should be
plotted.

Currently not working with the Matplotlib-implementation (only gnuplot)

### `pyFoamDisplayBlockMesh.py` no supports templates<a id="sec-5-5-8" name="sec-5-5-8"></a>

If a file with values is specified then the utility assumes you're
editing a template file and will evaluate it before displaying it

### `pyFoamCaseReport.py` is tolerant towards binary files<a id="sec-5-5-9" name="sec-5-5-9"></a>

New switch that makes the parser treat files that are declared
`binary` in the header as if they were `ascii`

### `pyFoamSamplePlot.py` and `pyFoamTimelinePlot.py` raise error if no plots are generated<a id="sec-5-5-10" name="sec-5-5-10"></a>

This makes it easier to catch faulty specifications (or empty
timeline-files)

### `pyFoamSurfacePlot.py` can wait for a key<a id="sec-5-5-11" name="sec-5-5-11"></a>

An option `--wait` has been added that makes the utility wait
before displaying the next picture

### `pyFoamEchoDictionary.py` is more flexible with binary files<a id="sec-5-5-12" name="sec-5-5-12"></a>

Switch allows forcing it to read a binary File as an ASCII

### All utilities now have a switch that starts the debugger even with syntax-errors<a id="sec-5-5-13" name="sec-5-5-13"></a>

Previously the option `--interactive-debug` only started the
debugger if the error was **no** syntax error. This is still the
default behavior, but can be overruled

### Utilities now can be killed with `USR1` and will give a traceback<a id="sec-5-5-14" name="sec-5-5-14"></a>

The option `--catch-USR1-signal` now installs a signal-handler
that prints a traceback and finishes the run. If the interactive
debugger is enabled then it goes to the debugger-shell.

Option `--keyboard-interrupt-trace` triggers the same behaviour
for keyboard interrupts with `<Ctrl>-C`

### Switch to switch on **all** debug options<a id="sec-5-5-15" name="sec-5-5-15"></a>

For the purpose of developing a switch `--i-am-a-developer` has
been added.

### Plotting utilities now allow specification of x-Axis label<a id="sec-5-5-16" name="sec-5-5-16"></a>

With the option `xlabel` in the `customRegexp`-file the label on
the x-axis of the plot can be changed. Setting `ylabel` and
`y2label` (for the secondary axis) was already possible

### Metrics and compare for `pyFoamTimelinePlot.py` and `pyFoamSamplePlot.py` support time ranges<a id="sec-5-5-17" name="sec-5-5-17"></a>

Now the options `--min-time` and `--max-time` are supported by
`--metrics` and `--compare`

### `pyFoamDisplayBlockMesh.py` allows graphical selection of blocks and patches<a id="sec-5-5-18" name="sec-5-5-18"></a>

New addition by Marc Immer allows the graphical selection of
blocks and patches and adds them to the `blockMeshDict`

### `pyFoamCloneCase.py` and `pyFoamPackCase.py` accept additional parameters<a id="sec-5-5-19" name="sec-5-5-19"></a>

The file `LocalConfigPyFoam` is read by these utilities and if
there is a parameter `addItem` in the section `Cloning` defined
then these files are cloned/packed automatically (no user
specification required)

### `pyFoamListCases.py` now calculates estimated end-times<a id="sec-5-5-20" name="sec-5-5-20"></a>

Additional option to print the estimated end times. These can be
wrong if the case did not start from the `startTime` in the
`controlDict`.

Also now allows printing the end and the start-time according to
the `controlDict`

## New features<a id="sec-5-6" name="sec-5-6"></a>

### Different "phases" for multi-region solvers<a id="sec-5-6-1" name="sec-5-6-1"></a>

Plots of type `phase` in `customRegexp` don't actually plot
anything. The set a phase-name that is used for subsequent values
(for instance to distinguish the different residuals)

### `pyFoamChangeBoundaryType.py` allows selection of region and time<a id="sec-5-6-2" name="sec-5-6-2"></a>

Options `--region` and `--time-directory` added that allow
selecting different `boundary`-files

### New class for storing case data in a sqlite-database and associated utilities<a id="sec-5-6-3" name="sec-5-6-3"></a>

The class `RunDatabase` stores the data from runs. Utility
`pyFoamAddCaseDataToDatabase.py` is one way to populate the
database. `pyFoamDumpRunDatabaseToCSV.py` allows dumping that
data to a file for further processing (in a spreadsheet for
instance)

Database can also be populated using a special post-run hook

## Bugfixes<a id="sec-5-7" name="sec-5-7"></a>

### Only binary packages of 1.x were found<a id="sec-5-7-1" name="sec-5-7-1"></a>

Pattern had to start with 1 (now every digit is possible))

### Option group *Regular expressions* was listed twice<a id="sec-5-7-2" name="sec-5-7-2"></a>

No harm done. But fixed

### `--clear`-option for `pyFoamDecompose.py` not working<a id="sec-5-7-3" name="sec-5-7-3"></a>

Reason was that `rmtree` does not allow wildcards. Fixed

### `pyFoamDisplayBlockmesh.py` not working with variable substitution<a id="sec-5-7-4" name="sec-5-7-4"></a>

The `DictRedirect` would not convert to float. Fixed. Although it
might happen again for other data types

### Option `--function-object-data` of `pyFoamClearCase.py` not working with directories<a id="sec-5-7-5" name="sec-5-7-5"></a>

The option was only implemented for the list-form of the
`functions` entry in `controlDict`

Now fixed to also work with the dictionary-form

### `nonuniform` of length 0 not correctly printed<a id="sec-5-7-6" name="sec-5-7-6"></a>

Seems like the length was interpreted as the name of the
list. Fixed

### Building of pseudocases with `pyFoamRunner.py` broken<a id="sec-5-7-7" name="sec-5-7-7"></a>

Only worked if no region was specified (= not at all). Fixed

### `pyFoamRedoPlot.py` did not correctly honor `--end` and `--start`<a id="sec-5-7-8" name="sec-5-7-8"></a>

Plots were over the whole data range. This is now fix (also the
issue that `--end` alone did not work)

### `WriteParameterFile` does not preserve the order of additions<a id="sec-5-7-9" name="sec-5-7-9"></a>

Contents was "only" set as a dictionary which does not preserve
the order in which entries are added. Replaced with a `DictProxy`

### Wrong number of arguments when using `TimelinePlot` in `positions`-mode<a id="sec-5-7-10" name="sec-5-7-10"></a>

Problem that was introduced by changes in the `fields`-mode

### `ClusterJob` uses only `metis` for decomposition<a id="sec-5-7-11" name="sec-5-7-11"></a>

For OpenFOAM-versions 1.6 and higher the automatic decomposition
used is now `scotch`

### `pyFoamSamplePlot.py` and `pyFoamTimelinePlot.py` produced no pictures for regions<a id="sec-5-7-12" name="sec-5-7-12"></a>

As regions have their own subdirectories the `/` from the
directory name was inserted into the filename and if the
subdirectory did not exist `gnuplot` did not create the picture

### Barplots in `pyFoamTimelinePlot.py` not working if value is a vector<a id="sec-5-7-13" name="sec-5-7-13"></a>

The base class didn't correctly handle the `(` and `)`. Fixed

### Mysterious deadlocks while plotting long logfiles<a id="sec-5-7-14" name="sec-5-7-14"></a>

The problem was that during splitting the timeline data an exception was
raised. This exception was caught by another part of PyFoam. This
left a lock on the data structure locked and the next access to
the structure was held indefinitely. Fixed

### Scanning linear expressions form the block coupled solver failed<a id="sec-5-7-15" name="sec-5-7-15"></a>

As there is a tuple of residuals the scanner did not analyze the
output of the output of the block-coupled solver from `1.6-ext`
correctly. This is now treated as a special case and each residual
is plotted separately (distinguished by a `[x]` with `x` being the
number of the component)

### `#include` not correctly working with macros in the included file<a id="sec-5-7-16" name="sec-5-7-16"></a>

Macros `$var` were not correctly expanded. Fixed

### Macros not correctly expanded to strings<a id="sec-5-7-17" name="sec-5-7-17"></a>

When being expanded to string form macros were not correctly
expanded

### `pyFoamPackCase.py` in the working directory produces 'invisible' tar<a id="sec-5-7-18" name="sec-5-7-18"></a>

If the utility was used in the form

    pyFoamPackCase.py .

then an 'invisible' tar `..tgz` was produced. Fixed

### String at the end of a linear solver output makes parsing fail<a id="sec-5-7-19" name="sec-5-7-19"></a>

Reported in
[<http://www.cfd-online.com/Forums/openfoam-solving/112278-pyfoam-struggles-adopted-solver-post403990.html>]
the string is assumed to be part of the iteration number. Fixed

### Paraview utilities not working with higher Paraview versions<a id="sec-5-7-20" name="sec-5-7-20"></a>

At least for PV 3.14 and 3.98 the way the version number is
determined has changed and the PV-utilities failed. This has been
fixed but is untested with old versions

### Camera settings not honored with `pyFoamPVSnapshot.py`<a id="sec-5-7-21" name="sec-5-7-21"></a>

For the first rendered view Paraview automatically resets the
camera. This has now been switched off (so the snapshot is
rendered correctly)

# Version 0.5.7 - 2012-04-13<a id="sec-6" name="sec-6"></a>

## Parser improvements<a id="sec-6-1" name="sec-6-1"></a>

-   Problem with nested comments
-   Parse code streams
-   Preserving of comments can be switched off
-   Ignore extra semicolons
-   Allows parsing lists of length 3 and 9 as lists and not as
    vectors and tensors
-   "lookup redirection" in OF-dictionaries now works

## Utility improvements<a id="sec-6-2" name="sec-6-2"></a>

-   pyFoamSamplePlot.py stops if the same directory is compared
-   pyFoamSamplePlot.py shows the location of the biggest difference
-   pyFoamSamplePlot.py allows only same ranges for comparisons
-   Generation of pickled-files can be switched of for runner-utilities
-   Frequency with which the pickled file is written is adapted (so
    that it doesn't use ALL the CPU-time)
-   pyFoamVersion.py improved (Version of Python is checked etc)
-   pyFoamRedoPlot.py: fixed parameter checking
-   pyFoamPotentialRunner.py: temporarily disable libs and functions
-   Only write last N loglines from Runner-utility
-   pyFoamClearCase.py: allow local specification of additional files
    that should be cleared
-   Runner utilities can report data about the run
-   pyFoamConvertToCSV.py now allows selection of columns
-   Utilities for quantative analysis now can return data
-   Utilities for quantative now correctly return data for multiple places
-   pyFoamSamplePlot.py now allows specification of valid variable pre and
    postfixes to allow correct parsing of variable names with a \_
-   endTime can be specified by the runner-utilities
-   Utilities now allow piping (using pickled data)
-   pyFoamSamplePlot.py now allows the specification of a reference time
-   Nomenclature of pyFoamSamplePlot.py and pyFoamTimelinePlots.py
    now similar (both call it fields)
-   pyFoamDecompose.py now can use the -region-option ifthe
    OF-version is right
-   Forcing debug-mode fixed for older OF-versions
-   pyFoamDecomposer.py now accepts globalFaceZones in Python or
    OpenFOAM-syntax
-   Plot-utilities now don't interpret \_ in names not as LaTeX

## New Utilities<a id="sec-6-3" name="sec-6-3"></a>

-   pyFoamEchoPickledApplicationData to output pickled data
-   pyFoamPrintData2DStatistics.py to output data from comparisons
-   pyFoamBuildHelper.py to build project and its prerequisites (work
    in progress)
-   pyFoamCreateModuleFile.py to create files for
    <http://modules.sourceforge.net/> (by Martin Beaudoin)
-   pyFoamSTLUtility.py to join STL-files

## Library improvements<a id="sec-6-4" name="sec-6-4"></a>

-   stabler comparisons
-   Paraview-Utilities work with 1.x and 2.x
-   Runner classes return a dictionary with data
-   TimelineDirectory ignores dot-files
-   Application-objects can now be used like dictionaries to access
    data
-   New class TableData for simple data tables
-   New class Data2DStatistics for statistics about tables
-   new class CTestRun as basis for automated testing
-   FoamOptionParser now resets environment variables so that
    application-classes can call other application classes
-   Improvements to HgInterface
-   Additional VCS-subclasses for git, svn and svk (implementation
    only as needed)
-   SolutionDir now uses 0.org as initial directory if no valid
    initial directory is present (this affects clearing and cloning)
-   FoamFileGenerator now more flexible for long lists
-   ParsedBlockMeshDict now doesn't introduce prefixes for 'long' lists

## Removed utilities<a id="sec-6-5" name="sec-6-5"></a>

-   pyFoamAPoMaFoX.py
-   pyFoamPlotResiduals.py

## Thirdparty<a id="sec-6-6" name="sec-6-6"></a>

-   Got rid of Numeric-support in Gnuplot-library

## Other<a id="sec-6-7" name="sec-6-7"></a>

-   script to generate man-pages for the utilities
-   Paraview3-example probeDisplay.py now renamed to
    probeAndSetDisplay.py and reads sampledSets from controlDict and
    sampleDict

# Older Versions<a id="sec-7" name="sec-7"></a>

The changes for older versions can be found on
[the Wiki-page](http://openfoamwiki.net/index.php/Contrib_PyFoam#History)

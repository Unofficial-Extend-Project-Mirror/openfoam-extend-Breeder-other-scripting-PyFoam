"""
New implementation of DisplayBlockMesh using PyQT4
"""

from PyFoam.RunDictionary.ParsedBlockMeshDict import ParsedBlockMeshDict
from PyFoam.Applications.PyFoamApplicationQt4 import PyFoamApplicationQt4
from PyFoam.Error import error,warning
from PyFoam.RunDictionary.SolutionDirectory import NoTouchSolutionDirectory
from PyFoam.Execution.BasicRunner import BasicRunner

import sys
from os import path

def doImports():
    try:
        global QtGui,QtCore
        from PyQt4 import QtGui,QtCore        
        global vtk
        try:
            import vtk
            print "Using system-VTK"
        except ImportError:
            print "Trying VTK implementation from Paraview"
            from paraview import vtk
        global QVTKRenderWindowInteractor
        from vtk.qt4 import QVTKRenderWindowInteractor
    except ImportError,e:
        error("Error while importing modules:",e)

doImports()

class ReportToThreadRunner(BasicRunner):
    def __init__(self,
                 argv,
                 thread):
        BasicRunner.__init__(self,
                             argv=argv,
                             noLog=True,
                             silent=True)
        self.thread=thread

    def lineHandle(self,line):
        self.thread.append(line)

class UtilityThread(QtCore.QThread):
    def __init__(self,
                 argv,
                 parent):
        super(UtilityThread,self).__init__(parent)
        self.argv=argv
        self.status=""
    def run(self):
        try:
            runner=ReportToThreadRunner(argv=self.argv,
                                        thread=self)
            runner.start()
            if not runner.runOK():
                self.status=" - Problem"
                
        except IOError:
            self.status=" - OS Problem"
    
    def append(self,line):
        self.emit(QtCore.SIGNAL("newLine(QString)"),line)
        
class DisplayBlockMeshDialog(QtGui.QMainWindow):
    def __init__(self,fName):
        super(DisplayBlockMeshDialog,self).__init__(None)
        self.fName=fName

        self.numberScale=2
        self.pointScale=1
        self.axisLabelScale=1
        self.axisTubeScale=0.5
        
        self.setWindowTitle("%s[*] - DisplayBlockMesh" % fName)

        self.caseDir=None
        try:
            caseDir=path.sep+apply(path.join,path.abspath(fName).split(path.sep)[:-3])
            isOK=NoTouchSolutionDirectory(caseDir)
            if isOK:
                self.caseDir=caseDir
                self.setWindowTitle("Case %s[*] - DisplayBlockMesh" % caseDir.split(path.sep)[-1])
        except:
            pass
        
        central = QtGui.QWidget()
        self.setCentralWidget(central)
        
        layout = QtGui.QVBoxLayout()
        central.setLayout(layout)
        self.renInteractor=QVTKRenderWindowInteractor.QVTKRenderWindowInteractor(central)
        #        self.renInteractor.Initialize() # this creates a segfault for old PyQt
        self.renInteractor.Start()
        
        layout.addWidget(self.renInteractor)

        mainDock=QtGui.QDockWidget("Main controls",
                                   self)
        mainDock.setObjectName("MainControlsDock")
        mainDock.setFeatures(QtGui.QDockWidget.DockWidgetFloatable | QtGui.QDockWidget.DockWidgetMovable)
        mainDock.setAllowedAreas(QtCore.Qt.TopDockWidgetArea | QtCore.Qt.BottomDockWidgetArea)
        mainDockWidget=QtGui.QWidget()
        mainDock.setWidget(mainDockWidget)
        
        subLayout=QtGui.QGridLayout()
        mainDockWidget.setLayout(subLayout)
        self.addDockWidget(QtCore.Qt.BottomDockWidgetArea, mainDock)
        
        self.renInteractor.show()
        self.renWin = self.renInteractor.GetRenderWindow()
        self.ren = vtk.vtkRenderer()
        self.renWin.AddRenderer(self.ren)
        self.renWin.SetSize(600, 600)
        self.ren.SetBackground(0.7, 0.7, 0.7)
        self.ren.ResetCamera()
        self.cam = self.ren.GetActiveCamera()
        self.axes = vtk.vtkCubeAxesActor2D()
        self.axes.SetCamera(self.ren.GetActiveCamera())

        self.undefinedActor=vtk.vtkTextActor()
        self.undefinedActor.GetPositionCoordinate().SetCoordinateSystemToNormalizedDisplay()
        self.undefinedActor.GetPositionCoordinate().SetValue(0.05,0.2)
        self.undefinedActor.GetTextProperty().SetColor(1.,0.,0.)
        self.undefinedActor.SetInput("")

        self.rereadAction=QtGui.QAction("&Reread",
                                        self)
        self.rereadAction.setShortcut("Ctrl+R")
        self.rereadAction.setToolTip("Reread the blockMesh-file")
        self.connect(self.rereadAction,
                     QtCore.SIGNAL("triggered()"),
                     self.reread)
        
        self.blockMeshAction=QtGui.QAction("&BlockMesh",
                                        self)
        self.blockMeshAction.setShortcut("Ctrl+B")
        self.blockMeshAction.setToolTip("Execute blockMesh-Utility")
        self.connect(self.blockMeshAction,
                     QtCore.SIGNAL("triggered()"),
                     self.blockMesh)
        
        self.checkMeshAction=QtGui.QAction("Chec&kMesh",
                                        self)
        self.checkMeshAction.setShortcut("Ctrl+K")
        self.checkMeshAction.setToolTip("Execute checkMesh-Utility")
        self.connect(self.checkMeshAction,
                     QtCore.SIGNAL("triggered()"),
                     self.checkMesh)
        if self.caseDir==None:
            self.blockMeshAction.setEnabled(False)
            self.checkMeshAction.setEnabled(False)
        
        self.quitAction=QtGui.QAction("&Quit",
                                      self)
        
        self.quitAction.setShortcut("Ctrl+Q")
        self.quitAction.setToolTip("Quit this program")
        self.connect(self.quitAction,
                     QtCore.SIGNAL("triggered()"),
                     self.close)

        self.saveAction=QtGui.QAction("&Save",
                                      self)
        
        self.saveAction.setShortcut(QtGui.QKeySequence.Save)
        self.saveAction.setToolTip("Save the blockmesh from the editor")
        self.connect(self.saveAction,
                     QtCore.SIGNAL("triggered()"),
                     self.saveBlockMesh)
        self.saveAction.setEnabled(False)
        
        self.fileMenu=self.menuBar().addMenu("&Blockmesh file")
        self.fileMenu.addAction(self.rereadAction)
        self.fileMenu.addAction(self.saveAction)
        self.fileMenu.addSeparator()
        self.fileMenu.addAction(self.quitAction)

        self.editorDock=QtGui.QDockWidget("Edit blockMesh",
                                          self)
        self.editorDock.setObjectName("EditorDock")
        self.editorDock.setAllowedAreas(QtCore.Qt.LeftDockWidgetArea | QtCore.Qt.RightDockWidgetArea)

        try:
            self.editor=QtGui.QPlainTextEdit()
            self.editor.setLineWrapMode(QtGui.QPlainTextEdit.NoWrap)
            self.editor.textChanged.connect(self.blockMeshWasModified)
            self.alwaysSave=False
        except AttributeError:
            warning("Old PyQT4-version. Editing might not work as expected")
            self.editor=QtGui.QTextEdit()
            self.alwaysSave=True
            self.saveAction.setEnabled(True)

        self.editor.setFont(QtGui.QFont("Courier"))
        
        self.editorDock.setWidget(self.editor)
        self.addDockWidget(QtCore.Qt.RightDockWidgetArea,self.editorDock)
        self.editorDock.hide()
        
        self.utilityDock=QtGui.QDockWidget("Utility output",
                                          self)
        self.utilityOutput=QtGui.QTextEdit()
        self.utilityOutput.setFont(QtGui.QFont("Courier"))
        self.utilityOutput.setLineWrapMode(QtGui.QTextEdit.NoWrap)
        self.utilityOutput.setReadOnly(True)
        self.utilityDock.setWidget(self.utilityOutput)
        self.utilityDock.setObjectName("UtilityDock")
        self.utilityDock.setAllowedAreas(QtCore.Qt.LeftDockWidgetArea | QtCore.Qt.RightDockWidgetArea)
        self.addDockWidget(QtCore.Qt.RightDockWidgetArea,self.utilityDock)
        self.utilityDock.hide()

        self.worker=None

        self.texteditorAction=self.editorDock.toggleViewAction()
        self.texteditorAction.setShortcut("Ctrl+E")

        self.utilityAction=self.utilityDock.toggleViewAction()
        self.utilityAction.setShortcut("Ctrl+U")

        self.displayDock=QtGui.QDockWidget("Display Properties",
                                           self)
        self.displayDock.setObjectName("DisplayPropertiesDock")
        self.displayDock.setAllowedAreas(QtCore.Qt.LeftDockWidgetArea | QtCore.Qt.RightDockWidgetArea)

        displayStuff=QtGui.QWidget()
        displayLayout=QtGui.QGridLayout()
        displayStuff.setLayout(displayLayout)
        displayLayout.addWidget(QtGui.QLabel("Number scale"),0,0)
        nrScale=QtGui.QDoubleSpinBox()
        nrScale.setValue(self.numberScale)
        nrScale.setMinimum(1e-2)
        nrScale.setSingleStep(0.1)
        self.connect(nrScale,QtCore.SIGNAL("valueChanged(double)"),self.numberScaleChanged)
        displayLayout.addWidget(nrScale,0,1)
        displayLayout.addWidget(QtGui.QLabel("Point scale"),1,0)
        ptScale=QtGui.QDoubleSpinBox()
        ptScale.setValue(self.pointScale)
        ptScale.setMinimum(1e-2)
        ptScale.setSingleStep(0.1)
        self.connect(ptScale,QtCore.SIGNAL("valueChanged(double)"),self.pointScaleChanged)
        displayLayout.addWidget(ptScale,1,1)
        displayLayout.addWidget(QtGui.QLabel("Axis label scale"),2,0)
        axisLScale=QtGui.QDoubleSpinBox()
        axisLScale.setValue(self.axisLabelScale)
        axisLScale.setMinimum(1e-2)
        axisLScale.setSingleStep(0.1)
        self.connect(axisLScale,QtCore.SIGNAL("valueChanged(double)"),self.axisLabelScaleChanged)
        displayLayout.addWidget(axisLScale,2,1)
        displayLayout.addWidget(QtGui.QLabel("Axis tube scale"),3,0)
        axisTScale=QtGui.QDoubleSpinBox()
        axisTScale.setValue(self.axisTubeScale)
        axisTScale.setMinimum(1e-2)
        axisTScale.setSingleStep(0.1)
        self.connect(axisTScale,QtCore.SIGNAL("valueChanged(double)"),self.axisTubeScaleChanged)
        displayLayout.addWidget(axisTScale,3,1)

        displayLayout.setRowStretch(4,10)
        
        self.displayDock.setWidget(displayStuff)
        self.addDockWidget(QtCore.Qt.LeftDockWidgetArea,self.displayDock)
        self.displayDock.hide()

        self.displaypropertiesAction=self.displayDock.toggleViewAction()
        self.displaypropertiesAction.setShortcut("Ctrl+D")
        
        self.displayMenu=self.menuBar().addMenu("&Display")
        self.displayMenu.addAction(self.texteditorAction)
        self.displayMenu.addAction(self.displaypropertiesAction)
        self.displayMenu.addAction(self.utilityAction)

        self.utilityMenu=self.menuBar().addMenu("&Utilities")
        self.utilityMenu.addAction(self.blockMeshAction)
        self.utilityMenu.addAction(self.checkMeshAction)

        self.rereadButton=QtGui.QPushButton("Reread blockMeshDict")

        try:
            self.readFile()
        except Exception,e:
            warning("While reading",self.fName,"this happened:",e)
            raise e
        
        self.ren.ResetCamera()

        self.oldBlock=-1
        self.blockActor=None
        self.blockTextActor=None
        self.blockAxisActor=None

        self.oldPatch=-1
        self.patchActor=None
        self.patchTextActor=vtk.vtkTextActor()
        self.patchTextActor.GetPositionCoordinate().SetCoordinateSystemToNormalizedDisplay()
        self.patchTextActor.GetPositionCoordinate().SetValue(0.05,0.1)
        self.patchTextActor.GetTextProperty().SetColor(0.,0.,0.)
        self.patchTextActor.SetInput("Patch: <none>")

        label1=QtGui.QLabel("Block (-1 is none)")
        subLayout.addWidget(label1,0,0)
        self.scroll=QtGui.QSlider(QtCore.Qt.Horizontal)
        self.scroll.setRange(-1,len(self.blocks)-1)
        self.scroll.setValue(-1)
        self.scroll.setTickPosition(QtGui.QSlider.TicksBothSides)
        self.scroll.setTickInterval(1)
        self.scroll.setSingleStep(1)
        self.connect(self.scroll,QtCore.SIGNAL("valueChanged(int)"),self.colorBlock)
        subLayout.addWidget(self.scroll,0,1)

        label2=QtGui.QLabel("Patch (-1 is none)")
        subLayout.addWidget(label2,1,0)
        self.scroll2=QtGui.QSlider(QtCore.Qt.Horizontal)
        self.scroll2.setRange(-1,len(self.patches.keys())-1)
        self.scroll2.setValue(-1)
        self.scroll2.setTickPosition(QtGui.QSlider.TicksBothSides)
        self.scroll2.setTickInterval(1)
        self.scroll2.setSingleStep(1)
        self.connect(self.scroll2,QtCore.SIGNAL("valueChanged(int)"),self.colorPatch)
        subLayout.addWidget(self.scroll2,1,1)

        buttonLayout=QtGui.QHBoxLayout()
        buttonLayout.addStretch()

        subLayout.addLayout(buttonLayout,2,0,1,2)
        buttonLayout.addWidget(self.rereadButton)
        self.connect(self.rereadButton,QtCore.SIGNAL("clicked()"),self.reread)
        b1=QtGui.QPushButton("Quit")
        buttonLayout.addWidget(b1)
        self.connect(b1,QtCore.SIGNAL("clicked()"),self.close)
        
        self.iren = self.renWin.GetInteractor()
        self.istyle = vtk.vtkInteractorStyleSwitch()

        self.iren.SetInteractorStyle(self.istyle)
        self.istyle.SetCurrentStyleToTrackballCamera()

        #        self.iren.Initialize() # Seems to be unnecessary and produces segfaults
        #        self.renWin.Render()
        self.iren.Start()

        self.addProps()

        self.setUnifiedTitleAndToolBarOnMac(True)

        self.restoreGeometry(QtCore.QSettings().value("geometry").toByteArray())
        self.restoreState(QtCore.QSettings().value("state").toByteArray())
        
        self.setStatus()

    def blockMesh(self):
        self.executeUtility("blockMesh")
        
    def checkMesh(self):
        self.executeUtility("checkMesh")

    def executeUtility(self,util):
        if self.worker!=None:
            self.error("There seems to be another worker")
            
        self.setStatus("Executing "+util)
        self.blockMeshAction.setEnabled(False)
        self.checkMeshAction.setEnabled(False)

        self.utilityOutput.clear()
        self.utilityOutput.append("Running "+util+" on case "+self.caseDir)
        self.utilityDock.show()

        self.worker=UtilityThread(argv=[util,
                                        "-case",
                                        self.caseDir],
                                  parent=self)
        self.connect(self.worker,QtCore.SIGNAL("finished()"),self.executionEnded)
        self.connect(self.worker,QtCore.SIGNAL("newLine(QString)"),self.utilityOutputAppend)
        self.worker.start()

    def utilityOutputAppend(self,line):
        self.utilityOutput.append(line)
        
    def executionEnded(self):
        self.blockMeshAction.setEnabled(True)
        self.checkMeshAction.setEnabled(True)
        self.setStatus("Execution of "+self.worker.argv[0]+" finished"+self.worker.status)
        self.worker=None
        
    def setStatus(self,message="Ready"):
        if self.isWindowModified():
            message="blockMesh modified - "+message
        self.statusBar().showMessage(message)
            
    def blockMeshWasModified(self):
        if not self.saveAction.isEnabled():
            self.saveAction.setEnabled(True)
        if self.rereadAction.isEnabled():
            self.rereadAction.setEnabled(False)
            self.rereadButton.setEnabled(False)
            
        self.setWindowModified(True)
        self.setStatus()
        
    def readFile(self,resetText=True):
        if resetText:
            txt=open(self.fName).read()
            self.editor.setPlainText(txt)
            
        self.setWindowModified(False)
        if not self.alwaysSave:
            self.saveAction.setEnabled(False)
        self.rereadAction.setEnabled(True)
        self.rereadButton.setEnabled(True)
        
        self.blockMesh=ParsedBlockMeshDict(self.fName,
                                           doMacroExpansion=True)

        self.vertices=self.blockMesh.vertices()
        self.vActors=[None]*len(self.vertices)
        self.tActors=[None]*len(self.vertices)
        self.spheres=[None]*len(self.vertices)

        self.blocks=self.blockMesh.blocks()
        self.patches=self.blockMesh.patches()

        self.vRadius=self.blockMesh.typicalLength()/50

        for i in range(len(self.vertices)):
            self.addVertex(i)

        self.setAxes()

        self.undefined=[]
        
        for i in range(len(self.blocks)):
            self.addBlock(i)

        for a in self.blockMesh.arcs():
            self.makeArc(a)

        if len(self.undefined)>0:
            self.undefinedActor.SetInput("Undefined vertices: "+str(self.undefined))
        else:
            self.undefinedActor.SetInput("")

        self.setStatus("Read file")

    def saveBlockMesh(self):
        txt=str(self.editor.toPlainText())
        open(self.fName,"w").write(txt)

        self.reread(resetText=False)
        self.setStatus("Saved file")        

    def addUndefined(self,i):
        if not i in self.undefined:
            self.undefined.append(i)
            
    def addProps(self):
        self.ren.AddViewProp(self.axes)
        self.ren.AddActor2D(self.patchTextActor)
        self.ren.AddActor2D(self.undefinedActor)

    def numberScaleChanged(self,scale):
        self.numberScale=scale
        for tActor in self.tActors:
            tActor.SetScale(self.numberScale*self.vRadius,self.numberScale*self.vRadius,self.numberScale*self.vRadius)
        self.renWin.Render()
            
    def pointScaleChanged(self,scale):
        self.pointScale=scale
        for sphere in self.spheres:
            sphere.SetRadius(self.vRadius*self.pointScale)
        self.renWin.Render()

    def axisLabelScaleChanged(self,scale):
        self.axisLabelScale=scale
        if self.blockTextActor:
            for t in self.blockTextActor:
                t.SetScale(self.axisLabelScale*self.vRadius,
                           self.axisLabelScale*self.vRadius,
                           self.axisLabelScale*self.vRadius)
            self.renWin.Render()
            
    def axisTubeScaleChanged(self,scale):
        self.axisTubeScale=scale
        if self.blockAxisActor:
            for t in self.blockAxisActor:
                t.SetRadius(self.vRadius*self.axisTubeScale)
            self.renWin.Render()
    
    def addPoint(self,coord,factor=1):
        sphere=vtk.vtkSphereSource()
        sphere.SetRadius(self.vRadius*factor*self.pointScale)
        sphere.SetCenter(coord)
        mapper=vtk.vtkPolyDataMapper()
        mapper.SetInputConnection(sphere.GetOutputPort())
        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        self.ren.AddActor(actor)

        return sphere,actor

    def addVertex(self,index):
        coord=self.vertices[index]
        self.spheres[index],self.vActors[index]=self.addPoint(coord)
        text=vtk.vtkVectorText()
        text.SetText(str(index))
        tMapper=vtk.vtkPolyDataMapper()
        tMapper.SetInput(text.GetOutput())
        tActor = vtk.vtkFollower()
        tActor.SetMapper(tMapper)
        tActor.SetScale(self.numberScale*self.vRadius,self.numberScale*self.vRadius,self.numberScale*self.vRadius)
        tActor.AddPosition(coord[0]+self.vRadius,coord[1]+self.vRadius,coord[2]+self.vRadius)
        tActor.SetCamera(self.cam)
        tActor.GetProperty().SetColor(1.0,0.,0.)
        self.tActors[index]=tActor
        self.ren.AddActor(tActor)

    def addLine(self,index1,index2):
        try:
            c1=self.vertices[index1]
            c2=self.vertices[index2]
        except:
            if index1>=len(self.vertices):
                self.addUndefined(index1)
            if index2>=len(self.vertices):
                self.addUndefined(index2)
            return None
        line=vtk.vtkLineSource()
        line.SetPoint1(c1)
        line.SetPoint2(c2)
        mapper=vtk.vtkPolyDataMapper()
        mapper.SetInputConnection(line.GetOutputPort())
        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        self.ren.AddActor(actor)
        return actor

    def makeDirection(self,index1,index2,label):
        try:
            c1=self.vertices[index1]
            c2=self.vertices[index2]
        except:
            return None,None
        line=vtk.vtkLineSource()
        line.SetPoint1(c1)
        line.SetPoint2(c2)
        tube=vtk.vtkTubeFilter()
        tube.SetRadius(self.vRadius*self.axisTubeScale)
        tube.SetNumberOfSides(10)
        tube.SetInput(line.GetOutput())
        text=vtk.vtkVectorText()
        text.SetText(label)
        tMapper=vtk.vtkPolyDataMapper()
        tMapper.SetInput(text.GetOutput())
        tActor = vtk.vtkFollower()
        tActor.SetMapper(tMapper)
        tActor.SetScale(self.axisLabelScale*self.vRadius,
                        self.axisLabelScale*self.vRadius,
                        self.axisLabelScale*self.vRadius)
        tActor.AddPosition((c1[0]+c2[0])/2+self.vRadius,
                           (c1[1]+c2[1])/2+self.vRadius,
                           (c1[2]+c2[2])/2+self.vRadius)
        tActor.SetCamera(self.cam)
        tActor.GetProperty().SetColor(0.0,0.,0.)    
        return tube,tActor

    def makeSpline(self,lst):
        points = vtk.vtkPoints()
        for i in range(len(lst)):
            v=lst[i]
            points.InsertPoint(i,v[0],v[1],v[2])
        spline=vtk.vtkParametricSpline()
        spline.SetPoints(points)
        spline.ClosedOff()
        splineSource=vtk.vtkParametricFunctionSource()
        splineSource.SetParametricFunction(spline)
        mapper=vtk.vtkPolyDataMapper()
        mapper.SetInputConnection(splineSource.GetOutputPort())
        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        self.ren.AddActor(actor)

    def makeArc(self,data):
        try:
            self.makeSpline([self.vertices[data[0]],data[1],self.vertices[data[2]]])
        except:
            if data[0]>=len(self.vertices):
                self.addUndefined(data[0])
            if data[2]>=len(self.vertices):
                self.addUndefined(data[2])
            
        self.addPoint(data[1],factor=0.5)

    def makeFace(self,lst):
        points = vtk.vtkPoints()
        side = vtk.vtkCellArray()
        side.InsertNextCell(len(lst))
        for i in range(len(lst)):
            try:
                v=self.vertices[lst[i]]
            except:
                self.addUndefined(lst[i])
                return None
            points.InsertPoint(i,v[0],v[1],v[2])
            side.InsertCellPoint(i)
        result=vtk.vtkPolyData()
        result.SetPoints(points)
        result.SetPolys(side)

        return result

    def addBlock(self,index):
        b=self.blocks[index]

        self.addLine(b[ 0],b[ 1])
        self.addLine(b[ 3],b[ 2])
        self.addLine(b[ 7],b[ 6])
        self.addLine(b[ 4],b[ 5])
        self.addLine(b[ 0],b[ 3])
        self.addLine(b[ 1],b[ 2])
        self.addLine(b[ 5],b[ 6])
        self.addLine(b[ 4],b[ 7])
        self.addLine(b[ 0],b[ 4])
        self.addLine(b[ 1],b[ 5])
        self.addLine(b[ 2],b[ 6])
        self.addLine(b[ 3],b[ 7])

    def setAxes(self):
        append=vtk.vtkAppendPolyData()
        for a in self.vActors:
            if a!=None:
                append.AddInput(a.GetMapper().GetInput())
        self.axes.SetInput(append.GetOutput())
    
    def reread(self,resetText=True):
        self.ren.RemoveAllViewProps()
        self.patchActor=None
        self.blockActor=None
        self.blockAxisActor=None
        self.blockTextActor=None
        self.addProps()
        self.readFile(resetText=resetText)
        
        tmpBlock=self.scroll.value()
        if not tmpBlock<len(self.blocks):
            tmpBlock=len(self.blocks)-1
        self.scroll.setRange(-1,len(self.blocks)-1)
        self.scroll.setValue(tmpBlock)
        self.colorBlock(tmpBlock)

        tmpPatch=self.scroll2.value()
        if not tmpPatch<len(self.patches.keys()):
            tmpPatch=len(self.patches.keys())-1
        self.scroll2.setRange(-1,len(self.patches.keys())-1)
        self.scroll2.setValue(tmpPatch)
        self.colorPatch(tmpPatch)

        self.renWin.Render()
        
    def colorBlock(self,value):
        newBlock=int(value)
        if self.oldBlock>=0 and self.blockActor!=None:
            self.ren.RemoveActor(self.blockActor)
            for ta in self.blockTextActor:
                self.ren.RemoveActor(ta)
            self.blockActor=None
            self.blockTextActor=None
            self.blockAxisActor=None
        if newBlock>=0:
            append=vtk.vtkAppendPolyData()
            append2=vtk.vtkAppendPolyData()
            b=self.blocks[newBlock]
            append.AddInput(self.makeFace([b[0],b[1],b[2],b[3]]))
            append.AddInput(self.makeFace([b[4],b[5],b[6],b[7]]))
            append.AddInput(self.makeFace([b[0],b[1],b[5],b[4]]))
            append.AddInput(self.makeFace([b[3],b[2],b[6],b[7]]))
            append.AddInput(self.makeFace([b[0],b[3],b[7],b[4]]))
            append.AddInput(self.makeFace([b[1],b[2],b[6],b[5]]))
            d1,t1=self.makeDirection(b[0],b[1],"x1")
            append.AddInput(d1.GetOutput())
            self.ren.AddActor(t1)
            d2,t2=self.makeDirection(b[0],b[3],"x2")
            append.AddInput(d2.GetOutput())
            self.ren.AddActor(t2)
            d3,t3=self.makeDirection(b[0],b[4],"x3")
            append.AddInput(d3.GetOutput())
            self.ren.AddActor(t3)
            self.blockTextActor=(t1,t2,t3)
            self.blockAxisActor=(d1,d2,d3)
            mapper=vtk.vtkPolyDataMapper()
            mapper.SetInputConnection(append.GetOutputPort())
            self.blockActor = vtk.vtkActor()
            self.blockActor.SetMapper(mapper)
            self.blockActor.GetProperty().SetColor(0.,1.,0.)
            self.blockActor.GetProperty().SetOpacity(0.3)
            self.ren.AddActor(self.blockActor)

        self.oldBlock=newBlock
        self.renWin.Render()

    def colorPatch(self,value):
        newPatch=int(value)
        if self.oldPatch>=0 and self.patchActor!=None:
            self.ren.RemoveActor(self.patchActor)
            self.patchActor=None
            self.patchTextActor.SetInput("Patch: <none>")
        if newPatch>=0:
            name=self.patches.keys()[newPatch]
            subs=self.patches[name]
            append=vtk.vtkAppendPolyData()
            for s in subs:
                append.AddInput(self.makeFace(s))
            mapper=vtk.vtkPolyDataMapper()
            mapper.SetInputConnection(append.GetOutputPort())
            self.patchActor = vtk.vtkActor()
            self.patchActor.SetMapper(mapper)
            self.patchActor.GetProperty().SetColor(0.,0.,1.)
            self.patchActor.GetProperty().SetOpacity(0.3)
            self.ren.AddActor(self.patchActor)
            self.patchTextActor.SetInput("Patch: "+name)

        self.oldPatch=newPatch
        self.renWin.Render()

    def closeEvent(self,event):
        print "Closing and saving settings to",QtCore.QSettings().fileName()
        QtCore.QSettings().setValue("geometry",QtCore.QVariant(self.saveGeometry()))
        QtCore.QSettings().setValue("state",QtCore.QVariant(self.saveState()))
        
class DisplayBlockMesh(PyFoamApplicationQt4):
    def __init__(self):
        description="""
Reads the contents of a blockMeshDict-file and displays the
vertices as spheres (with numbers). The blocks are sketched by
lines. One block can be seceted with a slider. It will be
displayed as a green cube with the local directions x1,x2 and
x3. Also a patch that is selected by a slider will be sketched
by blue squares

This is a new version with a QT-GUI
        """
        super(DisplayBlockMesh,self).__init__(description=description,
                                              usage="%prog [options] <blockMeshDict>",
                                              interspersed=True,
                                              nr=1)

    def setupGUI(self):
        bmFile=self.parser.getArgs()[0]
        if not path.exists(bmFile):
            self.error(bmFile,"not found")
        try:
            self.dialog=DisplayBlockMeshDialog(bmFile)
        except IOError:
            self.error("Problem with blockMesh file",bmFile)
        self.dialog.show()

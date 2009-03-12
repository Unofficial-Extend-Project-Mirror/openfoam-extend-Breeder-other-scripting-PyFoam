"""
Application-class that implements pyFoamAPoMaFoX.py (A Poor Man's FoamX)
"""
from optparse import OptionGroup
from os import path
import os
import shutil

from PyFoamApplication import PyFoamApplication
from CaseBuilderBackend import CaseBuilderFile,CaseBuilderDescriptionList
from CommonCaseBuilder import CommonCaseBuilder
from PyFoam import configuration as config

from PyFoam.Error import error

try:
    import urwid
except ImportError:
    error("This application needs an installed urwid-library")
    
try:
    import urwid.curses_display
except ImportError:
    error("This application needs an installed curses-library")
    
class APoMaFoX(PyFoamApplication,
               CommonCaseBuilder):
    def __init__(self,args=None):
        description="""
APoMaFoX is "A Poor Mans FoamX".

A small text interface to the CaseBuilder-Functionality
"""
        PyFoamApplication.__init__(self,
                                   args=args,
                                   description=description,
                                   usage="%prog <caseBuilderFile>",
                                   interspersed=True,
                                   nr=0,
                                   exactNr=False)

    def addOptions(self):
        CommonCaseBuilder.addOptions(self)
            
    def run(self):
        if self.pathInfo():
            return

        if len(self.parser.getArgs())==0:
            CaseBuilderBrowser()
        elif len(self.parser.getArgs())==1:
            fName=self.searchDescriptionFile(self.parser.getArgs()[0])

            if not path.exists(fName):
                error("The description file",fName,"does not exist")

            dialog=CaseBuilderDialog(fName)
            dialog.run()
        else:
            error("Too many arguments")

class CaseBuilderTUI(object):
    """Common stuff between the TUIs"""
    
    def __init__(self):
        self.ui = urwid.curses_display.Screen()    
            
        self.ui.register_palette( [
            ('alert', 'light gray', 'dark red', 'standout'),
            ('header', 'black', 'dark cyan', 'standout'),
            ('banner', 'black', 'dark green', ('standout', 'underline')),
            ('group',  'dark red', 'dark green', ('standout', 'underline')),
            ('button', 'black', 'dark red', 'standout'),
            ('bgbutton', 'black', 'dark blue', 'standout'),
            ('editbox', 'dark gray','light gray'),
            ('bg', 'dark green', 'black'),
            ('bgl', 'dark green', 'light gray'),
            ] )
        
class CaseBuilderBrowser(CaseBuilderTUI):
    """A browser of all the available descriptions"""
    def __init__(self):
        CaseBuilderTUI.__init__(self)

        self.descriptions=CaseBuilderDescriptionList()
        if len(self.descriptions)==0:
            error("No description-files (.pfcb) found in path",config().get("CaseBuilder","descriptionpath"))
            
        self.items=[]

        mxlen=apply(max,map(lambda x:len(x[2]),self.descriptions)+[0])
        
        for i,d in enumerate(self.descriptions):
            txt=urwid.Text([('button',d[2]+" "*(mxlen-len(d[2]))),"  ",d[1],"\n",d[3]])
            if i%2==0:
                attr='bgl'
            else:
                attr='bg'
            self.items.append(urwid.AttrWrap(txt,attr,'bgbutton'))

        self.walk=urwid.SimpleListWalker(self.items)
        self.listbox = urwid.ListBox(self.walk)

        self.statusText=urwid.Text(" Press <ESC> to exit  <ENTER> to select description")

        footer = urwid.AttrWrap( self.statusText, 'header' )

        top = urwid.Frame(self.listbox, footer=footer)
        if len(self.descriptions)%2==0:
            self.top=urwid.AttrWrap(top,'bgl')
        else:
            self.top=urwid.AttrWrap(top,'bg')
            
        self.ui.run_wrapper(self.runTUI)
        
    def runTUI(self):
	size = self.ui.get_cols_rows()

	txt = urwid.Text(('banner', " Hello World "), align="center")
	wrap1 = urwid.AttrWrap( txt, 'streak' )
	fill = urwid.Filler( wrap1 )
	wrap2 = urwid.AttrWrap( fill, 'bg' )

        self.goOn=True
        
	while self.goOn:
            self.draw_screen(size)
            keys = self.ui.get_input()
            if "esc" in keys:
                break
            elif "enter" in keys:
                w,i=self.walk.get_focus()
                cb=CaseBuilderDialog(self.descriptions[i][1])
                if cb.run():
                    break
                else:
                    continue
            for k in keys:
                if k=="window resize":
                    size = self.ui.get_cols_rows()
                    continue
                elif k=="down":
                    w,p=self.walk.get_focus()
                    self.walk.set_focus(p+1)
                    continue
                elif k=="up":
                    w,p=self.walk.get_focus()
                    if p>0:
                        self.walk.set_focus(p-1)
                    continue
                self.top.keypress( size, k )

    def draw_screen(self,size):
        canvas = self.top.render( size, focus=True )
        self.ui.draw_screen( size, canvas )

class CaseBuilderDialog(CaseBuilderTUI):
    """A dialog for a CaswBuilder-dialog"""
    def __init__(self,fName):
        CaseBuilderTUI.__init__(self)
        
        self.desc=CaseBuilderFile(fName)

#        print "Read case description",self.desc.name()

        items=[]

        items.append(
            urwid.AttrWrap(
            urwid.Text("Builder Template: "
                       + self.desc.name()+"\n"+self.desc.description()
                       ),'banner'))
        items.append(
            urwid.AttrWrap(
            urwid.Divider("-"),'banner'))
        items.append(
            urwid.AttrWrap(
            urwid.Text("Data Template: "
                       + self.desc.templatePath()
                       ),'banner'))
        items.append(
            urwid.AttrWrap(
            urwid.Divider("="),'banner'))

        self.caseField=urwid.Edit(('banner',"Name of the generated case "))
        items.append(urwid.AttrWrap(self.caseField,'editbox'))
        
        items.append(
            urwid.AttrWrap(
            urwid.Divider("="),'banner'))

        args=self.desc.arguments()
        mLen=apply(max,map(len,args))
        aDesc=self.desc.argumentDescriptions()
        aDef=self.desc.argumentDefaults()
        self.argfields=[]

        groups=[None]+self.desc.argumentGroups()
        gDesc=self.desc.argumentGroupDescription()
        
        for g in groups:
            if g!=None:
                items.append(urwid.AttrWrap(urwid.Text("\n"+g+" - "+gDesc[g]),"group"))
            for a in self.desc.groupArguments(g):
                items.append(urwid.Text(aDesc[a]))
                fld=urwid.Edit(('banner',a+" "*(mLen+1-len(a))),edit_text=aDef[a])
                self.argfields.append(fld)
                items.append(urwid.AttrWrap(fld,'editbox'))

        items.append(
            urwid.AttrWrap(
            urwid.Divider("="),'banner'))

        self.forceCheck=urwid.CheckBox("ForceOverwrite")
        items.append(
            urwid.Columns(
            [ urwid.AttrWrap(self.forceCheck,'bgbutton') ]
            ))
        
        items.append(
            urwid.Padding(
            urwid.AttrWrap(urwid.Button("Generate Case",self.doGenerate),'bgbutton','button'),
            align='center',width=20))
        
        self.items = urwid.SimpleListWalker(items)
        self.listbox = urwid.ListBox(self.items)
        self.statusText = urwid.Text("Dummy")
        footer = urwid.AttrWrap( self.statusText, 'header' )

        self.setStatus("")
        
        top = urwid.Frame(self.listbox, footer=footer)
        self.top=urwid.AttrWrap(top,'bg')
        self.done=False
        
    def run(self):
        self.ui.run_wrapper(self.runTUI)
        return self.done
    
    def setStatus(self,text):
        self.statusText.set_text([('alert',text)," Press ESC to exit"])
        
    def doGenerate(self,button):
        self.goOn=False
        self.ui.stop()
        caseName=self.caseField.get_edit_text()
        if len(caseName)==0:
            self.setStatus("Casename empty")
            self.goOn=True
            return
        
        if path.exists(caseName):
            if not self.forceCheck.get_state():
                self.setStatus("Directory "+caseName+" already existing")
                self.goOn=True
                return
            else:
                self.setStatus("Overwriting directory "+caseName)
                shutil.rmtree(caseName)
        
        self.setStatus("Generating the case "+caseName)
        args={}
        for i,a in enumerate(self.desc.arguments()):
            args[a]=self.argfields[i].get_edit_text()
            if len(args[a])==0:
                self.setStatus("No argument "+a+" was given")
                self.goOn=True
                return

        msg=self.desc.verifyArguments(args)
        if msg:
            self.setStatus(msg)
            self.goOn=True
            return
        
        self.setStatus("With the arguments "+str(args))

        self.desc.buildCase(caseName,args)

        self.done=True
        
    def runTUI(self):
	size = self.ui.get_cols_rows()

	txt = urwid.Text(('banner', " Hello World "), align="center")
	wrap1 = urwid.AttrWrap( txt, 'streak' )
	fill = urwid.Filler( wrap1 )
	wrap2 = urwid.AttrWrap( fill, 'bg' )

        self.goOn=True
        
	while self.goOn:
            self.draw_screen(size)
            keys = self.ui.get_input()
            if "esc" in keys:
                break
            for k in keys:
                if k=="window resize":
                    size = self.ui.get_cols_rows()
                    continue
                self.top.keypress( size, k )
                                                
    def draw_screen(self,size):
        canvas = self.top.render( size, focus=True )
        self.ui.draw_screen( size, canvas )


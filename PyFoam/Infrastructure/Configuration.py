#  ICE Revision: $Id: Configuration.py 11520 2010-04-22 15:35:51Z bgschaid $ 
"""Reads configuration-files that define defaults for various PyFoam-Settings

Also hardcodes defaults for the settings"""

from ConfigParser import ConfigParser,NoOptionError

from Hardcoded import globalConfigFile,userConfigFile,globalDirectory,userDirectory,globalConfigDir,userConfigDir

from os import path
import glob

_defaults={
    "Network": {
    "startServerPort"  : "18000",
    "nrServerPorts"    : "100",
    "portWait"         : "1.",
    "socketTimeout"    : "1.",
    "socketRetries"    : "10",
    },
    "Metaserver": {
    "port"             : "17999",
    "ip"               : "192.168.1.11",
    "checkerSleeping"  : "30.",
    "searchServers"    : "192.168.1.0/24,192.168.0.0/24",
    "webhost"          : "127.0.0.1:9000",
    "doWebsync"        : "True",
    "websyncInterval"  : "300.",
    },
    "IsAlive": {
    "maxTimeStart"     : "30.",
    "isLivingMargin"   : "1.1"
    },
    "Logging": {
    "default" : "INFO",
    "server" : "INFO",
    },
    "OpenFOAM": {
    "Installation" : "~/OpenFOAM",
    "Version" : "1.5",
    },
    "MPI": {
#    "run_OPENMPI":"mpirun",
#    "run_LAM":"mpirun",
    "options_OPENMPI_pre": '["--mca","pls","rsh","--mca","pls_rsh_agent","rsh"]',
    "options_OPENMPI_post":'["-x","PATH","-x","LD_LIBRARY_PATH","-x","WM_PROJECT_DIR","-x","PYTHONPATH","-x","FOAM_MPI_LIBBIN","-x","MPI_BUFFER_SIZE","-x","MPI_ARCH_PATH"]'
    },
    "Paths": {
    "python" : "/usr/bin/python",
    "bash" : "/bin/bash",
    },
    "ClusterJob": {
    "useFoamMPI":'["1.5"]',
    "path":"/opt/openmpi/bin",
    "ldpath":"/opt/openmpi/lib",
    },
    "Debug": {
#    "ParallelExecution":"True",
    },
    "Execution":{
    "controlDictRestoreWait":"60.",
    },
    "CaseBuilder":{
    "descriptionPath": eval('["'+path.curdir+'","'+path.join(userDirectory(),"caseBuilderDescriptions")+'","'+path.join(globalDirectory(),"caseBuilderDescriptions")+'"]'),
    },
    "Formats":{
    "error"       : "bold,red,standout",
    "warning"     : "under",
    "source"      : "red,bold",
    "destination" : "blue,bold",
    "difference"  : "green,back_black,bold",
    "question"    : "green,standout",
    "input"       : "cyan,under",
    },
    "CommandOptionDefaults":{
    "sortListCases":"mtime",
    },
    "Plotting":{
    "preferredImplementation":"gnuplot",
    },
    "OutfileCollection": {
    "maximumOpenFiles":"100",
    },
    "SolverOutput": {
    "timeRegExp": "^(Time =|Iteration:) (.+)$",
    },
    }

class Configuration(ConfigParser):
    """Reads the settings from files (if existing). Otherwise uses hardcoded
    defaults"""
    
    def __init__(self):
        """Constructs the ConfigParser and fills it with the hardcoded defaults"""
        ConfigParser.__init__(self)

        for section,content in _defaults.iteritems():
            self.add_section(section)
            for key,value in content.iteritems():
                self.set(section,key,value)
                
        self.read(self.configFiles())

        self.validSections={}
        for s in self.sections():
            minusPos=s.find('-')
            if minusPos<0:
                name=s
            else:
                name=s[:minusPos]
            try:
                self.validSections[name].append(s)
            except KeyError:
                self.validSections[name]=[s]

        for name,sections in self.validSections.iteritems():
            if not name in sections:
                print "Invalid configuration for",name,"there is no default section for it in",sections

    def bestSection(self,section,option):
        """Get the best-fitting section that has that option"""

        from PyFoam import foamVersionString

        try:
            if len(self.validSections[section])==1 or foamVersionString()=="":
                return section
        except KeyError:
            return section
        
        result=section
        fullName=section+"-"+foamVersionString()

        for s in self.validSections[section]:
            if fullName.find(s)==0 and len(s)>len(result):
                if self.has_option(s,option):
                    result=s
            
        return result
    
    def configSearchPath(self):
        """Defines a search path for the configuration files as a pare of type/name
        pairs"""
        files=[("file",globalConfigFile()),
               ("directory",globalConfigDir()),
               ("file",userConfigFile()),
               ("directory",userConfigDir())]
        return files
        
    def configFiles(self):
        """Return a list with the configurationfiles that are going to be used"""
        files=[]

        for t,f in self.configSearchPath():
            if path.exists(f):
                if t=="file":
                    files.append(f)
                elif t=="directory":
                    for ff in glob.glob(path.join(f,"*.cfg")):
                        files.append(ff)
                else:
                    error("Unknown type",t,"for the search entry",f)
                
        return files
    
    def addFile(self,filename,silent=False):
        """Add another file to the configuration (if it exists)"""
        if not path.exists(filename):
            if not silent:
                print "The configuration file",filename,"is not there"
        else:
            self.read([filename])
            
    def dump(self):
        """Dumps the contents in INI-Form
        @return: a string with the contents"""
        result=""
        for section in self.sections():
            result+="[%s]\n" % (section)
            for key,value in self.items(section):
                result+="%s: %s\n" % (key,value)
            result+="\n"

        return result

    def getboolean(self,section,option,default=None):
        """Overrides the original implementation from ConfigParser
        @param section: the section
        @param option: the option
        @param default: if set and the option is not found, then this value is used"""

        try:
            return ConfigParser.getboolean(self,
                                           self.bestSection(section,option),
                                           option)
        except NoOptionError:
            if default!=None:
                return default
            else:
                raise

    def getfloat(self,section,option,default=None):
        """Overrides the original implementation from ConfigParser
        @param section: the section
        @param option: the option
        @param default: if set and the option is not found, then this value is used"""

        try:
            return ConfigParser.getfloat(self,
                                         self.bestSection(section,option),
                                         option)
        except (NoOptionError,ValueError):
            if default!=None:
                return default
            else:
                raise

    def get(self,section,option,default=None):
        """Overrides the original implementation from ConfigParser
        @param section: the section
        @param option: the option
        @param default: if set and the option is not found, then this value is used"""

        try:
            return ConfigParser.get(self,
                                    self.bestSection(section,option),
                                    option)
        except NoOptionError:
            if default!=None:
                return default
            else:
                raise

    def getdebug(self,name):
        """Gets a debug switch"""

        return self.getboolean("Debug",name,default=False)
    

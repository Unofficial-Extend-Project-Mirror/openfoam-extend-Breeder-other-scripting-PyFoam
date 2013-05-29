#  ICE Revision: $Id: Configuration.py 12798 2013-03-04 10:41:53Z bgschaid $
"""Reads configuration-files that define defaults for various PyFoam-Settings

Also hardcodes defaults for the settings"""

from PyFoam.ThirdParty.six.moves import configparser
from PyFoam.ThirdParty.six import iteritems,PY3

from PyFoam.Infrastructure.Hardcoded import globalConfigFile,userConfigFile,globalDirectory,userDirectory,globalConfigDir,userConfigDir

from os import path
import glob,re

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
    "AdditionalInstallation" : "~/OpenFOAM",
    "Version" : "1.5",
    },
    "MPI": {
#    "run_OPENMPI":"mpirun",
#    "run_LAM":"mpirun",
    "OpenMPI_add_prefix":"False",
    "options_OPENMPI_pre": '["--mca","pls","rsh","--mca","pls_rsh_agent","rsh"]',
    "options_OPENMPI_post":'["-x","PATH","-x","LD_LIBRARY_PATH","-x","WM_PROJECT_DIR","-x","PYTHONPATH","-x","FOAM_MPI_LIBBIN","-x","MPI_BUFFER_SIZE","-x","MPI_ARCH_PATH"]'
    },
    "Paths": {
    "python" : "/usr/bin/python",
    "bash" : "/bin/bash",
    "paraview" : "paraview",
    },
    "ClusterJob": {
    "useFoamMPI":'["1.5"]',
    "path":"/opt/openmpi/bin",
    "ldpath":"/opt/openmpi/lib",
    "doAutoReconstruct":"True",
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
    "Clearing": {
    "additionalPatterns":"[]",
    },
    "postRunHook_WriteMySqlite" : {
        "enabled":False,
        "module":"WriteToSqliteDatabase",
        "createDatabase":False,
        "database":"~/databaseOfAllMyRuns.db",
    },
    "postRunHook_SendToPushover" : {
        "enabled":False,
        "minRunTime":600,
        "useSSL":True,
        "module":"SendToWebservice",
        "host":"api.pushover.net:443",
        "method":"POST",
        "url":"/1/messages",
        "param_token":"invalid_get_yourself_one_at_pushover.net",
        "param_user":"invalid_get_yourself_an_account_at_pushover.net",
        "param_title":"<!--(if OK)-->Finished<!--(else)-->Failed<!--(end)-->: |-casename-| (|-solver-|)",
        "param_message":"""Case |-casefullname-| ended after |-wallTime-|s
Last timestep: t=|-time-|
Machine: |-hostname-|
Full command: |-commandLine-|""",
        "header_Content-type": "application/x-www-form-urlencoded",
        "templates":"title message"
    },
    "Cloning" : {
        "addItem":"[]",
    },
    }

class ConfigurationSectionProxy(object):
    """Wraps a Confguration so that the section automatically becomes the
    first argument"""

    def __init__(self,conf,section):
        self.conf=conf
        self.section=section

    def __getattr__(self,name):
        f=getattr(self.conf,name)
        def curried(*args,**kwargs):
            return f(*((self.section,)+args),**kwargs)
        return curried

class Configuration(configparser.ConfigParser):
    """Reads the settings from files (if existing). Otherwise uses hardcoded
    defaults"""

    def __init__(self):
        """Constructs the ConfigParser and fills it with the hardcoded defaults"""
        configparser.ConfigParser.__init__(self)

        for section,content in iteritems(_defaults):
            self.add_section(section)
            for key,value in iteritems(content):
                self.set(section,key,str(value))

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

        for name,sections in iteritems(self.validSections):
            if not name in sections:
                print("Invalid configuration for",name,"there is no default section for it in",sections)

    def sectionProxy(self,section):
        """Return a proxy object that makes it possible to avoid the section
        specification"""
        return ConfigurationSectionProxy(self,section)

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
                print("The configuration file",filename,"is not there")
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

    def getList(self,section,option,default="",splitchar=","):
        """Get a list of strings (in the original they are separated by commas)
        @param section: the section
        @param option: the option
        @param default: if set and the option is not found, then this value is used
        @param splitchar: the character by which the values are separated"""

        val=self.get(section,option,default=default)
        if val=="":
            return []
        else:
            return val.split(splitchar)

    def getboolean(self,section,option,default=None):
        """Overrides the original implementation from ConfigParser
        @param section: the section
        @param option: the option
        @param default: if set and the option is not found, then this value is used"""

        try:
            return configparser.ConfigParser.getboolean(self,
                                           self.bestSection(section,option),
                                           option)
        except configparser.NoOptionError:
            if default!=None:
                return default
            else:
                raise

    def getint(self,section,option,default=None):
        """Overrides the original implementation from ConfigParser
        @param section: the section
        @param option: the option
        @param default: if set and the option is not found, then this value is used"""

        try:
            return int(configparser.ConfigParser.get(self,
                                                     self.bestSection(section,option),
                                                     option))
        except configparser.NoOptionError:
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
            return float(configparser.ConfigParser.get(self,
                                                       self.bestSection(section,option),
                                                       option))
        except (configparser.NoOptionError,ValueError):
            if default!=None:
                return default
            else:
                raise

    def getRegexp(self,section,option):
        """Get an entry and interpret it as a regular expression. Subsitute
        the usual regular expression value for floating point numbers
        @param section: the section
        @param option: the option
        @param default: if set and the option is not found, then this value is used"""
        floatRegExp="[-+]?[0-9]*\.?[0-9]+(?:[eE][-+]?[0-9]+)?"

        return re.compile(self.get(section,option).replace("%f%",floatRegExp))

    def get(self,section,option,default=None):
        """Overrides the original implementation from ConfigParser
        @param section: the section
        @param option: the option
        @param default: if set and the option is not found, then this value is used"""

        try:
            return configparser.ConfigParser.get(self,
                                    self.bestSection(section,option),
                                    option)
        except configparser.NoOptionError:
            if default!=None:
                return default
            else:
                raise

    def getdebug(self,name):
        """Gets a debug switch"""

        return self.getboolean("Debug",name,default=False)

# Should work with Python3 and Python2

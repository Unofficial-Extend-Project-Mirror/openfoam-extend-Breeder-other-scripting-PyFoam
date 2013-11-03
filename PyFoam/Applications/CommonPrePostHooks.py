"""
Class that implements the common functionality for executing hooks before and
after the running of the solver
"""
from optparse import OptionGroup
from PyFoam.ThirdParty.six.moves import configparser

from PyFoam import configuration
from PyFoam.Error import FatalErrorPyFoamException

from PyFoam.ThirdParty.six import print_,iteritems

import traceback

import sys

class CommonPrePostHooks(object):
    """ The class that runs the hooks
    """

    def addOptions(self):
        grp=OptionGroup(self.parser,
                        "Pre- and Postrun hooks",
                        "These options control the hooks that are either specified in the 'LocalConfigPyFoam' of the case or other config files (for a system-wide configuration)")
        self.parser.add_option_group(grp)

        grp.add_option("--disable-pre-hooks",
                       action="store_false",
                       dest="runPreHook",
                       default=True,
                       help="Disable running of hooks before the solver")
        grp.add_option("--disable-post-hooks",
                       action="store_false",
                       dest="runPostHook",
                       default=True,
                       help="Disable running of hooks after the solver")
        grp.add_option("--disable-all-hooks",
                       action="store_true",
                       dest="disableAllHooks",
                       default=False,
                       help="Disable running of hooks before and after the solver")
        grp.add_option("--verbose-hooks",
                       action="store_true",
                       dest="verboseHooks",
                       default=False,
                       help="Be more informative about what is going on")
        grp.add_option("--list-hooks",
                       action="store_true",
                       dest="listHooks",
                       default=False,
                       help="List the installed hooks")
        grp.add_option("--hook-errors-are-fatal",
                       action="store_true",
                       dest="hookErrorsFatal",
                       default=False,
                       help="If there are problems with the hooks then execution of the runner stops")

    def hookmessage(self,*args):
        if self.opts.verboseHooks:
            for a in args:
                print_(a,end="")
            print_()

    def stopExecutionOnHookError(self,spec=False):
         if spec or self.opts.hookErrorsFatal:
              self.error("Stopping because of error in hook")

    def runPreHooks(self):
        """Run the hooks before the execution of the solver"""
        if self.opts.runPreHook:
            self.hookmessage("Running pre-hooks")
            for h,spec in iteritems(self.preHookInstances):
                self.executeHook(h,spec)
        else:
            self.hookmessage("Pre-hooks disabled")

    def runPostHooks(self):
        """Run the hooks after the execution of the solver"""
        if self.opts.runPostHook:
            self.hookmessage("Running post-hooks")
            for h,spec in iteritems(self.postHookInstances):
                self.executeHook(h,spec)
        else:
            self.hookmessage("Post-hooks disabled")
        pass

    def executeHook(self,name,hDict):
        try:
            passed=self.getData()["wallTime"]
        except KeyError:
            passed=0
        if passed<hDict["minRunTime"]:
            self.hookmessage("Skipping",name,"because passed time",
                             passed,"smaller than",hDict["minRunTime"])
            return
        self.hookmessage("Executing hook",name)
        try:
             hDict["instance"]()
        except FatalErrorPyFoamException:
            e = sys.exc_info()[1] # Needed because python 2.5 does not support 'as e'

            self.warning("Problem executing",name,":",e)
        except Exception:
             self.warning("Problem while executing",
                          name,":",traceback.format_exc())
             self.stopExecutionOnHookError(hDict["stopOnError"])

    def prepareHooks(self):
        """Prepare the hooks and output additional info if wanted"""
        self.hookmessage("Preparing hooks")
        if self.opts.disableAllHooks:
            self.hookmessage("Disabling all hooks")
            self.opts.runPreHook=False
            self.opts.runPostHook=False

        if self.opts.listHooks:
            print_("Hooks to execute before run")
            print_("---------------------------")
            self.dumpHooks(self.getHooksWithPrefix("preRunHook"))
            print_()
            print_("Hooks to execute after run")
            print_("--------------------------")
            self.dumpHooks(self.getHooksWithPrefix("postRunHook"))

        self.preHookInstances={}
        self.postHookInstances={}

        self.hookmessage("Creating pre-hooks")
        if self.opts.runPreHook:
            self.checkAndCreateHookInstances(
                self.preHookInstances,
                "preRunHook"
            )
        self.hookmessage("Creating post-hooks")
        if self.opts.runPostHook:
            self.checkAndCreateHookInstances(
                self.postHookInstances,
                "postRunHook"
            )

    def checkAndCreateHookInstances(self,toDict,prefix):
        for h in self.getHooksWithPrefix(prefix):
            self.hookmessage("Checking",h)
            if configuration().getboolean(h,"enabled",default=True):
                subdict={}
                mod=configuration().get(h,"module",default="")
                if mod=="":
                    self.warning("No module specified for",h)
                    continue
                subdict["minRunTime"]=configuration().getfloat(h,
                                                               "minRunTime",
                                                               default=-1)
                subdict["stopOnError"]=configuration().getboolean(h,
                                                                  "stopOnError",
                                                                  default=False)
                self.hookmessage("Trying to import",mod)
                try:
                    try:
                        module=__import__(mod,globals(),locals(),["dummy"])
                    except ImportError:
                        e = sys.exc_info()[1] # Needed because python 2.5 does not support 'as e'
                        self.hookmessage("ImportError:",e)
                        mod="PyFoam.Infrastructure.RunHooks."+mod
                        self.hookmessage("Trying to import",mod)
                        try:
                            module=__import__(mod,globals(),locals(),["dummy"])
                        except ImportError:
                            self.hookmessage("ImportError:",e)
                            self.warning("Could not import module",
                                         mod.split(".")[-1],"for",h,
                                         "(Tried",mod,"too)")
                            continue
                except SyntaxError:
                    e = sys.exc_info()[1] # Needed because python 2.5 does not support 'as e'
                    self.hookmessage("SyntaxError:",e)
                    self.warning("Syntax error when trying to import",mod)
                    continue
                try:
                    theClass=getattr(module,mod.split(".")[-1])
                except AttributeError:
                    e = sys.exc_info()[1] # Needed because python 2.5 does not support 'as e'
                    self.hookmessage("AttributeError:",e)
                    self.hookmessage("Attributes:",dir(module))
                    self.warning("Class",mod.split(".")[-1],"missing form",
                                 mod)
                    continue
                try:
                    subdict["instance"]=theClass(self,h)
                except Exception:
                    self.warning("Problem while creating instance of",
                                 theClass,":",traceback.format_exc())
                    self.stopExecutionOnHookError(subdict["stopOnError"])
                    continue
                toDict[h]=subdict
            else:
                self.hookmessage(h,"is disabled")

    def dumpHooks(self,lst):
        for h in lst:
            print_(h)
            try:
                print_("  enabled:",configuration().getboolean(h,
                                                               "enabled",
                                                               default=True))
                print_("  module:",configuration().get(h,
                                                       "module"))
                print_("  minRunTime:",configuration().getfloat(h,
                                                                "minRunTime",
                                                                default=0))
                print_("  description:",configuration().get(h,
                                                            "description",
                                                            default="None"))
            except configparser.NoOptionError:
                e = sys.exc_info()[1] # Needed because python 2.5 does not support 'as e'
                self.error("Hook",h,"incompletely defined (",e,")")

    def getHooksWithPrefix(self,prefix):
        lst=[]
        for h in configuration().sections():
            if h.find(prefix+"_")==0:
                lst.append(h)
        return lst

# Should work with Python3 and Python2

# Just Print something

from __future__ import print_function

from pprint import pformat

from PyFoam.Infrastructure.RunHook import RunHook
from PyFoam.Basics.TemplateFile import TemplateFile
from PyFoam.ThirdParty.pyratemp import TemplateRenderError

class EchoHook(RunHook):
    def __init__(self,runner,name):
        RunHook.__init__(self,runner,name)
        print("Created",runner,name)
        self.message=self.conf().get("message")
    def __call__(self):
        print("Data:",pformat(self.runner.getData()))
        template=TemplateFile(content=self.message,
                              expressionDelimiter="|-",
                              encoding="ascii")
        print(template.getString(self.runner.getData()))

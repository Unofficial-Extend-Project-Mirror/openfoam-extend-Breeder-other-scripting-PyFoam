#! /usr/bin/env python
"""An interactive Shell that queries a pyFoamServer"""

from PyFoam.Applications.PyFoamApplication import PyFoamApplication

import readline,sys

import xmlrpclib,socket

class NetShell(PyFoamApplication):
    prompt="PFNET> "

    def __init__(self):
        description="""\
Connects to a running pyFoam-Server and executes commands via remote
procedure calls
        """
        PyFoamApplication.__init__(self,description=description,usage="%prog <host> <port>",interspersed=True,nr=2)
    def addOptions(self):
        self.parser.add_option("--command",type="string",dest="command",default=None,help="Executes this command and finishes")

    def run(self):
        host=self.parser.getArgs()[0]
        port=int(self.parser.getArgs()[1])

        cmd=self.parser.options.command

        try:
            self.server=xmlrpclib.ServerProxy("http://%s:%d" % (host,port))
            methods=self.server.system.listMethods()
            if not cmd:
                print "Connected to server",host,"on port",port
                print len(methods),"available methods found"
        except socket.error,reason:
            print "Socket error while connecting:",reason
            sys.exit(1)
        except xmlrpclib.ProtocolError,reason:
            print "XMLRPC-problem",reason
            sys.exit(1)

        if cmd:
            result=self.executeCommand(cmd)
            if result!=None:
                print result
            sys.exit(0)

        while 1:
            try: line = raw_input(self.prompt)
            except (KeyboardInterrupt,EOFError):    # Catch a ctrl-D
                print
                print "Goodbye"
                sys.exit()
            line.strip()
            parts=line.split()

            if len(parts)==0:
                print "For help type 'help'"
                continue

            if parts[0]=="help":
                if len(parts)==1:
                    print "For help on a method type 'help <method>'"
                    print "Available methods are:"
                    for m in methods:
                        print "\t",m
                elif len(parts)==2:
                    name=parts[1]
                    if name in methods:
                        signature=self.executeCommand("system.methodSignature(\""+name+"\")")
                        help=self.executeCommand("system.methodHelp(\""+name+"\")")
                        print "Method    : ",name
                        print "Signature : ",signature
                        print help
                    else:
                        print "Method",name,"does not exist"
                else:
                    print "Too many arguments"
            else:
                result=self.executeCommand(line)
                if result!=None:
                    print result

    def executeCommand(self,cmd):
        result=None
        try:
            result=eval("self.server."+cmd)
            if result==None: # this needed to catch the unmarschalled-None-exception
                return None
        except xmlrpclib.Fault,reason:
            print "XMLRPC-problem:",reason.faultString
        except socket.error,reason:
            print "Problem with socket (server propably dead):",reason
        except TypeError,reason:
            print "Type error: ",reason
            result=None
        except SyntaxError,reason:
            print "Syntax Error in:",cmd
            
        return result

NetShell()

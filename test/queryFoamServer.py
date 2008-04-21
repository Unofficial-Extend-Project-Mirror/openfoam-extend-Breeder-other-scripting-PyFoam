"""Test all the known methods of a pyFoam-XMLRPC-Server"""

from xmlrpclib import ServerProxy
import sys

name=sys.argv[1]
port=int(sys.argv[2])

server=ServerProxy("http://%s:%d" % (name,port))
print "Tail:",server.tail()
print "Lastline:",server.lastLine()
print "Elapsed:",server.elapsedTime()
print server.system.listMethods()
print "CPU:",server.cpuTime(),"User:",server.cpuUserTime(),"System:",server.cpuSystemTime()
print "Wall:",server.wallTime(),"Memory:",server.usedMemory()
print "Argv:",server.argv(),server.commandLine(),server.scriptName()
print "Parallel:",server.isParallel()
print "Warnings:",server.nrWarnings()
print "MPI: ",server.mpi()
print "Versions. Foam:",server.foamVersion(),"PyFoam:",server.pyFoamVersion()
print "PATH-variable:",server.getEnviron("PATH")
print "UName:",server.uname()
print "Host:",server.hostname()
print "Config:",server.configuration()
print "IsServer:",server.isFoamServer(),"IsLiving:",server.isLiving()

# for m in server.system.listMethods():
#    print m,":",server.system.methodSignature(m),server.system.methodHelp(m)
    
# server.kill()

# while True:
#    print "Lastline:",server.lastLine()
    

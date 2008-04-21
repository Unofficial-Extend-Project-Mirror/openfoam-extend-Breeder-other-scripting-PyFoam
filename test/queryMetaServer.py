"""Checks the functionality of the meta-Server"""

from xmlrpclib import ServerProxy
from PyFoam import configuration as config

host=config().get("Metaserver","ip")
port=config().getint("Metaserver","port")

server=ServerProxy("http://%s:%d" % (host,port))

print server.system.listMethods()
#for m in server.system.listMethods():
#    print m,":",server.system.methodSignature(m),server.system.methodHelp(m)

print server.list()
# server.collect()

server.kill()

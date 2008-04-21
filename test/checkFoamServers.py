"""Find the Foam-Servers in the network"""

from PyFoam.Infrastructure.NetworkHelpers import checkFoamServers
from PyFoam import configuration as config
from PyFoam.ThirdParty.IPy import IP

import socket
import sys

if len(sys.argv)>1:
    machines=sys.argv[1]
else:
    machines=config().get("Network","searchservers")
    
if len(sys.argv)>2:
    port=int(sys.argv[2])
else:
    port=config().getint("Network","startServerPort")

if len(sys.argv)>3:
    length=int(sys.argv[3])
else:
    length=config().getint("Network","nrServerPorts")


addreses=machines.split(',')

for a in addreses:
    for host in IP(a):
        try:
            name,alias,rest =socket.gethostbyaddr(str(host))
        except socket.herror,reason:
            # no name for the host
            name="unknown" 
             

        print str(host),name,
        
        result=checkFoamServers(str(host),port,length)
        if result!=None:
            print result
        else:
            print

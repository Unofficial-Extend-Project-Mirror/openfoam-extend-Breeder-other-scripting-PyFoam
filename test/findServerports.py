
from PyFoam.Infrastructure.NetworkHelpers import freeServerPort
import socket

firstport=1080

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
sock.bind(('',firstport))

print "First Port between 1080 and 1180:",freeServerPort(firstport,length=100)

sock.close()

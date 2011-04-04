#  ICE Revision: $Id: /local/openfoam/Python/PyFoam/PyFoam/Infrastructure/ServerBase.py 1532 2007-06-29T11:15:55.577361Z bgschaid  $ 
"""Basis for the XMLRPC-Servers in PyFoam

Based on 15.5 in "Python Cookbook" for faster restarting"""

from SimpleXMLRPCServer import SimpleXMLRPCServer
import socket

class ServerBase(SimpleXMLRPCServer):
    """The Base class for the servers"""
    def __init__(self,addr,logRequests=False):
        """@param addr: the (server address,port)-tuple)
        @param logRequests: patched thru to the base class"""
        SimpleXMLRPCServer.__init__(self,addr,logRequests=logRequests)

    def server_bind(self):
        """Should allow a fast restart after the server was killed"""
        self.socket.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
        SimpleXMLRPCServer.server_bind(self)

    def verify_request(self,request,client_addr):
        """To be overriden later"""
        return True

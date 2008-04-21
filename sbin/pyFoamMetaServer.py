#! /usr/bin/env python

import os,sys,time

from PyFoam.Infrastructure.FoamMetaServer import FoamMetaServer
from PyFoam.Applications.PyFoamApplication import PyFoamApplication

class MetaServer(PyFoamApplication):
    def __init__(self):
        description="""Starts the MetaServer"""
        PyFoamApplication.__init__(self,description=description,usage="%prog",interspersed=True,nr=0)
        
    def run(self):
        # Do the Unix double-fork magic; see Stevens's book "Advanced
        # Programming in the UNIX Environment" (Addison-Wesley) for details
        try:
            pid = os.fork( )
            if pid > 0:
                time.sleep(0.5)
                # Exit first parent
                sys.exit(0)
        except OSError, e:
            print >>sys.stderr, "fork #1 failed: %d (%s)" % (
                e.errno, e.strerror)
            sys.exit(1)
        # Decouple from parent environment
        os.chdir("/")
        os.setsid( )
        os.umask(0)
        # Do second fork
        try:
            pid = os.fork( )
            if pid > 0:
                # Exit from second parent; print eventual PID before exiting
                print "Daemon PID %d" % pid
                sys.exit(0)
        except OSError, e:
            print >>sys.stderr, "fork #2 failed: %d (%s)" % (
                e.errno, e.strerror)
            sys.exit(1)

        server=FoamMetaServer()

if __name__ == "__main__":
    MetaServer()

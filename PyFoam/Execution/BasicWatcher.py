#  ICE Revision: $Id$
"""Watches the output of Foam-run"""

from os import path
import stat
import os
import gzip
from time import sleep

from PyFoam.Basics.LineReader import LineReader
from PyFoam import configuration as config

from PyFoam.ThirdParty.six import print_

class BasicWatcher(object):
    """Base class for watching the output of commands

    Works like the UNIX-command 'tail -f <file>': the last lines of the file are output.
    If the file grows then these lines are output as they arrive"""

    def __init__(self,filename,
                 silent=False,
                 tailLength=1000,
                 sleep=0.1,
                 follow=True):
        """:param filename: name of the logfile to watch
        :param silent: if True no output is sent to stdout
        :param tailLength: number of bytes at the end of the fail that should be output.
        :param follow: if the end of the file is reached wait for further input
        Because data is output on a per-line-basis
        :param sleep: interval to sleep if no line is returned"""

        self.filename=filename
        self.silent=silent
        self.tail=tailLength
        self.sleep=sleep
        self.follow=follow
        self.isTailing=False

        if not path.exists(self.filename):
            print_("Error: Logfile ",self.filename,"does not exist")

        self.reader=LineReader(config().getboolean("SolverOutput","stripSpaces"))

    def getSize(self):
        """:return: the current size (in bytes) of the file"""
        return os.stat(self.filename)[stat.ST_SIZE]

    def start(self):
        """Reads the file and does the processing"""

        currSize=self.getSize()

        fn,ext=path.splitext(self.filename)
        if ext=='.gz':
            fh=gzip.open(self.filename)
        else:
            fh=open(self.filename)

        self.startHandle()

        while self.follow or currSize>self.reader.bytesRead():
            try:
                status=self.reader.read(fh)
                if status:
                    line=self.reader.line
                    if (currSize-self.reader.bytesRead())<=self.tail:
                        if not self.isTailing:
                            self.isTailing=True
                            self.timeHandle()
                            self.tailingHandle()

                        if not self.silent:
                            print_(line)

                    self.lineHandle(line)
                else:
                    if self.reader.userSaidStop():
                        break
                    sleep(self.sleep)
            except KeyboardInterrupt:
                print_("Watcher: Keyboard interrupt")
                break

        self.stopHandle()

        fh.close()

    def startHandle(self):
        """to be called before the program is started"""
        pass

    def stopHandle(self):
        """called after the program has stopped"""
        pass

    def tailingHandle(self):
        """called when the first line is output"""
        pass

    def lineHandle(self,line):
        """called every time a new line is read"""
        pass

# Should work with Python3 and Python2

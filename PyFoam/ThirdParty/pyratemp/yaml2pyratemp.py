#!/usr/bin/env python
# -*- coding: ascii -*-
"""
Fill out/render/syntax-check a pyratemp-temlate.

Read data from a JSON/YAML-file, fillout a pyratemp-template
and print the result in utf-8 to STDOUT.

HTML-escaping is used for "*.htm" and "*.html", LaTeX-escaping
will be used for "*.tex" in the future.

:Version:   2008-12-19
:Status:    beta

:Usage:
    see USAGE or "yaml2pyratemp.py --help"

:Note:
    additionally defines the variables: date, mtime_CCYYMMDD

:Uses:  pyratemp, yaml (optional), simplejson (optional)

:Author:    Roland Koebler (r.koebler@yahoo.de)
:Copyright: 2007-2008 by Roland Koebler (r.koebler@yahoo.de)
:License:   MIT/X11-like, see __license__

:TODO:
    - escaping
    - convert charset (xmlcharrefreplace, latex...)

:Changelog:
    - 2008-12-14: first release
    - 2008-12-19: in USAGE: "YAML/JSON" now in uppercase
"""

__version__ = "2008-12-19"
__author__   = "Roland Koebler <rk(at)simple-is-better(dot)org>"
__license__  = """Copyright (c) 2007-2008 by Roland Koebler

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
IN THE SOFTWARE."""

#=========================================
USAGE = """yaml2pyratemp.py [-s] <-d NAME=VALUE> <-f DATAFILE [-n NR_OF_ENTRY]> TEMPLATEFILES
    -s      syntax-check only (don't render the template)
    -d      define variables (these also override the values from files)
    -f      use variables from YAML/JSON file(s)
    -n      use nth entry of the YAML/JSON-file
            (YAML: n-th entry, JSON: n-th element of the root-array)
"""

#=========================================
try:
    import os, sys, getopt, time
    import pyratemp
except ImportError, (arg):
    sys.stderr.write("ERROR: some python-modules are missing (%s)\n" % (arg))
    sys.exit(1)

#----------------------
def parse(template_name):
    """Parse template + set encoding according to filename-extension.
    
    :Returns: the parsed template
    """
    ext = os.path.splitext(template_name)[1]
    if   ext == ".htm" or ext == ".html":
        t = pyratemp.Template(filename=template_name, escape=pyratemp.HTML)
    elif ext == ".tex":
        #TODO: change this to LATEX as soon as the latex-escaping works
        sys.stderr.write("Warning: LaTeX-escaping not yet supported.\n")
        t = pyratemp.Template(filename=template_name, escape=None)
    else:
        t = pyratemp.Template(filename=template_name)
    return t

def load_data(datafiles):
    """Load data from data-files using either 'yaml' or 'simplejson'.
   
    Exits if data is invalid or neither 'yaml' nor 'simplejson' are found.

    :Parameters:
        - datafiles: [ [filename, nr_of_entry], ...]
    :Returns: read data (dict)
    """
    imported_yaml = False
    imported_simplejson = False
    mydata = {}

    for filename, n in datafiles:
        if filename[-5:].lower() == ".json":
            if not imported_simplejson:
                try:
                    import simplejson
                except ImportError:
                    sys.stderr.write("ERROR: python-module 'simplejson' not found.\n")
                    sys.exit(4)
                imported_simplejson = True
            try:
                myjson = simplejson.load(open(filename, 'r'))
                if n == -1:
                    mydata.update(myjson)
                else:
                    mydata.update(myjson[n])
            except ValueError:
                sys.stderr.write(u"ERROR: '%s' is not valid JSON.\n" % filename)
                sys.exit(4)
        elif filename[-5:].lower() == ".yaml":
            if not imported_yaml:
                try:
                    import yaml
                except ImportError:
                    sys.stderr.write("ERROR: python-module 'yaml' not found.\n")
                    sys.exit(4)
                imported_yaml = True

            if n == -1:
                n = 0
            myyaml = yaml.load_all(open(filename, 'r'))
            mydata.update(list(myyaml)[n])
        else:
            sys.stderr.write("ERROR: -f files must be .json or .yaml.\n")
            sys.exit(4)
    return mydata

#----------------------

if __name__ == "__main__":
    # parameter parsing
    try:
        opt_list, files = getopt.getopt(sys.argv[1:], "sd:f:n:h", ("help",))
    except getopt.GetoptError, (arg):
        sys.stderr.write("ERROR: invalid option (%s)\n" % (arg))
        sys.exit(2)

    render = True
    template_name = ""
    namevals = {}
    datafiles = []      #[ [filename, nr_of_entry], ...]
    for key, value in opt_list:
        if "-h" == key or "--help" == key:
            sys.stderr.write(USAGE+"\n")
            sys.exit(2)
        if "-s" == key:
            render = False
        elif "-d" == key:
            (name, value) = value.split("=", 1)
            namevals[name] = value
        elif "-f" == key:
            datafiles.append([value, -1])
        elif "-n" == key:
            if not datafiles:
                sys.stderr.write("ERROR: -n only allowed after -f\n")
                sys.exit(2)
            datafiles[-1][1] = int(value)

    if not files:
        sys.stderr.write(USAGE+"\n")
        sys.exit(2)
    for template_name in files:
        try:
            t = parse(template_name)
        except pyratemp.TemplateSyntaxError, err:
            sys.stderr.write("file '%s':\n" % template_name)
            sys.stderr.write("  TemplateSyntaxError: %s\n" % str(err))
            sys.exit(3)
        if render:
            filedata = load_data(datafiles)

            localtime = time.localtime()
            data = {
                    'mtime_CCYYMMDD':time.strftime("%Y-%m-%d",localtime),
                    'date'          :time.strftime("%Y-%m-%d",localtime),
                    }
            data.update(filedata)
            data.update(namevals)
            data = pyratemp.dictkeyclean(data)

            try:
                print t(**data).encode("utf-8"),
            except pyratemp.TemplateRenderError, err:
                sys.stderr.write("file '%s':\n" % template_name)
                sys.stderr.write("  TemplateRenderError: %s\n" % str(err))
                sys.exit(3)

#=========================================


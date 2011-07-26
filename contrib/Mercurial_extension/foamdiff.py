# foamdiff.py - compares revisions of versioncontrolled OpenFOAM-files
#
# Copyright 2011 Bernhard Gschaider <bgschaid@ice-sf.at>
#
# This software may be used and distributed according to the terms of the
# GNU General Public License version 2 or any later version.

'''command to compare revisions of an OpenFOAM-dictionary

Very simple. Uses pyFoamCompareDictionary.py and does not pass
options along to it

Parts lifted from the extdiff-extension
'''

from mercurial.i18n import _
from mercurial import commands,util,scmutil
from mercurial.node import nullid,short

import tempfile,os,shutil
from os import path

from PyFoam.Applications.CompareDictionary import CompareDictionary

def snapshot(ui, repo, files, node, tmproot):
    '''snapshot files as of some revision
    if not using snapshot, -I/-X does not work and recursive diff
    in tools like kdiff3 and meld displays too many files.'''
    dirname = os.path.basename(repo.root)
    if dirname == "":
        dirname = "root"
    if node is not None:
        dirname = '%s.%s' % (dirname, short(node))
    base = os.path.join(tmproot, dirname)
    os.mkdir(base)
    if node is not None:
        ui.note(_('making snapshot of %d files from rev %s\n') %
                (len(files), short(node)))
    else:
        ui.note(_('making snapshot of %d files from working directory\n') %
            (len(files)))
    wopener = scmutil.opener(base)
    fns_and_mtime = []
    ctx = repo[node]
    for fn in files:
        wfn = util.pconvert(fn)
        if not wfn in ctx:
            # File doesn't exist; could be a bogus modify
            continue
        ui.note('  %s\n' % wfn)
        dest = os.path.join(base, wfn)
        fctx = ctx[wfn]
        data = repo.wwritedata(wfn, fctx.data())
        if 'l' in fctx.flags():
            wopener.symlink(data, wfn)
        else:
            wopener(wfn, 'w').write(data)
            if 'x' in fctx.flags():
                util.set_flags(dest, False, True)
        if node is None:
            fns_and_mtime.append((dest, repo.wjoin(fn), os.path.getmtime(dest)))
    return dirname, fns_and_mtime

def foamdiff(ui, repo, *files, **opts):
    '''
    Compare two OpenFOAM-dictionaries for semantic differences
    
    Very simple. Uses pyFoamCompareDictionary.py and does not pass
    options along to it
    '''

    revs = opts.get('rev')
    change = opts.get('change')

    if len(files)==0:
        raise util.Abort("No files specified")
    
    if revs and change:
        msg = _('cannot specify --rev and --change at the same time')
        raise util.Abort(msg)
    elif change:
        node2 = repo.lookup(change)
        node1a, node1b = repo.changelog.parents(node2)
    else:
        node1a, node2 = scmutil.revpair(repo, revs)
        if not revs:
            node1b = repo.dirstate.parents()[1]
        else:
            node1b = nullid

    if node1b!=nullid:
        raise util.Abort("Can't do 3-way comparisons")
    
    matcher = scmutil.match(repo[node2], files, opts)
    mod_a, add_a, rem_a = map(set, repo.status(node1a, node2, matcher)[:3])
    modadd = mod_a | add_a 
    common = modadd | rem_a 
    if not common:
        return 0
    
    tmproot = tempfile.mkdtemp(prefix='foamdiff.')
    ui.debug("Writing temporary files to %s\n" %tmproot)
    try:
        dir1a_files = mod_a | rem_a 
        dir1a=snapshot(ui, repo, dir1a_files, node1a, tmproot)[0]

        dir2root = tmproot
        if node2:
            dir2=snapshot(ui, repo, modadd, node2, tmproot)[0]
        else:
            dir2=''
            dir2root=repo.root

        for f in common:
            ui.write("\n  Comparing: %s\n" %f)
            f1=path.join(tmproot,dir1a,f)
            f2=path.join(dir2root,dir2,f)
            CompareDictionary(args=[f1,f2])
    finally:
        ui.note(_('cleaning up temp directory\n'))
        shutil.rmtree(tmproot)
        
cmdtable = {
    "foamdiff":
    (foamdiff,
     [('r', 'rev', [],
       _('revision'), _('REV')),
      ('c', 'change', '',
       _('change made by revision'), _('REV')),
     ] + commands.walkopts,
     _('hg foamdiff [OPT]... FILE...')),
    }

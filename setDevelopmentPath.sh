# points PATHs to the unstable development version
# adapt to your own environment

thisFile=$0

if [[ $thisFile == "bash" ]]
then
    # for bash-versions that don't know who they're called
    thisFile=${BASH_SOURCE[0]}
fi

# make path absolute
thisFile=`python2 -c "from os import path; print path.abspath('$thisFile')"`

# now get the directory
DEVELOPMENTDIR=`dirname $thisFile`

unset thisFile

export PATH=$DEVELOPMENTDIR/bin:$PATH
export PYTHONPATH=$DEVELOPMENTDIR:$PYTHONPATH

export PYFOAM_SITE_DIR=$DEVELOPMENTDIR/exampleSite
export PATH=$PYFOAM_SITE_DIR/bin:$PATH

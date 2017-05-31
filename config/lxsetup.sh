#!/usr/bin/env bash

if [ -z "$ROOTCOREBIN" ]; then
    lsetup root
    echo "Warning: I just set up a non RootCore environment for you!"
    echo "If you want to use trtpy alongside a RootCore environment"
    echo "start over with that set up"
fi

lsetup 'sft releases/LCG_88/numpy/1.11.0'
lsetup 'sft releases/LCG_88/scipy/0.18.1'
lsetup 'sft releases/LCG_88/matplotlib/1.5.1'
lsetup 'sft releases/LCG_88/setuptools/20.1.1'
lsetup 'sft releases/LCG_88/pyyaml/3.11'

export TRTPYDIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )/.."
export PYTHONPATH=$PYTHONPATH:$TRTPYDIR
export PATH=$PATH:$TRTPYDIR/scripts

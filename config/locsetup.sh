#!/usr/bin/env bash

export TRTPYDIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )/.."
export PYTHONPATH=$PYTHONPATH:$TRTPYDIR
export PATH=$PATH:$TRTPYDIR/scripts

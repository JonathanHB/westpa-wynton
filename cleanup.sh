#!/bin/bash

# This script should not be used unless you're attempting to totally remove all traces of a run from a directory without starting a new run.
# To clean the directory and start a new run, use init.sh

# Clean up from previous/ failed runs
rm -rf traj_segs seg_logs run_logs istates west.h5 *.log


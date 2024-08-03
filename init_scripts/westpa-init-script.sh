#!/bin/bash

# Set up simulation environment
source env.sh

#get initial progress coordinate value
init_pc=$(python3 westpa_scripts/calc_pcoord.py gromacs_config/input.gro gromacs_config/input.gro)
echo $init_pc > bstates/pcoord.init

#get initial ensemble value if applicable
if [ "$1" = "1" ]; then
    echo $(python3 westpa_scripts/pc_2_macrostate.py $init_pc) > bstates/ensemble.txt
else

# Clean up from previous/ failed runs
rm -rf traj_segs seg_logs run_logs istates h5-backups wynton-logs west.h5 
mkdir  traj_segs seg_logs run_logs istates h5-backups wynton-logs

# Set pointer to bstate and tstate
BSTATE_ARGS="--bstate-file $WEST_SIM_ROOT/bstates/bstates.txt"
#TSTATE_ARGS="--tstate-file $WEST_SIM_ROOT/tstate.file"

# Run w_init
w_init \
  $BSTATE_ARGS \
  --segs-per-state 5 \
  --work-manager=threads "$@"

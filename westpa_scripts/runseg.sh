#!/bin/bash
#
#


# If we are debugging, output a lot of extra information.
if [ -n "$SEG_DEBUG" ] ; then
    set -x
    env | sort
fi

######################## Set up for running the dynamics #######################
# Set up the directory where data for this segment will be stored.
cd $WEST_SIM_ROOT
mkdir -pv $WEST_CURRENT_SEG_DATA_REF
cd $WEST_CURRENT_SEG_DATA_REF

# Make a symbolic link to the topology file. This is not unique to each segment.
ln -sv $WEST_SIM_ROOT/gromacs_config/topol.top .
ln -sv $WEST_SIM_ROOT/gromacs_config/toppar .
ln -sv $WEST_SIM_ROOT/gromacs_config/index.ndx .
ln -sv $WEST_SIM_ROOT/gromacs_config/input.gro .


echo $WEST_SIM_ROOT
echo $WEST_CURRENT_SEG_DATA_REF

# Either continue an existing tractory, or start a new trajectory. Here, both
# cases are the same.  If you need to handle the cases separately, you can
# check the value of the environment variable "WEST_CURRENT_SEG_INIT_POINT",
# which is equal to either "SEG_INITPOINT_CONTINUES" or "SEG_INITPOINT_NEWTRAJ"
# for continuations of previous segments and new trajectories, respecitvely.
# For an example, see the nacl_amb tutorial.

# The weighted ensemble algorithm requires that dynamics are stochastic.
# We'll use the "sed" command to replace the string "RAND" with a randomly
# generated seed.

#08224 JHB update: I don't think this is necessary because our thermostat 
#is stochastic and at any rate the string 'RAND' is not present so it does nothing
sed "s/RAND/$WEST_RAND16/g" \
	  $WEST_SIM_ROOT/gromacs_config/md.mdp > md.mdp

# This trajectory segment will start off where its parent segment left off.
# The "ln" command makes symbolic links to the parent segment's edr, gro, and 
# and trr files. This is preferable to copying the files, since it doesn't
# require writing all the data again.

# check if this is an initial run or not. Probably a better way to do this.
# yes - there's a variable
if [ "$WEST_CURRENT_SEG_INITPOINT_TYPE" = "SEG_INITPOINT_NEWTRAJ" ]; then
    # this is the first iteration
    # based on examples, I think WEST_PARENT_DATA_REF is just the init state?
    ln -sv $WEST_PARENT_DATA_REF ./parent.gro
    #ln -sv ../../../bstates/ensemble_pcoord.init ./last_ensemble.txt

    $GMX grompp -f md.mdp -c parent.gro -p topol.top \
	  -o seg.tpr -po md_out.mdp -n index.ndx   
else
    # assume this is a continuation, the value should be SEG_INITPOINT_CONTINUES
    ln -sv $WEST_PARENT_DATA_REF/seg.edr ./parent.edr
    ln -sv $WEST_PARENT_DATA_REF/seg.gro ./parent.gro
    #ln -sv $WEST_PARENT_DATA_REF/ensemble.txt ./last_ensemble.txt

    # do we even need this?? ln -sv $WEST_PARENT_DATA_REF/seg.trr ./parent.trr
    # Run the GROMACS preprocessor 
    $GMX grompp -f md.mdp -c parent.gro -e parent.edr -p topol.top \
	  -o seg.tpr -po md_out.mdp -n index.ndx
fi

############################## Run the dynamics ################################
# Propagate the segment using gmx mdrun
echo $GPU_ID
echo $SGE_GPU
echo $CUDA_VISIBLE_DEVICES
echo $OMP_NUM_THREADS
echo $WM_PROCESS_INDEX

GPU_ID=$WM_PROCESS_INDEX
echo $GPU_ID

python3 $WEST_SIM_ROOT/westpa_scripts/robust_runseg_mdrun.py $PWD $GMX $OMP_NUM_THREADS $GPU_ID

	  
########################## Calculate and return data ###########################
#config_pcoord=$(python3 $WEST_SIM_ROOT/westpa_scripts/calc_pcoord.py seg.trr input.gro)
current_pcoord=$(python3 $WEST_SIM_ROOT/westpa_scripts/ha_pcoord.py seg.trr input.gro $WEST_PARENT_DATA_REF)

echo $current_pcoord > $WEST_PCOORD_RETURN 

# Clean up all the files that we don't need to save.
rm -f topol.top toppar index.ndx input.gro seg.trr parent.gro \
      parent.edr parent.trr seg.tpr md.mdp md_out.mdp state.cpt seg.trr 

#remove old .gro files and tar entire westpa rounds worth of folders
#this only actually runs for walker 0 and should probably only be called for it
python3 $WEST_SIM_ROOT/westpa_scripts/file_cleanup.py $PWD

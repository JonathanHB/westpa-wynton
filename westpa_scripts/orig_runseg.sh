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
    $GMX grompp -f md.mdp -c parent.gro -p topol.top \
	  -o seg.tpr -po md_out.mdp -n index.ndx  
else
    # assume this is a continuation, the value should be SEG_INITPOINT_CONTINUES
    ln -sv $WEST_PARENT_DATA_REF/seg.edr ./parent.edr
    ln -sv $WEST_PARENT_DATA_REF/seg.gro ./parent.gro
    # do we even eneed this?? ln -sv $WEST_PARENT_DATA_REF/seg.trr ./parent.trr
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

#N.F.: why are we setting num threads to 3, OMP threads to 3, and thread-MPI to 1? I don't know how these relate to eachother lol
$GMX mdrun -s  seg.tpr -o seg.trr -c  seg.gro -e seg.edr \
	  -cpi state.cpt -g seg.log -nb gpu -pme gpu -bonded gpu \
	  -maxh 2 -cpt 10 -nt $OMP_NUM_THREADS -gpu_id ${GPU_ID} -ntmpi 1

#$GMX mdrun -s  seg.tpr -o seg.trr -c  seg.gro -e seg.edr \
#          -cpi state.cpt -g seg.log -nb gpu -pme gpu -bonded gpu \
#          -maxh 2 -cpt 10 -nt 3 -gpu_id ${GPU_ID}
	  
########################## Calculate and return data ###########################
current_pcoord=$(python3 $WEST_SIM_ROOT/westpa_scripts/calc_pcoord.py seg.trr input.gro)
echo $current_pcoord > $WEST_PCOORD_RETURN 

#echo '5\n' | $GMX rmsdist \
#	  -f $WEST_CURRENT_SEG_DATA_REF/seg.trr \
#	  -s input.gro \
#	  -o seg_in.xvg \
#          -xvg none \
#	  -n index.ndx 
#echo '6\n' | $GMX rmsdist \
#	  -f seg.trr \
#	  -s input.gro \
#	  -o seg_out.xvg \
#          -xvg none \
#	  -n index.ndx 
#here's where we calculate the pcoord, which I commented out because we don't know it rn lol
#paste <(cat seg_in.xvg  | tail -n 2 | awk {'print $2'}) <(cat seg_out.xvg | tail -n 2 | awk {'print $2'})>$WEST_PCOORD_RETURN

# Clean up all the files that we don't need to save.
rm -f topol.top toppar index.ndx input.gro seg.trr parent.gro \
      parent.edr parent.trr seg.tpr md.mdp md_out.mdp state.cpt seg.trr 
# tar all the output files (redundant with tarring an entire set of directories)
#tar -cvzf seg.tar.gz seg.gro seg.log seg.edr

#remove old .gro files and tar entire westpa rounds worth of folders
python3 $WEST_SIM_ROOT/westpa_scripts/file_cleanup.py $PWD

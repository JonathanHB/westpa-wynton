#!/bin/bash
#$ -S /bin/bash         #-- the shell for the job
#$ -q gpu.q             #-- use the gpu queue
#$ -j y                 #-- tell the system that the STDERR and STDOUT should be joined
#$ -cwd                 #-- tell the job that it should start in your working directory
#$ -l mem_free=2G       #-- submits on nodes with enough free memory
#$ -l h_rt=2:00:00      #-- runtime limit - max 2 weeks == 336 hours
#$ -N WE_H_a            #-- do not change this without also changing all the associated log archiving scripts
#$ -t 1-64              #-- number to run at a time

#old settings
##$ -l hostname=cc-idgpu[4] #-- request the RTX 2080 Ti nodes

## GPU/CPU stuff
GMX_CPUS=8
export CUDA_VISIBLE_DEVICES=$SGE_GPU
export OMP_NUM_THREADS=$GMX_CPUS
export GMX_GPU_DD_COMMS=true
export GMX_GPU_PME_PP_COMMS=true
export GMX_FORCE_UPDATE_DEFAULT_GPU=true
echo $CUDA_VISIBLE_DEVICES
echo $OMP_NUM_THREADS

module purge
module load CBI
module load miniconda3/4.12.0-py39 #miniconda3/23.5.2-0-py39 #miniconda3-py39
conda activate westpa-2.0
export WEST_PYTHON=($which python2.7)
source env.sh

## Get software
module load Sali
module load cuda/10.0.130

GMX_VER=2020.6
GMX_BIN=/wynton/home/grabe/shared/gromacs/gromacs-${GMX_VER}_CUDA10_SSE4/bin/gmx

#WEST_ROOT=$(pwd) #Is this right? NF

## ZMQ run
SERVER_INFO=$WEST_SIM_ROOT/run_logs/west_zmq_info-$JOB_ID.json

# Start the server - on first gpu only
if [ $SGE_TASK_ID == 1 ]; then
  w_run --verbose \
                       --work-manager=zmq --n-workers=0 --zmq-mode=master \
                       --zmq-write-host-info=$SERVER_INFO --zmq-comm-mode=tcp \
                       &> run_logs/west-$JOB_ID.log &
fi

# wait on host info file up to three minutes
for ((n=0; n<180; n++)); do
    if [ -e $SERVER_INFO ]; then
        echo "== server info file $SERVER_INFO =="
        cat $SERVER_INFO
        break
    fi
    sleep 1
done

# exif it host info doesn't appear in one minute
if ! [ -e $SERVER_INFO ] ; then
    echo 'server failed to start'
    exit 1
fi

# start clients
w_run --verbose \
                         --work-manager=zmq --n-workers=1 --zmq-mode=client \
                         --zmq-read-host-info=$SERVER_INFO --zmq-comm-mode=tcp \
                         &> run_logs/west-$JOB_ID-$SGE_TASK_ID.log & 
wait

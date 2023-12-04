#import numpy as np
#import matplotlib.pyplot as plt
import h5py
#import sklearn
#from sklearn.preprocessing import normalize
import os


def walker_ancestors(h5path, walker_round, walker_num):
    
    #load h5 file
    with h5py.File(h5path, 'r') as f:
        
        pcoords = []
        walker_ids = []
        
        #determine names of westpa rounds
        #note that round 1's name is at index 0
        iterations = [iter for iter in f["iterations"]]

        current_round = walker_round
        
        for iter_ind in range(walker_round):
        
            #this extracts only the iteration name, not the iteration data
            iter_name = iterations[current_round-1] 
            #using the iteration name to extract the data
            
            #log walker ID and progress coordinate
            #zeros are for trimming excess nested array layers
            pcoords.append(f["iterations"][iter_name]["pcoord"][walker_num][0][0])
            walker_ids.append(walker_num)
            
            #update round and walker numbers
            current_round -= 1
            if current_round == 0:
                break
            walker_num = f["iterations"][iter_name]["seg_index"][walker_num][1]

    walker_ids.reverse()
    pcoords.reverse()
    return [walker_ids, pcoords]
            
#---------------------------------paths and target walker information---------------------------------

#specify input file and walker
#abspath = "/wynton/home/grabe/jborowsky/aac1/westpa-18"
#"/Users/jonathanborowsky/Documents/grabelab/aac1-cycle/wynton-trj/we18"
#date_time = "111923-2221" #"102423-0931"

h5path = f'west.h5' #{abspath}/ #-{date_time}

walker_round = 289    #503
walker_num = 889      #889

#-----------------------------------------------------------------------------------------------------

#make directory to store relevant traj segs
trj_seg_dir = f"{str(walker_round).zfill(6)}-{str(walker_num).zfill(6)}-ancestors"
os.mkdir(trj_seg_dir)

#get ancestors of target walkers
walker_ancestry = walker_ancestors(h5path, walker_round, walker_num)
walker_ids = walker_ancestry[0]

print(walker_ancestry)

#extract trajectory files of the ancestors of the target trajectory
for round in range(walker_round):
    archive = f"round-{str(round+1).zfill(6)}-segs"
    #print(archive)
    #print(walker_ids[round])
    os.system(f"tar -zxf traj_segs/{archive}.tar.gz traj_segs/{str(round+1).zfill(6)}/{str(walker_ids[round]).zfill(6)}/traj_comp.xtc; \
              mv traj_segs/{str(round+1).zfill(6)}/{str(walker_ids[round]).zfill(6)}/traj_comp.xtc {trj_seg_dir}/{str(round+1).zfill(6)}-trj.xtc")
    #os.system(f"tar -xvf traj_segs/{archive}.tar.gz -C {trj_seg_dir}/")
    #os.system(f"cp {trj_seg_dir}/traj_segs/{str(round+1).zfill(6)}/{str(walker_ids[round]).zfill(6)}/traj_comp.xtc {trj_seg_dir}/{str(round+1).zfill(6)}-trj.xtc;\
    #          rm -r {trj_seg_dir}/traj_segs/{str(round+1).zfill(6)}")
    
#concatenate trajectories
trjcat_commands = [
    "module load mpi",
    "module load Sali",
    "module load cuda/10.0.130",
    f"/wynton/home/grabe/shared/gromacs/gromacs-2020.6_CUDA10_SSE4/bin/gmx trjcat -f {trj_seg_dir}/*-trj.xtc -o {trj_seg_dir}/{str(walker_round).zfill(6)}-{str(walker_num).zfill(6)}-full-trj.xtc -cat"
]

os.system("; ".join(trjcat_commands))

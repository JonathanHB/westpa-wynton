import sys
import os

#Jonathan Borowsky
#10/16/23

#a script for automatically restarting crashed westpa jobs
# where one round has a crashed without generating a gro file but still reported a progress coordinate 
# and the next round has crashed due to the missing progress coordinate

#-----------------------------------------------------------------
#parse input

first_round_removed = int(sys.argv[1])
second_round_removed = first_round_removed + 1
#for making sure we don't remove any critical data for restarting
last_round_to_keep = first_round_removed - 1

#---------------------------safety interlock; do not touch------------------------------------
#verify that we are not removing the round we need to restart from by accident
round_keep_str = str(last_round_to_keep).zfill(6)

#log files
log_fns = os.listdir("seg_logs")

log_fn_nums = [fn[0:6] for fn in log_fns if fn[-4:] == ".log"]

if round_keep_str not in log_fn_nums:
    print(f"round {last_round_to_keep} logs not found in seg_logs/ ; exiting")
    sys.exit(0)

#trajectory files
traj_folders = os.listdir("traj_segs")

if round_keep_str not in traj_folders:
    print(f"round {last_round_to_keep} folder not found in traj_segs/ ; exiting")
    sys.exit(0)

#---------------------------end safety interlock; do not touch above--------------------------

#-----------------------------------------------------------------
#remove crashed westpa round files

print("deleting crashed logs and trajectories")

round1_str = str(first_round_removed).zfill(6)
round2_str = str(second_round_removed).zfill(6)

os.system(f"rm seg_logs/{round1_str}-*.log")
os.system(f"rm seg_logs/{round2_str}-*.log")

os.system(f"rm -r traj_segs/{round1_str}/")
os.system(f"rm -r traj_segs/{round2_str}/")


#-----------------------------------------------------------------
#restart westpa

print("restarting westpa")

if len(sys.argv) > 2:
    n_rounds = sys.argv[2]
else:
    n_rounds = 100 #default

restart_commands = [\
    "module load CBI miniconda3/4.12.0-py39",\
    "conda activate westpa-2.0",
    f"w_truncate -n {first_round_removed}",\
    f"./run_chain.sh -r run_zmq.sh -n {n_rounds}"
    ]

os.system("; ".join(restart_commands))

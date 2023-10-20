import sys
import os

#Jonathan Borowsky
#10/16/23

#a script for automatically restarting crashed westpa jobs
# where one round has a crashed without generating a gro file but still reported a progress coordinate 
# and the next round has crashed due to the missing progress coordinate

#-----------------------------------------------------------------
#parse input

if len(sys.argv) < 3:
    print("too few arguments; enter [first round to remove], ['none' or first and last wynton jobs to kill (as 2 arguments)], [number of westpa rounds to submit (optional)]")
    sys.exit(0)

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
#terminate current wynton jobs specified by the user, if any jobs remain from the crashed westpa run

#keep track of the indices of different arguments in sys.argv
argshift = 0

if sys.argv[2].lower() != "none":
    print(f"qdel {{{sys.argv[3]}..{sys.argv[3]}}}") #double curly braces escape curly braces in f strings
    #os.system(f"qdel {{{sys.argv[3]}..{sys.argv[3]}}}")
    argshift = 1

#-----------------------------------------------------------------
#remove crashed westpa round files
# this is what the safety interlock goes with

print("deleting crashed logs and trajectories")

round1_str = str(first_round_removed).zfill(6)
round2_str = str(second_round_removed).zfill(6)

os.system(f"rm seg_logs/{round1_str}-*.log")
os.system(f"rm seg_logs/{round2_str}-*.log")

os.system(f"rm -r traj_segs/{round1_str}/")
os.system(f"rm -r traj_segs/{round2_str}/")

#-----------------------------------------------------------------
#tar wynton log files (crashed or otherwise) and delete the originals
#the utility of this is questionable given the recent upgrade to file_cleanup.py

#get first and last job numbers in order to give each archive a unique systematic name
# fns = os.listdir(".")
# we_h_nums = [fn[8:15] for fn in fns if fn[0:8] == "WE_H_a.o"]

# if len(we_h_nums) > 0:
#     fn_min = min(we_h_nums)
#     fn_max = max(we_h_nums)

#     fn_wy_log_out = f"wynton-logs-{fn_min}-{fn_max}.tar.gz"

#     os.system(f"tar -czvf {fn_wy_log_out} WE_H_a.o*.*; mv {fn_wy_log_out} wynton-logs; rm WE_H_a.o*.*")

#-----------------------------------------------------------------
#restart westpa

print("restarting westpa")

if len(sys.argv) > 3+argshift:
    n_rounds = sys.argv[3+argshift]
else:
    n_rounds = 100 #default

restart_commands = [\
    "module load CBI miniconda3/4.12.0-py39",\
    "conda activate westpa-2.0",
    f"w_truncate -n {first_round_removed}",\
    f"./run_chain.sh -r run_zmq.sh -n {n_rounds}"
    ]

os.system("; ".join(restart_commands))

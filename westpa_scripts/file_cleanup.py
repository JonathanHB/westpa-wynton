#Jonathan Borowsky
#091923
#westpa gromacs file management

import sys
import os
import numpy as np
#os.system(f"echo {sys.argv[1]} > /wynton/home/grabe/jborowsky/aac1/westpa-07/test-io-log.txt")

round_str = sys.argv[1].split("/")[-2]
walker_str = sys.argv[1].split("/")[-1]

#print(sys.argv[1].split("/"))

round_num = int(round_str)
walker_num = int(walker_str)

round_lag=3

if round_num - round_lag > 0 and walker_num == 0:
	#leave more recent rounds alone since they're needed to start walkers
	round_tar = str(round_num - round_lag).zfill(6)
	#tar segment logs
	if not os.path.exists(f"../../../seg_logs/round-{round_tar}-logs.tar.gz") and os.path.exists(f"../../../seg_logs/{round_tar}-000000.log"):
		os.system(f"tar -czvf ../../../seg_logs/round-{round_tar}-logs.tar.gz ../../../seg_logs/{round_tar}-*.log; rm ../../../seg_logs/{round_tar}-*.log")
	
	#1.  delete gro files, which are mostly redundant with xtc files and take up 10 times as much space
	#2.  tar the rest of the files to avoid gumming up wynton
        #3.  delete the un-tarred file copies	
	#4.? copy the tarred files and a versioned copy of west.h5 to x01
		#cannot resolve x01 hostname and therefore cannot copy; rsync also doesn't work

	#doing these in one command ensures that the delete command does not get entered before the tar command is done
	if not os.path.exists(f"../../../traj_segs/round-{round_tar}-segs.tar.gz") and os.path.exists(f"../../../traj_segs/{round_tar}"):
		os.system(f"rm ../../../traj_segs/{round_tar}/*/seg.gro; tar -czvf ../../../traj_segs/round-{round_tar}-segs.tar.gz ../../../traj_segs/{round_tar}; rm -r ../../../traj_segs/{round_tar}")

#n_subjobs = 32 #number of subjobs

os.chdir("../../../") #should do this at the start of the program

#tar wynton log files (crashed or otherwise) and delete the originals

#get first and last job numbers in order to give each archive a unique systematic name
fns = os.listdir(".")
we_h_nums = np.unique([int(fn[8:].split(".")[0]) for fn in fns if fn[0:8] == "WE_H_a.o"])
we_h_nums.sort()

if len(we_h_nums) >= 2:
    #fn_min = min(we_h_nums)
    #fn_max = max(we_h_nums)
	tar_num = str(we_h_nums[-2]).zfill(7) #only once a newer job has started should the old one's logs be tarred

	fn_wy_log_out = f"wynton-logs-{tar_num}.tar.gz"

	os.system(f"tar -czvf {fn_wy_log_out} WE_H_a.o{tar_num}.*; mv {fn_wy_log_out} wynton-logs; rm WE_H_a.o{tar_num}.*")


#tar run_log files (crashed or otherwise) and delete the originals
#json files are unaffected

#get first and last job numbers in order to give each archive a unique systematic name
fns = os.listdir("run_logs")
we_log_nums = np.unique([int(fn[5:].split("-")[0]) for fn in fns if (fn[0:5] == "west-" and fn[-4:] == ".log")])
we_log_nums.sort()

if len(we_log_nums) >= 2:
    #fn_min = min(we_h_nums)
    #fn_max = max(we_h_nums)
	tar_num = str(we_log_nums[-2]).zfill(7) #only once a newer job has started should the old one's logs be tarred

	fn_wy_log_out = f"run-logs-{tar_num}.tar.gz"

	os.system(f"tar -czvf run_logs/{fn_wy_log_out} run_logs/west-{tar_num}*.log; rm run_logs/west-{tar_num}*.log")

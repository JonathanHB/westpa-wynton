#Jonathan Borowsky
#091923-042124
#westpa gromacs file management

import sys
import os
import numpy as np

#how many rounds of traj_segs and seg_logs to leave untarred
round_lag = 3
#how many rounds of run_logs and SGE job logs to leave untarred
job_lag = 2

#get current walker number
walker_num = int(sys.argv[1].split("/")[-1])

if walker_num == 0:

	os.chdir("../../../") 

	#path to my scratch directory
	scratch_path = f"/wynton/scratch/jborowsky/{os.getcwd().split('/')[-1]}"
	
	#------------------------------------------------------------------------
	#tar traj_segs and seg_logs
	#------------------------------------------------------------------------

	#get current round number
	round_num = int(sys.argv[1].split("/")[-2])

	if round_num - round_lag > 0: 
		
		#tar seg_logs
		round_tar = str(round_num - round_lag).zfill(6)
		if not os.path.exists(f"seg_logs/round-{round_tar}-logs.tar.gz") and os.path.exists(f"seg_logs/{round_tar}-000000.log"):
			os.system(f"tar -czvf seg_logs/round-{round_tar}-logs.tar.gz seg_logs/{round_tar}-*.log; rm seg_logs/{round_tar}-*.log")
		
		#delete gro files and tar the remaining traj_segs files

		#1.  delete gro files, which are mostly redundant with xtc files and take up 10 times as much space
		#2.  tar the rest of the files
		#3.  delete the un-tarred file copies	
		#4.  [potential future functionality]: copy the tarred files and a versioned copy of west.h5 to x01
		#	 cannot resolve x01 hostname and therefore cannot copy; rsync also doesn't work

		#doing these in one command ensures that the delete command does not get entered before the tar command is done
		if not os.path.exists(f"traj_segs/round-{round_tar}-segs.tar.gz") and os.path.exists(f"traj_segs/{round_tar}"):
			os.system(f"rm traj_segs/{round_tar}/*/seg.gro; tar -czvf {scratch_path}/round-{round_tar}-segs.tar.gz traj_segs/{round_tar}; rm -r traj_segs/{round_tar}")


	#------------------------------------------------------------------------
	#tar SGE job logs
	#------------------------------------------------------------------------

	#get first and last job numbers in order to give each archive a unique systematic name
	fns = os.listdir(".")
	we_h_nums = np.unique([int(fn[8:].split(".")[0]) for fn in fns if fn[0:8] == "WE_H_a.o"])
	we_h_nums.sort()

	#tar old log files and delete untarred copies
	if len(we_h_nums) >= job_lag:

		tar_num = we_h_nums[-job_lag]
		tar_fn = f"wynton-logs-{str(tar_num).zfill(8)}.tar.gz"

		os.system(f"tar -czvf {tar_fn} WE_H_a.o{tar_num}.*; mv {tar_fn} wynton-logs; rm WE_H_a.o{tar_num}.*")
	
	
	#------------------------------------------------------------------------
	#tar run_logs, excluding json files
	#------------------------------------------------------------------------

	#get first and last job numbers in order to give each archive a unique systematic name
	fns = os.listdir("run_logs")
	we_log_nums = np.unique([int(fn[5:].split("-")[0].split(".")[0]) for fn in fns if (fn[0:5] == "west-" and fn[-4:] == ".log")])
	we_log_nums.sort()
	
	#tar old log files and delete untarred copies
	if len(we_log_nums) >= job_lag:

		tar_num = we_log_nums[-job_lag]
		tar_fn = f"run-logs-{str(tar_num).zfill(8)}.tar.gz"

		os.system(f"tar -czvf run_logs/{tar_fn} run_logs/west-{tar_num}*.log; rm run_logs/west-{tar_num}*.log")

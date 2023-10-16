#Jonathan Borowsky
#091923
#westpa gromacs file management

import sys
import os
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
	os.system(f"tar -czvf ../../../seg_logs/round-{round_tar}-logs.tar.gz ../../../seg_logs/{round_tar}-*.log; rm ../../../seg_logs/{round_tar}-*.log")
	
	#1.  delete gro files, which are redundant with xtc files and take up 10 times as much space
	#2.  tar the rest of the files to avoid gumming up wynton
        #3.  delete the un-tarred file copies	
	#4.? next copy the tarred files and a versioned copy of west.h5 to x01
		#cannot resolve x01 hostname and therefore cannot copy; rsync also doesn't work

	#doing these in one command is essential so that the delete command does not get entered before the tar command is done
	os.system(f"rm ../../../traj_segs/{round_tar}/*/seg.gro; tar -czvf ../../../traj_segs/round-{round_tar}-segs.tar.gz ../../../traj_segs/{round_tar}; rm -r ../../../traj_segs/{round_tar}")



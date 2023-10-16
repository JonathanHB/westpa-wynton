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

if round_num-2 > 0 and walker_num == 0:
	#leave more recent rounds alone since they're needed to start walkers
	round_tar = str(round_num-2).zfill(6)
	#tar segment logs
	os.system(f"tar -czvf ../../../seg_logs/round-{round_tar}-logs.tar.gz ../../../seg_logs/{round_tar}-*.log; rm ../../../seg_logs/{round_tar}-*.log")
	
	#delete gro files, which are redundant with xtc files and take up 10 times as much space
	os.system(f"rm ../../../traj_segs/{round_tar}/*/seg.gro")

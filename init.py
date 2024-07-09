import os
import sys

scratch_path = f"/wynton/scratch/jborowsky/{os.getcwd().split('/')[-1]}"

#if output files exist, proceed only if instructed to overwrite them
if (os.path.exists("traj_segs") or os.path.exists("seg_logs") or os.path.exists("run_logs") or os.path.exists(scratch_path)) and not (len(sys.argv) == 2 and sys.argv[1] == 'overwrite'):
    print("output folders already exist: aborting: rerun with argument 'overwrite' to override")
    sys.exit(0) #redundant with 'else' but this is a safety interlock

else:
    #make scratch folder if necessary
    if not os.path.exists(scratch_path):
        os.mkdir(scratch_path)

    os.system("bash init_scripts/westpa-init-script.sh")

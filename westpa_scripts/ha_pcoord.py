import os
import sys

# if we are not doing history augmented binning, 
# pass the configurational progress coordinate, 
# which is the entire progress coordinate, to output
if not os.path.exists("../../../westpa_scripts/pc_2_macrostate.py"):
    print(sys.argv[1])

#implement history augmented binning
else:
    config_pc = [float(pci) for pci in sys.argv[1].split(" ")]
    config_macrostate = os.system(f"python3 ../../../westpa_scripts/pc_2_macrostate.py {config_pc}")
    
    #if we are in a macrostate we go to the corresponding ensemble
    if config_macrostate != -1:
        ensemble = str(config_macrostate)

    #if we are not in a macrostate, we remain in the current ensemble
    else:
        #first round
        if sys.argv[2][-4:] == ".gro":
            f = open("../../../bstates/ensemble.txt", 'r')
            ensemble = [line for line in f][0].strip()
        #subsequent rounds
        else:
            f = open(f"{sys.argv[2]}/ensemble.txt", 'r')
            ensemble = [line for line in f][0].strip()

    #write the ensemble to a text file
    f = open(f"ensemble.txt", 'w')
    f.write(ensemble)

    # add the history augmented progress coordinate 
    # to the regular one as an extra dimension
    print(sys.argv[1] + " " + ensemble)

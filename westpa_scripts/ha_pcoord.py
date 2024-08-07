import os
import sys
from calc_pcoord import calc_pcoord

config_pc = calc_pcoord(sys.argv[1], sys.argv[2])

config_pc_string = " ".join([str(i) for i in config_pc])

# if we are not doing history augmented binning, 
# pass the configurational progress coordinate, 
# which is the entire progress coordinate, to output
if not os.path.exists("../../../westpa_scripts/pc_2_macrostate.py") and not os.path.exists("westpa_scripts/pc_2_macrostate.py"):
    #print(sys.argv[1])
    print(config_pc_string)

#implement history augmented binning
else:
    from pc_2_macrostate import pc_2_macrostate

    #config_pc_string = " ".join([sys.argv[i].strip() for i in range(2, len(sys.argv))])
    config_macrostate = pc_2_macrostate(config_pc) 
    #os.system(f"python3 ../../../westpa_scripts/pc_2_macrostate.py {config_pc_string}")
    
    #if we are in a macrostate we go to the corresponding ensemble
    if config_macrostate != -1:
        ensemble = str(config_macrostate)

    #if we are not in a macrostate, we remain in the current ensemble
    else:
        #first round (not seed state, which must have a config_macrostate != -1)
        if sys.argv[3][-4:] == ".gro":
            f = open("../../../bstates/pcoord.init", 'r')
            ensemble = [line for line in f][0].strip().split(" ")[-1]
            f.close()
        #subsequent rounds
        else:
            f = open(f"{sys.argv[3]}/ensemble.txt", 'r')
            ensemble = [line for line in f][0].strip()
            f.close()

    #write the ensemble to a text file
    f2 = open(f"ensemble.txt", 'x')
    f2.write(ensemble)
    f2.close()

    # add the history augmented progress coordinate 
    # to the regular one as an extra dimension
    print(config_pc_string + " " + ensemble)

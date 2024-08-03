import sys

#------------------------
# Parameters: 
# pc: a progress coordinate (currently a 1d array [or list] of floats, 
# but could be changed to a 2d array if the PC had multiple time points 
# and the indexing in get_unique_transitions() was adjusted accordingly)
#------------------------
# Returns: 
# macrostate: An integer. The possible values should be consecutive integers counting up from 0, and -1.
#             takes values in the range [-1,4] in this implementation
# note that this method must return a number other than -1 for the macrostate of the initial structure

def pc_2_macrostate(pc):
    pc0_min = 0.33
    pc0_max = 0.7 #adjust if including protonatable groups
    
    if pc[0] > pc0_max: 
        macrostate = 0
    elif pc[0] < pc0_min:
        macrostate = int(np.round(pc[1])+1)
    else:
        macrostate = -1
        
    return macrostate



print(pc_2_macrostate([float(i) for i in sys.argv[1].strip().split(" ")]))

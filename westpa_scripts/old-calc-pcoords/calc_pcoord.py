### Jonathan Borowsky
### laptop name = aac1_reaction_coord_3d_v2.py
import sys
import numpy as np
import itertools
import mdtraj as md
import matplotlib.pyplot as plt

def get_distance_matrix(state1, resseqs, periodic):

    # c-alpha indices
    prot_ca_state1 = [a.index for a in state1.top.atoms if a.residue.is_protein and a.name == 'CA' and a.residue.resSeq in resseqs]

    #number of atoms used
    n_ca_state1 = len(prot_ca_state1)

    # list of atom pairs
    pairs_state1 = list(itertools.product(prot_ca_state1, prot_ca_state1))

    # calculate pairwise distances
    #periodic = True is an issue for rcsb pdb structures with unit cell information if the residues are far enough apart
    distances_state1 = md.compute_distances(state1, pairs_state1, periodic=periodic, opt=True).reshape(n_ca_state1, n_ca_state1)

    return distances_state1


#note that this is the dRMSD
#this yields the same output as if the inputs were flattened
def elementwise_matrix_rmsd(mat1, mat2):
    return np.sqrt(np.mean((mat1 - mat2)**2))


# Calculate the progress coordinate or a component thereof
# using two structures defining the progress coordinate endpoints
# and a trajectory with the same residue numbering as the first structure (state1).
# The [ref_state] structure defines the 0 value of the progress coordinate.
def calc_progress_coord_component(state1, state2, resseqs_s1, resseqs_s2, frame, ref_state):

    #calculate distance matrices for the selected residues in each state from experimental structures
    distance_matrix_s1 = get_distance_matrix(state1, resseqs_s1, False)
    distance_matrix_s2 = get_distance_matrix(state2, resseqs_s2, False)

    #calculate the raw value of the progress coordinate between the two states
    pc_component_s1s2 = elementwise_matrix_rmsd(distance_matrix_s1, distance_matrix_s2)

    #calculate distance matrices for the selected residues in a trajectory frame
    distance_matrix_frame = get_distance_matrix(frame, resseqs_s1, True)

    #compute fractional progression of the structure in the frame along the progress coordinate
    if ref_state == 1:
        ref_mat = distance_matrix_s1
    elif ref_state == 2:
        ref_mat = distance_matrix_s2
    else:
        print("invalid state; exiting")
        sys.exit(0)

    fractional_pc = elementwise_matrix_rmsd(distance_matrix_frame, ref_mat)/pc_component_s1s2

    return fractional_pc

#--------------------------------define residues used for progress coordinate calculation-------------------------------
#abbreviations
#bovine = bov
#fungal = fun

#all of the residues below are positioned with approximate threefold symmetry on their respective helices

#cytoplasmic side
# 6 salt bridge residues
# + 3 inner brace residues (2 tyrosines and arg/lys which is mutated conservatively between the species)
# + 3 hydrophobic gate residues
bov_cytoplasmic_resseqs = [92, 95, 195,198,291,294,91, 194,290,88, 191,287]
fun_cytoplasmic_resseqs = [101,104,205,208,299,302,100,204,298,97, 201,295]

#matrix side
# 6 salt bridge residues + 3 pocket base residues
bov_matrix_resseqs = [29, 32, 134,137,231,234,33, 138,235]
fun_matrix_resseqs = [37, 40, 142,145,242,245,41, 146,246]

#linker helices on matrix side
bov_linker_resseqs = [i for i in range(54, 63+1)] + [i for i in range(157, 166+1)] + [i for i in range(254, 263+1)]
fun_linker_resseqs = [i for i in range(63, 72+1)] + [i for i in range(167, 176+1)] + [i for i in range(262, 271+1)]
#there were significant differences for all three segments; the problem is not likely a result of the gap before the final segment

#print("+".join([str(i) for i in bov_linker_resseqs]))
#print("+".join([str(i) for i in fun_linker_resseqs]))

#-------------------------------------parameters and file paths-------------------------------------

#the state we want to reach
ref_state = 1

#paths to structures and trajectories
inputpath = "/wynton/home/grabe/jborowsky/aac1/westpa-05/westpa_scripts/pcoord-ref-structures"
#"/Users/jonathanborowsky/Documents/grabelab/aac1-cycle/input-structures"

#which frame of trajectory to use
t=-1

#for westpa input
trj_in = sys.argv[1]
top_in = sys.argv[2]

#-------------------------------------load files-------------------------------------

bov_cstate_structure = md.load(f"{inputpath}/btAAC1_cdl_cstate_2c3e.pdb")
fun_mstate_structure = md.load(f"{inputpath}/6gci-nonb.pdb")

trj = md.load(trj_in, top=top_in)
frame = trj[t]

#----------test inputs---------
#frame = bov_cstate_structure

#trj_path = "/Users/jonathanborowsky/Documents/grabelab/aac1-cycle/wynton-trj/cube-107-102"
#frame =  md.load(trj_path+"/eq19-whole.xtc", top=trj_path+"/eq19.gro")[t]

#frame = md.load(f"{inputpath}/btAAC1_cdl_mstate_6gci_model.pdb") #sanity check with a bovine-numbering-scheme model
#frame = md.load(f"{inputpath}/btAAC1_cdl_cstate_2c3e.pdb")

#frame = md.load(f"/Users/jonathanborowsky/Documents/grabelab/aac1-cycle/105A-systems/charmm-gui-9326047169/gromacs/edited_step5_input.gro") #(0.9955518245697021 1.0056196451187134 1.00505793094635)
#frame = md.load(f"/Users/jonathanborowsky/Documents/grabelab/aac1-cycle/105A-systems/charmm-gui-9326050549/gromacs/step5_input.gro") #(0.008511162362992764 0.020596543326973915 0.018341928720474243)


#-------------------------------------calculate progress coordinate-------------------------------------

cyt_pc = calc_progress_coord_component(bov_cstate_structure, fun_mstate_structure, bov_cytoplasmic_resseqs, fun_cytoplasmic_resseqs, frame, ref_state)#, "m-side gate")
mat_pc = calc_progress_coord_component(bov_cstate_structure, fun_mstate_structure, bov_matrix_resseqs, fun_matrix_resseqs, frame, ref_state)#, "c-side gate")
linker_pc = calc_progress_coord_component(bov_cstate_structure, fun_mstate_structure, bov_linker_resseqs, fun_linker_resseqs, frame, ref_state)

#3d progress coordinate
print(f"{cyt_pc} {mat_pc} {linker_pc}")

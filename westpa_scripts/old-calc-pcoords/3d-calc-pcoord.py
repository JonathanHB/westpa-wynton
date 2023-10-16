### Jonathan Borowsky
### Loosely adapted from Chloe Sheen's adaptation of Paola Bisignano's Contact_map.ipynb
import sys
import numpy as np
import itertools
import mdtraj as md

def get_distance_matrix(state1, resseqs):

    # c-alpha indices
    prot_ca_state1 = [a.index for a in state1.top.atoms if a.residue.is_protein and a.name == 'CA' and a.residue.resSeq in resseqs]

    #number of atoms used
    n_ca_state1 = len(prot_ca_state1)

    # list of atom pairs
    pairs_state1 = list(itertools.product(prot_ca_state1, prot_ca_state1))

    # calculate pairwise distances
    distances_state1 = md.compute_distances(state1, pairs_state1, periodic=True, opt=True).reshape(n_ca_state1, n_ca_state1)

    return distances_state1

#the value of this method is debatable since it appears to be referenced twice
#this yields the same output as if the inputs were flattened
def elementwise_matrix_rmsd(mat1, mat2):
    return np.sqrt(np.mean((mat1 - mat2)**2))


# Calculate the progress coordinate or a component thereof
# using two structures defining the progress coordinate endpoints
# and a trajectory with the same residue numbering as the first structure (state1).
# The second structure (state2) defines the 0 value of the progress coordinate.
def calc_progress_coord_component(state1, state2, resseqs_s1, resseqs_s2, frame):
    #note that "matrix" here refers to the data structure, not the side of the mitochondrial membrane

    #calculate distance matrices for the selected residues in each state from experimental structures
    distance_matrix_s1 = get_distance_matrix(state1, resseqs_s1)
    distance_matrix_s2 = get_distance_matrix(state2, resseqs_s2)

    #calculate the raw value of the progress coordinate between the two states
    pc_component_s1s2 = elementwise_matrix_rmsd(distance_matrix_s1, distance_matrix_s2)

    #calculate distance matrices for the selected residues in a trajectory frame
    distance_matrix_frame = get_distance_matrix(frame, resseqs_s1)

    #compute and return fractional progression of the structure in the frame along the progress coordinate
    fractional_pc = elementwise_matrix_rmsd(distance_matrix_frame, distance_matrix_s2)/pc_component_s1s2

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

#-------------------------------------file paths-------------------------------------

#paths to structures and trajectories
inputpath = "/wynton/home/grabe/jborowsky/aac1/westpa-01/westpa_scripts/pcoord-ref-structures"
#"/Users/jonathanborowsky/Documents/grabelab/aac1-cycle/input-structures"
#trj_path = "/Users/jonathanborowsky/Documents/grabelab/aac1-cycle/wynton-trj/cube3"

#which frame of trajectory to use
t=-1

trj = sys.argv[1]
top = sys.argv[2]

#-------------------------------------load files-------------------------------------

bov_cstate_structure = md.load(f"{inputpath}/btAAC1_cdl_cstate_2c3e.pdb")
fun_mstate_structure = md.load(f"{inputpath}/6gci-nonb.pdb")
trj = md.load(trj, top=top)
#md.load(trj_path+"/eq19.trr", top=trj_path+"/eq19.gro") #md.load(trj, top=top)
frame = trj[t]

#-------------------------------------calculate progress coordinate-------------------------------------

cyt_pc = calc_progress_coord_component(bov_cstate_structure, fun_mstate_structure, bov_cytoplasmic_resseqs, fun_cytoplasmic_resseqs, frame)
mat_pc = calc_progress_coord_component(bov_cstate_structure, fun_mstate_structure, bov_matrix_resseqs, fun_matrix_resseqs, frame)

#2d progress coordinate
print(f"{cyt_pc},{mat_pc}")

#average fractional progressions along each component to get 1D PC
#pc = (cyt_pc + mat_pc)/2

#print(pc)

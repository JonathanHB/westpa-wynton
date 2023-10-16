#Jonathan Borowsky
#progress coordinate calculation for UCP1-DNP simulations based on DNP z coordinate relative to UCP1 center
#calc_dnp_pc_2d_v3.py

import numpy as np
import mdtraj as md
import itertools
import sys

#define methods

#-------------------------------------DNP motion

def get_circmean_coordinates(frame, query, box_lengths):

    #get protein atom coordinates
    atom_inds = frame.top.select(query)
    atom_xyz = [frame.xyz[0][i] for i in atom_inds]

    #calculate angles representing the protein's distance between opposite sides of the box,
    # placing the center of the box at theta = 0
    #c is a coordinate, j is an axis (0,1,2 = x,y,z)
    atom_angles = [[c[j]*2*np.pi/box_lengths[j] - np.pi for c in atom_xyz] for j in [0,1,2]]

    #compute the unweighted circular mean of the coordinates in the protein atoms
    #a is an angle, j is an axis (0,1,2 = x,y,z)
    circmean_xyz = [np.arctan2(np.mean([np.sin(a) for a in atom_angles[j]]), np.mean([np.cos(a) for a in atom_angles[j]]))
                 *box_lengths[j]/(2*np.pi) for j in [0,1,2]]

    return circmean_xyz


def calc_protein_ligand_z_pc_comp(frame):

    #-----------box lengths---------------------------------------------------
    #for converting lengths to angles
    box_lengths = frame.unitcell_lengths[0]

    #-----------circular mean coordinates-------------------------------------
    #circular mean protein coordinates:
    prot_cm_xyz = get_circmean_coordinates(frame, "protein", box_lengths)

    #circular mean dinitrophenol coordinates:
    dnf_cm_xyz = get_circmean_coordinates(frame, "resname DNF", box_lengths)

    #-----------vector between molecules and periodicity correction-----------
    #beware that this assumes the following:
    #   the membrane lies in the xy plane
    #   the protein's long pseudosymmetric axis points in a constant direction along +z or -z
    #   protein flipping and membrane dissolution or reorientation are assumed not to occur

    #the vector pointing from the protein to the ligand within the periodic box
    #this can have a length of up to sqrt(lx**2 + ly**2 + lz**2)
    raw_prot_lig_vector = np.array(dnf_cm_xyz) - np.array(prot_cm_xyz)

    #periodic correction, yielding the shortest vector pointing from the protein to the ligand
    # so that there is no degeneracy in the progress coordinate
    # this can have a length of up to sqrt(lx**2 + ly**2 + lz**2)/2 as no two objects in a periodic box can be further apart
    periodicity_corrected_prot_lig_vector = (raw_prot_lig_vector+box_lengths/2) % box_lengths - box_lengths/2

    #-----------calculate progress coordinates-------------------------------------

    pc_xy = np.sqrt(periodicity_corrected_prot_lig_vector[0]**2 + periodicity_corrected_prot_lig_vector[1]**2)
    pc_z = periodicity_corrected_prot_lig_vector[2]

    return pc_z


#-------------------------------------protein conformational changes

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
def calc_progress_coord_component(state1, state2, frame, resseqs_s1, resseqs_s2, resseqs_frame, ref_state):

    #calculate distance matrices for the selected residues in each state from experimental structures
    distance_matrix_s1 = get_distance_matrix(state1, resseqs_s1, False)
    distance_matrix_s2 = get_distance_matrix(state2, resseqs_s2, False)
    #calculate distance matrices for the selected residues in a trajectory frame
    distance_matrix_frame = get_distance_matrix(frame, resseqs_frame, True)

    #calculate the raw value of the progress coordinate between the two states
    pc_component_s1s2 = elementwise_matrix_rmsd(distance_matrix_s1, distance_matrix_s2)

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
ucp1_cyt_resseqs = []

#matrix side
# 6 salt bridge residues + 3 pocket base residues
bov_matrix_resseqs = [29, 32, 134,137,231,234,33, 138,235]
fun_matrix_resseqs = [37, 40, 142,145,242,245,41, 146,246]
ucp1_mat_resseqs = []

#------------------------------------load input files------------------------------------

#The AAC1 state which defines the progress coordinate 0 value
ref_state = 2

mode = 0
#0 = take command line input from westpa
#1 = load hardcoded file for debugging

if mode == 0:
    # take westpa input
    trj_in = sys.argv[1]
    top_in = sys.argv[2]

    #load trajectory
    trj = md.load(trj_in, top=top_in)

    #select frame of trajectory to use
    t = -1
    frame = trj[t]
    
    ref_inputpath = "/wynton/home/grabe/jborowsky/aac1/westpa-04/westpa_scripts/pcoord-ref-structures"

elif mode == 1:
    #path to structures and trajectories
    inputpath = "/Users/jonathanborowsky/Documents/grabelab/ucp1"

    #frame = md.load(f"{inputpath}/charmmgui/multicomponent assembler/charmm-gui-9342720837/gromacs/step5_input.gro")
    #frame = md.load(f"{inputpath}/eq05/input.gro")
    frame = md.load(f"{inputpath}/we06/000013-000039/seg.gro")

    ref_inputpath = "/Users/jonathanborowsky/Documents/grabelab/aac1-cycle/input-structures"

bov_cstate_structure = md.load(f"{ref_inputpath}/btAAC1_cdl_cstate_2c3e.pdb")
fun_mstate_structure = md.load(f"{ref_inputpath}/6gci-nonb.pdb")

#----------------------------calculate circular mean coordinates of protein and ligand----------------------------


pc_z = calc_protein_ligand_z_pc_comp(frame)
cyt_pc = calc_progress_coord_component(bov_cstate_structure, fun_mstate_structure, frame, bov_cytoplasmic_resseqs, fun_cytoplasmic_resseqs, ucp1_cyt_resseqs, ref_state)
mat_pc = calc_progress_coord_component(bov_cstate_structure, fun_mstate_structure, frame, bov_matrix_resseqs, fun_matrix_resseqs, ucp1_mat_resseqs, ref_state)


#if I understand MAB binning this is not necessary
#set pc to a fixed value just outside the mouth of the protein except in the cylinder containing the protein 
# so that we don't waste time sampling DNF in the membrane or water.

# prot_radius = 1.5 # nm
# prot_z_halflen = 3 # nm

# if pc_xy > prot_radius or abs(pc_z) > prot_z_halflen:
#     pc_xy = 0
#     pc_z = prot_z_halflen

#

#------------------------return PCs------------------------

print(f"{pc_z} {cyt_pc} {mat_pc}")

#-----------------------trimmings------------------------

# import matplotlib.pyplot as plt
# plt.hist(prot_z_to_angle)
# plt.show()

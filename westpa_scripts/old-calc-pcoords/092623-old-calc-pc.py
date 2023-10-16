#Jonathan Borowsky
#progress coordinate calculation for UCP1-DNP simulations based on DNP z coordinate relative to UCP1 center
#calc_dnp_pc_2d_v3.py

import numpy as np
import mdtraj as md
import itertools
import sys

#define methods

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

#------------------------------------load input files------------------------------------

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

elif mode == 1:
    #path to structures and trajectories
    inputpath = "/Users/jonathanborowsky/Documents/grabelab/ucp1"

    #frame = md.load(f"{inputpath}/charmmgui/multicomponent assembler/charmm-gui-9342720837/gromacs/step5_input.gro")
    #frame = md.load(f"{inputpath}/eq05/input.gro")
    frame = md.load(f"{inputpath}/we06/000013-000039/seg.gro")

#----------------------------calculate circular mean coordinates of protein and ligand----------------------------

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

#set pc to a fixed value just outside the mouth of the protein except in the cylinder containing the protein 
# so that we don't waste time sampling DNF in the membrane or water.

prot_radius = 1.5 # nm
prot_z_halflen = 3 # nm

if pc_xy > prot_radius or abs(pc_z) > prot_z_halflen:
    pc_xy = 0
    pc_z = prot_z_halflen

#------------------------return PCs------------------------

print(f"{pc_z} {pc_xy}")

#-----------------------trimmings------------------------

# import matplotlib.pyplot as plt
# plt.hist(prot_z_to_angle)
# plt.show()

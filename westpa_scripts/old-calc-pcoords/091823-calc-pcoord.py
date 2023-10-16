#Jonathan Borowsky
#progress coordinate calculation for UCP1-DNP simulations based on DNP z coordinate relative to UCP1 center
#calc_dnp_pc_2d_v1.py on laptop

import numpy as np
import mdtraj as md
import itertools
import sys

#------------------------------------input file information

ref_state = 1

#paths to structures and trajectories
inputpath = "/Users/jonathanborowsky/Documents/grabelab/ucp1"

#which frame of trajectory to use
t=-1

#for westpa input
trj_in = sys.argv[1]
top_in = sys.argv[2]


#-------------------------------------calculate PC 1------------------------------------

#---------------load files----------------

#frame = md.load(f"{inputpath}/charmmgui/multicomponent assembler/charmm-gui-9342720837/gromacs/step5_input.gro")
#frame = md.load(f"{inputpath}/eq05/input.gro")

trj = md.load(trj_in, top=top_in)
frame = trj[t]

#for converting lengths to angles
box_z_length = frame.unitcell_lengths[0][2]

#-------------protein-------------
protein_inds = frame.top.select("protein")

prot_z_to_angle = [frame.xyz[0][i][2]*2*np.pi/box_z_length - np.pi for i in protein_inds]
circmean_prot_z = np.arctan2(np.mean([np.sin(z) for z in prot_z_to_angle]), np.mean([np.cos(z) for z in prot_z_to_angle]))*box_z_length/(2*np.pi)
#mean_prot_z = np.mean([frame.xyz[0][i][2] for i in protein_inds])

#-------------dinitrophenol-------------
dnf_inds = frame.top.select("resname DNF")

dnf_z_to_angle = [frame.xyz[0][i][2]*2*np.pi/box_z_length - np.pi for i in dnf_inds]
circmean_dnf_z = np.arctan2(np.mean([np.sin(z) for z in dnf_z_to_angle]), np.mean([np.cos(z) for z in dnf_z_to_angle]))*box_z_length/(2*np.pi)
#mean_dnf_z = np.mean([frame.xyz[0][i][2] for i in dnf_inds])

#-------------difference-------------
pc_z = circmean_dnf_z - circmean_prot_z

#-------------periodicity correction-------------
if pc_z > box_z_length/2:
    pc_z -= box_z_length
elif pc_z < -box_z_length/2:
    pc_z += box_z_length


#-------------------------------------calculate PC 2------------------------------------

#project coordinates onto the xy plane to calculate distances perpendicular to z

for i in range(len(frame.xyz[0])):
    frame.xyz[0][i][2] = 0

#all pairs of protein and ligand atoms
pairs_prot_dnf = list(itertools.product(protein_inds, dnf_inds))

#distances in xy plane
xy_distances = md.compute_distances(frame, pairs_prot_dnf, periodic=True, opt=True)

pc_xy = np.mean(xy_distances)

#------------------------return PCs------------------------

print(f"{pc_z} {pc_xy}")


# import matplotlib.pyplot as plt
# plt.hist(xy_distances.flatten())
# plt.show()


# print(circmean_prot_z)
# print(circmean_dnf_z)
#
# print(mean_prot_z)
# print(mean_dnf_z)


# import matplotlib.pyplot as plt
# plt.hist(prot_z_to_angle)
# plt.show()


import scipy.stats
import mdtraj as md
import sys

#----------load trajectory----------
trj = sys.argv[1]
top = sys.argv[2]

trj = md.load(trj, top=top)

#----------select components----------

#select lipids
lipid = trj.top.select("resn PA or resn PC or resn OL")
#select ligand
ligname="LJP"
ligand=trj.top.select("resname %s" % ligname)

#----------calculate positions and distances----------

#get the lipid and ligand z coordinates at each frame, corrected for periodicity
lipid_mean_zcoord = scipy.stats.circmean([trj.xyz[-1][i][2] for i in lipid], high=trj.unitcell_lengths[-1][2])
ligand_mean_zcoord = scipy.stats.circmean([trj.xyz[-1][i][2] for i in ligand], high=trj.unitcell_lengths[-1][2])

#calculate the minimum z distance from the ligand to the membrane center
#accounting for box periodicity by taking the shorter z distance
ligand_lipid_distance = min(abs(ligand_mean_zcoord-lipid_mean_zcoord), 
                            abs(trj.unitcell_lengths[-1][2]-(ligand_mean_zcoord-lipid_mean_zcoord)))

print(ligand_lipid_distance)
#sys.exit(ligand_lipid_distance)

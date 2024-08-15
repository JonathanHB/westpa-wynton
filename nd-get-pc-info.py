#Jonathan Borowsky
#updated 5/15/24
#westpa progress coordinate data aggregation

import sys
import os

#round_n = sys.argv[1]
pcoord_dim = 2

seg_logs = os.listdir("./seg_logs/")
linehead = "+ current_pcoord"

def printpcoords(round_n):

    pcoords = [[] for i in range(pcoord_dim)]
    walker_ids = []

    for seg_log in seg_logs:
        fn = seg_log.split("/")[-1]
        try:
            a = int(fn[:6])
        except:
	    #skip analysis for this westpa round without terminating if the log files have been tarred 
            if fn.split("-")[0] == "round" and int(fn.split("-")[1]) == round_n:
                print("round %s logs have been tarred" % round_n)
                return True
            continue


        if int(fn[:6]) == round_n:
            f = open("./seg_logs/" + seg_log)
            for line in f:
                if line[0:len(linehead)] == linehead:
                    pcoord_str = line.split("=")[-1].strip()
                    #print(pcoord_str)
                    walker_ids.append(int(fn[7:13]))
                    
                    
                    try:
                        pcoord = [round(float(pcc), 3) for pcc in pcoord_str[1:-1].split(" ")]
                    except:
                        print("error parsing walker %s; pcoord string %s" % (walker_ids[-1], pcoord_str))
                        #print(walker_ids[-1])
                        #print(pcoord_str)
            
                    for pc_dim in range(pcoord_dim):
                        pcoords[pc_dim].append(pcoord[pc_dim])
            
            f.close() 


    if pcoords[0] == []:
        return False
    
    #pcmins = []
    #pcmin_inds = []
    #pcmin_ortho = []

    print("round: " + str(round_n))

    for pci, pc in enumerate(pcoords):
        if pci == 0: #for the z progress coordinate
            pc2 = pc #[pcx for pcx in pc if pcx != 3]
            
            if True:
                for i, p in enumerate(pc):
                    if p < .33:
                        print("--------")
                        print(pcoords[0][i])
                        print(pcoords[1][i])
                        print(walker_ids[i])
        else:
            pc2 = pc
	
        #print(min(pc))
        #print(min(pc2))
        #if pc == 0:
        #    continue
        #pcmins.append(min(pc))
        #pcmin_inds.append(pc.index(min(pc)))
        printmax = True
        printmin = True
        if printmax:
            print("walker %s reached pc%s = %s" % (walker_ids[pc.index(max(pc2))], pci, max(pc2)))
        if printmin:
            print("walker %s reached pc%s = %s" % (walker_ids[pc.index(min(pc2))], pci, min(pc2)))
    #print("walker %s reached pc1 = %s, pc2 = %s" % (pcoords1.index(min(pcoords1)), min(pcoords1), pcoords2[pcoords1.index(min(pcoords1))] ))
    #print("walker %s reached pc2 = %s, pc1 = %s" % (pcoords2.index(min(pcoords2)), min(pcoords2), pcoords1[pcoords2.index(min(pcoords2))] ))
    #print("walker %s reached pc2 = %s, pc1 = %s" % (pcoords2.index(min(pcoords2)), min(pcoords2), pcoords1[pcoords2.index(min(pcoords2))] ))

    return True


for i in range(1, 999):
    if not printpcoords(i):
        break

#printpcoords(62)
#bins = [0.0, 0.05, 0.1, 0.15, 0.2, 0.25, 0.3, 0.35, 0.4, 0.45, 0.5, 0.55, 0.6, 0.65, 0.7, 0.75, 0.8, 0.85, 0.9, 0.95, 1.0, 'inf']


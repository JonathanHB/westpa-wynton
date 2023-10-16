#Jonathan Borowsky

#westpa progress coordinate data aggregation

import sys
import os

#round_n = sys.argv[1]

seg_logs = os.listdir("./seg_logs/")
linehead = "+ current_pcoord"

def printpcoords(round_n):

    pcoords1 = []
    pcoords2 = []

    for seg_log in seg_logs:
        fn = seg_log.split("/")[-1]
        if int(fn[:6]) == round_n:
            for line in open("./seg_logs/" + seg_log):
                if line[0:len(linehead)] == linehead:
                    pcoord_str = line.split("=")[-1].strip()[1:-1]
                    #print(pcoord_str)
                    pcoord = [round(float(pcc), 3) for pcc in pcoord_str.split(" ")]
                
    pcoords1.append(pcoord[0])
                    pcoords2.append(pcoord[1])
		pcoords2.append(pcoord[1])


    if pcoords1 == []:
        return False
    

    print("round: " + str(round_n))
    print("walker %s reached pc1 = %s, pc2 = %s" % (pcoords1.index(min(pcoords1)), min(pcoords1), pcoords2[pcoords1.index(min(pcoords1))] ))
    print("walker %s reached pc2 = %s, pc1 = %s" % (pcoords2.index(min(pcoords2)), min(pcoords2), pcoords1[pcoords2.index(min(pcoords2))] ))


    return True


for i in range(1, 999):
    if not printpcoords(i):
        break

#printpcoords(62)
#bins = [0.0, 0.05, 0.1, 0.15, 0.2, 0.25, 0.3, 0.35, 0.4, 0.45, 0.5, 0.55, 0.6, 0.65, 0.7, 0.75, 0.8, 0.85, 0.9, 0.95, 1.0, 'inf']


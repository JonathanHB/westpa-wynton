#####
# author csheen
# date 5.15.23
# generate a iteration vs. bin probabilities plot
# this is specific to the three defined states (folded, transient, unfolded)
# but can easily be adapted to generate other postanalysis figures
#####
import h5py
import numpy as np
import matplotlib.pyplot as plt
import os

currdir = os.getcwd()
infile = h5py.File(currdir + '/west.h5','r')
# specify desired number of iterations
iters = 200
bin1,bin2,bin3,bin4,bin5,bin6,bin7,bin8,bin9,bin10,bin11,bin12,bin13,bin14=([] for i in range(14))
bin1_sum,bin2_sum,bin3_sum,bin4_sum,bin5_sum,bin6_sum,bin7_sum,bin8_sum,bin9_sum,bin10_sum,bin11_sum,bin12_sum,bin13_sum,bin14_sum=([] for i in range(14))
pcbins,weight=[],[]
# walk through all iterations
for i in range(1,3):
    print(i)
    # assigning variables
    #folded_bin, transient_bin, unfolded_bin = [],[],[]
    weights = infile['iterations']['iter_0000%04d'%i]['seg_index']
    format_iter = "{0:08}".format(i)
    pcoords = infile["/iterations/iter_"+format_iter+"/pcoord"]
    pcoord_color = pcoords
    weight_pcoord = []
    
    seg_num = int(infile["/iterations/iter_"+format_iter+"/pcoord"].shape[0])
    # walk through all the replicates
    for j in range(0,len(weights)):
        print(j)
        weight_pcoord.append([weights[j][0],float(pcoords[j][0])])
        #print(weight_pcoord)
        # sum up probabilities based on pcoord values
        # fix this later for efficiency's sake
        #pcbins.append(weight_pcoord[j][1])
        #weight.append(weight_pcoord[j][0])
        #plt.hist(weight, density=True, bins=pcbins)

        if weight_pcoord[j][1] < 0.2:
            bin1.append(weight_pcoord[j][0])
        elif weight_pcoord[j][1] >= 0.2 and weight_pcoord[j][1] < 0.4:
            bin2.append(weight_pcoord[j][0])
        elif weight_pcoord[j][1] >= 0.4 and weight_pcoord[j][1] < 0.6:
            bin3.append(weight_pcoord[j][0])
        elif weight_pcoord[j][1] >= 0.6 and weight_pcoord[j][1] < 0.8:
            bin4.append(weight_pcoord[j][0])
        elif weight_pcoord[j][1] >= 0.8 and weight_pcoord[j][1] < 1.0:
            bin5.append(weight_pcoord[j][0])
        elif weight_pcoord[j][1] >= 1.0 and weight_pcoord[j][1] < 1.2:
            bin6.append(weight_pcoord[j][0])
        elif weight_pcoord[j][1] >= 1.2 and weight_pcoord[j][1] < 1.4:
            bin7.append(weight_pcoord[j][0])
        elif weight_pcoord[j][1] >= 1.4 and weight_pcoord[j][1] < 1.6:
            bin8.append(weight_pcoord[j][0])
        elif weight_pcoord[j][1] >= 1.6 and weight_pcoord[j][1] < 1.8:
            bin9.append(weight_pcoord[j][0])
        elif weight_pcoord[j][1] >= 2.0 and weight_pcoord[j][1] < 2.2:
            bin10.append(weight_pcoord[j][0])        
        elif weight_pcoord[j][1] >= 2.2 and weight_pcoord[j][1] < 2.5:
            bin11.append(weight_pcoord[j][0])
        elif weight_pcoord[j][1] >= 2.5 and weight_pcoord[j][1] < 3.0:
            bin12.append(weight_pcoord[j][0])
        elif weight_pcoord[j][1] >= 3.0 and weight_pcoord[j][1] < 4.0:
            bin13.append(weight_pcoord[j][0])
        elif weight_pcoord[j][1] >= 4.0 and weight_pcoord[j][1] < 8.0:
            bin14.append(weight_pcoord[j][0])

    # summing up weights in the three states
  
    bin1_sum.append(sum(bin1))
    bin2_sum.append(sum(bin2))
    bin3_sum.append(sum(bin3))
    bin4_sum.append(sum(bin4))
    bin5_sum.append(sum(bin5))
    bin6_sum.append(sum(bin6))
    bin7_sum.append(sum(bin7))
    bin8_sum.append(sum(bin8))
    bin9_sum.append(sum(bin9))
    bin10_sum.append(sum(bin10))
    bin11_sum.append(sum(bin11))
    bin12_sum.append(sum(bin12))
    bin13_sum.append(sum(bin13))
    bin14_sum.append(sum(bin14))

total_bin_probs = []
total_bin_probs.extend([sum(bin1),sum(bin2),sum(bin3),sum(bin4),sum(bin5),sum(bin6),sum(bin7),sum(bin8),sum(bin9),sum(bin10),sum(bin11),sum(bin12),sum(bin13),sum(bin14)])


print(total_bin_probs)
def running_mean(x, N):
    x = np.pad(x, (N//2, N-1-N//2), mode='edge')
    cumsum = np.cumsum(np.insert(x, 0, 0)) 
    return (cumsum[N:] - cumsum[:-N]) / float(N)
"""
#print(bin1_prob_sum[199:205])
#print(bin2_prob_sum[199:205])
#print(bin3_prob_sum[199:205])

smoothed_bin1_rw1 = running_mean([float(value) for value in bin1_prob_sum[0:iters]], 50)
smoothed_bin2_rw1 = running_mean([float(value) for value in bin2_prob_sum[0:iters]], 50)
smoothed_bin3_rw1 = running_mean([float(value) for value in bin3_prob_sum[0:iters]], 50)


smoothed_bin1_rw2 = running_mean([float(value) for value in bin1_prob_sum[641:1322]], 80)
smoothed_bin2_rw2 = running_mean([float(value) for value in bin2_prob_sum[641:1322]], 80)
smoothed_bin3_rw2 = running_mean([float(value) for value in bin3_prob_sum[641:1322]], 80)

smoothed_bin1_rw3 = running_mean([float(value) for value in bin1_prob_sum[1323:2003]], 80)
smoothed_bin2_rw3 = running_mean([float(value) for value in bin2_prob_sum[1323:2003]], 80)
smoothed_bin3_rw3 = running_mean([float(value) for value in bin3_prob_sum[1323:2003]], 80)

smoothed_bin1_rw4 = running_mean([float(value) for value in bin1_prob_sum[2004:2100]], 80)
smoothed_bin2_rw4 = running_mean([float(value) for value in bin2_prob_sum[2004:2100]], 80)
smoothed_bin3_rw4 = running_mean([float(value) for value in bin3_prob_sum[2004:2100]], 80)
"""
#plt.figure(figsize=(30,5))


#uncomment for unsmoothened plot
##plt.plot(bin1_prob_sum, color='#8db600', label='folded')
#plt.plot(bin2_prob_sum, color='#f8de7e', label='transient')
#plt.plot(bin3_prob_sum, color='#fa8072', label='unfolded')
"""
plt.plot(smoothed_bin1_rw1, color='#008000')
plt.plot(smoothed_bin2_rw1, color='#fcc200')
plt.plot(smoothed_bin3_rw1, color='#dc143c')
plt.plot(range(640, 640+len(smoothed_bin1_rw2)), smoothed_bin1_rw2, color='#008000')
plt.plot(range(640, 640+len(smoothed_bin1_rw2)), smoothed_bin2_rw2, color='#fcc200')
plt.plot(range(640, 640+len(smoothed_bin1_rw2)), smoothed_bin3_rw2, color='#dc143c')

plt.plot(range(1322, 1322+len(smoothed_bin1_rw3)), smoothed_bin1_rw3, color='#008000')
plt.plot(range(1322, 1322+len(smoothed_bin1_rw3)), smoothed_bin2_rw3, color='#fcc200')
plt.plot(range(1322, 1322+len(smoothed_bin1_rw3)), smoothed_bin3_rw3, color='#dc143c')

plt.plot(range(2003, 2003+len(smoothed_bin1_rw4)), smoothed_bin1_rw4, color='#008000')
plt.plot(range(2003, 2003+len(smoothed_bin1_rw4)), smoothed_bin2_rw4, color='#fcc200')
plt.plot(range(2003, 2003+len(smoothed_bin1_rw4)), smoothed_bin3_rw4, color='#dc143c')

plt.axvline(x=640, color='black', linestyle='dotted')
plt.axvline(x=1322, color='black', linestyle='dotted')
plt.axvline(x=2003, color='black', linestyle='dotted')

plt.plot(640, bin1_prob_sum[640], marker='v', markersize=8,color='#008000')
plt.plot(640, bin2_prob_sum[640], marker='v',markersize=8,color='#fcc200')
plt.plot(640, bin3_prob_sum[640], marker='v',markersize=8,color='#dc143c')

plt.plot(1323, bin1_prob_sum[1323], marker='v',markersize=8,color='#008000')
plt.plot(1323, bin2_prob_sum[1323], marker='v',markersize=8,color='#fcc200')
plt.plot(1323, bin3_prob_sum[1323], marker='v',markersize=8,color='#dc143c')

plt.plot(2004, bin1_prob_sum[2004], marker='v',markersize=8,color='#008000')
plt.plot(2004, bin2_prob_sum[2004], marker='v',markersize=8,color='#fcc200')
plt.plot(2004, bin3_prob_sum[2004], marker='v',markersize=8,color='#dc143c')

plt.legend(bbox_to_anchor=(1.15, 1), loc="upper right", fontsize = 25)

plt.xlim([0, iters])
plt.ylim([0, 1])
plt.xlabel('iterations', fontsize = 25)
plt.ylabel('total weight', fontsize = 25)

plt.ticklabel_format(useOffset=False, style='plain')
plt.title('Bin Probabilities over Time', fontsize = 25)
plt.tick_params(axis='both', which='major', labelsize=25)
"""
bins = [0, 0.2, 0.4, 0.6, 0.8, 1.0, 1.2, 1.4, 1.6, 1.8, 2.0, 2.2, 2.5, 3.0, 4.0, 8.0]
plt.tight_layout(pad=0)

plt.hist(total_bin_probs, bins=bins, edgecolor="k")
#plt.bar(bins,total_bin_probs)
plt.savefig('binprobs.png', bbox_inches="tight")
plt.show()
plt.close()

infile.close()

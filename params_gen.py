import os
import csv

header = ['sim_times','ecc_algorithm','file_name','bytes_per_oligo','address_size','ecc_param','miss_extension_prob','deletion_prob','over_extension_prob','molcule_num','reaction_cycle']

params = []
for i in range(10):
    for j in range(50):
        params.append([100,'r','1k_data',32,4,i + 1,0.001,0.0,0.0,j + 1,3])

with open('sim7.csv', 'w') as f:
    writer = csv.writer(f)
    writer.writerow(header)
    writer.writerows(params)

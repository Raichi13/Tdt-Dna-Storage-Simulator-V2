import csv
import itertools

miss_extension_prob_range = [0.001]
deletion_prob_range = [0.01]
over_extension_prob_range = [0.01]

sim_times_values = [192]
ecc_algorithm_values = ['h', 'r', 'd']
bytes_per_oligo_values = [8,16,32]
address_size_values = [4]
ecc_param_values_for_r = [1,5,10]
molcule_num_values = [1,2,5,10,20,50]
reaction_cycle_values = [1,2,5]
base_num_values = [3, 4]
file_name = '1k_data'

with open('./params/2023f/sim1.csv', 'w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(['sim_times', 'ecc_algorithm', 'file_name', 'bytes_per_oligo', 'address_size', 'ecc_param', 'miss_extension_prob', 'deletion_prob', 'over_extension_prob', 'molcule_num', 'reaction_cycle', 'base_num'])
    for sim_time, ecc_algo, bytes_per_oligo, address_size, miss_ext_prob, del_prob, over_ext_prob, molcule_num, reaction_cycle, base_num in itertools.product(
        sim_times_values, ecc_algorithm_values, bytes_per_oligo_values, address_size_values, miss_extension_prob_range, deletion_prob_range, over_extension_prob_range, molcule_num_values, reaction_cycle_values, base_num_values
    ):
        if ecc_algo == 'r':
            for ecc_param in ecc_param_values_for_r:
                writer.writerow([sim_time, ecc_algo, file_name, bytes_per_oligo, address_size, ecc_param, miss_ext_prob, del_prob, over_ext_prob, molcule_num, reaction_cycle, base_num])
        else:
            writer.writerow([sim_time, ecc_algo, file_name, bytes_per_oligo, address_size, 1, miss_ext_prob, del_prob, over_ext_prob, molcule_num, reaction_cycle, base_num])
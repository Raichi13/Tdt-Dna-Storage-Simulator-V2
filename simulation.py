from tdt import TdT
import numpy as np
from typing import Union,List
from dna_transcoder import DNATranscoder
from hamming_encoder import HammingEncoder
import pandas as pd
from hamming_decoder import HammingDecoder
from error_counter import ErrorCounter
from rs_encoder import RSEncoder
from rs_decoder import RSDecoder
from default_encoder import DefaultEncoder
from default_decoder import DefaultDecoder
import multiprocessing as mp
from functools import partial
import json
import os
import sys
import argparse
import time

def sum_of_elements(nested_list):
    if isinstance(nested_list, list):
        return sum(sum_of_elements(sub_list) for sub_list in nested_list)
    else:
        return 1


def simulate_single(ecc_algorithm:str,file_name:str,bytes_per_oligo:int,address_size:int,ecc_param:any,miss_extension_prob:int,deletion_prob:int,over_extension_prob:int,molcule_num:int,reaction_cycle:int,dummy=None):
    if not ecc_algorithm in ['h','r','d']:
        raise ValueError()
    encoder = None
    decoder = None
    if ecc_algorithm == 'h':
        encoder = HammingEncoder(file_name,bytes_per_oligo,address_size,ecc_param)
        decoder = HammingDecoder(bytes_per_oligo,address_size,ecc_param)
    elif ecc_algorithm == 'r':
        encoder = RSEncoder(file_name,bytes_per_oligo,address_size,ecc_param)
        decoder = RSDecoder(bytes_per_oligo,address_size,ecc_param)
    elif ecc_algorithm == 'd':
        encoder = DefaultEncoder(file_name,bytes_per_oligo,address_size,ecc_param)
        decoder = DefaultDecoder(bytes_per_oligo,address_size)

    encoded_data = encoder.encode()

    dna_transcoder = DNATranscoder()
    target_bases = dna_transcoder.encode_many(encoded_data)

    tdt = TdT(target_bases,reaction_cycle,molcule_num,miss_extension_prob,deletion_prob,over_extension_prob)
    ext_simlated_data = tdt.synthesis()

    decoded_data_from_dna = dna_transcoder.decode_with_consensus_base(ext_simlated_data)
    decoded_data = decoder.decode(decoded_data_from_dna)

    error_counter = ErrorCounter(encoder.ref,decoder.for_error_check)
    error_bytes = error_counter.count_error()
    total_bytes = encoder.file_size
    total_bases_before_synthesis = sum_of_elements([list(oligo) for oligo in target_bases])
    total_bases_after_synthesis = sum_of_elements(ext_simlated_data)

    return error_bytes,total_bytes,total_bases_before_synthesis,total_bases_after_synthesis


def simulate(sim_times:int,ecc_algorithm:str,file_name:str,bytes_per_oligo:int,address_size:int,ecc_param:any,miss_extension_prob:int,deletion_prob:int,over_extension_prob:int,molcule_num:int,reaction_cycle:int):
    simulate_single_partial = partial(simulate_single,ecc_algorithm, file_name, bytes_per_oligo, address_size, ecc_param, miss_extension_prob, deletion_prob, over_extension_prob, molcule_num, reaction_cycle)
    with mp.Pool(mp.cpu_count()) as pool:
        results = np.array(pool.map(simulate_single_partial, [None]*sim_times))
    error_bytes = results[:, 0]
    total_bytes = results[:, 1]
    total_bases_before_synthesis = results[:, 2]
    total_bases_after_synthesis = results[:, 3]

    error_bytes_min = error_bytes.min()
    error_bytes_max = error_bytes.max()
    error_bytes_avg = error_bytes.mean()

    total_bytes = total_bytes[0]

    total_bases_before_synthesis_sum = total_bases_before_synthesis.sum()

    total_bases_after_synthesis_min = total_bases_after_synthesis.min()
    total_bases_after_synthesis_max = total_bases_after_synthesis.max()
    total_bases_after_synthesis_avg = total_bases_after_synthesis.mean()

    return error_bytes_avg, error_bytes_min, error_bytes_max, total_bytes, total_bases_before_synthesis_sum, total_bases_after_synthesis_avg, total_bases_after_synthesis_min, total_bases_after_synthesis_max

def simtest(args):
    #miss,del,over
    input_csv = args.param
    out_path = os.path.splitext(input_csv)[0] + '_result.json'

    params_df = pd.read_csv(input_csv)
    params = [tuple(row) for row in params_df.values]

    # res = simulate(100,'h','1k_data',16,4,1,0.001,0.0,0.0,1,3)
    # print(res)
    simulations = []
    i = 1
    for p in params:
        print('Simulation {} of {} start'.format(i,len(params)))
        start_time = time.time()
        res = simulate(*p)
        end_time = time.time()
        simulation_duration = end_time - start_time
        print(res)
        simulation_result = {
            'index': i-1,
            'results': {
                'error_bytes_avg': int(res[0]),
                'error_bytes_min': int(res[1]),
                'error_bytes_max': int(res[2]),
                'total_bytes': int(res[3]),
                'total_bases_before_synthesis_sum': int(res[4]),
                'total_bases_after_synthesis_avg': int(res[5]),
                'total_bases_after_synthesis_min': int(res[6]),  
                'total_bases_after_synthesis_max': int(res[7])
            }
        }
        simulations.append(simulation_result)
        print('Simulation {} of {} done in {:.2f} seconds'.format(i, len(params), simulation_duration))
        i += 1
        

    with open(out_path, 'w') as f:
        json.dump(simulations, f)    
        
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='TdT sim')
    parser.add_argument('-p', '--param', help='input param csv', required=True)
    args = parser.parse_args()
    print(args)
    simtest(args)

# print(simulate_single('h','1k_data',16,4,1,0.0,0.0,0.0,50,3))
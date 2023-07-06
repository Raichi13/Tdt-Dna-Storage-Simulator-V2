from typing import Union
import numpy as np


byte_max = {1:2,2:3,3:4,4:5} #ecc_intervalごとのECC付与後byteのサイズ

def str2bits(input_str):
    bits = [1 << i for i in range(8)]
    return np.array([1 if ord(char) & b > 0 else 0 for char in input_str for b in bits])


def bits2str(input_bits):
    bits = [1 << i for i in range(8)]
    return ''.join(chr(
        sum(b * ib for b, ib in zip(bits, input_bits[i:i+8]))
    ) for i in range(0, len(input_bits), 8))

def int2bits(input_int):
    bits = [1 << i for i in range(32)]
    return np.array([1 if input_int & b > 0 else 0 for b in bits])

def bits2int(input_bits):
    bits = [1 << i for i in range(32)]
    return sum(b * ib for b, ib in zip(bits, input_bits))

def bits2mat(bits, n_cols=4):
    n_rows = len(bits) // n_cols
    mat = np.zeros((n_rows, n_cols), dtype=np.int32)
    for i in range(n_rows):
        for j in range(n_cols):
            if bits[i * n_cols + j] > 0:
                mat[i, j] = 1
    return mat


def mat2bits(mat):
    n_rows, n_cols = mat.shape
    return [mat[i, j] for i in range(n_rows) for j in range(n_cols)]

def encode(mat):
    G = np.array([
        [1, 0, 0, 0, 0, 1, 1],
        [0, 1, 0, 0, 1, 0, 1],
        [0, 0, 1, 0, 1, 1, 0],
        [0, 0, 0, 1, 1, 1, 1]
    ])
    return np.dot(mat, G) % 2


def decode(encoded_mat):
    R = np.array([
        [1, 0, 0, 0],
        [0, 1, 0, 0],
        [0, 0, 1, 0],
        [0, 0, 0, 1],
        [0, 0, 0, 0],
        [0, 0, 0, 0],
        [0, 0, 0, 0]
    ])
    return np.dot(encoded_mat, R) % 2

def find_error(encoded_vec):
    H = np.array([
        [0, 1, 1, 1, 1, 0, 0],
        [1, 0, 1, 1, 0, 1, 0],
        [1, 1, 0, 1, 0, 0, 1]
    ])
    syndrome = np.dot(encoded_vec, H.T) % 2
    n_column = H.shape[1]
    for column in range(n_column):
        if np.all(H[:, column] == syndrome):
            error = np.zeros(n_column, dtype=np.uint8)
            error[column] = 1
            return error
    return np.zeros(n_column, dtype=np.uint8)


def find_error_mat(encoded_mat):
    return np.apply_along_axis(find_error, 1, encoded_mat)

def hamming_encode(input_int):
    input_bits = int2bits(input_int)
    input_mat = bits2mat(input_bits)
    encoded_mat = encode(input_mat)
    return bits2int(mat2bits(encoded_mat))

def hamming_decode(encoded_int):
    encoded_bits = int2bits(encoded_int)
    encoded_mat = bits2mat(encoded_bits, n_cols=7)
    decoded_mat = decode(encoded_mat)
    return bits2int(mat2bits(decoded_mat))


def add_humming_ecc(datas = Union[np.uint8,int],ecc_interval = 4):
  res = []
  for d in datas:
    splited = [d[i:i+ecc_interval] for i in range(0, len(d), ecc_interval)]
    added_ecc = []
    for s in splited:
      added = hamming_encode(int.from_bytes(bytearray(np.array(s,dtype=np.uint8)),'big'))
      added_ecc.append(added)
    res.append(added_ecc)
  return np.array(res)

def max_uint(n_bytes):
    return 2 ** (8 * n_bytes) - 1

def correct_error_and_decode(datas = Union[np.uint8,int],ecc_interval = 4):
  res = []
  for d in datas:
    splited = [d[i:i+byte_max[ecc_interval]] for i in range(0, len(d), byte_max[ecc_interval])]
    ibyte = np.array([],dtype=np.uint8)
    for s in splited:
      if int.from_bytes(bytearray(s),'big') > max_uint(byte_max[ecc_interval]):
        continue    
      di = hamming_decode(int.from_bytes(bytearray(s),'big'))
      if di > max_uint(ecc_interval):
        continue
      ibyte = np.r_["-1",ibyte,np.frombuffer(int(di).to_bytes(ecc_interval,'big'),dtype=np.uint8)]
    res.append(ibyte)
  return res


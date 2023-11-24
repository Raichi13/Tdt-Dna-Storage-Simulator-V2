import numpy as np
from typing import Union,List
import pandas as pd
import ctypes


class DNATranscoder:
    def __init__(self, origin_base: str = "A") -> None:
        self.origin_base = origin_base
        self.lib = ctypes.CDLL('./cpp_libs/Build/libDnaTranscoder.so')
        self.lib.getConsensusSequence.restype = ctypes.c_void_p
        self.lib.getConsensusSequence.argtypes = [ctypes.POINTER(ctypes.c_char_p), ctypes.c_int, ctypes.POINTER(ctypes.c_int)]
        self.lib.free_consensus_sequence.argtypes = [ctypes.c_void_p]

    def __to_trit_bytes_flatten(self,ns=Union[np.uint8, int]) -> np.array:
        trits = []
        for n in ns:
            trit = np.base_repr(n, 3)
            trits.append(
                np.r_[
                    "-1",
                    [0] * (6 - len(str(trit))),
                    np.array(list(str(trit)), dtype=np.uint8),
                ]
            )
        return np.array(trits, dtype=np.uint8).flatten()

    def __trits_bytes_to_ints(self,trits=Union[np.uint8, int]):
        ints = []
        if len(trits) < 6:
            return np.array([], dtype=np.uint8)
        remainder = len(trits) % 6
        trits = trits[: len(trits) - remainder :]
        split_as_byte = np.split(trits, len(trits) / 6)
        for byte in split_as_byte:
            ints.append(int("".join(list(map(str, byte))), 3))
        return np.array(ints, dtype=np.uint8)

    def __trits_to_dna_bases(self, trits=Union[np.uint8, int]):
        bases: List[str] = [self.origin_base]
        mapper = {
            "A": {0: "G", 1: "C", 2: "T"},
            "C": {0: "T", 1: "G", 2: "A"},
            "G": {0: "A", 1: "T", 2: "C"},
            "T": {0: "C", 1: "A", 2: "G"},
        }
        for i, t in enumerate(trits):
            bases.append(mapper[bases[i]][t])
        return bases

    def __dna_bases_to_trits(self, bases: List[str]):
        trits = []
        mapper = {
            "A": {"G": 0, "C": 1, "T": 2},
            "C": {"T": 0, "G": 1, "A": 2},
            "G": {"A": 0, "T": 1, "C": 2},
            "T": {"C": 0, "A": 1, "G": 2},
        }
        for i, b in enumerate(bases):
            if i == len(bases) - 1:
                break
            if bases[i + 1] == b:
                continue
            trits.append(mapper[b][bases[i + 1]])
        return np.array(trits, dtype=np.uint8)
    
    def __build_consensus_base(self,bases:List,trim_margin:int = 0):
      avg = np.round(np.average(list(map(lambda x:len(x),bases))))
      df = pd.DataFrame(bases)
      mode = df.mode().iloc[0].tolist()
      return list(mode[:int(avg+trim_margin):]),avg
    
    def __remove_dna_repeat(self,bases:List):
      last_base = ''
      removed = []
      for b in bases:
          if last_base != b:
              removed.append(b)
          last_base = b
      return removed
    
    def decode_with_consensus_base(self,bases_list:List,trim_margin:int = 0):
        decoded_datas = []
        for bases_item in bases_list:
            sequences_c = [bytes(''.join(self.__remove_dna_repeat(bases)), 'utf-8') for bases in bases_item]
            sequences_ptrs = (ctypes.c_char_p * len(sequences_c))(*sequences_c)
            sequence_lengths = (ctypes.c_int * len(sequences_c))(*[len(seq) for seq in sequences_c])

            result_ptr = self.lib.getConsensusSequence(sequences_ptrs, len(sequences_c), sequence_lengths)
            result = ctypes.cast(result_ptr, ctypes.c_char_p).value
            consensus_base = result.decode('utf-8')
            self.lib.free_consensus_sequence(result_ptr)
            decoded_datas.append(self.decode(list(consensus_base)))
        return decoded_datas
    
    def encode_many(self,datas:List):
        encoded_datas = []
        for data in datas:
            encoded_datas.append(self.encode(data))
        return encoded_datas

    def encode(self, data: Union[np.uint8, int]):
        trits = self.__to_trit_bytes_flatten(data)
        bases = self.__trits_to_dna_bases(trits)
        return "".join(bases)

    def decode(self, bases: List[str]):
        trits = self.__dna_bases_to_trits(bases)
        data = self.__trits_bytes_to_ints(trits)
        return data

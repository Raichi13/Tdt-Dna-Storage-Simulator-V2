from abc import ABC, abstractmethod
import numpy as np
import ctypes
from typing import Union, List

class TranscoderBase(ABC):
    def __init__(self, origin_base: str = "A") -> None:
        self.origin_base = origin_base
        self.lib = ctypes.CDLL('./cpp_libs/Build/libDnaTranscoder.so')
        self.lib.getConsensusSequence.restype = ctypes.c_void_p
        self.lib.getConsensusSequence.argtypes = [ctypes.POINTER(ctypes.c_char_p), ctypes.c_int, ctypes.POINTER(ctypes.c_int)]
        self.lib.free_consensus_sequence.argtypes = [ctypes.c_void_p]

    @abstractmethod
    def encode(self, data: Union[np.uint8, int]) -> str:
        pass

    @abstractmethod
    def decode(self, bases: List[str]) -> np.array:
        pass

    def encode_many(self,datas:List):
        encoded_datas = []
        for data in datas:
            encoded_datas.append(self.encode(data))
        return encoded_datas

    def decode_with_consensus_base(self, bases_list: List, trim_margin: int = 0):
        decoded_datas = []
        for bases_item in bases_list:
            sequences_c = [bytes(''.join(bases), 'utf-8') for bases in bases_item]
            sequences_ptrs = (ctypes.c_char_p * len(sequences_c))(*sequences_c)
            sequence_lengths = (ctypes.c_int * len(sequences_c))(*[len(seq) for seq in sequences_c])

            result_ptr = self.lib.getConsensusSequence(sequences_ptrs, len(sequences_c), sequence_lengths)
            result = ctypes.cast(result_ptr, ctypes.c_char_p).value
            consensus_base = result.decode('utf-8')
            self.lib.free_consensus_sequence(result_ptr)
            decoded_datas.append(self.decode(list(consensus_base)))
        return decoded_datas

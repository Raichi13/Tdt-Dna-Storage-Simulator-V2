import numpy as np
from typing import Union, List
import ctypes
from transcoder_base import TranscoderBase

class BinaryDNATranscoder(TranscoderBase):
    def __init__(self, origin_base: str = "A") -> None:
        super().__init__(origin_base)
        self.mapper = {
            "A": {0: "G", 1: "C"},
            "G": {0: "C", 1: "A"},
            "C": {0: "A", 1: "G"},
        }
        self.reverse_mapper = {
            "A": {"G": 0, "C": 1},
            "G": {"C": 0, "A": 1},
            "C": {"A": 0, "G": 1},
        }

    def __bytes_to_binary(self, data: Union[np.uint8, int]) -> np.array:
        bits = []
        for byte in data:
            for i in range(8):
                bits.append((byte >> (7 - i)) & 1)
        return np.array(bits, dtype=np.uint8)

    def __binary_to_bytes(self, bits: np.array) -> np.array:
        bytes_list = []
        for i in range(0, len(bits), 8):
            byte = 0
            for j in range(8):
                if i + j < len(bits):
                    byte |= bits[i + j] << (7 - j)
            bytes_list.append(byte)
        return np.array(bytes_list, dtype=np.uint8)

    def encode(self, data: Union[np.uint8, int]) -> str:
        bits = self.__bytes_to_binary(data)
        bases = [self.origin_base]
        for bit in bits:
            bases.append(self.mapper[bases[-1]][bit])
        return "".join(bases)

    def decode(self, bases: List[str]) -> np.array:
        bits = []
        for i in range(len(bases) - 1):
            bits.append(self.reverse_mapper[bases[i]][bases[i + 1]])
        return self.__binary_to_bytes(np.array(bits, dtype=np.uint8))

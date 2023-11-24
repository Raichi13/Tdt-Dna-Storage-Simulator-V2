import ctypes

class TdT:
    def __init__(self, target_bases, reaction_cycle, molecule_number, miss_extension_probability, deletion_probability, over_extension_probability, bases_list=None):
        self.target_bases = target_bases
        self.reaction_cycle = reaction_cycle
        self.molecule_number = molecule_number
        self.miss_extension_probability = miss_extension_probability
        self.deletion_probability = deletion_probability
        self.over_extension_probability = over_extension_probability
        self.miss_extension_count = 0
        self.deletion_count = 0
        self.over_extension_count = 0
        self.synthesis_products = []
        if bases_list is None:
            self.bases_list = ['A','G','C','T']
        else:
            self.bases_list = bases_list
        self.lib = ctypes.CDLL('./cpp_libs/Build/libtdt.so')

        # C++関数の引数と戻り値の型を設定
        self.lib.extension.argtypes = [ctypes.c_char_p, ctypes.c_double, ctypes.c_int, ctypes.c_char_p]
        self.lib.extension.restype = ctypes.c_int
        self.lib.synthesis.argtypes = [ctypes.c_char_p, ctypes.c_double, ctypes.c_int, ctypes.c_char_p, ctypes.c_int]
        self.lib.synthesis.restype = ctypes.c_int
        self.lib.free_memory.argtypes = [ctypes.c_int]
        self.lib.free_memory.restype = None
        self.lib.get_data_pointer.argtypes = [ctypes.c_int]
        self.lib.get_data_pointer.restype = ctypes.c_void_p

    def _get_data_from_id(self, data_id):
        ptr = self.lib.get_data_pointer(data_id)
        if ptr:
            result = ctypes.cast(ptr, ctypes.c_char_p).value.decode('utf-8')
            return result
        return ""

    def __synthesis(self, target_base):
        bases_list_str = ''.join(self.bases_list)
        syn_id = self.lib.synthesis(target_base.encode('utf-8'), 
                                    self.miss_extension_probability, 
                                    self.reaction_cycle, 
                                    bases_list_str.encode('utf-8'), 
                                    self.molecule_number)
        result = self._get_data_from_id(syn_id)
        self.lib.free_memory(syn_id)
        return [seq for seq in result.split(';') if seq]

    def synthesis(self):
        self.synthesis_products = []
        for tb in self.target_bases:
            self.synthesis_products.append(self.__synthesis(tb))
        return self.synthesis_products
from decoder_base import DecoderBase

class DefaultDecoder(DecoderBase):
    def __init__(self, bytes_per_oligo: int, address_size: int) -> None:
        super().__init__(bytes_per_oligo, address_size)
    
    def decode(self,data):
        sp,raw_data = super().assemble_saparated_data(data)
        self.for_error_check = sp
        return raw_data